# Wikipedia Web Scraper

Web scraper Python untuk mengambil data dari Wikipedia menggunakan BeautifulSoup4 dan Requests, dengan dukungan Telegram Bot untuk akses mudah.

## Fitur

### Command Line Interface
- Scraping homepage Wikipedia untuk mengambil title, meta description, links, images, dan headings
- Extract article links dari halaman
- Scraping artikel lengkap dengan title, summary, content, categories, infobox, dan references
- Mendukung multiple bahasa Wikipedia (en, id, dll)
- **Export artikel ke PDF** dengan format yang rapi dan mudah dibaca
- **Search artikel** menggunakan Wikipedia API
- Extract JSON-LD structured data
- Simpan hasil ke file JSON
- Logging untuk monitoring proses scraping
- Rate limiting untuk menghindari blocking
- User-Agent headers untuk menghindari deteksi bot

### Telegram Bot (NEW!)
- **Search artikel** - Cari artikel Wikipedia langsung dari chat
- **Export to PDF** - Generate dan kirim PDF artikel ke Telegram
- **Compare articles** - Bandingkan 2 artikel side-by-side
- **Multi-language** - Support English dan Indonesian Wikipedia
- **Bookmark system** - Simpan artikel favorit
- **Random article** - Discover artikel random
- **Statistics tracking** - Monitor penggunaan personal
- **Inline keyboard** - Navigasi interaktif dengan buttons
- **Rate limiting** - Built-in protection dari spam

