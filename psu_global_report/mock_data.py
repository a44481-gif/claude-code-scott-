"""
模擬數據生成器
用於測試全流程或在爬蟲無法訪問時生成示範數據
"""
import random
import json
from datetime import datetime
from collections import defaultdict

BRANDS = [
    ("華碩（ASUS）", ["ASUS ROG Thor", "ASUS TUF Gaming", "ASUS Prime"]),
    ("技嘉（GIGABYTE）", ["GIGABYTE AORUS", "GIGABYTE P850GM", "GIGABYTE UD"]),
    ("微星（MSI）", ["MSI MPG", "MSI MAG", "MSI A", "MSI MEG"]),
    ("海盜船（Corsair）", ["Corsair RM", "Corsair TX", "Corsair SF", "Corsair HX"]),
    ("海韻（Seasonic）", ["Seasonic Focus", "Seasonic Prime", "Seasonic GX"]),
    ("安鈦克（Antec）", ["Antec NeoECO", "Antec Signature", "Antec CG"]),
    ("酷冷至尊（Cooler Master）", ["Cooler Master V", "Cooler Master MWE", "Cooler Master GX"]),
    ("BQT", ["be quiet! Straight Power", "be quiet! Dark Power", "be quiet! Pure Power"]),
    ("九州風神（DeepCool）", ["DeepCool PQ", "DeepCool DA", "DeepCool PK"]),
    ("聯力（Lian Li）", ["Lian Li SP", "Lian Li PE", "Lian Li O11"]),
]

PLATFORMS = {
    "Amazon US": {"region": "北美", "currency": "USD", "price_mult": 1.0},
    "Newegg": {"region": "北美", "currency": "USD", "price_mult": 0.98},
    "Best Buy US": {"region": "北美", "currency": "USD", "price_mult": 1.02},
    "Amazon Canada": {"region": "北美", "currency": "CAD", "price_mult": 1.35},
    "Best Buy Canada": {"region": "北美", "currency": "CAD", "price_mult": 1.38},
    "Amazon DE": {"region": "歐洲", "currency": "EUR", "price_mult": 0.92},
    "Amazon UK": {"region": "歐洲", "currency": "GBP", "price_mult": 0.79},
    "MediaMarkt": {"region": "歐洲", "currency": "EUR", "price_mult": 0.95},
    "Saturn": {"region": "歐洲", "currency": "EUR", "price_mult": 0.93},
    "Ozon": {"region": "俄羅斯", "currency": "RUB", "price_mult": 95.0},
    "Wildberries": {"region": "俄羅斯", "currency": "RUB", "price_mult": 92.0},
    "Yandex Market": {"region": "俄羅斯", "currency": "RUB", "price_mult": 90.0},
    "京東": {"region": "亞洲", "currency": "CNY", "price_mult": 7.2},
    "天貓": {"region": "亞洲", "currency": "CNY", "price_mult": 7.3},
    "淘寶": {"region": "亞洲", "currency": "CNY", "price_mult": 6.8},
    "PChome": {"region": "亞洲", "currency": "TWD", "price_mult": 31.5},
    "Momo": {"region": "亞洲", "currency": "TWD", "price_mult": 32.0},
    "Amazon JP": {"region": "亞洲", "currency": "JPY", "price_mult": 150.0},
    "Rakuten": {"region": "亞洲", "currency": "JPY", "price_mult": 148.0},
    "Gmarket": {"region": "亞洲", "currency": "KRW", "price_mult": 1350.0},
    "Coupang": {"region": "亞洲", "currency": "KRW", "price_mult": 1320.0},
    "Flipkart": {"region": "亞洲", "currency": "INR", "price_mult": 83.0},
    "Amazon IN": {"region": "亞洲", "currency": "INR", "price_mult": 85.0},
    "Shopee TH": {"region": "東南亞", "currency": "THB", "price_mult": 35.0},
    "Shopee VN": {"region": "東南亞", "currency": "VND", "price_mult": 24500.0},
    "Shopee ID": {"region": "東南亞", "currency": "IDR", "price_mult": 15800.0},
    "Shopee MY": {"region": "東南亞", "currency": "MYR", "price_mult": 4.7},
    "Shopee PH": {"region": "東南亞", "currency": "PHP", "price_mult": 56.0},
    "Lazada TH": {"region": "東南亞", "currency": "THB", "price_mult": 34.5},
    "Tokopedia": {"region": "東南亞", "currency": "IDR", "price_mult": 15700.0},
    "MercadoLibre AR": {"region": "南美", "currency": "ARS", "price_mult": 850.0},
    "MercadoLibre BR": {"region": "南美", "currency": "BRL", "price_mult": 5.1},
    "MercadoLibre MX": {"region": "南美", "currency": "MXN", "price_mult": 17.5},
    "Noon": {"region": "中東", "currency": "AED", "price_mult": 3.67},
    "Amazon SAE": {"region": "中東", "currency": "AED", "price_mult": 3.65},
}

WATTAGES = ["450W", "550W", "650W", "750W", "850W", "1000W", "1200W", "1600W"]
CERTS = ["80+ Bronze", "80+ Silver", "80+ Gold", "80+ Platinum", "80+ Titanium"]
USD_BASE_PRICES = {
    "450W": 40, "550W": 55, "650W": 70, "750W": 90,
    "850W": 110, "1000W": 145, "1200W": 200, "1600W": 300,
}

def generate_mock_data(num_per_platform=3) -> list[dict]:
    products = []
    for platform, info in PLATFORMS.items():
        for i in range(num_per_platform):
            brand, series_list = random.choice(BRANDS)
            series = random.choice(series_list)
            wattage = random.choice(WATTAGES)
            cert = random.choice(CERTS)
            base_usd = USD_BASE_PRICES.get(wattage, 80)
            cert_mult = {"80+ Bronze": 1.0, "80+ Silver": 1.1, "80+ Gold": 1.2,
                          "80+ Platinum": 1.4, "80+ Titanium": 1.8}.get(cert, 1.0)
            price_usd = base_usd * cert_mult * random.uniform(0.9, 1.3)
            local_price = price_usd * info["price_mult"]

            products.append({
                "platform": platform,
                "region": info["region"],
                "brand": brand,
                "product_name": f"{series} {wattage} {cert} 全模組",
                "price": round(price_usd, 2),
                "original_price": f"{local_price:.0f}",
                "currency": info["currency"],
                "sales_count": str(random.randint(50, 5000)),
                "rating": f"{random.uniform(4.0, 5.0):.1f}",
                "url": f"https://{platform.lower().replace(' ', '')}.com/product/{i}",
                "seller": f"{platform} Official Store",
                "wattage": wattage,
                "certification": cert,
                "reviews_count": str(random.randint(10, 500)),
                "stock_status": random.choice(["有貨", "有貨", "少量現貨", "預購"]),
                "timestamp": datetime.now().isoformat(),
            })
    return products


if __name__ == "__main__":
    data = generate_mock_data(3)
    with open("reports/mock_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Generated {len(data)} mock products")
    by_platform = defaultdict(int)
    for p in data:
        by_platform[p["platform"]] += 1
    for pl, cnt in sorted(by_platform.items()):
        print(f"  {pl}: {cnt}")
