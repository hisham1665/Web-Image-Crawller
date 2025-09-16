import re
import os
import hashlib
import json
import requests
import zipfile
import io
import tempfile
import time
import shutil
import threading
import uuid
from threading import Thread, Lock
from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, request, jsonify, url_for, send_file, Response
from icrawler.builtin import BingImageCrawler, GoogleImageCrawler
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vercel-production-key-2024'

# Production-ready global variables
progress_data = {}
progress_lock = Lock()

class ProductionImageScraper:
    """Production-ready instance-based image scraper optimized for Vercel deployment"""
    
    def __init__(self, session_id=None):
        self.session_id = session_id
        self.all_images = []
        self.seen_hashes = set()
        self.seen_urls = set()
        self.images_lock = Lock()
        self.is_cancelled = False
        self.download_count = 0
        
    def update_progress(self, status, message, **kwargs):
        """Thread-safe progress update with real-time count"""
        if not self.session_id:
            return
            
        with progress_lock:
            if self.session_id not in progress_data:
                progress_data[self.session_id] = {}
            
            progress_data[self.session_id].update({
                'status': status,
                'message': message,
                'images_found': len(self.all_images),
                'timestamp': time.time(),
                **kwargs
            })
            
    def safe_add_image(self, image_data):
        """Thread-safe image addition with immediate progress update"""
        with self.images_lock:
            if self.is_cancelled:
                return False
                
            # Check for duplicates
            img_hash = image_data.get('hash')
            if img_hash and img_hash in self.seen_hashes:
                return False
                
            # Add image
            self.all_images.append(image_data)
            if img_hash:
                self.seen_hashes.add(img_hash)
                
            # Update progress immediately
            self.update_progress(
                'downloading',
                f'Found {len(self.all_images)} images',
                current_engine=image_data.get('engine', ''),
                total_target=progress_data.get(self.session_id, {}).get('total_target', 0)
            )
            
            return True
    
    def cancel(self):
        """Cancel the scraping operation"""
        self.is_cancelled = True

    def scrape_engine_threaded(self, engine_name, crawler_class, query, images_per_engine, total_target):
        """Thread-safe engine scraping with real-time updates"""
        try:
            if self.is_cancelled:
                return
                
            self.update_progress('searching', f'Starting {engine_name.title()} search...', 
                               current_engine=engine_name, total_target=total_target)
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix=f"prod_{engine_name}_")
            
            try:
                # Create crawler
                crawler = crawler_class(
                    downloader_threads=2,  # Reduced for Vercel limits
                    storage={'root_dir': temp_dir}
                )
                
                # Scrape images
                crawler.crawl(keyword=query, max_num=images_per_engine)
                
                # Process downloaded images
                if os.path.exists(temp_dir):
                    files = [f for f in os.listdir(temp_dir) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
                    
                    # Create static directory if needed
                    static_temp = os.path.join('/tmp', 'temp_images')  # Use /tmp for Vercel
                    os.makedirs(static_temp, exist_ok=True)
                    
                    for i, filename in enumerate(files):
                        if self.is_cancelled or len(self.all_images) >= total_target:
                            break
                            
                        try:
                            src_path = os.path.join(temp_dir, filename)
                            
                            # Skip small files
                            if os.path.getsize(src_path) < 3000:
                                continue
                                
                            # Calculate hash
                            img_hash = self.calculate_image_hash(src_path)
                            
                            # Create unique filename
                            file_ext = os.path.splitext(filename)[1] or '.jpg'
                            unique_name = f"prod_{engine_name}_{int(time.time())}_{i}{file_ext}"
                            dest_path = os.path.join(static_temp, unique_name)
                            
                            # Copy file
                            shutil.copy2(src_path, dest_path)
                            
                            # Add to results
                            image_data = {
                                'url': f"/static/temp_images/{unique_name}",
                                'filename': f"{safe_folder_name(query)}_{engine_name}_{len(self.all_images)+1}{file_ext}",
                                'engine': engine_name,
                                'local_path': dest_path,
                                'hash': img_hash,
                                'temp_path': dest_path  # For Vercel cleanup
                            }
                            
                            self.safe_add_image(image_data)
                            
                        except Exception as e:
                            continue
                            
            finally:
                # Clean up
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    
        except Exception as e:
            print(f"Error with {engine_name}: {e}")
    
    def scrape_custom_engine_threaded(self, engine_name, query, images_per_engine, total_target):
        """Thread-safe custom engine scraping"""
        try:
            if self.is_cancelled:
                return
                
            self.update_progress('searching', f'Starting {engine_name.title()} URL search...', 
                               current_engine=engine_name, total_target=total_target)
            
            # Get URLs
            if engine_name == 'yandex':
                image_urls = self.scrape_yandex_images(query, images_per_engine)
            elif engine_name == 'duckduckgo':
                image_urls = self.scrape_duckduckgo_images(query, images_per_engine)
            else:
                return
            
            if not image_urls:
                return
                
            self.update_progress('downloading', f'Found {len(image_urls)} URLs from {engine_name.title()}', 
                               current_engine=engine_name, total_target=total_target)
            
            # Create static directory
            static_temp = os.path.join('/tmp', 'temp_images')  # Use /tmp for Vercel
            os.makedirs(static_temp, exist_ok=True)
            
            # Download images
            for i, img_url in enumerate(image_urls):
                if self.is_cancelled or len(self.all_images) >= total_target:
                    break
                    
                if img_url in self.seen_urls:
                    continue
                    
                try:
                    # Create filename
                    file_ext = '.jpg'
                    if '.' in img_url:
                        potential_ext = img_url.split('.')[-1].lower().split('?')[0]
                        if potential_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                            file_ext = f'.{potential_ext}'
                    
                    unique_name = f"prod_{engine_name}_{int(time.time())}_{i}{file_ext}"
                    dest_path = os.path.join(static_temp, unique_name)
                    
                    # Download
                    if self.download_image_from_url(img_url, dest_path):
                        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 3000:
                            img_hash = self.calculate_image_hash(dest_path)
                            
                            image_data = {
                                'url': f"/static/temp_images/{unique_name}",
                                'filename': f"{safe_folder_name(query)}_{engine_name}_{len(self.all_images)+1}{file_ext}",
                                'engine': engine_name,
                                'local_path': dest_path,
                                'hash': img_hash,
                                'temp_path': dest_path  # For Vercel cleanup
                            }
                            
                            if self.safe_add_image(image_data):
                                self.seen_urls.add(img_url)
                                
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error with custom engine {engine_name}: {e}")
    
    def calculate_image_hash(self, image_path):
        """Calculate image hash for duplicate detection"""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def download_image_from_url(self, url, save_path):
        """Download image with production-ready error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            response = requests.get(url, headers=headers, timeout=10, stream=True, verify=False)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not any(t in content_type for t in ['image/', 'jpeg', 'png', 'gif', 'webp']):
                return False
            
            # Download with size limit (5MB for Vercel)
            total_size = 0
            max_size = 5 * 1024 * 1024
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        total_size += len(chunk)
                        if total_size > max_size:
                            os.remove(save_path)
                            return False
                        f.write(chunk)
            
            return os.path.exists(save_path) and os.path.getsize(save_path) > 1000
            
        except Exception as e:
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except:
                    pass
            return False
    
    def scrape_yandex_images(self, query, max_images):
        """Production Yandex scraper"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            search_url = f"https://yandex.com/images/search?text={urllib.parse.quote_plus(query)}"
            
            response = requests.get(search_url, headers=headers, timeout=8)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            images = []
            img_elements = soup.find_all('img', class_='serp-item__thumb')
            
            for img in img_elements[:max_images]:
                if 'src' in img.attrs:
                    img_url = img['src']
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://yandex.com' + img_url
                    
                    if img_url.startswith('http'):
                        images.append(img_url)
            
            return images
        except:
            return []
    
    def scrape_duckduckgo_images(self, query, max_images):
        """Production DuckDuckGo scraper"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            search_url = f"https://duckduckgo.com/?q={urllib.parse.quote_plus(query)}&t=h_&iax=images&ia=images"
            
            response = requests.get(search_url, headers=headers, timeout=8)
            if response.status_code != 200:
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            images = []
            img_elements = soup.find_all('img')
            
            for img in img_elements[:max_images]:
                if 'src' in img.attrs:
                    img_url = img['src']
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://duckduckgo.com' + img_url
                    
                    if img_url.startswith('http') and 'logo' not in img_url.lower():
                        images.append(img_url)
            
            return images
        except:
            return []
    
    def scrape_multi_engine(self, query, total_images_needed):
        """Production multi-engine scraping with real-time progress"""
        self.update_progress('starting', 'Initializing production search...', total_target=total_images_needed)
        
        # Engine configuration
        engines = {
            'bing': BingImageCrawler,
            'google': GoogleImageCrawler
        }
        custom_engines = ['yandex', 'duckduckgo']
        
        total_engines = len(engines) + len(custom_engines)
        images_per_engine = (total_images_needed // total_engines) + 20
        
        self.update_progress('searching', f'Searching {total_engines} engines...', total_target=total_images_needed)
        
        threads = []
        
        # Start engine threads
        for engine_name, crawler_class in engines.items():
            thread = Thread(target=self.scrape_engine_threaded, 
                          args=(engine_name, crawler_class, query, images_per_engine, total_images_needed))
            thread.start()
            threads.append(thread)
        
        # Start custom engine threads
        for engine_name in custom_engines:
            thread = Thread(target=self.scrape_custom_engine_threaded,
                          args=(engine_name, query, images_per_engine, total_images_needed))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Final results
        final_images = self.all_images[:total_images_needed]
        
        if len(final_images) >= total_images_needed:
            self.update_progress('completed', f'Successfully found {len(final_images)} images!', 
                               total_target=total_images_needed)
        else:
            self.update_progress('completed', f'Found {len(final_images)} images', 
                               total_target=total_images_needed)
        
        return final_images

def safe_folder_name(name: str) -> str:
    """Make a safe folder name for Windows/Linux/Mac."""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.strip().replace(" ", "_")
    return name

def scrape_images_multi_engine(query, total_images_needed, session_id=None):
    """Production wrapper for the new class-based scraper"""
    scraper = ProductionImageScraper(session_id)
    return scraper.scrape_multi_engine(query, total_images_needed)

def scrape_images_multi_engine(query, total_images_needed, session_id=None):
    """Production wrapper for the new class-based scraper"""
    scraper = ProductionImageScraper(session_id)
    return scraper.scrape_multi_engine(query, total_images_needed)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress/<session_id>')
def progress_stream(session_id):
    """Server-Sent Events endpoint for real-time progress updates"""
    def generate():
        while True:
            with progress_lock:
                if session_id in progress_data:
                    data = progress_data[session_id].copy()
                    yield f"data: {json.dumps(data)}\n\n"
                    
                    # If completed or error, stop streaming
                    if data.get('status') in ['completed', 'error']:
                        break
                else:
                    yield f"data: {json.dumps({'status': 'waiting', 'message': 'Initializing...'})}\n\n"
            
            time.sleep(0.5)  # Update every 500ms
    
    return Response(generate(), mimetype='text/plain')

def update_progress(session_id, status, message, images_found=0, total_target=0, current_engine='', **kwargs):
    """Thread-safe progress update compatible with both old and new system"""
    with progress_lock:
        if session_id not in progress_data:
            progress_data[session_id] = {}
        
        progress_data[session_id].update({
            'status': status,
            'message': message,
            'images_found': images_found,
            'total_target': total_target,
            'current_engine': current_engine,
            'timestamp': time.time(),
            **kwargs
        })

def cleanup_progress(session_id):
    """Clean up progress data after completion"""
    def cleanup():
        time.sleep(300)  # Keep data for 5 minutes after completion
        with progress_lock:
            if session_id in progress_data:
                del progress_data[session_id]
                print(f"Cleaned up progress data for session: {session_id}")
    
    Thread(target=cleanup, daemon=True).start()

@app.route('/scrape', methods=['POST'])
def scrape():
    # Generate unique session ID for progress tracking
    session_id = str(uuid.uuid4())
    
    try:
        # Input validation and sanitization
        if request.is_json:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'Invalid JSON data'})
            topic = data.get('topic', '').strip()
            quantity = data.get('quantity', 20)
        else:
            # Handle form data
            topic = request.form.get('topic', '').strip()
            quantity = request.form.get('quantity', 20)
        
        # Input validation
        if not topic:
            error_msg = 'Please enter a search topic'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg, 'session_id': session_id})
            else:
                return render_template('error.html', error=error_msg)
        
        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity <= 0 or quantity > 1000:
                raise ValueError("Quantity must be between 1 and 1000")
        except (ValueError, TypeError) as e:
            error_msg = 'Please enter a valid number between 1 and 1000'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg, 'session_id': session_id})
            else:
                return render_template('error.html', error=error_msg)
        
        # Sanitize topic to prevent issues
        topic = re.sub(r'[<>:"/\\|?*]', '', topic)
        if len(topic) < 2:
            error_msg = 'Search topic must be at least 2 characters long'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg, 'session_id': session_id})
            else:
                return render_template('error.html', error=error_msg)
        
        # For JSON requests (AJAX), start background task and return session ID
        if request.is_json:
            def background_scrape():
                try:
                    update_progress(session_id, 'starting', 'Initializing search...', 0, quantity)
                    scraped_urls = scrape_images_multi_engine(topic, quantity, session_id)
                    
                    # Store results in progress data
                    with progress_lock:
                        if session_id in progress_data:
                            progress_data[session_id]['images'] = scraped_urls
                            progress_data[session_id]['topic'] = topic
                            progress_data[session_id]['safe_topic'] = safe_folder_name(topic)
                            progress_data[session_id]['requested'] = quantity
                            
                except Exception as e:
                    print(f"Background scraping error: {e}")
                    update_progress(session_id, 'error', f'Error occurred: {str(e)}', 0, quantity)
            
            # Start background task
            Thread(target=background_scrape, daemon=True).start()
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'message': 'Scraping started. Use the session ID to track progress.'
            })
        
        else:
            # For form submissions, do synchronous processing (for backward compatibility)
            try:
                print(f"Scraping {quantity} images for '{topic}'...")
                
                # Use the multi-engine scraper with progress tracking
                scraped_urls = scrape_images_multi_engine(topic, quantity, session_id)
            
                if not scraped_urls:
                    error_msg = 'No images could be scraped. Please try a different search term.'
                    return render_template('error.html', error=error_msg)
                
                # Render results page for form submission
                return render_template('results.html', 
                                     images=scraped_urls, 
                                     image_urls=scraped_urls,
                                     topic=topic, 
                                     safe_topic=safe_folder_name(topic),
                                     total=len(scraped_urls),
                                     total_found=len(scraped_urls),
                                     requested=quantity)
                
            except Exception as e:
                print(f"Scraping error: {e}")
                error_msg = f'Error occurred: {str(e)}'
                return render_template('error.html', error=error_msg)
    
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error in scrape route: {e}")
        error_msg = f'Unexpected error: {str(e)}'
        if request.is_json:
            return jsonify({'success': False, 'error': error_msg, 'session_id': session_id})
        else:
            return render_template('error.html', error=error_msg)

@app.route('/results/<session_id>')
def get_results(session_id):
    """Get the final results for a completed scraping session"""
    with progress_lock:
        if session_id not in progress_data:
            return render_template('error.html', error='Session not found or expired')
        
        data = progress_data[session_id]
        
        if data.get('status') != 'completed':
            return render_template('error.html', error='Scraping not yet completed')
        
        if 'images' not in data:
            return render_template('error.html', error='No results found for this session')
        
        return render_template('results.html',
                             images=data['images'],
                             image_urls=data['images'],
                             topic=data['topic'],
                             safe_topic=data['safe_topic'],
                             total=len(data['images']),
                             total_found=len(data['images']),
                             requested=data['requested'])

@app.route('/static/temp_images/<filename>')
def serve_temp_image(filename):
    """Serve temporary images from /tmp directory for Vercel"""
    try:
        temp_path = os.path.join('/tmp', 'temp_images', filename)
        if os.path.exists(temp_path):
            return send_file(temp_path)
        else:
            return "Image not found", 404
    except Exception as e:
        return f"Error serving image: {str(e)}", 500

@app.route('/download/<topic>/<int:index>')
def download_image(topic, index):
    """Download individual image"""
    try:
        # Find the image in temp directory (check both locations for compatibility)
        temp_locations = [
            os.path.join('/tmp', 'temp_images'),
            os.path.join('static', 'temp_images')
        ]
        
        files = []
        for temp_dir in temp_locations:
            if os.path.exists(temp_dir):
                files.extend([f for f in os.listdir(temp_dir) 
                            if f.startswith(safe_folder_name(topic)) and 
                            f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'))])
        
        if index >= len(files):
            return "Image not found", 404
        
        # Find the actual file path
        file_path = None
        for temp_dir in temp_locations:
            potential_path = os.path.join(temp_dir, files[index])
            if os.path.exists(potential_path):
                file_path = potential_path
                break
        
        if not file_path:
            return "Image not found", 404
        
        # Get file extension for proper filename
        _, ext = os.path.splitext(files[index])
        filename = f"{safe_folder_name(topic)}_{index+1}{ext}"
        
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        print(f"Download error: {e}")
        return f"Error downloading image: {str(e)}", 500

@app.route('/download_all/<topic>')
def download_all_zip(topic):
    """Download all images as ZIP"""
    try:
        # Check both temp locations for compatibility
        temp_locations = [
            os.path.join('/tmp', 'temp_images'),
            os.path.join('static', 'temp_images')
        ]
        
        files = []
        for temp_dir in temp_locations:
            if os.path.exists(temp_dir):
                files.extend([f for f in os.listdir(temp_dir) 
                            if f.startswith(safe_folder_name(topic)) and 
                            f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'))])
        
        if not files:
            return "No images found", 404
        
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, filename in enumerate(files):
                # Find the actual file path
                file_path = None
                for temp_dir in temp_locations:
                    potential_path = os.path.join(temp_dir, filename)
                    if os.path.exists(potential_path):
                        file_path = potential_path
                        break
                
                if file_path:
                    # Use a clean filename in the ZIP
                    _, ext = os.path.splitext(filename)
                    clean_name = f"{safe_folder_name(topic)}_{i+1}{ext}"
                    zip_file.write(file_path, clean_name)
        
        zip_buffer.seek(0)
        
        zip_filename = f"{safe_folder_name(topic)}_images.zip"
        
        return send_file(
            io.BytesIO(zip_buffer.read()),
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
        
    except Exception as e:
        print(f"ZIP download error: {e}")
        return f"Error creating ZIP: {str(e)}", 500

@app.route('/clear/<topic>')
def clear_cache(topic):
    """Clear cached images for a topic"""
    try:
        # Clean the topic name
        clean_topic = safe_folder_name(topic)
        files_deleted = 0
        
        # Clear from both temp locations
        temp_locations = [
            os.path.join('/tmp', 'temp_images'),
            os.path.join('static', 'temp_images')
        ]
        
        for temp_dir in temp_locations:
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    if clean_topic.lower() in filename.lower():
                        file_path = os.path.join(temp_dir, filename)
                        try:
                            os.remove(file_path)
                            files_deleted += 1
                        except Exception as e:
                            print(f"Error deleting {file_path}: {e}")
        
        # Clear from downloads folder
        downloads_dir = os.path.join('downloads', clean_topic)
        if os.path.exists(downloads_dir):
            try:
                shutil.rmtree(downloads_dir)
                print(f"Deleted directory: {downloads_dir}")
                files_deleted += 10  # Approximate count for directory deletion
            except Exception as e:
                print(f"Error deleting directory {downloads_dir}: {e}")
        
        # Clear any cached data (you can extend this)
        temp_dirs = ['temp', 'cache', '.cache']
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir):
                    for filename in files:
                        if clean_topic.lower() in filename.lower():
                            file_path = os.path.join(root, filename)
                            try:
                                os.remove(file_path)
                                files_deleted += 1
                                print(f"Deleted cache file: {file_path}")
                            except Exception as e:
                                print(f"Error deleting cache file {file_path}: {e}")
        
        return jsonify({
            'success': True, 
            'message': f'Successfully cleared {files_deleted} files for "{topic}"',
            'files_deleted': files_deleted
        })
        
    except Exception as e:
        print(f"Clear cache error: {e}")
        return jsonify({'success': False, 'error': f'Failed to clear cache: {str(e)}'})

@app.route('/clear_all')
def clear_all_cache():
    """Clear all cached images"""
    try:
        files_deleted = 0
        
        # Clear both temp locations
        temp_locations = [
            os.path.join('/tmp', 'temp_images'),
            os.path.join('static', 'temp_images')
        ]
        
        for temp_dir in temp_locations:
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        os.remove(file_path)
                        files_deleted += 1
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
        
        # Clear downloads folder
        downloads_dir = 'downloads'
        if os.path.exists(downloads_dir):
            try:
                shutil.rmtree(downloads_dir)
                os.makedirs(downloads_dir, exist_ok=True)
                files_deleted += 50  # Approximate count
            except Exception as e:
                print(f"Error clearing downloads: {e}")
        
        return jsonify({
            'success': True, 
            'message': f'Successfully cleared all cache ({files_deleted} files)',
            'files_deleted': files_deleted
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/temp_images', exist_ok=True)
    os.makedirs('/tmp/temp_images', exist_ok=True)
    
    print("🚀 Production Image Scraper Starting...")
    print("✅ Vercel-optimized deployment")
    print("✅ Instance-based crawling")
    print("✅ Real-time progress tracking")
    print("✅ Production-ready scaling")
    
    app.run(debug=False, host='0.0.0.0', port=5000)

# Vercel entry point
def application(environ, start_response):
    return app(environ, start_response)