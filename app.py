import requests
from bs4 import BeautifulSoup
import json
import time
import argparse
from typing import Dict, List, Optional
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WikipediaScraper:
    """Web scraper untuk Wikipedia"""

    def __init__(self, language: str = 'en'):
        self.language = language
        self.base_url = f"https://{language}.wikipedia.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def get_page(self, url: str, timeout: int = 10) -> Optional[requests.Response]:
        """
        Mendapatkan halaman dari URL

        Args:
            url: URL yang akan di-scrape
            timeout: Timeout dalam detik

        Returns:
            Response object atau None jika gagal
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html_content: str) -> BeautifulSoup:
        """
        Parse HTML content dengan BeautifulSoup

        Args:
            html_content: HTML string

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html_content, 'html.parser')

    def scrape_homepage(self) -> Dict:
        """
        Scrape homepage Wikipedia

        Returns:
            Dictionary berisi data yang di-scrape
        """
        response = self.get_page(self.base_url)
        if not response:
            return {}

        soup = self.parse_html(response.text)

        data = {
            'title': '',
            'meta_description': '',
            'links': [],
            'images': [],
            'headings': [],
            'scripts': [],
        }

        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            data['title'] = title_tag.get_text(strip=True)

        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            data['meta_description'] = meta_desc.get('content', '')

        # Extract all links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text(strip=True)
            data['links'].append({
                'url': href,
                'text': text
            })

        # Extract all images
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            data['images'].append({
                'src': src,
                'alt': alt
            })

        # Extract headings (h1, h2, h3, etc.)
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                data['headings'].append({
                    'level': i,
                    'text': heading.get_text(strip=True)
                })

        # Extract script sources (untuk identifikasi teknologi)
        for script in soup.find_all('script', src=True):
            data['scripts'].append(script.get('src'))

        logger.info(f"Scraped {len(data['links'])} links, {len(data['images'])} images")
        return data

    def scrape_article_links(self, max_links: int = 20) -> List[str]:
        """
        Extract article links dari homepage

        Args:
            max_links: Maksimum jumlah link yang akan diambil

        Returns:
            List of article URLs
        """
        response = self.get_page(self.base_url)
        if not response:
            return []

        soup = self.parse_html(response.text)
        article_links = []

        # Cari semua link artikel Wikipedia
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            # Filter link artikel Wikipedia (yang dimulai dengan /wiki/)
            if href.startswith('/wiki/') and ':' not in href:
                full_url = self.base_url + href
                if full_url not in article_links:
                    article_links.append(full_url)

                if len(article_links) >= max_links:
                    break

        logger.info(f"Found {len(article_links)} article links")
        return article_links

    def scrape_article(self, article_url: str) -> Dict:
        """
        Scrape artikel Wikipedia spesifik

        Args:
            article_url: URL artikel Wikipedia

        Returns:
            Dictionary berisi data artikel
        """
        response = self.get_page(article_url)
        if not response:
            return {}

        soup = self.parse_html(response.text)

        data = {
            'url': article_url,
            'title': '',
            'summary': '',
            'content': '',
            'categories': [],
            'references': [],
            'infobox': {},
        }

        # Extract title
        title_tag = soup.find('h1', class_='firstHeading')
        if title_tag:
            data['title'] = title_tag.get_text(strip=True)

        # Extract summary (first paragraph)
        content_div = soup.find('div', class_='mw-parser-output')
        if content_div:
            first_p = content_div.find('p', recursive=False)
            if first_p:
                data['summary'] = first_p.get_text(strip=True)

            # Extract all text content
            data['content'] = content_div.get_text(separator='\n', strip=True)

        # Extract categories
        categories_div = soup.find('div', id='mw-normal-catlinks')
        if categories_div:
            for cat_link in categories_div.find_all('a'):
                if cat_link.get_text(strip=True) != 'Categories':
                    data['categories'].append(cat_link.get_text(strip=True))

        # Extract infobox
        infobox = soup.find('table', class_='infobox')
        if infobox:
            for row in infobox.find_all('tr'):
                header = row.find('th')
                value = row.find('td')
                if header and value:
                    data['infobox'][header.get_text(strip=True)] = value.get_text(strip=True)

        # Extract references count
        references = soup.find_all('li', id=lambda x: x and x.startswith('cite_note'))
        data['references'] = len(references)

        logger.info(f"Scraped article: {data['title']}")
        return data

    def extract_json_ld(self, html_content: str) -> List[Dict]:
        """
        Extract JSON-LD structured data dari halaman

        Args:
            html_content: HTML string

        Returns:
            List of JSON-LD objects
        """
        soup = self.parse_html(html_content)
        json_ld_data = []

        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                json_ld_data.append(data)
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"Failed to parse JSON-LD: {e}")

        return json_ld_data

    def search_article(self, query: str) -> Optional[str]:
        """
        Search artikel di Wikipedia berdasarkan query

        Args:
            query: Kata kunci pencarian

        Returns:
            URL artikel yang ditemukan atau None
        """
        search_url = f"{self.base_url}/w/api.php"
        params = {
            'action': 'opensearch',
            'search': query,
            'limit': 1,
            'namespace': 0,
            'format': 'json'
        }

        try:
            logger.info(f"Searching for: {query}")
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data and len(data) > 3 and data[3]:
                article_url = data[3][0]
                logger.info(f"Found article: {article_url}")
                return article_url
            else:
                logger.warning(f"No article found for query: {query}")
                return None

        except Exception as e:
            logger.error(f"Error searching: {e}")
            return None

    def save_to_json(self, data: Dict, filename: str = 'wikipedia_data.json'):
        """
        Simpan data ke file JSON

        Args:
            data: Data yang akan disimpan
            filename: Nama file output
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")

    def export_to_pdf(self, article_data: Dict, filename: str = 'wikipedia_article.pdf'):
        """
        Export artikel ke PDF

        Args:
            article_data: Data artikel yang akan di-export
            filename: Nama file PDF output
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#000000',
                spaceAfter=30,
                alignment=TA_CENTER
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor='#333333',
                spaceAfter=12,
                spaceBefore=12
            )

            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=11,
                alignment=TA_JUSTIFY,
                spaceAfter=12
            )

            # Title
            if article_data.get('title'):
                title = Paragraph(article_data['title'], title_style)
                story.append(title)
                story.append(Spacer(1, 0.2 * inch))

            # URL
            if article_data.get('url'):
                url_text = f"<b>URL:</b> {article_data['url']}"
                url_para = Paragraph(url_text, body_style)
                story.append(url_para)
                story.append(Spacer(1, 0.2 * inch))

            # Summary
            if article_data.get('summary'):
                summary_heading = Paragraph("Summary", heading_style)
                story.append(summary_heading)

                # Clean summary text for PDF
                summary_text = article_data['summary'].replace('<', '&lt;').replace('>', '&gt;')
                summary_para = Paragraph(summary_text, body_style)
                story.append(summary_para)
                story.append(Spacer(1, 0.3 * inch))

            # Categories
            if article_data.get('categories'):
                cat_heading = Paragraph("Categories", heading_style)
                story.append(cat_heading)

                categories_text = ', '.join(article_data['categories'][:10])
                categories_para = Paragraph(categories_text, body_style)
                story.append(categories_para)
                story.append(Spacer(1, 0.3 * inch))

            # Infobox
            if article_data.get('infobox') and article_data['infobox']:
                infobox_heading = Paragraph("Infobox", heading_style)
                story.append(infobox_heading)

                for key, value in list(article_data['infobox'].items())[:10]:
                    # Clean text for PDF
                    key_clean = key.replace('<', '&lt;').replace('>', '&gt;')
                    value_clean = value.replace('<', '&lt;').replace('>', '&gt;')

                    infobox_text = f"<b>{key_clean}:</b> {value_clean}"
                    infobox_para = Paragraph(infobox_text, body_style)
                    story.append(infobox_para)

                story.append(Spacer(1, 0.3 * inch))

            # References count
            if 'references' in article_data:
                ref_heading = Paragraph("References", heading_style)
                story.append(ref_heading)

                ref_text = f"Total references: {article_data['references']}"
                ref_para = Paragraph(ref_text, body_style)
                story.append(ref_para)
                story.append(Spacer(1, 0.3 * inch))

            # Content (limited to avoid huge PDFs)
            if article_data.get('content'):
                content_heading = Paragraph("Content", heading_style)
                story.append(content_heading)

                # Limit content length
                content_text = article_data['content'][:5000]
                if len(article_data['content']) > 5000:
                    content_text += "\n\n... (Content truncated for PDF export)"

                # Clean and split content into paragraphs
                content_text = content_text.replace('<', '&lt;').replace('>', '&gt;')
                paragraphs = content_text.split('\n')

                for para_text in paragraphs[:50]:  # Limit to 50 paragraphs
                    if para_text.strip():
                        para = Paragraph(para_text.strip(), body_style)
                        story.append(para)

            # Build PDF
            doc.build(story)
            logger.info(f"PDF exported to {filename}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            return False


def main():
    """Main function untuk menjalankan scraper"""

    # Setup argparse
    parser = argparse.ArgumentParser(
        description='Wikipedia Web Scraper - Scrape articles from Wikipedia',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape default homepage
  python app.py

  # Search and scrape specific article (English)
  python app.py -s "Python programming"
  python app.py --search "Artificial Intelligence"

  # Search and export to PDF
  python app.py -s "Python programming" --pdf
  python app.py --search "Machine Learning" --pdf

  # Search in Indonesian Wikipedia
  python app.py -s "Indonesia" -l id
  python app.py --search "Teknologi" --language id

  # Search in Indonesian and export to PDF
  python app.py -s "Indonesia" -l id --pdf

  # Use different language
  python app.py -l id
        """
    )

    parser.add_argument(
        '-s', '--search',
        type=str,
        help='Search for a specific article by keyword',
        metavar='QUERY'
    )

    parser.add_argument(
        '-l', '--language',
        type=str,
        default='en',
        choices=['en', 'id'],
        help='Wikipedia language (default: en for English, id for Indonesian)',
        metavar='LANG'
    )

    parser.add_argument(
        '--pdf',
        action='store_true',
        help='Export article detail to PDF (only works with --search)'
    )

    args = parser.parse_args()

    # Inisialisasi scraper dengan bahasa yang dipilih
    language_name = 'English' if args.language == 'en' else 'Indonesian'
    logger.info(f"Initializing scraper for {language_name} Wikipedia...")
    scraper = WikipediaScraper(language=args.language)

    # Jika ada query search
    if args.search:
        logger.info(f"Search mode: Looking for '{args.search}'")

        # Search artikel
        article_url = scraper.search_article(args.search)

        if article_url:
            # Scrape artikel yang ditemukan
            article_data = scraper.scrape_article(article_url)

            if article_data:
                print("\n" + "=" * 60)
                print(f"ARTICLE FOUND: {article_data['title']}")
                print("=" * 60)
                print(f"\nURL: {article_data['url']}")
                print(f"\nSummary:\n{article_data['summary']}\n")
                print(f"Categories: {', '.join(article_data['categories'][:5])}")
                print(f"References: {article_data['references']}")

                if article_data['infobox']:
                    print("\nInfobox:")
                    for key, value in list(article_data['infobox'].items())[:5]:
                        print(f"  • {key}: {value[:80]}...")

                # Simpan hasil JSON
                json_filename = f"wikipedia_search_{args.search.replace(' ', '_')}.json"
                scraper.save_to_json(article_data, json_filename)
                print(f"\nJSON data saved to: {json_filename}")

                # Export ke PDF jika diminta
                if args.pdf:
                    pdf_filename = f"wikipedia_search_{args.search.replace(' ', '_')}.pdf"
                    print(f"\nExporting to PDF...")
                    if scraper.export_to_pdf(article_data, pdf_filename):
                        print(f"PDF exported to: {pdf_filename}")
                    else:
                        print("Failed to export PDF. Check logs for details.")
        else:
            logger.error(f"Article not found for query: {args.search}")
            print(f"\nNo article found for '{args.search}'. Please try a different search term.")

    elif args.pdf:
        # Jika --pdf digunakan tanpa --search
        logger.warning("--pdf flag requires --search argument")
        print("\nWarning: --pdf flag only works with --search argument.")
        print("Example: python app.py -s \"Python programming\" --pdf")

    else:
        # Mode default: scrape homepage
        logger.info("Default mode: Scraping Wikipedia homepage...")
        homepage_data = scraper.scrape_homepage()

        if homepage_data:
            logger.info(f"Homepage Title: {homepage_data.get('title')}")
            logger.info(f"Total Links: {len(homepage_data.get('links', []))}")
            logger.info(f"Total Images: {len(homepage_data.get('images', []))}")

            # Simpan data ke JSON
            scraper.save_to_json(homepage_data, f'wikipedia_homepage_{args.language}.json')

        # Delay untuk menghindari rate limiting
        time.sleep(1)

        # Extract article links
        logger.info("Extracting article links...")
        article_links = scraper.scrape_article_links(max_links=10)

        if article_links:
            logger.info(f"Found {len(article_links)} article links:")
            for i, link in enumerate(article_links[:5], 1):
                logger.info(f"  {i}. {link}")

            # Simpan article links
            scraper.save_to_json({
                'article_links': article_links,
                'total': len(article_links)
            }, f'wikipedia_articles_{args.language}.json')

            # Scrape beberapa artikel sebagai contoh
            logger.info("Scraping sample articles...")
            articles_data = []
            for link in article_links[:3]:  # Ambil 3 artikel pertama
                time.sleep(1)  # Delay antar request
                article_data = scraper.scrape_article(link)
                if article_data:
                    articles_data.append(article_data)

            if articles_data:
                scraper.save_to_json({
                    'articles': articles_data,
                    'total': len(articles_data)
                }, f'wikipedia_articles_detail_{args.language}.json')

        # Extract JSON-LD data
        response = scraper.get_page(scraper.base_url)
        if response:
            json_ld_data = scraper.extract_json_ld(response.text)
            if json_ld_data:
                logger.info(f"Found {len(json_ld_data)} JSON-LD objects")
                scraper.save_to_json({
                    'json_ld': json_ld_data
                }, f'wikipedia_jsonld_{args.language}.json')

    logger.info("Scraping completed!")


if __name__ == "__main__":
    main()
