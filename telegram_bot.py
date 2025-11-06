"""
Wikipedia Scraper Telegram Bot
Implementasi lengkap bot Telegram dengan berbagai fitur
"""

import os
import logging
import time
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode

from app import WikipediaScraper

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN tidak ditemukan! Pastikan ada di file .env")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize scrapers
scrapers = {
    'en': WikipediaScraper(language='en'),
    'id': WikipediaScraper(language='id')
}

# User data storage (dalam produksi, gunakan database)
user_data = {}


# Decorators
def rate_limit(seconds=2):
    """Rate limiting decorator untuk mencegah spam"""
    def decorator(func):
        last_called = {}

        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            current_time = time.time()

            if user_id in last_called:
                elapsed = current_time - last_called[user_id]
                if elapsed < seconds:
                    await update.message.reply_text(
                        f"⏳ Mohon tunggu {int(seconds - elapsed)} detik..."
                    )
                    return

            last_called[user_id] = current_time
            return await func(update, context)

        return wrapper
    return decorator


def get_user_language(user_id: int) -> str:
    """Get user's preferred language"""
    if user_id not in user_data:
        user_data[user_id] = {'language': 'en', 'bookmarks': [], 'searches': 0}
    return user_data[user_id]['language']


def set_user_language(user_id: int, language: str):
    """Set user's preferred language"""
    if user_id not in user_data:
        user_data[user_id] = {'language': language, 'bookmarks': [], 'searches': 0}
    else:
        user_data[user_id]['language'] = language


def increment_search_count(user_id: int):
    """Increment user's search count"""
    if user_id not in user_data:
        user_data[user_id] = {'language': 'en', 'bookmarks': [], 'searches': 1}
    else:
        user_data[user_id]['searches'] += 1


# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /start command"""
    user = update.effective_user
    user_id = user.id

    # Initialize user data
    if user_id not in user_data:
        user_data[user_id] = {'language': 'en', 'bookmarks': [], 'searches': 0}

    welcome_text = (
        f"👋 Hi *{user.first_name}*!\n\n"
        f"Saya *Wikipedia Scraper Bot* yang dapat membantu Anda:\n\n"
        f"🔍 Mencari artikel Wikipedia\n"
        f"📄 Export artikel ke PDF\n"
        f"🌍 Mendukung berbagai bahasa\n"
        f"🔖 Simpan artikel favorit\n"
        f"🎲 Temukan artikel random\n\n"
        f"Ketik /help untuk melihat semua perintah."
    )

    keyboard = [
        [
            InlineKeyboardButton("🔍 Search", switch_inline_query_current_chat=""),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("🌍 Language", callback_data="language"),
            InlineKeyboardButton("📊 Stats", callback_data="stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /help command"""
    help_text = """
📚 *Perintah yang Tersedia:*

🔹 *Pencarian & Informasi*
/search <query> - Cari artikel Wikipedia
/pdf <query> - Export artikel ke PDF
/random - Dapatkan artikel random
/compare <A> vs <B> - Bandingkan 2 artikel

🔹 *Bookmark & Favorit*
/bookmark <query> - Simpan artikel
/bookmarks - Lihat artikel tersimpan
/clear\\_bookmarks - Hapus semua bookmark

🔹 *Pengaturan*
/language - Ganti bahasa (EN/ID)
/stats - Lihat statistik Anda

🔹 *Lainnya*
/help - Tampilkan pesan ini
/about - Tentang bot ini

*Contoh Penggunaan:*
`/search Python programming`
`/pdf Artificial Intelligence`
`/compare Python vs Java`
`/bookmark Machine Learning`

_Tip: Anda juga bisa mention bot di group chat!_
    """

    keyboard = [[InlineKeyboardButton("🏠 Back to Home", callback_data="start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )


@rate_limit(seconds=3)
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /search command"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    scraper = scrapers[language]

    # Get query from command
    query = ' '.join(context.args)

    if not query:
        await update.message.reply_text(
            "❌ Mohon berikan kata kunci pencarian.\n\n"
            "*Contoh:*\n"
            "`/search Python programming`\n"
            "`/search Artificial Intelligence`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Send searching message
    msg = await update.message.reply_text(
        f"🔍 Mencari: *{query}*...",
        parse_mode=ParseMode.MARKDOWN
    )

    try:
        # Search article
        article_url = scraper.search_article(query)

        if not article_url:
            await msg.edit_text(
                f"❌ Artikel tidak ditemukan: *{query}*\n\n"
                f"Coba kata kunci lain atau ganti bahasa dengan /language",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        # Scrape article
        await msg.edit_text(f"📖 Mengambil artikel...")
        article_data = scraper.scrape_article(article_url)

        if article_data:
            # Increment search count
            increment_search_count(user_id)

            # Truncate summary if too long
            summary = article_data['summary']
            if len(summary) > 500:
                summary = summary[:500] + "..."

            # Format categories
            categories = ', '.join(article_data['categories'][:5])
            if len(article_data['categories']) > 5:
                categories += f" (+{len(article_data['categories']) - 5} lainnya)"

            # Format response
            response = (
                f"✅ *{article_data['title']}*\n\n"
                f"📝 *Ringkasan:*\n{summary}\n\n"
                f"📊 *Kategori:* {categories}\n"
                f"📚 *Referensi:* {article_data['references']}\n\n"
                f"🔗 [Baca di Wikipedia]({article_data['url']})"
            )

            # Create inline keyboard
            keyboard = [
                [
                    InlineKeyboardButton("📄 Export PDF", callback_data=f"pdf:{query}"),
                    InlineKeyboardButton("🔖 Bookmark", callback_data=f"bookmark:{query}")
                ],
                [
                    InlineKeyboardButton("🔍 Search Lagi", switch_inline_query_current_chat="")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await msg.edit_text(
                response,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        else:
            await msg.edit_text("❌ Gagal mengambil artikel. Coba lagi.")

    except Exception as e:
        logger.error(f"Error in search: {e}")
        await msg.edit_text(
            "❌ Terjadi kesalahan. Mohon coba lagi nanti."
        )


@rate_limit(seconds=5)
async def pdf_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /pdf command"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    scraper = scrapers[language]

    query = ' '.join(context.args)

    if not query:
        await update.message.reply_text(
            "❌ Mohon berikan kata kunci.\n\n"
            "*Contoh:*\n"
            "`/pdf Python programming`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Send processing message
    msg = await update.message.reply_text(
        f"🔍 Mencari artikel...",
    )

    try:
        # Search article
        article_url = scraper.search_article(query)

        if not article_url:
            await msg.edit_text(f"❌ Artikel tidak ditemukan: *{query}*", parse_mode=ParseMode.MARKDOWN)
            return

        # Scrape article
        await msg.edit_text("📖 Mengambil data artikel...")
        article_data = scraper.scrape_article(article_url)

        if article_data:
            # Generate PDF
            await msg.edit_text("📄 Membuat PDF...")
            pdf_filename = f"wikipedia_{query.replace(' ', '_')}_{int(time.time())}.pdf"

            if scraper.export_to_pdf(article_data, pdf_filename):
                # Send PDF file
                await msg.edit_text("📤 Mengirim PDF...")

                with open(pdf_filename, 'rb') as pdf_file:
                    await update.message.reply_document(
                        document=pdf_file,
                        filename=f"{article_data['title']}.pdf",
                        caption=f"📄 *{article_data['title']}*\n\n🌍 Language: {language.upper()}",
                        parse_mode=ParseMode.MARKDOWN
                    )

                # Delete the status message
                await msg.delete()

                # Clean up file
                if os.path.exists(pdf_filename):
                    os.remove(pdf_filename)

                # Increment search count
                increment_search_count(user_id)
            else:
                await msg.edit_text("❌ Gagal membuat PDF. Coba lagi.")
        else:
            await msg.edit_text("❌ Gagal mengambil artikel.")

    except Exception as e:
        logger.error(f"Error in PDF generation: {e}")
        await msg.edit_text("❌ Terjadi kesalahan. Mohon coba lagi.")


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /language command"""
    user_id = update.effective_user.id
    current_lang = get_user_language(user_id)

    text = (
        f"🌍 *Pilih Bahasa Wikipedia*\n\n"
        f"Bahasa saat ini: *{'English' if current_lang == 'en' else 'Indonesian'}*\n\n"
        f"Pilih bahasa di bawah ini:"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🇬🇧 English" + (" ✓" if current_lang == 'en' else ""),
                callback_data="lang:en"
            ),
            InlineKeyboardButton(
                "🇮🇩 Indonesian" + (" ✓" if current_lang == 'id' else ""),
                callback_data="lang:id"
            )
        ],
        [InlineKeyboardButton("🏠 Back", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /stats command"""
    user_id = update.effective_user.id

    if user_id not in user_data:
        user_data[user_id] = {'language': 'en', 'bookmarks': [], 'searches': 0}

    data = user_data[user_id]
    language_name = 'English 🇬🇧' if data['language'] == 'en' else 'Indonesian 🇮🇩'

    stats_text = (
        f"📊 *Statistik Anda*\n\n"
        f"🔍 Pencarian: *{data['searches']}*\n"
        f"🔖 Bookmark: *{len(data['bookmarks'])}*\n"
        f"🌍 Bahasa: *{language_name}*\n"
    )

    keyboard = [[InlineKeyboardButton("🏠 Back to Home", callback_data="start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )


async def bookmark_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /bookmark command"""
    user_id = update.effective_user.id
    query = ' '.join(context.args)

    if not query:
        await update.message.reply_text(
            "❌ Mohon berikan nama artikel.\n\n"
            "*Contoh:*\n`/bookmark Python programming`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    if user_id not in user_data:
        user_data[user_id] = {'language': 'en', 'bookmarks': [], 'searches': 0}

    # Check if already bookmarked
    if query not in user_data[user_id]['bookmarks']:
        user_data[user_id]['bookmarks'].append(query)
        await update.message.reply_text(
            f"✅ Artikel disimpan: *{query}*\n\n"
            f"Lihat semua bookmark: /bookmarks",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await update.message.reply_text(
            f"ℹ️ Artikel sudah ada di bookmark: *{query}*",
            parse_mode=ParseMode.MARKDOWN
        )


async def bookmarks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /bookmarks command"""
    user_id = update.effective_user.id

    if user_id not in user_data or not user_data[user_id]['bookmarks']:
        await update.message.reply_text(
            "📚 Belum ada bookmark.\n\n"
            "Simpan artikel dengan: `/bookmark <nama artikel>`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    bookmarks = user_data[user_id]['bookmarks']
    text = "📚 *Bookmarks Anda:*\n\n"

    for i, bookmark in enumerate(bookmarks, 1):
        text += f"{i}. {bookmark}\n"

    text += f"\n_Total: {len(bookmarks)} artikel_"

    keyboard = [[InlineKeyboardButton("🗑️ Clear All", callback_data="clear_bookmarks")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )


async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /random command"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    scraper = scrapers[language]

    msg = await update.message.reply_text("🎲 Mencari artikel random...")

    try:
        # Get random article URL
        random_url = f"{scraper.base_url}/wiki/Special:Random"
        response = scraper.get_page(random_url)

        if response:
            article_url = response.url
            article_data = scraper.scrape_article(article_url)

            if article_data:
                summary = article_data['summary'][:400] + "..."

                response_text = (
                    f"🎲 *Artikel Random*\n\n"
                    f"*{article_data['title']}*\n\n"
                    f"{summary}\n\n"
                    f"🔗 [Baca Lengkap]({article_data['url']})"
                )

                keyboard = [
                    [
                        InlineKeyboardButton("📄 Export PDF", callback_data=f"pdf:{article_data['title']}"),
                        InlineKeyboardButton("🎲 Random Lagi", callback_data="random")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await msg.edit_text(
                    response_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
            else:
                await msg.edit_text("❌ Gagal mengambil artikel. Coba lagi.")
        else:
            await msg.edit_text("❌ Gagal mengambil artikel random.")

    except Exception as e:
        logger.error(f"Error in random: {e}")
        await msg.edit_text("❌ Terjadi kesalahan.")


@rate_limit(seconds=5)
async def compare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /compare command - membandingkan dua artikel"""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    scraper = scrapers[language]

    # Parse arguments - expected format: /compare Article1 vs Article2
    args = ' '.join(context.args)

    if not args or ' vs ' not in args.lower():
        await update.message.reply_text(
            "❌ Format tidak valid.\n\n"
            "*Gunakan format:*\n"
            "`/compare Topic1 vs Topic2`\n\n"
            "*Contoh:*\n"
            "`/compare Python vs Java`\n"
            "`/compare iPhone vs Android`\n"
            "`/compare Bitcoin vs Ethereum`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Split by 'vs' (case insensitive)
    parts = args.lower().split(' vs ')
    if len(parts) != 2:
        await update.message.reply_text(
            "❌ Mohon bandingkan tepat 2 topik.\n"
            "Contoh: `/compare Python vs Java`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    topic1 = parts[0].strip()
    topic2 = parts[1].strip()

    msg = await update.message.reply_text(
        f"🔍 Membandingkan *{topic1.title()}* vs *{topic2.title()}*...",
        parse_mode=ParseMode.MARKDOWN
    )

    try:
        # Search both articles
        await msg.edit_text(f"📖 Mencari artikel pertama: *{topic1.title()}*...", parse_mode=ParseMode.MARKDOWN)
        url1 = scraper.search_article(topic1)

        await msg.edit_text(f"📖 Mencari artikel kedua: *{topic2.title()}*...", parse_mode=ParseMode.MARKDOWN)
        url2 = scraper.search_article(topic2)

        if not url1:
            await msg.edit_text(f"❌ Artikel tidak ditemukan: *{topic1}*", parse_mode=ParseMode.MARKDOWN)
            return

        if not url2:
            await msg.edit_text(f"❌ Artikel tidak ditemukan: *{topic2}*", parse_mode=ParseMode.MARKDOWN)
            return

        # Scrape both articles
        await msg.edit_text("🔄 Mengambil data artikel...")
        article1 = scraper.scrape_article(url1)
        article2 = scraper.scrape_article(url2)

        if not article1 or not article2:
            await msg.edit_text("❌ Gagal mengambil data artikel.")
            return

        # Build comparison
        comparison = f"📊 *Perbandingan: {article1['title']} vs {article2['title']}*\n\n"

        # Compare basic info
        comparison += "━━━━━━━━━━━━━━━━━━━━\n"
        comparison += f"*📝 {article1['title']}*\n"
        comparison += f"• Kategori: {len(article1['categories'])}\n"
        comparison += f"• Referensi: {article1['references']}\n"
        comparison += f"• Panjang: {len(article1['content'])} karakter\n\n"

        comparison += f"*📝 {article2['title']}*\n"
        comparison += f"• Kategori: {len(article2['categories'])}\n"
        comparison += f"• Referensi: {article2['references']}\n"
        comparison += f"• Panjang: {len(article2['content'])} karakter\n"
        comparison += "━━━━━━━━━━━━━━━━━━━━\n\n"

        # Compare categories
        cats1 = set(article1['categories'][:10])
        cats2 = set(article2['categories'][:10])
        common_cats = cats1.intersection(cats2)

        if common_cats:
            comparison += f"*🔗 Kategori Sama:*\n"
            for cat in list(common_cats)[:3]:
                comparison += f"• {cat}\n"
            if len(common_cats) > 3:
                comparison += f"_... dan {len(common_cats) - 3} lainnya_\n"
            comparison += "\n"

        # Compare infobox if available
        if article1.get('infobox') and article2.get('infobox'):
            comparison += "*📋 Perbandingan Info:*\n"

            # Find common keys
            keys1 = set(article1['infobox'].keys())
            keys2 = set(article2['infobox'].keys())
            common_keys = keys1.intersection(keys2)

            if common_keys:
                for key in list(common_keys)[:3]:
                    val1 = article1['infobox'][key][:50]
                    val2 = article2['infobox'][key][:50]
                    comparison += f"\n*{key}:*\n"
                    comparison += f"  1️⃣ {val1}...\n"
                    comparison += f"  2️⃣ {val2}...\n"
            comparison += "\n"

        # Add summaries
        comparison += "*📄 Ringkasan:*\n\n"
        comparison += f"*{article1['title']}:*\n{article1['summary'][:200]}...\n\n"
        comparison += f"*{article2['title']}:*\n{article2['summary'][:200]}...\n\n"

        # Add links
        comparison += "*🔗 Baca Selengkapnya:*\n"
        comparison += f"[{article1['title']}]({article1['url']})\n"
        comparison += f"[{article2['title']}]({article2['url']})"

        # Create keyboard
        keyboard = [
            [
                InlineKeyboardButton(f"📄 PDF {article1['title'][:15]}", callback_data=f"pdf:{topic1}"),
                InlineKeyboardButton(f"📄 PDF {article2['title'][:15]}", callback_data=f"pdf:{topic2}")
            ],
            [
                InlineKeyboardButton("🔍 Compare Lagi", switch_inline_query_current_chat="/compare ")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send comparison (split if too long)
        if len(comparison) > 4000:
            # Send in parts
            parts = [comparison[i:i+4000] for i in range(0, len(comparison), 4000)]
            await msg.edit_text(parts[0], parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            for part in parts[1:-1]:
                await update.message.reply_text(part, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            await update.message.reply_text(
                parts[-1],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        else:
            await msg.edit_text(
                comparison,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )

        # Increment search count
        increment_search_count(user_id)

    except Exception as e:
        logger.error(f"Error in compare: {e}")
        await msg.edit_text("❌ Terjadi kesalahan saat membandingkan artikel.")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /about command"""
    about_text = """
ℹ️ *Tentang Wikipedia Scraper Bot*

Bot ini membantu Anda mengakses Wikipedia dengan mudah langsung dari Telegram.

*Fitur:*
• 🔍 Search artikel dengan cepat
• 📄 Export ke PDF
• 🌍 Multi-language (EN/ID)
• 🔖 Bookmark artikel favorit
• 🎲 Discover artikel random
• 📊 Compare dua artikel

*Teknologi:*
• Python 3.x
• python-telegram-bot
• BeautifulSoup4
• ReportLab

*Developer:*
Wikipedia Scraper Bot v1.0

*Source Code:*
GitHub: [wikipedia-scraper]

_Bot ini dibuat untuk tujuan edukatif._
    """

    keyboard = [[InlineKeyboardButton("🏠 Back to Home", callback_data="start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        about_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


# Callback Query Handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk inline button callbacks"""
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

    # Handle different callback actions
    if data == "start":
        await start_callback(update, context)
    elif data == "help":
        await help_command(update, context)
    elif data == "language":
        await language_command(update, context)
    elif data == "stats":
        await stats_command(update, context)
    elif data.startswith("lang:"):
        lang = data.split(":")[1]
        set_user_language(user_id, lang)
        await query.answer(f"✅ Bahasa diubah ke {'English' if lang == 'en' else 'Indonesian'}")
        await language_command(update, context)
    elif data.startswith("pdf:"):
        search_query = data.split(":", 1)[1]
        await query.answer("📄 Generating PDF...")
        # Simulate message for pdf_command
        context.args = search_query.split()
        update.message = query.message
        await pdf_command(update, context)
    elif data.startswith("bookmark:"):
        bookmark_query = data.split(":", 1)[1]
        if user_id not in user_data:
            user_data[user_id] = {'language': 'en', 'bookmarks': [], 'searches': 0}
        if bookmark_query not in user_data[user_id]['bookmarks']:
            user_data[user_id]['bookmarks'].append(bookmark_query)
            await query.answer(f"✅ Disimpan: {bookmark_query}")
        else:
            await query.answer("ℹ️ Sudah ada di bookmark")
    elif data == "clear_bookmarks":
        if user_id in user_data:
            user_data[user_id]['bookmarks'] = []
        await query.answer("✅ Semua bookmark dihapus")
        await query.edit_message_text(
            "📚 Semua bookmark telah dihapus.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Home", callback_data="start")]])
        )
    elif data == "random":
        context.args = []
        update.message = query.message
        await random_command(update, context)


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback untuk tombol back to home"""
    user = update.effective_user

    welcome_text = (
        f"👋 Hi *{user.first_name}*!\n\n"
        f"Saya *Wikipedia Scraper Bot* yang dapat membantu Anda:\n\n"
        f"🔍 Mencari artikel Wikipedia\n"
        f"📄 Export artikel ke PDF\n"
        f"🌍 Mendukung berbagai bahasa\n"
        f"🔖 Simpan artikel favorit\n"
        f"🎲 Temukan artikel random\n\n"
        f"Ketik /help untuk melihat semua perintah."
    )

    keyboard = [
        [
            InlineKeyboardButton("🔍 Search", switch_inline_query_current_chat=""),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("🌍 Language", callback_data="language"),
            InlineKeyboardButton("📊 Stats", callback_data="stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk unknown commands"""
    await update.message.reply_text(
        "❌ Perintah tidak dikenal.\n\n"
        "Ketik /help untuk melihat perintah yang tersedia."
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Main function to run the bot"""

    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN tidak ditemukan!")
        return

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("pdf", pdf_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("bookmark", bookmark_command))
    application.add_handler(CommandHandler("bookmarks", bookmarks_command))
    application.add_handler(CommandHandler("random", random_command))
    application.add_handler(CommandHandler("compare", compare_command))
    application.add_handler(CommandHandler("about", about_command))

    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))

    # Add unknown command handler
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("🤖 Wikipedia Scraper Bot started...")
    logger.info(f"Bot is running. Press Ctrl+C to stop.")

    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
