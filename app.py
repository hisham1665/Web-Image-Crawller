import re
import os
import hashlib
import json
import requests
import zipfile
import io
import tempfile
import time
from threading import Thread
from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, request, jsonify, url_for, send_file
from icrawler.builtin import BingImageCrawler, GoogleImageCrawler
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

def safe_folder_name(name: str) -> str:
    """Make a safe folder name for Windows/Linux/Mac."""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.strip().replace(" ", "_")
    return name

def calculate_image_hash(image_path):
    """Calculate hash of image file for duplicate detection"""
    try:
        with open(image_path, 'rb') as f:
            content = f.read()
            return hashlib.md5(content).hexdigest()
    except:
        return None

def scrape_yandex_images(query, max_images):
    """Custom Yandex image scraper"""
    images = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        search_url = f"https://yandex.com/images/search?text={urllib.parse.quote_plus(query)}"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find image elements in Yandex
        img_elements = soup.find_all('img', class_='serp-item__thumb')
        
        for i, img in enumerate(img_elements[:max_images]):
            if 'src' in img.attrs:
                img_url = img['src']
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://yandex.com' + img_url
                
                if img_url.startswith('http'):
                    images.append(img_url)
        
        print(f"Yandex found {len(images)} image URLs")
        return images
        
    except Exception as e:
        print(f"Yandex scraping error: {e}")
        return []

def scrape_duckduckgo_images(query, max_images):
    """Custom DuckDuckGo image scraper"""
    images = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # DuckDuckGo image search
        search_url = f"https://duckduckgo.com/?q={urllib.parse.quote_plus(query)}&t=h_&iax=images&ia=images"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        # Try to find image URLs in the response
        if response.status_code == 200:
            # DuckDuckGo uses a different approach, let's try a simple method
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for image elements
            img_elements = soup.find_all('img')
            
            for i, img in enumerate(img_elements[:max_images]):
                if 'src' in img.attrs:
                    img_url = img['src']
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://duckduckgo.com' + img_url
                    
                    if img_url.startswith('http') and 'logo' not in img_url.lower():
                        images.append(img_url)
        
        print(f"DuckDuckGo found {len(images)} image URLs")
        return images
        
    except Exception as e:
        print(f"DuckDuckGo scraping error: {e}")
        return []

