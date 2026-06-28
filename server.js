const express = require('express');
const ytdl = require('@distube/ytdl-core');
const session = require('express-session');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.use(session({
  secret: 'supersecretkey123',
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 30 * 60 * 1000 }
}));

// Login
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (username === 'test' && password === 'test') {
    req.session.loggedIn = true;
    res.json({ success: true });
  } else {
    res.status(401).json({ success: false, message: 'Invalid credentials' });
  }
});

// Auth middleware
const isAuthenticated = (req, res, next) => {
  if (req.session.loggedIn) return next();
  res.status(401).json({ error: 'Unauthorized' });
};

// Get video info
app.get('/info', isAuthenticated, async (req, res) => {
  try {
    const url = req.query.url;
    if (!ytdl.validateURL(url)) return res.status(400).json({ error: 'Invalid YouTube URL' });

    const info = await ytdl.getInfo(url);
    const formats = info.formats
      .filter(f => f.hasVideo || f.hasAudio)
      .map(f => ({
        itag: f.itag,
        quality: f.qualityLabel || (f.audioBitrate ? f.audioBitrate + 'kbps' : 'Unknown'),
        container: f.container,
        hasVideo: f.hasVideo,
        hasAudio: f.hasAudio,
        size: f.contentLength ? (parseInt(f.contentLength)/1024/1024).toFixed(1) + ' MB' : 'Unknown'
      }));

    res.json({
      title: info.videoDetails.title,
      thumbnail: info.videoDetails.thumbnails[0].url,
      formats: formats.slice(0, 15)
    });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Failed to fetch video info' });
  }
});

// Download
app.get('/download', isAuthenticated, (req, res) => {
  try {
    const { url, itag, format } = req.query;

    let options = { 
      quality: itag ? parseInt(itag) : 'highest' 
    };

    if (format === 'audio') {
      options = { 
        filter: 'audioonly', 
        quality: 'highestaudio' 
      };
    }

    const stream = ytdl(url, options);
    const title = 'video'; // will be updated if possible

    ytdl.getInfo(url).then(info => {
      const safeTitle = info.videoDetails.title.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 80);
      const ext = format === 'audio' ? 'mp3' : 'mp4';
      res.header('Content-Disposition', `attachment; filename="${safeTitle}.${ext}"`);
    }).catch(() => {});

    res.header('Content-Type', format === 'audio' ? 'audio/mpeg' : 'video/mp4');

    stream.pipe(res);

    stream.on('error', (err) => {
      console.error(err);
      if (!res.headersSent) res.status(500).send('Download failed');
    });

  } catch (e) {
    console.error(e);
    res.status(500).send('Server error');
  }
});

app.listen(PORT, () => {
  console.log(`✅ Server running at http://localhost:${PORT}`);
});