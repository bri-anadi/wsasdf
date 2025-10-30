# Wikipedia Web Scraper

Web scraper Python untuk mengambil data dari Wikipedia menggunakan BeautifulSoup4 dan Requests.

## Fitur

- Scraping homepage Wikipedia untuk mengambil title, meta description, links, images, dan headings
- Extract article links dari halaman
- Scraping artikel lengkap dengan title, summary, content, categories, infobox, dan references
- Mendukung multiple bahasa Wikipedia (en, id, dll)
- **Export artikel ke PDF** dengan format yang rapi dan mudah dibaca
- Extract JSON-LD structured data
- Simpan hasil ke file JSON
- Logging untuk monitoring proses scraping
- Rate limiting untuk menghindari blocking
- User-Agent headers untuk menghindari deteksi bot

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml
- reportlab (untuk export PDF)

## Instalasi

1. Clone atau download repository ini

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Cara Penggunaan

### Menjalankan scraper:

#### Mode Default (Scrape Homepage):
```bash
# Scrape English Wikipedia homepage
python app.py

# Scrape Indonesian Wikipedia homepage
python app.py -l id
python app.py --language id
```

#### Mode Search (Search & Scrape Artikel):
```bash
# Search article in English Wikipedia
python app.py -s "Python programming"
python app.py --search "Artificial Intelligence"

# Search and export to PDF
python app.py -s "Python programming" --pdf
python app.py --search "Machine Learning" --pdf

# Search article in Indonesian Wikipedia
python app.py -s "Indonesia" -l id
python app.py --search "Teknologi" --language id

# Search in Indonesian and export to PDF
python app.py -s "Indonesia" -l id --pdf
```

#### Lihat help:
```bash
python app.py -h
python app.py --help
```

### Output Files

#### Mode Default:
Script akan menghasilkan 4 file JSON:

1. **wikipedia_homepage_{language}.json** - Data dari homepage (title, links, images, headings)
2. **wikipedia_articles_{language}.json** - List of article links
3. **wikipedia_articles_detail_{language}.json** - Detail dari 3 artikel sampel (title, summary, content, categories, infobox, references)
4. **wikipedia_jsonld_{language}.json** - JSON-LD structured data

#### Mode Search:
Script akan menghasilkan file:

1. **wikipedia_search_{query}.json** - Detail lengkap artikel yang dicari
2. **wikipedia_search_{query}.pdf** - PDF artikel (jika menggunakan flag --pdf)

### Menjalankan contoh:
```bash
# Jalankan contoh dasar
python example.py

# Jalankan contoh PDF export
python example_pdf.py
```

### Menggunakan sebagai module:

```python
from app import WikipediaScraper

# Inisialisasi scraper (English Wikipedia)
scraper = WikipediaScraper(language='en')

# Untuk Wikipedia Bahasa Indonesia
scraper_id = WikipediaScraper(language='id')

# Scrape homepage
data = scraper.scrape_homepage()
print(data)

# Get article links
articles = scraper.scrape_article_links(max_links=20)
print(articles)

# Scrape artikel spesifik
article_data = scraper.scrape_article('https://en.wikipedia.org/wiki/Python_(programming_language)')
print(article_data)

# Export artikel ke PDF
scraper.export_to_pdf(article_data, 'python_article.pdf')
```

## Customization

### Mengubah bahasa Wikipedia:

```python
# English Wikipedia (default)
scraper_en = WikipediaScraper(language='en')

# Wikipedia Bahasa Indonesia
scraper_id = WikipediaScraper(language='id')

# Wikipedia Bahasa Jepang
scraper_ja = WikipediaScraper(language='ja')
```

### Mengubah User-Agent:

```python
scraper = WikipediaScraper()
scraper.session.headers['User-Agent'] = 'Your Custom User Agent'
```

### Mengubah timeout:

```python
response = scraper.get_page(url, timeout=30)
```

### Scrape artikel spesifik:

```python
scraper = WikipediaScraper(language='en')

# Scrape artikel Python
article = scraper.scrape_article('https://en.wikipedia.org/wiki/Python_(programming_language)')
print(f"Title: {article['title']}")
print(f"Summary: {article['summary']}")
print(f"Categories: {article['categories']}")
print(f"References: {article['references']}")
```

## Command Line Arguments

- `-s, --search QUERY` - Search dan scrape artikel spesifik berdasarkan keyword
- `-l, --language LANG` - Pilih bahasa Wikipedia (en untuk English, id untuk Indonesian)
- `--pdf` - Export artikel ke PDF (hanya bekerja dengan --search)
- `-h, --help` - Tampilkan help message

## Class Methods

### WikipediaScraper

- `__init__(language='en')` - Inisialisasi scraper dengan bahasa tertentu
- `get_page(url, timeout=10)` - Fetch halaman dari URL
- `parse_html(html_content)` - Parse HTML dengan BeautifulSoup
- `scrape_homepage()` - Scrape data dari homepage Wikipedia
- `scrape_article_links(max_links=20)` - Extract article links
- `scrape_article(article_url)` - Scrape artikel Wikipedia lengkap (title, summary, content, categories, infobox, references)
- `search_article(query)` - Search artikel berdasarkan keyword menggunakan Wikipedia API
- `extract_json_ld(html_content)` - Extract JSON-LD data
- `save_to_json(data, filename)` - Simpan data ke JSON file
- `export_to_pdf(article_data, filename)` - Export artikel ke PDF dengan format yang rapi

## Catatan Penting

- Script ini hanya untuk tujuan edukatif dan penelitian
- Wikipedia memiliki API resmi yang lebih direkomendasikan untuk penggunaan production
- Pastikan mematuhi robots.txt dan terms of service dari Wikipedia
- Gunakan rate limiting untuk menghindari overload server
- Wikipedia bersifat open dan mendukung scraping untuk tujuan non-komersial
- Pertimbangkan menggunakan Wikipedia API untuk kebutuhan yang lebih kompleks

## Troubleshooting

### Error "Connection refused" atau "Timeout"

- Periksa koneksi internet
- Website mungkin memblokir scraping
- Coba gunakan proxy atau VPN
- Tingkatkan timeout value

### Tidak ada data yang di-scrape

- Website mungkin menggunakan JavaScript untuk render konten
- Coba inspect HTML source untuk memastikan data ada
- Pertimbangkan menggunakan Selenium atau Playwright untuk dynamic content

### Rate limiting / IP blocked

- Tambahkan delay lebih lama antara requests
- Gunakan rotating proxies
- Respect robots.txt

## License

MIT License
