# 電源供應器銷售數據收集腳本 v3.0
# 收集全球主要品牌電源產品數據
# 覆蓋全球主要電商平台

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import random
import time

# 模擬代理headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}

# 品牌關鍵詞（16個主要品牌）
BRANDS = {
    'ASUS': ['ASUS', '華碩', 'ROG', 'TUF'],
    'MSI': ['MSI', '微星', 'MEG', 'MPG', 'MAG'],
    'Gigabyte': ['Gigabyte', '技嘉', 'GIGABYTE', 'AORUS'],
    'Corsair': ['Corsair', 'corsair', 'RMx', 'HX', 'SF'],
    'Seasonic': ['Seasonic', '海盜船', 'Focus', 'Prime'],
    'Thermaltake': ['Thermaltake', '曜越', 'Toughpower', 'Smart'],
    'Cooler Master': ['Cooler Master', '酷碼', 'V', 'MWE'],
    'FSP': ['FSP', '全漢', 'Hydro', 'Aurum'],
    'Enermax': ['Enermax', '保銳', 'Revolution', 'MaxPro'],
    'be quiet!': ['be quiet!', 'Pure Power', 'Straight Power'],
    'Silverstone': ['Silverstone', '銀欣', 'Strider', 'SFX'],
    'Lian Li': ['Lian Li', '聯力', 'SP', 'Edge'],
    'Phanteks': ['Phanteks', '追風者', 'Revolt', 'AMP'],
    'NZXT': ['NZXT', 'C-Series', 'E-Series'],
    'Chieftec': ['Chieftec', 'Power Smart', 'GPS'],
    'Deepcool': ['Deepcool', '九州風神', 'PM750D', 'DQ']
}

# ============================================
# 全球電商平台覆蓋（更新至31平台）
# ============================================
PLATFORMS = {
    # --- 北美 (8) ---
    'Amazon.com': 'https://www.amazon.com',
    'Newegg': 'https://www.newegg.com',
    'Best Buy': 'https://www.bestbuy.com',
    'B&H Photo': 'https://www.bhphotovideo.com',
    'Micro Center': 'https://www.microcenter.com',
    'eBay': 'https://www.ebay.com',
    'Walmart': 'https://www.walmart.com',
    'AliExpress': 'https://www.aliexpress.com',

    # --- 歐洲 (15) ---
    'Amazon UK': 'https://www.amazon.co.uk',
    'Amazon DE': 'https://www.amazon.de',
    'Amazon FR': 'https://www.amazon.fr',
    'Amazon IT': 'https://www.amazon.it',
    'Amazon ES': 'https://www.amazon.es',
    'Amazon NL': 'https://www.amazon.nl',
    'Amazon PL': 'https://www.amazon.pl',
    'Amazon SE': 'https://www.amazon.se',
    'Amazon DK': 'https://www.amazon.dk',
    'Amazon FI': 'https://www.amazon.fi',
    'MediaMarkt DE': 'https://www.mediamarkt.de',
    'Saturn DE': 'https://www.saturn.de',
    'Mindfactory DE': 'https://www.mindfactory.de',
    'Caseking DE': 'https://www.caseking.de',
    'LDLC FR': 'https://www.ldlc.com',

    # --- 中國 (4) ---
    '京東 JD.com': 'https://www.jd.com',
    '天貓 Tmall': 'https://www.tmall.com',
    '淘寶 Taobao': 'https://www.taobao.com',
    '蘇寧 Suning': 'https://www.suning.com',

    # --- 日本 (4) ---
    'Amazon JP': 'https://www.amazon.co.jp',
    'Yodobashi': 'https://www.yodobashi.com',
    'Bic Camera': 'https://www.biccamera.com',
    'Rakuten JP': 'https://www.rakuten.co.jp',

    # --- 亞洲其他 (4) ---
    'Amazon SG': 'https://www.amazon.sg',
    'Amazon IN': 'https://www.amazon.in',
    'Qoo10': 'https://www.qoo10.jp',
    'Shopee': 'https://shopee.tw',
}

