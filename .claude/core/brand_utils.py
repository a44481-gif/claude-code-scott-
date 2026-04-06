"""
Brand classification utilities for PC components.
"""
import re
from typing import Optional, Dict, List, Tuple

# ── Brand Aliases ─────────────────────────────────────────────────

BRAND_ALIASES: Dict[str, str] = {
    # GPU
    "nvidia": "NVIDIA",
    "nv": "NVIDIA",
    "geforce": "NVIDIA",
    "rtx": "NVIDIA",
    "gtx": "NVIDIA",
    "amd": "AMD",
    "radeon": "AMD",
    "rx ": "AMD",
    "intel arc": "Intel Arc",
    "arc": "Intel Arc",
    # CPU
    "intel": "Intel",
    "core": "Intel",
    "xeon": "Intel",
    "ryzen": "AMD",
    "epyc": "AMD",
    "threadripper": "AMD",
    # Storage
    "samsung": "Samsung",
    "samsung 990": "Samsung",
    "samsung 980": "Samsung",
    "wd": "Western Digital",
    "western digital": "Western Digital",
    "wd_black": "Western Digital",
    "wd_blue": "Western Digital",
    "crucial": "Crucial",
    "micron": "Micron",
    "seagate": "Seagate",
    "kingston": "Kingston",
    "kc": "Kingston",
    "sn": "Samsung",  # Samsung SSD model prefix
    # Memory
    "g.skill": "G.Skill",
    "gskill": "G.Skill",
    "corsair": "Corsair",
    " vengeance": "Corsair",
    "kingston": "Kingston",
    "adata": "Adata",
    "xpg": "Adata",
    # PSU
    "seasonic": "Seasonic",
    "corsair": "Corsair",
    "evga": "EVGA",
    "antec": "Antec",
    "be quiet": "be quiet!",
    "bequiet": "be quiet!",
    "msi": "MSI",
    "asus": "ASUS",
    "rog": "ASUS",
    "tuf": "ASUS",
    "gigabyte": "Gigabyte",
    "gigabyte aorus": "Gigabyte",
    "aorus": "Gigabyte",
    # Motherboard
    "asrock": "ASRock",
    "biostar": "Biostar",
    # Cases
    "fractal": "Fractal Design",
    "fractal design": "Fractal Design",
    "lian li": "Lian Li",
    "lianli": "Lian Li",
    "nzxt": "NZXT",
    "coolermaster": "Cooler Master",
    "cooler master": "Cooler Master",
    "thermaltake": "Thermaltake",
    "phanteks": "Phanteks",
}

# Canonical brand names
CANONICAL_BRANDS = sorted(set(BRAND_ALIASES.values()), key=str.lower)


# ── Category Tags ─────────────────────────────────────────────────

PC_CATEGORY_TAGS: Dict[str, List[str]] = {
    "GPU": [
        "gpu", "graphics card", "graphics", "video card", "vga",
        "rtx", "gtx", "radeon", "rx ", "geforce", "arc",
        "rtx 4090", "rtx 4080", "rtx 4070", "rtx 4060",
        "rx 7900", "rx 7800", "rx 7700", "rx 7600",
    ],
    "CPU": [
        "cpu", "processor", "core i", "ryzen", "xeon", "epyc",
        "i9", "i7", "i5", "i3", "ryzen 9", "ryzen 7", "ryzen 5",
        "r9", "r7", "r5",
    ],
    "RAM": [
        "ram", "memory", "ddr5", "ddr4", "ddr3",
        "16gb", "32gb", "64gb", "128gb",
        "ddr5 6000", "ddr5 6400", "ddr4 3600",
    ],
    "SSD": [
        "ssd", "nvme", "m.2", "sata ssd", "solid state",
        "990 pro", "980 pro", "990 evo",
        "wd black", "wd blue", "sn850x", "sn770",
        "crucial p3", "p5 plus", "p2",
    ],
    "PSU": [
        "psu", "power supply", "power supply unit",
        "850w", "750w", "1000w", "1200w", "1600w",
        "80 plus", "gold", "platinum", "titanium",
        "rm", "rmx", "focus", "prime", "corsair hx",
    ],
    "Motherboard": [
        "motherboard", "mainboard", "mobo",
        "z790", "z690", "b760", "b650", "x670",
        "atx", "matx", "itx", "e-atx",
    ],
    "Storage": [
        "hdd", "hard drive", "nas", "external",
        "barracuda", "wd red", "ironwolf", "exos",
    ],
    "Case": [
        "case", "chassis", "pc case", "tower",
        "atx case", "full tower", "mid tower", "mini itx",
    ],
    "Cooling": [
        "cooler", "cpu cooler", "aio", "liquid cooling",
        "air cooler", "case fan", "radiator",
        "noctua", "deepcool", "arctic",
    ],
    "Monitor": [
        "monitor", "display", "screen", "4k", "144hz",
        "oled", "ips", "va panel",
    ],
}


