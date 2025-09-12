# Web-Image-Crawller

Web-Image-Crawller is a Python-based tool designed to automatically download and deduplicate images from the web based on a user-specified topic. It leverages both Bing and Google image search engines to maximize the number of unique images retrieved.

## Features

- **Multi-Engine Crawling**: Downloads images using both Bing and Google search engines for broader coverage.
- **Duplicate Detection**: Uses MD5 hashing to automatically detect and remove duplicate images across engines.
- **Customizable Quantity**: Specify the exact number of unique images you want for any topic.
- **Threaded Downloads**: Crawling is performed in parallel for faster results.
- **Organized Storage**: Images are saved in organized folders by topic.

## Usage

1. Make sure you have Python installed.
2. Install dependencies:
   ```bash
   pip install icrawler
   ```
3. Run the script:
   ```bash
   python Crawller.py
   ```
4. Enter your desired topic and the number of images when prompted.

Images will be saved in the `downloads/<your-topic>` directory.

## Example

```
Enter topic: cats
Enter number of images: 50
✅ Downloaded 50/50 unique images for 'cats'
📂 Saved in: downloads/cats
```

## License

This project is licensed under the MIT License.
