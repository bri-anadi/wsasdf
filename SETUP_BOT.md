# Panduan Setup Wikipedia Scraper Telegram Bot

Panduan lengkap step-by-step untuk setup dan menjalankan bot Telegram dari awal hingga deployment.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Membuat Bot di Telegram](#membuat-bot-di-telegram)
3. [Setup Project](#setup-project)
4. [Konfigurasi Environment](#konfigurasi-environment)
5. [Kustomisasi Bot](#kustomisasi-bot)
6. [Menjalankan Bot](#menjalankan-bot)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- Python 3.7 atau lebih tinggi
- pip (Python package manager)
- Git (opsional, untuk clone repository)
- Terminal/Command Line access
- Text editor (VSCode, Sublime, Nano, dll)

### Akun & Services
- Akun Telegram (install di smartphone atau desktop)
- Koneksi internet yang stabil

### Cek Python Version
```bash
python3 --version
# Output: Python 3.x.x
```

---

## Membuat Bot di Telegram

### Step 1: Buka BotFather

1. Buka aplikasi Telegram di smartphone atau desktop
2. Di search bar, ketik: `@BotFather`
3. Klik pada bot dengan verified checkmark (centang biru)
4. Klik tombol **START** atau ketik `/start`

BotFather adalah bot resmi dari Telegram untuk membuat dan mengelola bot.

### Step 2: Buat Bot Baru

Ketik command berikut di chat dengan BotFather:

```
/newbot
```

BotFather akan memandu Anda melalui proses pembuatan:

```
BotFather:
Alright, a new bot. How are we going to call it?
Please choose a name for your bot.

Anda: Wikipedia Scraper Bot

BotFather:
Good. Now let's choose a username for your bot.
It must end in `bot`. Like this, for example:
TetrisBot or tetris_bot.

Anda: wikipedia_scraper_bot

BotFather:
Done! Congratulations on your new bot.
You will find it at t.me/wikipedia_scraper_bot

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567

Keep your token secure and store it safely,
it can be used by anyone to control your bot.
```

### Step 3: Simpan Token

Token yang diberikan terlihat seperti ini:
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
```

**SANGAT PENTING:**
- Token ini adalah "password" bot Anda
- **JANGAN** share ke siapapun
- **JANGAN** commit ke GitHub public repository
- **JANGAN** posting di forum atau chat group
- Simpan di tempat aman (password manager atau file .env)

Jika token bocor, segera revoke dengan command:
```
/revoke
```
di BotFather, lalu pilih bot Anda.

---

## Setup Project

### Step 1: Navigasi ke Project Directory

```bash
cd /path/to/wsasdf
```

Jika belum ada project, clone repository:
```bash
git clone <repository-url>
cd wsasdf
```

### Step 2: Buat Virtual Environment (Strongly Recommended)

Virtual environment mengisolasi dependencies project dari system Python.

**Buat venv:**
```bash
python3 -m venv venv
```

**Aktifkan venv:**

Di macOS/Linux:
```bash
source venv/bin/activate
```

Di Windows:
```bash
venv\Scripts\activate
```

Setelah aktif, Anda akan melihat `(venv)` di awal prompt terminal:
```bash
(venv) user@computer:~/wsasdf$
```

### Step 3: Install Dependencies

Install semua package yang diperlukan:

```bash
pip install -r requirements.txt
```

Dependencies yang akan di-install:
```
requests>=2.31.0           # HTTP requests
beautifulsoup4>=4.12.0     # HTML parsing
lxml>=4.9.0                # Fast HTML parser
reportlab>=4.0.0           # PDF generation
python-telegram-bot>=20.0  # Telegram Bot API
python-dotenv>=1.0.0       # Environment variables
```

Verifikasi instalasi:
```bash
pip list | grep telegram
# Output: python-telegram-bot    20.x
```

---

## Konfigurasi Environment

### Step 1: Buat File .env

Copy template .env.example:

```bash
cp .env.example .env
```

Jika file .env.example tidak ada, buat manual:
```bash
touch .env
```

### Step 2: Edit File .env

Buka file .env dengan text editor:

```bash
nano .env
# atau
code .env  # jika pakai VSCode
# atau
vim .env
```

Masukkan token bot Anda:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
```

**Ganti** `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567` dengan token yang Anda dapatkan dari BotFather.

**Format yang BENAR:**
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567
```

**Format yang SALAH:**
```env
TELEGRAM_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567"  # JANGAN ada spasi atau quotes
TELEGRAM_BOT_TOKEN= 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567     # JANGAN ada spasi sebelum =
```

Simpan file (Ctrl+X, Y, Enter jika pakai nano).

### Step 3: Verifikasi .env File

Pastikan file .env ada dan berisi token:

```bash
cat .env
# Output: TELEGRAM_BOT_TOKEN=1234567890:ABC...
```

### Step 4: Pastikan .env Tidak Di-commit ke Git

Cek .gitignore:
```bash
cat .gitignore | grep .env
# Output: .env
```

Jika tidak ada, tambahkan:
```bash
echo ".env" >> .gitignore
```

---

## Kustomisasi Bot

Kustomisasi ini opsional tapi sangat direkomendasikan untuk user experience yang lebih baik.

### Step 1: Set Commands Menu

Ini akan membuat menu commands yang muncul ketika user ketik "/" di chat.

Di Telegram, chat dengan @BotFather:

```
/setcommands
```

BotFather akan meminta Anda memilih bot. Klik bot Anda, lalu kirim commands list berikut:

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

Copy-paste semua text di atas dan kirim ke BotFather.

**Hasil:** User sekarang bisa klik "/" dan melihat menu commands dengan deskripsi.

### Step 2: Set Description

Description muncul di halaman info bot dan saat user pertama kali chat dengan bot.

Di BotFather:
```
/setdescription
```

Pilih bot Anda, lalu kirim description:

```
Search and read Wikipedia articles with ease!

Features:
- Smart search
- PDF export
- Compare articles
- Multi-language (EN/ID)
- Bookmarks
- Random discovery

Start exploring now!
```

### Step 3: Set About Text

About text muncul di profile bot.

Di BotFather:
```
/setabouttext
```

Pilih bot Anda, lalu kirim:

```
Wikipedia Scraper Bot - Your personal Wikipedia assistant. Search, compare, and export articles in multiple languages.
```

### Step 4: Set Profile Picture (Opsional)

Buat atau download gambar 512x512 pixels untuk profile picture.

Di BotFather:
```
/setuserpic
```

Pilih bot Anda, lalu upload gambar.

**Tips:** Gunakan gambar yang relate dengan Wikipedia atau knowledge (misalnya: Wikipedia logo, buku, atau simbol search).

### Step 5: Set Inline Mode (Opsional)

Inline mode memungkinkan user mention bot di chat lain.

Di BotFather:
```
/setinline
```

Pilih bot Anda, lalu ketik placeholder text, misalnya:
```
Search Wikipedia...
```

### Step 6: Disable Group Privacy (untuk Group Chat)

Jika ingin bot bekerja di group chat:

Di BotFather:
```
/setprivacy
```

Pilih bot Anda, lalu pilih **Disable**.

**Note:** Privacy **Enabled** = bot hanya menerima messages yang mention bot.
Privacy **Disabled** = bot menerima semua messages di group (not recommended).

---

## Menjalankan Bot

### Step 1: Test Run (Development)

Jalankan bot di terminal:

```bash
python telegram_bot.py
```

atau jika python3:
```bash
python3 telegram_bot.py
```

**Output yang diharapkan:**
```
2025-01-15 10:00:00 - __main__ - INFO - Wikipedia Scraper Bot started...
2025-01-15 10:00:00 - __main__ - INFO - Bot is running. Press Ctrl+C to stop.
```

**Jika ada error:**
- Cek apakah .env file ada dan berisi token yang benar
- Cek apakah semua dependencies ter-install
- Lihat section [Troubleshooting](#troubleshooting)

### Step 2: Keep Bot Running

Bot akan terus running di terminal. Untuk stop bot:
- Tekan `Ctrl+C` di terminal

**Note:** Bot akan stop jika Anda close terminal atau matikan komputer.

---

## Testing

### Step 1: Cari Bot Anda di Telegram

1. Buka Telegram
2. Di search bar, ketik username bot Anda: `@wikipedia_scraper_bot`
3. Klik bot Anda dari hasil search
4. Klik tombol **START**

### Step 2: Test Basic Commands

**Test 1: Welcome Message**
```
/start
```
Expected: Bot mengirim welcome message dengan inline keyboard buttons.

**Test 2: Help Menu**
```
/help
```
Expected: Bot mengirim list commands dengan contoh penggunaan.

**Test 3: Search Article**
```
/search Python programming
```
Expected:
- Bot mengirim "Searching..." message
- Bot update message dengan hasil search (title, summary, kategori, referensi)
- Ada inline buttons untuk "Export PDF" dan "Bookmark"

**Test 4: Export PDF**
```
/pdf Artificial Intelligence
```
Expected:
- Bot mengirim progress messages
- Bot upload dan kirim file PDF
- PDF bisa dibuka dan berisi artikel lengkap

**Test 5: Compare Articles** (NEW!)
```
/compare Python vs Java
```
Expected:
- Bot mencari kedua artikel
- Bot menampilkan perbandingan (statistik, kategori sama, infobox, ringkasan)
- Ada buttons untuk export PDF masing-masing artikel

**Test 6: Language Switch**
```
/language
```
Expected:
- Bot menampilkan pilihan bahasa (English/Indonesian)
- Klik salah satu, bot konfirmasi bahasa berubah

**Test 7: Random Article**
```
/random
```
Expected:
- Bot mengambil artikel random
- Bot menampilkan title, summary, dan link
- Ada button untuk "Random Lagi"

**Test 8: Bookmark System**
```
/bookmark Machine Learning
/bookmarks
```
Expected:
- Command pertama: Bot konfirmasi artikel disimpan
- Command kedua: Bot menampilkan list semua bookmark

**Test 9: Statistics**
```
/stats
```
Expected:
- Bot menampilkan jumlah pencarian, bookmark, dan bahasa yang digunakan

**Test 10: Inline Keyboard**
- Klik button "Help" di welcome message
Expected: Message berubah menampilkan help text

### Step 3: Test Error Handling

**Test artikel yang tidak ada:**
```
/search xyzabcnotexist123456
```
Expected: Bot mengirim message "Artikel tidak ditemukan"

**Test format compare yang salah:**
```
/compare Python
```
Expected: Bot mengirim message dengan format yang benar

### Step 4: Test Rate Limiting

Kirim command yang sama berulang-ulang dengan cepat:
```
/search Python
/search Python
/search Python
```

Expected: Bot mengirim message "Mohon tunggu X detik..."

---

## Deployment

Untuk menjalankan bot 24/7, deploy ke server atau cloud.

### Option 1: Screen (Simple, untuk VPS/Server)

Screen memungkinkan bot tetap running meskipun Anda logout dari SSH.

**Install screen:**
```bash
sudo apt update
sudo apt install screen
```

**Create screen session:**
```bash
screen -S wiki_bot
```

**Run bot:**
```bash
cd /path/to/wsasdf
source venv/bin/activate
python telegram_bot.py
```

**Detach dari screen:**
- Tekan `Ctrl+A`, lalu tekan `D`

**Reattach ke screen:**
```bash
screen -r wiki_bot
```

**List semua screen sessions:**
```bash
screen -ls
```

**Kill screen session:**
```bash
screen -X -S wiki_bot quit
```

### Option 2: Systemd Service (Recommended untuk Linux)

Systemd akan auto-start bot saat server boot dan auto-restart jika crash.

**Create service file:**
```bash
sudo nano /etc/systemd/system/wiki_bot.service
```

**Paste content berikut:**
```ini
[Unit]
Description=Wikipedia Scraper Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/wsasdf
Environment="PATH=/path/to/wsasdf/venv/bin"
ExecStart=/path/to/wsasdf/venv/bin/python telegram_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**GANTI:**
- `your_username` dengan username Linux Anda
- `/path/to/wsasdf` dengan path absolut ke project directory

**Enable dan start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable wiki_bot
sudo systemctl start wiki_bot
```

**Cek status:**
```bash
sudo systemctl status wiki_bot
```

**View logs:**
```bash
sudo journalctl -u wiki_bot -f
```

**Stop/Restart:**
```bash
sudo systemctl stop wiki_bot
sudo systemctl restart wiki_bot
```

### Option 3: Docker (Advanced)

**Create Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run bot
CMD ["python", "telegram_bot.py"]
```

**Create .dockerignore:**
```
venv/
*.pyc
__pycache__/
.env
*.json
*.pdf
.git/
```

**Build image:**
```bash
docker build -t wiki_bot .
```

**Run container:**
```bash
docker run -d \
  --name wiki_bot \
  --env-file .env \
  --restart unless-stopped \
  wiki_bot
```

**View logs:**
```bash
docker logs -f wiki_bot
```

**Stop/Start:**
```bash
docker stop wiki_bot
docker start wiki_bot
```

**Remove container:**
```bash
docker rm -f wiki_bot
```

### Option 4: Cloud Platforms

**Heroku:**
1. Install Heroku CLI
2. Create Procfile: `worker: python telegram_bot.py`
3. Deploy: `git push heroku main`
4. Set config var: `heroku config:set TELEGRAM_BOT_TOKEN=your_token`

**Railway.app:**
1. Connect GitHub repository
2. Add environment variable `TELEGRAM_BOT_TOKEN`
3. Deploy automatically

**Render.com:**
1. Create new Web Service
2. Connect repository
3. Add environment variable
4. Deploy

---

## Monitoring & Maintenance

### View Bot Statistics

Di BotFather:
```
/mybots
```
Pilih bot Anda, lalu klik **Statistics**.

Anda akan melihat:
- Total users
- Active users (24h, 7d, 30d)
- Messages per day
- Graph retention rate

### View Logs

**Systemd:**
```bash
sudo journalctl -u wiki_bot -n 100        # Last 100 lines
sudo journalctl -u wiki_bot -f            # Follow (real-time)
sudo journalctl -u wiki_bot --since today # Today's logs
```

**Docker:**
```bash
docker logs wiki_bot --tail 100
docker logs -f wiki_bot
```

**Screen:**
```bash
screen -r wiki_bot  # View live output
```

### Update Bot

**Pull latest changes:**
```bash
cd /path/to/wsasdf
git pull origin main
```

**Update dependencies:**
```bash
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

**Restart bot:**

Systemd:
```bash
sudo systemctl restart wiki_bot
```

Screen:
```bash
screen -X -S wiki_bot quit
screen -S wiki_bot
python telegram_bot.py
# Ctrl+A, D to detach
```

Docker:
```bash
docker build -t wiki_bot .
docker rm -f wiki_bot
docker run -d --name wiki_bot --env-file .env wiki_bot
```

### Backup User Data

Jika implement database untuk user data:

```bash
# Backup
cp user_data.db user_data_backup_$(date +%Y%m%d).db

# Automated daily backup (crontab)
0 2 * * * cp /path/to/user_data.db /path/to/backups/user_data_$(date +\%Y\%m\%d).db
```

---

## Troubleshooting

### Error: "TELEGRAM_BOT_TOKEN tidak ditemukan!"

**Penyebab:**
- File .env tidak ada
- File .env kosong atau format salah
- .env tidak di directory yang sama dengan telegram_bot.py

**Solusi:**
1. Pastikan file .env ada:
   ```bash
   ls -la .env
   ```

2. Cek isi file .env:
   ```bash
   cat .env
   ```

3. Pastikan format benar (tanpa spasi atau quotes):
   ```env
   TELEGRAM_BOT_TOKEN=1234567890:ABCdef...
   ```

4. Jika masih error, hardcode token untuk testing (HANYA untuk testing):
   ```python
   # Di telegram_bot.py
   TELEGRAM_TOKEN = "1234567890:ABCdef..."  # JANGAN commit ini!
   ```

### Error: "No module named 'telegram'"

**Penyebab:**
- Library python-telegram-bot belum ter-install
- Virtual environment tidak aktif

**Solusi:**
```bash
# Aktifkan venv jika belum
source venv/bin/activate

# Install library
pip install python-telegram-bot

# Atau install semua dependencies
pip install -r requirements.txt
```

### Bot tidak merespon di Telegram

**Checklist:**
1. **Bot script masih running?**
   ```bash
   # Systemd
   sudo systemctl status wiki_bot

   # Screen
   screen -ls
   ```

2. **Token benar?**
   - Cek token di .env
   - Bandingkan dengan token di BotFather
   - Coba revoke dan create token baru

3. **Internet connection OK?**
   ```bash
   ping telegram.org
   ```

4. **Firewall blocking?**
   ```bash
   sudo ufw status
   # Pastikan port 443 dan 80 open untuk outbound
   ```

5. **Check logs untuk error:**
   ```bash
   sudo journalctl -u wiki_bot -n 50
   ```

### Error: "Connection refused" atau "Timeout"

**Penyebab:**
- Network issue
- Telegram API down (rare)
- Firewall blocking

**Solusi:**
1. Cek koneksi:
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```

2. Restart bot:
   ```bash
   sudo systemctl restart wiki_bot
   ```

3. Cek Telegram API status: https://www.telegramstatus.org/

### Bot slow atau sering timeout

**Penyebab:**
- Wikipedia server slow
- Internet connection lambat
- Too many concurrent requests

**Solusi:**
1. Increase timeout di app.py:
   ```python
   response = self.session.get(url, timeout=30)  # Default 10
   ```

2. Add caching (advanced):
   ```python
   # Install redis
   pip install redis

   # Implement caching di scraper methods
   ```

### PDF generation fails

**Error message:** "Failed to export PDF"

**Solusi:**
1. Check reportlab installation:
   ```bash
   pip install --upgrade reportlab
   ```

2. Check disk space:
   ```bash
   df -h
   ```

3. Check permissions:
   ```bash
   ls -la /path/to/wsasdf
   # Make sure write permission ada
   ```

### User data lost after restart

**Penyebab:**
- Bot menggunakan in-memory storage (dictionary)
- Data hilang saat restart

**Solusi untuk persistent storage:**
1. Implement SQLite database
2. Atau gunakan JSON file untuk save/load user data
3. Atau gunakan Redis untuk caching

**Quick fix - Save to JSON:**
```python
import json

# Save user data before exit
def save_user_data():
    with open('user_data.json', 'w') as f:
        json.dump(user_data, f)

# Load on startup
def load_user_data():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
```

### Rate limit error from Telegram

**Error:** "429 Too Many Requests"

**Penyebab:**
- Mengirim terlalu banyak messages dalam waktu singkat
- Telegram API rate limit

**Solusi:**
1. Bot sudah include rate limiting di decorators
2. Jangan spam bot dengan banyak requests
3. Jika terkena limit, tunggu beberapa menit

### Compare feature tidak bekerja

**Error:** "Format tidak valid"

**Penyebab:**
- Format command salah

**Solusi:**
Gunakan format yang benar:
```
/compare Python vs Java        ✓ Correct
/compare python VS java         ✓ Correct (case insensitive)
/compare Python and Java        ✗ Wrong (harus "vs")
/compare Python                 ✗ Wrong (harus 2 topik)
```

---

## FAQ (Frequently Asked Questions)

### Q: Apakah bot ini gratis?
A: Ya, bot ini open source dan gratis digunakan. Telegram Bot API juga gratis.

### Q: Berapa lama setup?
A: Sekitar 15-30 menit jika mengikuti panduan ini.

### Q: Apakah perlu server untuk running bot?
A: Untuk development, bisa run di laptop/PC. Untuk production (24/7), perlu VPS atau cloud hosting.

### Q: Apakah bisa run multiple bots?
A: Ya, create multiple bots di BotFather dengan username berbeda, lalu run dengan .env file berbeda.

### Q: Bagaimana cara hapus bot?
A: Di BotFather, ketik `/deletebot` dan pilih bot yang ingin dihapus. **Warning:** Tidak bisa di-undo!

### Q: Apakah bisa custom command names?
A: Ya, edit commands di telegram_bot.py. Tapi pastikan update juga di BotFather `/setcommands`.

### Q: Bagaimana cara add admin commands?
A: Check user ID di handler dan compare dengan admin ID:
```python
ADMIN_IDS = [123456789, 987654321]

async def admin_command(update, context):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Unauthorized")
        return
    # Admin logic here
```

### Q: Bot bisa untuk commercial use?
A: Yes, tapi pastikan comply dengan Wikipedia terms dan Telegram TOS.

---

## Additional Resources

### Documentation
- Telegram Bot API: https://core.telegram.org/bots/api
- python-telegram-bot: https://python-telegram-bot.org/
- Wikipedia API: https://www.mediawiki.org/wiki/API:Main_page

### Community
- python-telegram-bot GitHub: https://github.com/python-telegram-bot/python-telegram-bot
- Telegram Bot Developers: https://t.me/BotDevelopers

### Tools
- BotFather: https://t.me/BotFather
- Bot API Status: https://www.telegramstatus.org/
- Test your bot: https://t.me/wikiscrap_bot

---

## Support

Jika masih ada masalah setelah mengikuti troubleshooting:

1. Check logs dengan detail
2. Test dengan token baru dari BotFather
3. Pastikan semua dependencies ter-install dengan benar
4. Coba run di environment baru (clean install)

**Demo bot:** [@wikiscrap_bot](https://t.me/wikiscrap_bot)

---

**Selamat! Bot Telegram Anda sudah siap digunakan!**

Next steps:
- Share bot dengan teman untuk testing
- Monitor usage statistics di BotFather
- Consider implement database untuk persistent storage
- Add more custom features sesuai kebutuhan

Happy coding! 🚀