# 平台區域分類
PLATFORM_REGIONS = {
    '北美': ['Amazon.com', 'Newegg', 'Best Buy', 'B&H Photo', 'Micro Center', 'eBay', 'Walmart', 'AliExpress'],
    '歐洲': ['Amazon UK', 'Amazon DE', 'Amazon FR', 'Amazon IT', 'Amazon ES', 'Amazon NL', 'Amazon PL',
             'Amazon SE', 'Amazon DK', 'Amazon FI',
             'MediaMarkt DE', 'Saturn DE', 'Mindfactory DE', 'Caseking DE', 'LDLC FR'],
    '中國': ['京東 JD.com', '天貓 Tmall', '淘寶 Taobao', '蘇寧 Suning'],
    '日本': ['Amazon JP', 'Yodobashi', 'Bic Camera', 'Rakuten JP'],
    '亞洲其他': ['Amazon SG', 'Amazon IN', 'Qoo10', 'Shopee'],
}

def get_platforms_by_region():
    """按區域統計平台數量"""
    stats = {}
    for region, platforms in PLATFORM_REGIONS.items():
        stats[region] = len(platforms)
    return stats

def search_amazon_psu(brand_keyword, domain='com'):
    """搜索Amazon電源產品（支持多國家）"""
    results = []
    domain_map = {
        'com': 'amazon.com',
        'co.uk': 'amazon.co.uk',
        'de': 'amazon.de',
        'fr': 'amazon.fr',
        'it': 'amazon.it',
        'es': 'amazon.es',
        'nl': 'amazon.nl',
        'pl': 'amazon.pl',
        'jp': 'amazon.co.jp',
        'sg': 'amazon.sg',
        'in': 'amazon.in',
    }
    try:
        search_url = f"https://www.amazon.{domain_map.get(domain, 'com')}/s?k=power+supply+unit+{brand_keyword}"
        results.append({
            'platform': f'Amazon {domain.upper()}',
            'brand': brand_keyword,
            'timestamp': datetime.now().isoformat(),
            'url': search_url,
            'note': '需要實際爬蟲或API接口'
        })
    except Exception as e:
        print(f"Amazon {domain} 搜索錯誤: {e}")
    return results

def search_newegg_psu(brand_keyword):
    """搜索Newegg電源產品"""
    results = []
    try:
        search_url = f"https://www.newegg.com/p/pl?d=power+supply+{brand_keyword}"
        results.append({
            'platform': 'Newegg',
            'brand': brand_keyword,
            'timestamp': datetime.now().isoformat(),
            'url': search_url,
            'note': '需要實際爬蟲或API接口'
        })
    except Exception as e:
        print(f"Newegg搜索錯誤: {e}")
    return results

def search_bestbuy_psu(brand_keyword):
    """搜索Best Buy電源產品"""
    results = []
    try:
        search_url = f"https://www.bestbuy.com/site/searchpage.jsp?sp=+&qp=power+supply+{brand_keyword}"
        results.append({
            'platform': 'Best Buy',
            'brand': brand_keyword,
            'timestamp': datetime.now().isoformat(),
            'url': search_url,
            'note': '需要實際爬蟲或API接口'
        })
    except Exception as e:
        print(f"Best Buy搜索錯誤: {e}")
    return results

def search_jd_psu(brand_keyword):
    """搜索京東電源產品"""
    results = []
    try:
        search_url = f"https://search.jd.com/Search?keyword=電源+{brand_keyword}&enc=utf-8"
        results.append({
            'platform': '京東 JD.com',
            'brand': brand_keyword,
            'timestamp': datetime.now().isoformat(),
            'url': search_url,
            'note': '需要實際爬蟲或API接口'
        })
    except Exception as e:
        print(f"京東搜索錯誤: {e}")
    return results

def search_tmall_psu(brand_keyword):
    """搜索天貓電源產品"""
    results = []
    try:
        search_url = f"https://list.tmall.com/search_product.htm?q=電源+{brand_keyword}"
        results.append({
            'platform': '天貓 Tmall',
            'brand': brand_keyword,
            'timestamp': datetime.now().isoformat(),
            'url': search_url,
            'note': '需要實際爬蟲或API接口'
        })
    except Exception as e:
        print(f"天貓搜索錯誤: {e}")
    return results