# ── News Category Tags ─────────────────────────────────────────────

NEWS_CATEGORY_TAGS: Dict[str, List[str]] = {
    "AI Infrastructure": [
        "ai", "artificial intelligence", "gpu server", "data center",
        "h100", "h200", "a100", "llm", "gpt", "claude", "gemini",
        "openai", "anthropic", "nvidia ai", "ai chip", "ai accelerator",
        "cloud ai", "machine learning", "deep learning",
    ],
    "PC Components": [
        "cpu", "gpu", "processor", "graphics card", "motherboard",
        "ryzen", "intel core", "rtx", "radeon", "x86", "arm",
        "laptop", "desktop", "pc build", "gaming pc",
    ],
    "Storage": [
        "ssd", "hdd", "nvme", "nand", "dram", "solid state",
        "storage market", "samsung semiconductor", "microns",
        "wd", "seagate", "kingston",
    ],
    "Cloud Services": [
        "cloud", "aws", "azure", "google cloud", "gcp",
        "saas", "paas", "iaas", "cloud computing",
        "data center", "server", "enterprise",
    ],
    "Semiconductor": [
        "semiconductor", "chip", "foundry", "tsmc", "samsung foundry",
        "intel foundry", "3nm", "2nm", "5nm", "7nm",
        " wafer", "fabrication", "asml", "euv",
    ],
}


# ── Functions ─────────────────────────────────────────────────────

def classify_brand(text: str) -> Optional[str]:
    """
    Classify brand from text (product name, title, etc.)
    Returns canonical brand name or None.
    """
    text_lower = text.lower()
    for alias, canonical in BRAND_ALIASES.items():
        if alias.lower() in text_lower:
            return canonical
    return None


def classify_category(text: str) -> str:
    """
    Classify PC component category from text.
    Returns category name or "Other".
    """
    text_lower = text.lower()
    scores: Dict[str, int] = {}

    for category, tags in PC_CATEGORY_TAGS.items():
        score = sum(1 for tag in tags if tag in text_lower)
        if score > 0:
            scores[category] = score

    if scores:
        return max(scores, key=scores.get)
    return "Other"


def classify_news_category(text: str) -> str:
    """
    Classify news into categories (AI Infrastructure, PC Components, etc.)
    """
    text_lower = text.lower()
    scores: Dict[str, int] = {}

    for category, tags in NEWS_CATEGORY_TAGS.items():
        score = sum(1 for tag in tags if tag in text_lower)
        if score > 0:
            scores[category] = score

    if scores:
        return max(scores, key=scores.get)
    return "General"


def extract_wattage(text: str) -> Optional[str]:
    """Extract PSU wattage from text like '850W' or '750 龍瓦'."""
    patterns = [
        r'(\d{3,4})\s*[Ww]',  # 750W, 850W
        r'(\d{3,4})\s*龍\s*瓦',  # 850龍瓦
        r'(\d{3,4})\s*額定\s*瓦',  # 850額定瓦
        r'(\d{3,4})\s*瓦\s*金牌',  # 850瓦金牌
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1) + "W"
    return None


def extract_certification(text: str) -> Optional[str]:
    """Extract 80+ certification from text."""
    certifications = [
        "80+ Titanium",
        "80+ Platinum",
        "80+ Gold",
        "80+ Silver",
        "80+ Bronze",
        "80+",
    ]
    text_lower = text.lower()
    for cert in certifications:
        if cert.lower() in text_lower:
            return cert
    return None


def extract_memory_size(text: str) -> Optional[str]:
    """Extract memory size like '16GB', '32GB'."""
    patterns = [
        r'(\d{1,3})\s*GB',  # 16GB, 32GB
        r'(\d{1,3})\s*TB',  # 1TB, 2TB
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            size = int(match.group(1))
            unit = match.group(0)[-2:].upper()
            # Normalize TB
            if unit == "TB":
                return f"{size}TB"
            return f"{size}GB"
    return None


def extract_all_specs(text: str) -> Dict[str, Optional[str]]:
    """Extract all common specs from product text."""
    return {
        "brand": classify_brand(text),
        "category": classify_category(text),
        "wattage": extract_wattage(text),
        "certification": extract_certification(text),
        "memory": extract_memory_size(text),
    }
