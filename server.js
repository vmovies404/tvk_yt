const express = require('express');
const ytdl = require('@distube/ytdl-core');
const session = require('express-session');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

app.use(session({
  secret: 'tvk-secret',
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 60 * 60 * 1000 }
}));

// Login
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (username === 'test' && password === 'test') {
    req.session.loggedIn = true;
    res.json({ success: true });
  } else {
    res.status(401).json({ success: false });
  }
});

const isAuthenticated = (req, res, next) => {
  if (req.session.loggedIn) return next();
  res.status(401).json({ error: 'Unauthorized' });
};

// Info
app.get('/info', isAuthenticated, async (req, res) => {
  try {
    const url = req.query.url;
    const info = await ytdl.getInfo(url);
    const formats = info.formats
      .filter(f => f.hasVideo)
      .map(f => ({
        itag: f.itag,
        quality: f.qualityLabel || 'Unknown',
        container: f.container,
        size: f.contentLength ? (parseInt(f.contentLength)/1024/1024).toFixed(1) + ' MB' : 'Unknown'
      }));

    res.json({
      title: info.videoDetails.title,
      thumbnail: info.videoDetails.thumbnails[0].url,
      formats: formats
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Download
app.get('/download', isAuthenticated, (req, res) => {
  try {
    const { url, itag, format } = req.query;
    let options = itag ? { quality: parseInt(itag) } : { quality: 'highest' };

    if (format === 'audio') {
      options = { filter: 'audioonly', quality: 'highestaudio' };
    }

    const stream = ytdl(url, options);
    ytdl.getInfo(url).then(info => {
      const title = info.videoDetails.title.replace(/[^a-zA-Z0-9]/g, '_');
      const ext = format === 'audio' ? 'mp3' : 'mp4';
      res.header('Content-Disposition', `attachment; filename="${title}.${ext}"`);
    });

    stream.pipe(res);
  } catch (e) {
    res.status(500).send('Download failed');
  }
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));