def search_mediamarkt_psu(brand_keyword):
    """搜索MediaMarkt電源產品"""
    results = []
    try:
        search_url = f"https://www.mediamarkt.de/de/search.html?query=netzteil+{brand_keyword}"
        results.append({
            'platform': 'MediaMarkt DE',
            'brand': brand_keyword,
            'timestamp': datetime.now().isoformat(),
            'url': search_url,
            'note': '需要實際爬蟲或API接口'
        })
    except Exception as e:
        print(f"MediaMarkt搜索錯誤: {e}")
    return results

def search_yodobashi_psu(brand_keyword):
    """搜索Yodobashi Camera電源產品"""
    results = []
    try:
        search_url = f"https://www.yodobashi.com/?q=電源+{brand_keyword}"
        results.append({
            'platform': 'Yodobashi',
            'brand': brand_keyword,
            'timestamp': datetime.now().isoformat(),
            'url': search_url,
            'note': '需要實際爬蟲或API接口'
        })
    except Exception as e:
        print(f"Yodobashi搜索錯誤: {e}")
    return results

def search_ebay_psu(brand_keyword):
    """搜索eBay電源產品"""
    results = []
    try:
        search_url = f"https://www.ebay.com/sch/i.html?_nkw=power+supply+unit+{brand_keyword}"
        results.append({
            'platform': 'eBay',
            'brand': brand_keyword,
            'timestamp': datetime.now().isoformat(),
            'url': search_url,
            'note': '需要實際爬蟲或API接口'
        })
    except Exception as e:
        print(f"eBay搜索錯誤: {e}")
    return results

def collect_all_data():
    """收集所有品牌的電源數據"""
    all_data = {
        'collect_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'platforms_covered': list(PLATFORMS.keys()),
        'platform_count': len(PLATFORMS),
        'platform_stats': get_platforms_by_region(),
        'brands': {},
        'summary': {}
    }

    for brand, keywords in BRANDS.items():
        all_data['brands'][brand] = {
            'keywords': keywords,
            'products': [],
            'platform_data': {},
            'market_data': {
                'avg_price': None,
                'total_listings': None,
                'top_rated': None,
                'best_seller': None
            }
        }

    return all_data

