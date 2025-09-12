import re
import os
import hashlib
from icrawler.builtin import BingImageCrawler, GoogleImageCrawler
from threading import Thread

SAVE_DIR = "downloads"

def file_hash(path):
    """Compute MD5 hash of a file (for duplicate detection)."""
    hasher = hashlib.md5()
    with open(path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def scrape_images(query, num_images, engine="bing"):
    save_dir = os.path.join(SAVE_DIR, query, engine)
    os.makedirs(save_dir, exist_ok=True)

    if engine == "google":
        crawler = GoogleImageCrawler(downloader_threads=8, storage={"root_dir": save_dir})
    else:
        crawler = BingImageCrawler(downloader_threads=8, storage={"root_dir": save_dir})

    crawler.crawl(keyword=query, max_num=num_images * 2)  # overshoot for duplicates

    return save_dir  # return raw folder path


def safe_folder_name(name: str) -> str:
    """Make a safe folder name for Windows/Linux/Mac."""
    # remove illegal characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # strip spaces and replace inner spaces with underscore
    name = name.strip().replace(" ", "_")
    return name


def merge_and_deduplicate(query, quantity, engine_folders):
    final_dir = os.path.join(SAVE_DIR, query)
    os.makedirs(final_dir, exist_ok=True)

    seen_hashes = set()
    count = 1

    for folder in engine_folders:
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                h = file_hash(file_path)
                if h not in seen_hashes:
                    seen_hashes.add(h)
                    ext = file.split(".")[-1].lower()
                    new_name = os.path.join(final_dir, f"{count}.{ext}")
                    os.rename(file_path, new_name)
                    count += 1
                else:
                    os.remove(file_path)
            except Exception:
                pass

    # trim extra images if more than needed
    all_images = sorted(os.listdir(final_dir), key=lambda x: int(x.split(".")[0]))
    if len(all_images) > quantity:
        for extra in all_images[quantity:]:
            os.remove(os.path.join(final_dir, extra))

    return len(os.listdir(final_dir))


if __name__ == "__main__":
    topic = input("Enter topic: ")
    quantity = int(input("Enter number of images: "))
    topic = safe_folder_name(topic)
    results = []
    engine_folders = []

    def run_scraper(engine):
        path = scrape_images(topic, quantity, engine)
        engine_folders.append(path)

    t1 = Thread(target=run_scraper, args=("bing",))
    t2 = Thread(target=run_scraper, args=("google",))

    t1.start(); t2.start()
    t1.join(); t2.join()

    total = merge_and_deduplicate(topic, quantity, engine_folders)

    print(f"✅ Downloaded {total}/{quantity} unique images for '{topic}'")
    print(f"📂 Saved in: downloads/{topic}")