def download_image_from_url(url, save_path):
    """Download an image from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return False

def scrape_images_multi_engine(query, total_images_needed):
    """Advanced multi-engine scraping with deduplication"""
    
    # Search engines configuration
    engines = {
        'bing': BingImageCrawler,
        'google': GoogleImageCrawler
    }
    
    # Custom URL-based engines
    custom_engines = ['yandex', 'duckduckgo']
    
    all_images = []
    seen_hashes = set()
    seen_urls = set()
    
    # Calculate images per engine (with extra to account for duplicates)
    total_engines = len(engines) + len(custom_engines)
    images_per_engine = (total_images_needed // total_engines) + 30  # Increased buffer
    
    def scrape_engine(engine_name, crawler_class):
        try:
            print(f"Starting {engine_name} scraping for {images_per_engine} images...")
            
            # Create temporary directory for this engine
            temp_dir = tempfile.mkdtemp(prefix=f"{engine_name}_")
            
            # Create crawler with higher limits
            crawler = crawler_class(
                downloader_threads=4,
                storage={'root_dir': temp_dir}
            )
            
            # Scrape with higher number to account for failed downloads
            crawler.crawl(keyword=query, max_num=images_per_engine)
            
            # Process downloaded images
            if os.path.exists(temp_dir):
                files = [f for f in os.listdir(temp_dir) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'))]
                
                print(f"{engine_name} downloaded {len(files)} files")
                
                # Create static temp directory
                static_temp = os.path.join('static', 'temp_images')
                os.makedirs(static_temp, exist_ok=True)
                
                for i, filename in enumerate(files):
                    try:
                        src_path = os.path.join(temp_dir, filename)
                        
                        # Skip small files (likely broken)
                        if os.path.getsize(src_path) < 5000:  # Skip files < 5KB
                            continue
                            
                        # Calculate image hash for deduplication
                        img_hash = calculate_image_hash(src_path)
                        if img_hash and img_hash in seen_hashes:
                            continue  # Skip duplicate
                        
                        # Create unique filename
                        file_ext = os.path.splitext(filename)[1] or '.jpg'
                        unique_name = f"{safe_folder_name(query)}_{engine_name}_{int(time.time())}_{i}{file_ext}"
                        dest_path = os.path.join(static_temp, unique_name)
                        
                        # Copy file
                        import shutil
                        shutil.copy2(src_path, dest_path)
                        
                        # Add to results
                        if img_hash:
                            seen_hashes.add(img_hash)
                        
                        all_images.append({
                            'url': f"/static/temp_images/{unique_name}",
                            'filename': f"{safe_folder_name(query)}_{engine_name}_{len(all_images)+1}{file_ext}",
                            'engine': engine_name,
                            'local_path': dest_path,
                            'hash': img_hash
                        })
                        
                        # Stop if we have enough unique images
                        if len(all_images) >= total_images_needed:
                            break
                            
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                        continue
            
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            print(f"{engine_name} contributed {sum(1 for img in all_images if img['engine'] == engine_name)} unique images")
            
        except Exception as e:
            print(f"Error with {engine_name}: {e}")
    
    def scrape_custom_engine(engine_name):
        try:
            print(f"Starting {engine_name} URL scraping for {images_per_engine} images...")
            
            # Get image URLs from custom engines
            if engine_name == 'yandex':
                image_urls = scrape_yandex_images(query, images_per_engine)
            elif engine_name == 'duckduckgo':
                image_urls = scrape_duckduckgo_images(query, images_per_engine)
            else:
                return
            
            # Create static temp directory
            static_temp = os.path.join('static', 'temp_images')
            os.makedirs(static_temp, exist_ok=True)
            
            # Download images from URLs
            for i, img_url in enumerate(image_urls):
                if len(all_images) >= total_images_needed:
                    break
                    
                if img_url in seen_urls:
                    continue  # Skip duplicate URLs
                
                try:
                    # Create unique filename
                    file_ext = '.jpg'  # Default extension
                    if '.' in img_url:
                        url_ext = img_url.split('.')[-1].lower()
                        if url_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
                            file_ext = f'.{url_ext}'
                    
                    unique_name = f"{safe_folder_name(query)}_{engine_name}_{int(time.time())}_{i}{file_ext}"
                    dest_path = os.path.join(static_temp, unique_name)
                    
                    # Download image
                    if download_image_from_url(img_url, dest_path):
                        # Check file size
                        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 5000:
                            # Calculate hash for deduplication
                            img_hash = calculate_image_hash(dest_path)
                            if img_hash and img_hash in seen_hashes:
                                os.remove(dest_path)  # Remove duplicate
                                continue
                            
                            # Add to results
                            seen_urls.add(img_url)
                            if img_hash:
                                seen_hashes.add(img_hash)
                            
                            all_images.append({
                                'url': f"/static/temp_images/{unique_name}",
                                'filename': f"{safe_folder_name(query)}_{engine_name}_{len(all_images)+1}{file_ext}",
                                'engine': engine_name,
                                'local_path': dest_path,
                                'hash': img_hash
                            })
                        else:
                            if os.path.exists(dest_path):
                                os.remove(dest_path)  # Remove small/invalid files
                    
                except Exception as e:
                    print(f"Error downloading from {engine_name}: {e}")
                    continue
            
            print(f"{engine_name} contributed {sum(1 for img in all_images if img['engine'] == engine_name)} unique images")
            
        except Exception as e:
            print(f"Error with custom engine {engine_name}: {e}")
    
    # Run all engines in parallel
    threads = []
    
    # Start icrawler-based engines
    for engine_name, crawler_class in engines.items():
        thread = Thread(target=scrape_engine, args=(engine_name, crawler_class))
        thread.start()
        threads.append(thread)
    
    # Start custom URL-based engines
    for engine_name in custom_engines:
        thread = Thread(target=scrape_custom_engine, args=(engine_name,))
        thread.start()
        threads.append(thread)
    
    # Wait for all engines to complete
    for thread in threads:
        thread.join()
    
    # If we still don't have enough images, try to get more from successful engines
    if len(all_images) < total_images_needed:
        print(f"Only got {len(all_images)} images, need {total_images_needed}. Trying additional search...")
        
        # Try additional searches with different parameters
        for engine_name, crawler_class in engines.items():
            if len(all_images) >= total_images_needed:
                break
                
            try:
                temp_dir = tempfile.mkdtemp(prefix=f"{engine_name}_extra_")
                crawler = crawler_class(
                    downloader_threads=4,
                    storage={'root_dir': temp_dir}
                )
                
                # Search with additional keywords
                extended_query = f"{query} images photos pictures"
                crawler.crawl(keyword=extended_query, max_num=total_images_needed - len(all_images) + 30)
                
                if os.path.exists(temp_dir):
                    files = [f for f in os.listdir(temp_dir) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'))]
                    
                    for i, filename in enumerate(files):
                        if len(all_images) >= total_images_needed:
                            break
                            
                        try:
                            src_path = os.path.join(temp_dir, filename)
                            if os.path.getsize(src_path) < 5000:
                                continue
                                
                            img_hash = calculate_image_hash(src_path)
                            if img_hash and img_hash in seen_hashes:
                                continue
                            
                            file_ext = os.path.splitext(filename)[1] or '.jpg'
                            unique_name = f"{safe_folder_name(query)}_{engine_name}_extra_{int(time.time())}_{i}{file_ext}"
                            dest_path = os.path.join('static', 'temp_images', unique_name)
                            
                            import shutil
                            shutil.copy2(src_path, dest_path)
                            
                            if img_hash:
                                seen_hashes.add(img_hash)
                            
                            all_images.append({
                                'url': f"/static/temp_images/{unique_name}",
                                'filename': f"{safe_folder_name(query)}_{engine_name}_extra_{len(all_images)+1}{file_ext}",
                                'engine': f"{engine_name}_extra",
                                'local_path': dest_path,
                                'hash': img_hash
                            })
                            
                        except Exception as e:
                            continue
                
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
            except Exception as e:
                print(f"Error with extra search on {engine_name}: {e}")
    
    # Return exact number requested (or all if we couldn't get enough)
    final_images = all_images[:total_images_needed]
    print(f"Final result: {len(final_images)} unique images out of {total_images_needed} requested")
    
    return final_images

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        quantity = int(data.get('quantity', 20))
    else:
        # Handle form data
        topic = request.form.get('topic', '').strip()
        quantity = int(request.form.get('quantity', 20))
    
    if not topic:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Please enter a search topic'})
        else:
            return render_template('error.html', error='Please enter a search topic')
    
    try:
        print(f"Scraping {quantity} images for '{topic}'...")
        
        # Use the multi-engine scraper
        scraped_urls = scrape_images_multi_engine(topic, quantity)
        
        if not scraped_urls:
            error_msg = 'No images could be scraped. Please try a different search term.'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg})
            else:
                return render_template('error.html', error=error_msg)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'images': scraped_urls,
                'topic': topic,
                'total': len(scraped_urls),
                'total_found': len(scraped_urls),
                'requested': quantity
            })
        else:
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
        if request.is_json:
            return jsonify({'success': False, 'error': error_msg})
        else:
            return render_template('error.html', error=error_msg)

@app.route('/download/<topic>/<int:index>')
def download_image(topic, index):
    """Download individual image"""
    try:
        # Find the image in temp directory
        static_temp = os.path.join('static', 'temp_images')
        if not os.path.exists(static_temp):
            return "Image not found", 404
        
        # Find files matching the pattern
        files = [f for f in os.listdir(static_temp) 
                if f.startswith(safe_folder_name(topic)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'))]
        
        if index >= len(files):
            return "Image not found", 404
        
        file_path = os.path.join(static_temp, files[index])
        
        if not os.path.exists(file_path):
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
        static_temp = os.path.join('static', 'temp_images')
        if not os.path.exists(static_temp):
            return "No images found", 404
        
        # Find all files for this topic
        files = [f for f in os.listdir(static_temp) 
                if f.startswith(safe_folder_name(topic)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'))]
        
        if not files:
            return "No images found", 404
        
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, filename in enumerate(files):
                file_path = os.path.join(static_temp, filename)
                if os.path.exists(file_path):
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
        static_temp = os.path.join('static', 'temp_images')
        if os.path.exists(static_temp):
            files = [f for f in os.listdir(static_temp) 
                    if f.startswith(safe_folder_name(topic))]
            
            for filename in files:
                file_path = os.path.join(static_temp, filename)
                try:
                    os.remove(file_path)
                except:
                    pass
        
        return jsonify({'success': True, 'message': f'Cleared {len(files)} images for {topic}'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/temp_images', exist_ok=True)
    
    print("🚀 Advanced Multi-Engine Image Scraper Starting...")
    print("✅ Search Engines: Bing, Google, Yandex, DuckDuckGo")
    print("✅ Duplicate detection enabled")
    print("✅ Exact count delivery")
    print("✅ High-quality filtering")
    print("✅ No count limits - get exactly what you request!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)