# 🖼️ Flask Image Scraper Web App

A web-based image scraper that downloads images from both Bing and Google search engines, removes duplicates, and provides a clean web interface for browsing and downloading the results.

## ✨ Features

- **Dual Search Engine**: Scrapes images from both Bing and Google
- **Duplicate Removal**: Automatically detects and removes duplicate images using MD5 hash comparison
- **Web Interface**: Clean, responsive web interface with modern design
- **Image Gallery**: View scraped images in a beautiful grid layout with lightbox functionality
- **Download Options**: Download individual images or view them in full size
- **Progress Tracking**: Shows real-time statistics of scraping progress
- **Topic Management**: Organize images by search topics and clear them when needed

## 🚀 Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd Web-Image-Crawller
   ```

2. **Install required dependencies**
   ```bash
   pip install Flask icrawler
   ```

## 💻 Usage

### Starting the Web Application

1. **Run the Flask app**
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

### Using the Web Interface

1. **Enter Search Topic**: Type what you want to search for (e.g., "cats", "mountains", "cars")
2. **Set Quantity**: Choose how many images you want (1-100)
3. **Click "Start Scraping"**: The app will search both Bing and Google
4. **View Results**: Browse the downloaded images in a responsive grid
5. **Download Images**: Click individual download links or view full-size images
6. **Manage Topics**: Clear downloaded images for any topic when done

### Features Explained

- **Parallel Scraping**: The app searches Bing and Google simultaneously for faster results
- **Smart Deduplication**: Uses MD5 hashing to identify and remove duplicate images
- **Safe File Naming**: Automatically sanitizes search terms for safe folder/file names
- **Error Handling**: Gracefully handles network errors and invalid requests
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 📁 Project Structure

```
Flask-Image-Scraper/
├── app.py                 # Main Flask application
├── Scrapper.py           # Original command-line scraper (legacy)
├── templates/
│   ├── index.html        # Home page with search form
│   └── results.html      # Results page with image gallery
├── static/
│   ├── style.css         # Additional CSS styles
│   └── downloads/        # Downloaded images storage
│       └── [topic]/      # Images organized by search topic
├── README.md             # This file
└── LICENSE               # License file
```

## 🎯 API Endpoints

- **GET /**: Home page with search form
- **POST /scrape**: Process image scraping request
- **GET /clear/<topic>**: Clear downloaded images for a specific topic
- **Static files**: Serve downloaded images and CSS

## ⚙️ Configuration

You can modify these settings in `app.py`:

```python
# Maximum number of images per request
MAX_IMAGES = 100

# Download directory
SAVE_DIR = "static/downloads"

# Flask configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
```

## 🔧 Advanced Usage

### Command Line Version

The original command-line version is still available in `Scrapper.py`:

```bash
python Scrapper.py
```

### Custom Storage

To change the download location, modify the `SAVE_DIR` variable in `app.py`.

### Production Deployment

For production use, consider:

1. **Use a production WSGI server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Set up a reverse proxy** with Nginx or Apache

3. **Configure environment variables** for sensitive settings

## 🛡️ Error Handling

The application includes comprehensive error handling for:

- Invalid search terms
- Network connectivity issues
- File system errors
- Missing dependencies
- Quota limitations from search engines

## 📱 Browser Compatibility

- ✅ Chrome/Chromium (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

## ⚠️ Important Notes

1. **Respect Copyright**: Only use downloaded images in accordance with copyright laws
2. **Rate Limiting**: Search engines may impose rate limits; use responsibly
3. **Storage Space**: Downloaded images are stored locally; monitor disk usage
4. **Network Usage**: Large image downloads may consume significant bandwidth

## 🆘 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install Flask icrawler
   ```

2. **Permission errors on Windows**
   - Run as administrator or change download directory

3. **No images found**
   - Try different search terms
   - Check internet connection
   - Verify search engines are accessible

4. **Slow scraping**
   - Normal for large quantities
   - Consider reducing number of images
   - Check network connection speed

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the error messages in the web interface
3. Check the terminal output for detailed error logs
4. Open an issue on the repository

---

**Happy Image Scraping! 🎉**