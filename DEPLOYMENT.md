# Production Image Scraper

A scalable, production-ready image scraper optimized for Vercel deployment with real-time progress tracking.

## 🚀 Features

- **Instance-based Crawling**: Optimized class-based architecture for better resource management
- **Real-time Progress**: Live updates showing actual crawled image count
- **Multi-engine Search**: Bing, Google, Yandex, DuckDuckGo support
- **Vercel Optimized**: Serverless deployment ready
- **Duplicate Detection**: Hash-based deduplication
- **Production Ready**: Error handling, timeouts, resource limits

## 📦 Quick Deploy to Vercel

1. **Clone & Setup**:
```bash
git clone <your-repo>
cd Web-Image-Crawller
```

2. **Deploy to Vercel**:
```bash
npm i -g vercel
vercel --prod
```

3. **Environment Setup**: No additional environment variables needed!

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

Visit `http://localhost:5000`

## 📁 File Structure

```
├── app.py              # Main Flask application
├── vercel.json         # Vercel deployment config  
├── requirements.txt    # Python dependencies
├── static/             # Static assets
│   ├── css/           # Styles
│   ├── js/            # Frontend JavaScript
│   └── temp_images/   # Temporary images (local)
└── templates/         # HTML templates
```

## ⚡ Production Optimizations

- **Serverless Compatible**: Uses `/tmp` directory for Vercel
- **Resource Limits**: 5MB max file size, optimized timeouts
- **Thread Safety**: Proper locking mechanisms
- **Memory Efficient**: Streaming downloads, cleanup routines
- **Error Resilient**: Comprehensive error handling

## 🔄 Real-time Progress Features

- Live image count updates
- Current search engine status
- Progress bar with percentage
- Cancellation support
- Session-based tracking

## 🌐 API Endpoints

- `GET /` - Main interface
- `POST /scrape` - Start image scraping
- `GET /progress/<session_id>` - Real-time progress (SSE)
- `GET /results/<session_id>` - Get final results
- `GET /download/<topic>/<index>` - Download single image
- `GET /download_all/<topic>` - Download ZIP archive
- `POST /clear/<topic>` - Clear topic cache

## 📊 Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: Vanilla JavaScript, CSS3
- **Crawling**: icrawler, requests, BeautifulSoup
- **Deployment**: Vercel serverless
- **Progress**: Server-Sent Events (SSE)

## 🔒 Production Security

- Input validation and sanitization
- File type verification
- Size limits and timeouts
- Path traversal protection
- CORS handling

## 🚀 Deployment Notes

- No additional packages required
- Works with Vercel's free tier
- Automatic scaling
- Global CDN distribution
- Zero-config deployment

## 📈 Performance

- Multi-threaded crawling
- Parallel engine execution  
- Efficient duplicate detection
- Resource cleanup
- Optimized for serverless cold starts