**Coba bot sekarang:** [@wikiscrap_bot](https://t.me/wikiscrap_bot)

**Setup bot sendiri:** Lihat [BOT_SETUP.md](BOT_SETUP.md) untuk panduan lengkap

## Requirements

### Untuk Command Line
- Python 3.7+
- requests
- beautifulsoup4
- lxml
- reportlab (untuk export PDF)

### Untuk Telegram Bot (tambahan)
- python-telegram-bot >= 20.0
- python-dotenv >= 1.0.0

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

## Telegram Bot

### Fitur Bot

#### 1. Search Article
```
/search Python programming
```
Bot akan mencari artikel dan menampilkan:
- Title artikel
- Ringkasan (summary)
- Jumlah kategori dan referensi
- Link ke artikel asli
- Inline buttons untuk export PDF atau bookmark

#### 2. Export to PDF
```
/pdf Artificial Intelligence
```
Bot akan:
- Search artikel
- Scrape konten lengkap
- Generate PDF dengan format rapi
- Upload dan kirim file PDF langsung ke chat

#### 3. Compare Articles (NEW!)
```
/compare Python vs Java
/compare iPhone vs Android
/compare Bitcoin vs Ethereum
```

Bot akan membandingkan dua artikel dengan menampilkan:
- **Basic Statistics**: Jumlah kategori, referensi, dan panjang konten
- **Common Categories**: Kategori yang sama antara kedua artikel
- **Infobox Comparison**: Perbandingan data terstruktur dari infobox
- **Summaries**: Ringkasan masing-masing artikel
- **Quick Links**: Link ke kedua artikel

Format yang didukung:
- `/compare Topic1 vs Topic2`
- Case insensitive (vs, VS, Vs)
- Bekerja dengan bahasa yang dipilih user

Contoh output:
```
📊 Perbandingan: Python vs Java

━━━━━━━━━━━━━━━━━━━━
📝 Python (programming language)
• Kategori: 25
• Referensi: 156
• Panjang: 45234 karakter

📝 Java (programming language)
• Kategori: 28
• Referensi: 189
• Panjang: 52341 karakter
━━━━━━━━━━━━━━━━━━━━

🔗 Kategori Sama:
• Programming languages
• Object-oriented programming
• Cross-platform software

📋 Perbandingan Info:
Paradigm:
  1️⃣ Multi-paradigm: object-oriented...
  2️⃣ Object-oriented (class-based)...

📄 Ringkasan:
Python: Python is a high-level...
Java: Java is a high-level...
```

#### 4. Language Switch
```
/language
```
Pilih bahasa Wikipedia:
- English (default)
- Indonesian

#### 5. Random Article
```
/random
```
Dapatkan artikel random untuk discovery.

#### 6. Bookmark System
```
/bookmark Machine Learning
/bookmarks
```
Simpan artikel favorit dan lihat list bookmark.

#### 7. Statistics
```
/stats
```
Lihat statistik personal:
- Total pencarian
- Jumlah bookmark
- Bahasa yang digunakan

### Setup Bot Telegram

Untuk menjalankan bot Telegram sendiri:

1. **Buat bot di Telegram:**
   - Chat dengan [@BotFather](https://t.me/BotFather)
   - Ketik `/newbot` dan ikuti instruksi
   - Simpan token yang diberikan

2. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env dan masukkan token
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan bot:**
   ```bash
   python telegram_bot.py
   ```

5. **Konfigurasi bot (opsional):**
   - Set commands menu dengan BotFather: `/setcommands`
   - Set description: `/setdescription`
   - Set about text: `/setabouttext`
   - Upload profile picture: `/setuserpic`

**Panduan lengkap:** Lihat [BOT_SETUP.md](BOT_SETUP.md)

### Bot Commands

```
start - Start the bot
help - Show help message
search - Search Wikipedia article
pdf - Export article to PDF
compare - Compare two articles (format: /compare A vs B)
language - Change language (EN/ID)
random - Get random article
bookmark - Save article to bookmarks
bookmarks - View saved bookmarks
stats - View your reading stats
about - About this bot
```

### Coba Bot

Bot sudah live dan bisa dicoba di Telegram:
**[@wikiscrap_bot](https://t.me/wikiscrap_bot)**

Fitur yang tersedia:
- Search artikel Wikipedia
- Export artikel ke PDF
- Compare dua artikel
- Multi-language (EN/ID)
- Bookmark system
- Random article discovery
- Personal statistics

## Update Log

### Version 1.1.0 (Latest)
**Tanggal:** 2025-01-15

**Fitur Baru:**
- **Telegram Bot Integration**
  - Implementasi lengkap Telegram Bot dengan python-telegram-bot
  - Support untuk semua fitur CLI melalui chat interface
  - Inline keyboard untuk navigasi interaktif
  - Rate limiting built-in untuk mencegah spam

- **Compare Articles Feature**
  - Command: `/compare Topic1 vs Topic2`
  - Bandingkan statistik dasar (kategori, referensi, panjang)
  - Tampilkan kategori yang sama
  - Perbandingan infobox data
  - Ringkasan masing-masing artikel
  - Available di CLI dan Telegram Bot

- **Search Enhancement**
  - Method `search_article()` menggunakan Wikipedia OpenSearch API
  - Auto-suggest artikel yang relevan
  - Support untuk pencarian multi-kata

**Improvements:**
- User data management dengan in-memory storage
- Language preference per user
- Bookmark system untuk simpan artikel favorit
- Statistics tracking (jumlah pencarian, bookmark)
- Better error handling dan logging
- Responsive inline keyboard interface

**Files Added:**
- `telegram_bot.py` - Main bot implementation
- `BOT_SETUP.md` - Panduan lengkap setup bot
- `.env.example` - Template environment variables
- Updated `requirements.txt` dengan dependencies bot

### Version 1.0.0
**Tanggal:** 2025-01-10

**Initial Release:**
- Web scraper untuk Wikipedia
- Support multi-language (EN/ID)
- Export to PDF
- Command line interface
- JSON output
- Basic scraping features

## Catatan Penting

- Script ini hanya untuk tujuan edukatif dan penelitian
- Wikipedia memiliki API resmi yang lebih direkomendasikan untuk penggunaan production
- Pastikan mematuhi robots.txt dan terms of service dari Wikipedia
- Gunakan rate limiting untuk menghindari overload server
- Wikipedia bersifat open dan mendukung scraping untuk tujuan non-komersial
- Pertimbangkan menggunakan Wikipedia API untuk kebutuhan yang lebih kompleks
- Bot Telegram sudah include rate limiting untuk mencegah abuse

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