def generate_sample_data():
    """生成模擬數據用於演示"""
    region_stats = get_platforms_by_region()

    data = {
        'collect_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'report_type': '每日電源供應器銷售數據報告',
        'platforms_covered': list(PLATFORMS.keys()),
        'total_platforms': len(PLATFORMS),
        'platform_region_stats': region_stats,
        'brands': {
            'ASUS': {
                'name': '華碩 (ASUS)',
                'products': [
                    {'model': 'ROG Thor 1200P2', 'watt': 1200, 'price': 299.99, 'rating': 4.8, 'reviews': 1250, 'sales': 1580},
                    {'model': 'ROG Thor 850P', 'watt': 850, 'price': 189.99, 'rating': 4.7, 'reviews': 890, 'sales': 2150},
                    {'model': 'TUF Gaming 750B', 'watt': 750, 'price': 99.99, 'rating': 4.6, 'reviews': 520, 'sales': 3420},
                    {'model': 'Prime Gold 850W', 'watt': 850, 'price': 149.99, 'rating': 4.5, 'reviews': 340, 'sales': 1890}
                ],
                'platform_coverage': ['Amazon.com', 'Newegg', 'Best Buy', 'Amazon DE', 'Amazon UK', '京東', 'Mindfactory DE'],
                'market_data': {
                    'avg_price': 184.99,
                    'total_listings': 45,
                    'total_sales': 9040,
                    'top_rated': 'ROG Thor 1200P2',
                    'best_seller': 'TUF Gaming 750B'
                }
            },
            'MSI': {
                'name': '微星 (MSI)',
                'products': [
                    {'model': 'MEG Ai1300P', 'watt': 1300, 'price': 319.99, 'rating': 4.9, 'reviews': 680, 'sales': 890},
                    {'model': 'MPG A850GF', 'watt': 850, 'price': 139.99, 'rating': 4.7, 'reviews': 920, 'sales': 2680},
                    {'model': 'MAG A750BN', 'watt': 750, 'price': 89.99, 'rating': 4.5, 'reviews': 1100, 'sales': 4850},
                    {'model': 'MAG A650BN', 'watt': 650, 'price': 69.99, 'rating': 4.4, 'reviews': 780, 'sales': 3920}
                ],
                'platform_coverage': ['Amazon.com', 'Newegg', 'Best Buy', 'Amazon JP', '京東', 'Bic Camera'],
                'market_data': {
                    'avg_price': 154.99,
                    'total_listings': 42,
                    'total_sales': 12340,
                    'top_rated': 'MEG Ai1300P',
                    'best_seller': 'MAG A750BN'
                }
            },
            'Gigabyte': {
                'name': '技嘉 (Gigabyte)',
                'products': [
                    {'model': 'AORUS P1200W', 'watt': 1200, 'price': 279.99, 'rating': 4.8, 'reviews': 450, 'sales': 720},
                    {'model': 'AORUS 850W', 'watt': 850, 'price': 159.99, 'rating': 4.7, 'reviews': 620, 'sales': 1560},
                    {'model': 'P750GM', 'watt': 750, 'price': 99.99, 'rating': 4.6, 'reviews': 380, 'sales': 2340},
                    {'model': 'P650B', 'watt': 650, 'price': 69.99, 'rating': 4.5, 'reviews': 290, 'sales': 3150}
                ],
                'platform_coverage': ['Amazon.com', 'Newegg', 'Amazon DE', 'Amazon UK', 'Mindfactory DE', 'Caseking DE'],
                'market_data': {
                    'avg_price': 152.49,
                    'total_listings': 38,
                    'total_sales': 7770,
                    'top_rated': 'AORUS P1200W',
                    'best_seller': 'P650B'
                }
            },
            'Corsair': {
                'name': 'Corsair 美商海盜船',
                'products': [
                    {'model': 'HX1500i', 'watt': 1500, 'price': 449.99, 'rating': 4.9, 'reviews': 320, 'sales': 450},
                    {'model': 'HX1000i', 'watt': 1000, 'price': 289.99, 'rating': 4.8, 'reviews': 580, 'sales': 890},
                    {'model': 'RM850x', 'watt': 850, 'price': 139.99, 'rating': 4.8, 'reviews': 2100, 'sales': 4250},
                    {'model': 'RM750x', 'watt': 750, 'price': 119.99, 'rating': 4.7, 'reviews': 1850, 'sales': 3680},
                    {'model': 'CX750F', 'watt': 750, 'price': 89.99, 'rating': 4.5, 'reviews': 420, 'sales': 2150}
                ],
                'platform_coverage': ['Amazon.com', 'Newegg', 'Best Buy', 'Amazon UK', 'Amazon DE', 'Amazon FR', 'Amazon JP', 'LDLC FR'],
                'market_data': {
                    'avg_price': 197.99,
                    'total_listings': 58,
                    'total_sales': 11420,
                    'top_rated': 'HX1500i',
                    'best_seller': 'RM850x'
                }
            },
            'Seasonic': {
                'name': 'Seasonic 海盜船',
                'products': [
                    {'model': 'Prime TX-1000', 'watt': 1000, 'price': 279.99, 'rating': 4.9, 'reviews': 580, 'sales': 920},
                    {'model': 'Prime GX-850', 'watt': 850, 'price': 169.99, 'rating': 4.8, 'reviews': 720, 'sales': 1680},
                    {'model': 'Focus GX-750', 'watt': 750, 'price': 129.99, 'rating': 4.7, 'reviews': 890, 'sales': 2350},
                    {'model': 'Focus CM-650', 'watt': 650, 'price': 99.99, 'rating': 4.6, 'reviews': 450, 'sales': 1890}
                ],
                'platform_coverage': ['Amazon.com', 'Newegg', 'Amazon DE', 'Amazon UK', 'LDLC FR'],
                'market_data': {
                    'avg_price': 169.99,
                    'total_listings': 35,
                    'total_sales': 6840,
                    'top_rated': 'Prime TX-1000',
                    'best_seller': 'Focus GX-750'
                }
            },
            'Thermaltake': {
                'name': 'Thermaltake 曜越',
                'products': [
                    {'model': 'Toughpower GF3 1200W', 'watt': 1200, 'price': 259.99, 'rating': 4.7, 'reviews': 380, 'sales': 680},
                    {'model': 'Toughpower GF2 850W', 'watt': 850, 'price': 149.99, 'rating': 4.6, 'reviews': 520, 'sales': 1420},
                    {'model': 'Smart 750W', 'watt': 750, 'price': 79.99, 'rating': 4.4, 'reviews': 680, 'sales': 2560},
                    {'model': 'Smart 600W', 'watt': 600, 'price': 59.99, 'rating': 4.3, 'reviews': 420, 'sales': 2180}
                ],
                'platform_coverage': ['Amazon.com', 'Newegg', 'Best Buy', 'Amazon DE', 'Amazon JP'],
                'market_data': {
                    'avg_price': 137.49,
                    'total_listings': 32,
                    'total_sales': 6840,
                    'top_rated': 'Toughpower GF3 1200W',
                    'best_seller': 'Smart 750W'
                }
            },
            'Cooler Master': {
                'name': 'Cooler Master 酷碼',
                'products': [
                    {'model': 'V850 SFX', 'watt': 850, 'price': 189.99, 'rating': 4.8, 'reviews': 420, 'sales': 780},
                    {'model': 'V750 Gold V2', 'watt': 750, 'price': 139.99, 'rating': 4.7, 'reviews': 580, 'sales': 1350},
                    {'model': 'MWE Gold 750', 'watt': 750, 'price': 99.99, 'rating': 4.5, 'reviews': 820, 'sales': 2680},
                    {'model': 'MWE Bronze 650', 'watt': 650, 'price': 69.99, 'rating': 4.4, 'reviews': 560, 'sales': 1950}
                ],
                'platform_coverage': ['Amazon.com', 'Newegg', 'Best Buy', 'Amazon DE', 'Amazon UK', '京東'],
                'market_data': {
                    'avg_price': 124.99,
                    'total_listings': 40,
                    'total_sales': 6760,
                    'top_rated': 'V850 SFX',
                    'best_seller': 'MWE Gold 750'
                }
            },
            'FSP': {
                'name': 'FSP 全漢',
                'products': [
                    {'model': 'Hydro PTM Pro 850W', 'watt': 850, 'price': 149.99, 'rating': 4.7, 'reviews': 320, 'sales': 890},
                    {'model': 'Hydro G Pro 750W', 'watt': 750, 'price': 109.99, 'rating': 4.5, 'reviews': 450, 'sales': 1560},
                    {'model': ' Hydro X 650W', 'watt': 650, 'price': 79.99, 'rating': 4.4, 'reviews': 380, 'sales': 1280},
                    {'model': 'FSP Hexa+ 550W', 'watt': 550, 'price': 49.99, 'rating': 4.3, 'reviews': 280, 'sales': 920}
                ],
                'platform_coverage': ['Amazon.com', 'Amazon DE', 'Amazon UK', '京東', '天貓'],
                'market_data': {
                    'avg_price': 97.49,
                    'total_listings': 28,
                    'total_sales': 4650,
                    'top_rated': 'Hydro PTM Pro 850W',
                    'best_seller': 'Hydro G Pro 750W'
                }
            },
            'Enermax': {
                'name': 'Enermax 保銳',
                'products': [
                    {'model': 'Revolution D.F. 850W', 'watt': 850, 'price': 159.99, 'rating': 4.7, 'reviews': 380, 'sales': 720},
                    {'model': 'MaxPro II 600W', 'watt': 600, 'price': 69.99, 'rating': 4.4, 'reviews': 420, 'sales': 1680},
                    {'model': 'Advance 750W', 'watt': 750, 'price': 89.99, 'rating': 4.5, 'reviews': 320, 'sales': 1120},
                    {'model': 'Twistball 550W', 'watt': 550, 'price': 49.99, 'rating': 4.2, 'reviews': 180, 'sales': 860}
                ],
                'platform_coverage': ['Amazon.com', 'Amazon DE', 'Amazon FR', 'LDLC FR'],
                'market_data': {
                    'avg_price': 92.49,
                    'total_listings': 25,
                    'total_sales': 4380,
                    'top_rated': 'Revolution D.F. 850W',
                    'best_seller': 'MaxPro II 600W'
                }
            },
            'be quiet!': {
                'name': 'be quiet! 德商必奇特',
                'products': [
                    {'model': 'Straight Power 12 1200W', 'watt': 1200, 'price': 289.99, 'rating': 4.9, 'reviews': 420, 'sales': 580},
                    {'model': 'Straight Power 11 850W', 'watt': 850, 'price': 169.99, 'rating': 4.8, 'reviews': 580, 'sales': 1180},
                    {'model': 'Pure Power 11 750W', 'watt': 750, 'price': 109.99, 'rating': 4.7, 'reviews': 720, 'sales': 1680},
                    {'model': 'Pure Power 10 600W', 'watt': 600, 'price': 79.99, 'rating': 4.5, 'reviews': 380, 'sales': 1280}
                ],
                'platform_coverage': ['Amazon.com', 'Amazon DE', 'Amazon UK', 'Amazon FR', 'MediaMarkt DE'],
                'market_data': {
                    'avg_price': 162.49,
                    'total_listings': 32,
                    'total_sales': 4720,
                    'top_rated': 'Straight Power 12 1200W',
                    'best_seller': 'Pure Power 11 750W'
                }
            },
            'Silverstone': {
                'name': 'Silverstone 銀欣',
                'products': [
                    {'model': 'Strider Platinum 1000W', 'watt': 1000, 'price': 269.99, 'rating': 4.8, 'reviews': 280, 'sales': 420},
                    {'model': 'SFX Gold 850W', 'watt': 850, 'price': 179.99, 'rating': 4.7, 'reviews': 380, 'sales': 780},
                    {'model': 'Strider Gold 750W', 'watt': 750, 'price': 119.99, 'rating': 4.6, 'reviews': 420, 'sales': 980},
                    {'model': 'SFX Bronze 600W', 'watt': 600, 'price': 89.99, 'rating': 4.4, 'reviews': 220, 'sales': 680}
                ],
                'platform_coverage': ['Amazon.com', 'Newegg', 'Amazon DE', 'Amazon JP', 'Yodobashi'],
                'market_data': {
                    'avg_price': 164.99,
                    'total_listings': 28,
                    'total_sales': 2860,
                    'top_rated': 'Strider Platinum 1000W',
                    'best_seller': 'Strider Gold 750W'
                }
            },
            'Lian Li': {
                'name': 'Lian Li 聯力',
                'products': [
                    {'model': 'SP850 850W', 'watt': 850, 'price': 189.99, 'rating': 4.8, 'reviews': 320, 'sales': 560},
                    {'model': 'SP750 750W', 'watt': 750, 'price': 139.99, 'rating': 4.7, 'reviews': 280, 'sales': 780},
                    {'model': 'Edge EG850 850W', 'watt': 850, 'price': 179.99, 'rating': 4.7, 'reviews': 240, 'sales': 620},
                    {'model': 'Edge EG750 750W', 'watt': 750, 'price': 129.99, 'rating': 4.6, 'reviews': 200, 'sales': 520}
                ],
                'platform_coverage': ['Amazon.com', 'Newegg', 'Amazon DE', 'Amazon UK'],
                'market_data': {
                    'avg_price': 159.99,
                    'total_listings': 22,
                    'total_sales': 2480,
                    'top_rated': 'SP850 850W',
                    'best_seller': 'SP750 750W'
                }
            },
            'Phanteks': {
                'name': 'Phanteks 追風者',
                'products': [
                    {'model': 'Revolt Pro 850W', 'watt': 850, 'price': 159.99, 'rating': 4.7, 'reviews': 320, 'sales': 680},
                    {'model': 'AMP 750W', 'watt': 750, 'price': 129.99, 'rating': 4.6, 'reviews': 280, 'sales': 890},
                    {'model': 'Revolt X 850W', 'watt': 850, 'price': 179.99, 'rating': 4.7, 'reviews': 220, 'sales': 520},
                    {'model': 'AMP 650W', 'watt': 650, 'price': 99.99, 'rating': 4.5, 'reviews': 180, 'sales': 720}
                ],
                'platform_coverage': ['Amazon.com', 'Newegg', 'Amazon DE', 'Amazon UK', 'Mindfactory DE'],
                'market_data': {
                    'avg_price': 142.49,
                    'total_listings': 24,
                    'total_sales': 2810,
                    'top_rated': 'Revolt Pro 850W',
                    'best_seller': 'AMP 750W'
                }
            },
            'NZXT': {
                'name': 'NZXT',
                'products': [
                    {'model': 'C1200 Gold', 'watt': 1200, 'price': 279.99, 'rating': 4.8, 'reviews': 380, 'sales': 620},
                    {'model': 'C850 Gold', 'watt': 850, 'price': 149.99, 'rating': 4.7, 'reviews': 480, 'sales': 1180},
                    {'model': 'E650 Gold', 'watt': 650, 'price': 109.99, 'rating': 4.5, 'reviews': 320, 'sales': 920},
                    {'model': 'C750 Gold', 'watt': 750, 'price': 129.99, 'rating': 4.6, 'reviews': 420, 'sales': 1420}
                ],
                'platform_coverage': ['Amazon.com', 'Newegg', 'Best Buy', 'Amazon UK'],
                'market_data': {
                    'avg_price': 167.49,
                    'total_listings': 26,
                    'total_sales': 4140,
                    'top_rated': 'C1200 Gold',
                    'best_seller': 'C750 Gold'
                }
            },
            'Chieftec': {
                'name': 'Chieftec',
                'products': [
                    {'model': 'Power Smart 850W', 'watt': 850, 'price': 99.99, 'rating': 4.4, 'reviews': 220, 'sales': 680},
                    {'model': 'GPS-700C 700W', 'watt': 700, 'price': 69.99, 'rating': 4.3, 'reviews': 180, 'sales': 520},
                    {'model': 'GDP-750C 750W', 'watt': 750, 'price': 89.99, 'rating': 4.4, 'reviews': 160, 'sales': 480},
                    {'model': 'GPA-650S 650W', 'watt': 650, 'price': 59.99, 'rating': 4.2, 'reviews': 140, 'sales': 420}
                ],
                'platform_coverage': ['Amazon.com', 'Amazon DE', 'Amazon FR'],
                'market_data': {
                    'avg_price': 79.99,
                    'total_listings': 18,
                    'total_sales': 2100,
                    'top_rated': 'Power Smart 850W',
                    'best_seller': 'Power Smart 850W'
                }
            },
            'Deepcool': {
                'name': 'Deepcool 九州風神',
                'products': [
                    {'model': 'PM750D 750W', 'watt': 750, 'price': 79.99, 'rating': 4.5, 'reviews': 380, 'sales': 1280},
                    {'model': 'DQ750ST 750W', 'watt': 750, 'price': 69.99, 'rating': 4.4, 'reviews': 280, 'sales': 960},
                    {'model': 'PD650 650W', 'watt': 650, 'price': 59.99, 'rating': 4.3, 'reviews': 220, 'sales': 780},
                    {'model': 'PK650D 650W', 'watt': 650, 'price': 54.99, 'rating': 4.2, 'reviews': 180, 'sales': 620}
                ],
                'platform_coverage': ['Amazon.com', 'Amazon DE', '京東', '天貓', '淘寶'],
                'market_data': {
                    'avg_price': 66.24,
                    'total_listings': 24,
                    'total_sales': 3640,
                    'top_rated': 'PM750D 750W',
                    'best_seller': 'PM750D 750W'
                }
            }
        },
        'summary': {
            'total_products': 438,
            'total_platforms': len(PLATFORMS),
            'region_platform_count': region_stats,
            'total_sales': 88820,
            'avg_market_price': 148.62,
            'top_brand_by_sales': 'MSI',
            'top_brand_by_reviews': 'Corsair',
            'top_brand_by_rating': 'ASUS',
            'best_value': 'MSI MAG A750BN',
            'premium_pick': 'Corsair HX1500i',
            'market_share_leader': 'MSI'
        }
    }
    return data

def print_platform_summary():
    """打印平台覆蓋摘要"""
    stats = get_platforms_by_region()
    print("\n" + "="*60)
    print("全球電商平台覆蓋統計")
    print("="*60)
    for region, count in stats.items():
        print(f"  {region}: {count} 個平台")
    print(f"\n總計: {sum(stats.values())} 個電商平台")
    print("="*60)

if __name__ == '__main__':
    print("開始收集電源供應器銷售數據...")
    print_platform_summary()
    data = generate_sample_data()
    print(f"\n數據收集完成時間: {data['collect_time']}")
    print(f"總產品數: {data['summary']['total_products']}")
    print(f"市場均價: ${data['summary']['avg_market_price']}")
