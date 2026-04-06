#!/usr/bin/env python3
"""
IT Hardware Daily Report - Main Entry Point
Collects data from multiple platforms, generates AI analysis,
creates HTML report, and sends via email.

Usage:
    python run_daily.py                    # Full pipeline (collect + analyze + report + email)
    python run_daily.py --mode collect     # Data collection only
    python run_daily.py --mode analyze     # Analysis only (uses existing data)
    python run_daily.py --mode report      # Generate report only
    python run_daily.py --mode email       # Send email only
    python run_daily.py --test             # Test all components
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import modules
from crawlers.jd_crawler import JDCrawler
from crawlers.tmall_crawler import TmallCrawler
from crawlers.amazon_crawler import AmazonCrawler
from crawlers.newegg_crawler import NeweggCrawler
from crawlers.base_crawler import ProductInfo
from analysis.ai_analyzer import MiniMaxAnalyzer
from reporting.html_generator import HTMLReportGenerator
from notification.email_sender import EmailSender


def setup_logging(date_str: str) -> logging.Logger:
    """Setup structured logging"""
    log_dir = PROJECT_ROOT / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f'it_daily_{date_str}.log'

    logger = logging.getLogger('it_daily_report')
    logger.setLevel(logging.INFO)
    if logger.handlers:
        logger.handlers.clear()

    # File handler (UTF-8)
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'
    ))
    logger.addHandler(fh)

    # Console handler (Windows-safe: avoid emojis in handler, use basicConfig workaround)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
    logger.addHandler(ch)

    # Fix Windows GBK encoding for stdout
    try:
        import io
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

    return logger


def load_config() -> Dict:
    """Load system configuration"""
    config_path = PROJECT_ROOT / 'config' / 'settings.json'
    if config_path.exists():
        with open(config_path, encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_brands() -> List[str]:
    """Load brand list from config"""
    config_path = PROJECT_ROOT / 'config' / 'brands.json'
    if config_path.exists():
        with open(config_path, encoding='utf-8') as f:
            data = json.load(f)
            # Get all brands from PSU section (primary category)
            return list(data.get('psu', {}).get('brands', {}).keys())
    return ["ASUS", "MSI", "Corsair", "Seasonic", "Gigabyte"]


def run_collection(config: Dict, logger: logging.Logger) -> List[Dict]:
    """Collect data from all platforms"""
    logger.info("=" * 50)
    logger.info("STEP 1: Data Collection")
    logger.info("=" * 50)

    brands = load_brands()
    categories = config.get('categories', [{"id": "psu", "name": "電源供應器"}])
    category = categories[0]['id']  # Focus on PSU for now

    all_products = []

    crawlers = [
        ("JD", JDCrawler()),
        ("Tmall", TmallCrawler()),
        ("Amazon-US", AmazonCrawler("us")),
        ("Newegg", NeweggCrawler()),
    ]

    for name, crawler in crawlers:
        try:
            logger.info(f"  Crawling {name}...")
            products = crawler.collect(brands, category)
            all_products.extend([p.to_dict() for p in products])
            logger.info(f"  ✅ {name}: collected {len(products)} products")
        except Exception as e:
            logger.error(f"  ❌ {name}: {e}")
        finally:
            crawler.close()

    # Also try Amazon CN
    try:
        logger.info("  Crawling Amazon-CN...")
        crawler = AmazonCrawler("cn")
        products = crawler.collect(brands, category)
        all_products.extend([p.to_dict() for p in products])
        logger.info(f"  ✅ Amazon-CN: collected {len(products)} products")
        crawler.close()
    except Exception as e:
        logger.error(f"  ❌ Amazon-CN: {e}")

    logger.info(f"Total collected: {len(all_products)} products")
    return all_products


def run_analysis(products: List[Dict], config: Dict, logger: logging.Logger) -> Dict:
    """Run AI analysis on collected data"""
    logger.info("=" * 50)
    logger.info("STEP 2: AI Analysis")
    logger.info("=" * 50)

    analyzer = MiniMaxAnalyzer()
    analysis = analyzer.get_analysis_dict(products)

    logger.info(f"Summary: {analysis.get('summary', 'N/A')}")
    logger.info(f"Brand rankings: {len(analysis.get('brand_rankings', []))} brands analyzed")
    logger.info(f"Top products: {len(analysis.get('top_products', []))} recommended")
    logger.info(f"Recommendations: {len(analysis.get('recommendations', []))} items")

    return analysis


def run_report(
    products: List[Dict],
    analysis: Dict,
    config: Dict,
    date_str: str,
    logger: logging.Logger
) -> tuple[str, str]:
    """Generate HTML report and save JSON data"""
    logger.info("=" * 50)
    logger.info("STEP 3: Report Generation")
    logger.info("=" * 50)

    # Generate HTML
    generator = HTMLReportGenerator()
    html = generator.generate(products, analysis, date_str)
    html_path = generator.save_report(html, date_str)
    logger.info(f"✅ HTML report saved: {html_path}")

    # Save JSON data
    data_dir = PROJECT_ROOT / 'data'
    data_dir.mkdir(exist_ok=True)
    json_path = data_dir / f'it_daily_data_{date_str}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'date': date_str,
            'products': products,
            'analysis': analysis,
            'generated_at': datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ JSON data saved: {json_path}")

    return html_path, str(json_path)


def run_email(
    html_path: str,
    json_path: str,
    date_str: str,
    config: Dict,
    logger: logging.Logger
) -> Dict:
    """Send report via email"""
    logger.info("=" * 50)
    logger.info("STEP 4: Email Delivery")
    logger.info("=" * 50)

    sender = EmailSender()
    result = sender.send_daily_report(html_path, json_path, date_str)

    if result.get('success'):
        logger.info(f"✅ Email sent successfully!")
    else:
        logger.error(f"❌ Email failed: {result.get('error')}")

    return result


def run_test(logger: logging.Logger):
    """Test all components"""
    logger.info("=" * 50)
    logger.info("TEST MODE: Testing all components")
    logger.info("=" * 50)

    # 1. Config
    config = load_config()
    logger.info(f"✅ Config loaded: {len(config)} sections")

    # 2. Crawler
    try:
        with JDCrawler() as crawler:
            products = crawler.collect(["MSI", "ASUS"], "psu")
            logger.info(f"✅ JD Crawler: {len(products)} products")
    except Exception as e:
        logger.error(f"❌ JD Crawler: {e}")

    # 3. Analysis
    mock_data = [
        {"brand": "MSI", "model": "MAG A750BN", "price": 89.99, "rating": 4.5, "reviews": 1100, "platform": "JD", "currency": "CNY"},
        {"brand": "ASUS", "model": "ROG Thor 850P", "price": 189.99, "rating": 4.7, "reviews": 890, "platform": "Amazon", "currency": "USD"},
        {"brand": "Corsair", "model": "RM850x", "price": 139.99, "rating": 4.8, "reviews": 2100, "platform": "Amazon", "currency": "USD"},
    ]
    analyzer = MiniMaxAnalyzer()
    analysis = analyzer.get_analysis_dict(mock_data)
    logger.info(f"✅ AI Analyzer: {analysis.get('summary', 'N/A')}")

    # 4. HTML Report
    generator = HTMLReportGenerator()
    html = generator.generate(mock_data, analysis)
    html_path = generator.save_report(html)
    logger.info(f"✅ HTML Report: {html_path}")

    # 5. Email (dry run - just validate)
    sender = EmailSender()
    if sender.validate_config():
        logger.info("✅ Email Config: Valid")
        # Uncomment to actually send:
        # sender.send_daily_report(html_path, None)
    else:
        logger.warning("⚠️ Email Config: Invalid or missing")

    logger.info("=" * 50)
    logger.info("TEST COMPLETE")
    logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='IT Hardware Daily Report')
    parser.add_argument(
        '--mode',
        choices=['full', 'collect', 'analyze', 'report', 'email'],
        default='full',
        help='Run mode: full pipeline or specific step'
    )
    parser.add_argument(
        '--config',
        default=None,
        help='Path to config file'
    )
    parser.add_argument(
        '--date',
        default=None,
        help='Date string (YYYYMMDD) for report'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode'
    )
    args = parser.parse_args()

    # Setup
    date_str = args.date or datetime.now().strftime('%Y%m%d')
    logger = setup_logging(date_str)

    logger.info(f"IT Hardware Daily Report - {date_str}")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Project root: {PROJECT_ROOT}")

    if args.test:
        run_test(logger)
        return

    config = load_config()

    # Check for existing data if not in full/collect mode
    data_path = PROJECT_ROOT / 'data' / f'it_daily_data_{date_str}.json'
    products = []
    analysis = {}

    if args.mode in ('full', 'collect'):
        products = run_collection(config, logger)
        # Save collected data
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump({'date': date_str, 'products': products, 'generated_at': datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

    if args.mode in ('full', 'analyze', 'report', 'email'):
        # Load existing data if available
        if not products and data_path.exists():
            with open(data_path, encoding='utf-8') as f:
                data = json.load(f)
                products = data.get('products', [])
            logger.info(f"Loaded {len(products)} products from {data_path}")

        if products:
            analysis = run_analysis(products, config, logger)
        else:
            logger.warning("No products to analyze")

    if args.mode in ('full', 'report'):
        if not analysis and data_path.exists():
            with open(data_path, encoding='utf-8') as f:
                data = json.load(f)
                analysis = data.get('analysis', {})
                products = data.get('products', products)

        if products and analysis:
            html_path, json_path = run_report(products, analysis, config, date_str, logger)
        elif products:
            logger.warning("No analysis results — generating with mock analysis")
            mock_analysis = MiniMaxAnalyzer().get_analysis_dict(products)
            html_path, json_path = run_report(products, mock_analysis, config, date_str, logger)
        else:
            logger.error("No data to report")
            return

    if args.mode == 'full':
        # Find the latest HTML report
        reports_dir = PROJECT_ROOT / 'reports'
        html_files = sorted(reports_dir.glob('it_daily_report_*.html'), reverse=True)
        if html_files:
            html_path = str(html_files[0])
        else:
            html_path = str(PROJECT_ROOT / 'reports' / f'it_daily_report_{date_str}.html')

        json_path = str(data_path)

        if os.path.exists(html_path):
            run_email(html_path, json_path, date_str, config, logger)
        else:
            logger.warning(f"HTML report not found: {html_path}")

    if args.mode == 'email':
        # Send latest report
        reports_dir = PROJECT_ROOT / 'reports'
        html_files = sorted(reports_dir.glob('it_daily_report_*.html'), reverse=True)
        if html_files:
            run_email(str(html_files[0]), str(data_path), date_str, config, logger)
        else:
            logger.error("No HTML report found to send")

    logger.info("=" * 50)
    logger.info("DONE")
    logger.info("=" * 50)


if __name__ == '__main__':
    main()
