#!/usr/bin/env python3
"""
處理器市場分析自動化腳本
功能：數據整理、Excel導出、圖表生成
"""

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional

# ============================================================
# 數據模型
# ============================================================

@dataclass
class ProcessorSpec:
    """處理器規格"""
    vendor: str           # AMD/Intel/ARM/NVIDIA
    category: str         # CPU/APU/GPU/NPU
    model: str            # 型號
    release_date: str      # 發布時間
    process_node: str     # 製程
    cores_threads: str     # 核心/線程
    frequency: str        # 頻率
    cache: str            # 緩存
    tdp: str              # TDP
    ai_tops: str          # AI算力 TOPS
    ai_pflops: str        # AI算力 PFLOPS
    memory: str           # 內存
    bandwidth: str        # 帶寬
    interconnect: str      # 互聯技術
    positioning: str       # 市場定位
    # AI滿意度評分 (1-10)
    score_local_llm: int = 0
    score_ai_training: int = 0
    score_multimodal: int = 0
    score_edge_ai: int = 0
    score_ecosystem: int = 0
    notes: str = ""

def to_dict(p: ProcessorSpec) -> dict:
    return asdict(p)

# ============================================================
# AMD 數據
# ============================================================

AMD_PRODUCTS: List[ProcessorSpec] = [
    # 桌面 CPU
    ProcessorSpec(
        vendor="AMD",
        category="桌面CPU",
        model="Ryzen 9 9950X3D",
        release_date="2026.1",
        process_node="3nm Zen5",
        cores_threads="16C/32T",
        frequency="5.7GHz",
        cache="144MB L3 (3D V-Cache)",
        tdp="170W",
        ai_tops="N/A",
        ai_pflops="N/A",
        memory="DDR5-8000",
        bandwidth="N/A",
        interconnect="AM5",
        positioning="旗艦遊戲",
        score_local_llm=7,
        score_ai_training=6,
        score_multimodal=6,
        score_edge_ai=3,
        score_ecosystem=8,
        notes="3D V-Cache遊戲提升20-30%, Zen5 IPC +15%"
    ),
    ProcessorSpec(
        vendor="AMD",
        category="桌面CPU",
        model="Ryzen 9 9850X3D",
        release_date="2026.1",
        process_node="3nm Zen5",
        cores_threads="12C/24T",
        frequency="5.5GHz",
        cache="96MB L3 (3D V-Cache)",
        tdp="120W",
        ai_tops="N/A",
        ai_pflops="N/A",
        memory="DDR5-8000",
        bandwidth="N/A",
        interconnect="AM5",
        positioning="高端遊戲",
        score_local_llm=7,
        score_ai_training=6,
        score_multimodal=6,
        score_edge_ai=3,
        score_ecosystem=8,
        notes="性價比X3D, 遊戲旗艦替代"
    ),
    # AI 桌面 APU
    ProcessorSpec(
        vendor="AMD",
        category="桌面APU",
        model="Ryzen AI 9 395X",
        release_date="2025.6",
        process_node="4nm",
        cores_threads="16C/32T",
        frequency="5.1GHz",
        cache="64MB L3",
        tdp="45-120W",
        ai_tops="80+",
        ai_pflops="N/A",
        memory="128GB LPDDR5X",
        bandwidth="256GB/s",
        interconnect="AM5",
        positioning="AI PC旗艦",
        score_local_llm=8,
        score_ai_training=5,
        score_multimodal=7,
        score_edge_ai=7,
        score_ecosystem=7,
        notes="統一內存架構, Copilot+ PC超額滿足40+ TOPS要求, Llama 3.1 70B@30tok/s"
    ),
    ProcessorSpec(
        vendor="AMD",
        category="移動APU",
        model="Ryzen AI 9 HX 370",
        release_date="2025.6",
        process_node="4nm",
        cores_threads="12C/24T",
        frequency="5.1GHz",
        cache="24MB L3",
        tdp="28-54W",
        ai_tops="50+",
        ai_pflops="N/A",
        memory="LPDDR5X",
        bandwidth="N/A",
        interconnect="FP8",
        positioning="輕薄AI PC",
        score_local_llm=8,
        score_ai_training=4,
        score_multimodal=7,
        score_edge_ai=8,
        score_ecosystem=7,
        notes="Qwen2.5-72B流暢, RDNA3.5 40CU GPU"
    ),
    # 數據中心 GPU
    ProcessorSpec(
        vendor="AMD",
        category="數據中心GPU",
        model="Instinct MI355X",
        release_date="2026.Q1",
        process_node="3nm CDNA4",
        cores_threads="N/A",
        frequency="N/A",
        cache="N/A",
        tdp="1000W",
        ai_tops="N/A",
        ai_pflops="2.5 PFLOPS FP8",
        memory="288GB HBM3E",
        bandwidth="6.5 TB/s",
        interconnect="Infinity Fabric, CXL 3.0",
        positioning="AI推理旗艦",
        score_local_llm=9,
        score_ai_training=9,
        score_multimodal=9,
        score_edge_ai=2,
        score_ecosystem=8,
        notes="推理提升2-3x vs MI300X, ROCm 7.x, vLLM優化"
    ),
    ProcessorSpec(
        vendor="AMD",
        category="數據中心GPU",
        model="Instinct MI350",
        release_date="2025.9",
        process_node="3nm CDNA4",
        cores_threads="N/A",
        frequency="N/A",
        cache="N/A",
        tdp="750W",
        ai_tops="N/A",
        ai_pflops="1.5 PFLOPS FP8",
        memory="192GB HBM3E",
        bandwidth="4.8 TB/s",
        interconnect="Infinity Fabric",
        positioning="AI推理中端",
        score_local_llm=8,
        score_ai_training=8,
        score_multimodal=8,
        score_edge_ai=2,
        score_ecosystem=8,
        notes="性價比MI355X, 入門AI推理"
    ),
    # 數據中心 CPU
    ProcessorSpec(
        vendor="AMD",
        category="數據中心CPU",
        model="EPYC 9575F",
        release_date="2025.8",
        process_node="3nm Zen5",
        cores_threads="128C/256T",
        frequency="3.3/5.0GHz",
        cache="512MB L3",
        tdp="400W",
        ai_tops="N/A",
        ai_pflops="N/A",
        memory="DDR5-6000",
        bandwidth="500+ GB/s",
        interconnect="CXL 3.0",
        positioning="旗艦服務器",
        score_local_llm=7,
        score_ai_training=8,
        score_multimodal=6,
        score_edge_ai=3,
        score_ecosystem=8,
        notes="AVX-512 VNNI, AI推理向量加速"
    ),
]

# ============================================================
# Intel 數據
# ============================================================

INTEL_PRODUCTS: List[ProcessorSpec] = [
    ProcessorSpec(
        vendor="Intel",
        category="桌面CPU",
        model="Core Ultra 9 285K",
        release_date="2025.10",
        process_node="18A",
        cores_threads="8P+16E/24T",
        frequency="5.6GHz",
        cache="36MB L3",
        tdp="125W",
        ai_tops="13+",
        ai_pflops="N/A",
        memory="DDR5-6400",
        bandwidth="N/A",
        interconnect="LGA 1851",
        positioning="旗艦桌面",
        score_local_llm=7,
        score_ai_training=4,
        score_multimodal=7,
        score_edge_ai=7,
        score_ecosystem=8,
        notes="NPU3 + Xe2 LPG, Qwen2.5-32B流暢"
    ),
    ProcessorSpec(
        vendor="Intel",
        category="移動CPU",
        model="Core Ultra 9 285H",
        release_date="2025.10",
        process_node="18A",
        cores_threads="6P+8E+2LPE/24T",
        frequency="5.4GHz",
        cache="24MB L3",
        tdp="45W",
        ai_tops="13+",
        ai_pflops="N/A",
        memory="LPDDR5X",
        bandwidth="N/A",
        interconnect="FPBGA",
        positioning="AI PC",
        score_local_llm=7,
        score_ai_training=4,
        score_multimodal=7,
        score_edge_ai=8,
        score_ecosystem=8,
        notes="NPU3 + Xe2核顯, OpenVINO優化"
    ),
    ProcessorSpec(
        vendor="Intel",
        category="數據中心GPU",
        model="Gaudi 3",
        release_date="2025.6",
        process_node="5nm",
        cores_threads="N/A",
        frequency="N/A",
        cache="N/A",
        tdp="900W",
        ai_tops="N/A",
        ai_pflops="1.8 PFLOPS FP8",
        memory="96GB HBM2e",
        bandwidth="3.35 TB/s",
        interconnect="400GbE RoCE",
        positioning="AI推理",
        score_local_llm=7,
        score_ai_training=7,
        score_multimodal=7,
        score_edge_ai=2,
        score_ecosystem=7,
        notes="原生集群支持, MLIR編譯, SynapseAI"
    ),
    ProcessorSpec(
        vendor="Intel",
        category="數據中心CPU",
        model="Xeon 6980P",
        release_date="2025.8",
        process_node="3nm",
        cores_threads="128C/256T",
        frequency="3.8/4.8GHz",
        cache="480MB L3",
        tdp="350W",
        ai_tops="N/A",
        ai_pflops="N/A",
        memory="DDR5-6400",
        bandwidth="800+ GB/s",
        interconnect="CXL 2.0",
        positioning="AI服務器旗艦",
        score_local_llm=7,
        score_ai_training=8,
        score_multimodal=6,
        score_edge_ai=3,
        score_ecosystem=9,
        notes="AMX加速 BF16/INT8, oneAPI統一編程"
    ),
]

# ============================================================
# ARM 數據
# ============================================================

ARM_PRODUCTS: List[ProcessorSpec] = [
    ProcessorSpec(
        vendor="ARM",
        category="服務器CPU",
        model="Neoverse V3",
        release_date="2026.3",
        process_node="3nm TSMC",
        cores_threads="136C",
        frequency="N/A",
        cache="N/A",
        tdp="350W",
        ai_tops="N/A",
        ai_pflops="N/A",
        memory="DDR5, CXL 3.0",
        bandwidth="900 GB/s",
        interconnect="CCI",
        positioning="超大規模計算",
        score_local_llm=6,
        score_ai_training=8,
        score_multimodal=5,
        score_edge_ai=6,
        score_ecosystem=7,
        notes="vs V2 +40%性能 +35%能效, AWS Graviton4"
    ),
    ProcessorSpec(
        vendor="ARM",
        category="消費SoC",
        model="Cortex-X925 (旗艦)",
        release_date="2026.2",
        process_node="3nm N3E",
        cores_threads="1+3+4 (8C)",
        frequency="4.4GHz",
        cache="N/A",
        tdp="10-15W",
        ai_tops="70+",
        ai_pflops="N/A",
        memory="LPDDR5X",
        bandwidth="N/A",
        interconnect="AMBA",
        positioning="旗艦手機",
        score_local_llm=7,
        score_ai_training=2,
        score_multimodal=8,
        score_edge_ai=9,
        score_ecosystem=7,
        notes="70B端側推理, Mali-G925 MC20 GPU, 端側多模態"
    ),
    ProcessorSpec(
        vendor="ARM",
        category="AI加速IP",
        model="Ethos N980",
        release_date="2026.2",
        process_node="N/A",
        cores_threads="N/A",
        frequency="N/A",
        cache="N/A",
        tdp="N/A",
        ai_tops="60+",
        ai_pflops="N/A",
        memory="N/A",
        bandwidth="N/A",
        interconnect="AMBA",
        positioning="旗艦NPU IP",
        score_local_llm=7,
        score_ai_training=2,
        score_multimodal=7,
        score_edge_ai=9,
        score_ecosystem=7,
        notes="端側LLM, 多模態, TFLite/PyTorch Mobile"
    ),
]

# ============================================================
# NVIDIA 數據
# ============================================================

NVIDIA_PRODUCTS: List[ProcessorSpec] = [
    ProcessorSpec(
        vendor="NVIDIA",
        category="消費GPU",
        model="RTX 5090",
        release_date="2025.10",
        process_node="4NP Blackwell",
        cores_threads="21760 CUDA",
        frequency="2.4/2.9GHz",
        cache="N/A",
        tdp="575W",
        ai_tops="N/A",
        ai_pflops="1829 TFLOPS",
        memory="32GB GDDR7",
        bandwidth="1.8 TB/s",
        interconnect="PCIe 5.0, NVLink",
        positioning="旗艦遊戲",
        score_local_llm=9,
        score_ai_training=8,
        score_multimodal=9,
        score_edge_ai=3,
        score_ecosystem=10,
        notes="DLSS 4.5 Transformer, 遊戲+AI創作首選"
    ),
    ProcessorSpec(
        vendor="NVIDIA",
        category="消費GPU",
        model="RTX 5080",
        release_date="2025.10",
        process_node="4NP Blackwell",
        cores_threads="10752 CUDA",
        frequency="2.6/3.0GHz",
        cache="N/A",
        tdp="360W",
        ai_tops="N/A",
        ai_pflops="1057 TFLOPS",
        memory="16GB GDDR7",
        bandwidth="960 GB/s",
        interconnect="PCIe 5.0, NVLink",
        positioning="高端遊戲",
        score_local_llm=8,
        score_ai_training=7,
        score_multimodal=8,
        score_edge_ai=4,
        score_ecosystem=10,
        notes="4K144Hz遊戲, AI創作性價比"
    ),
    ProcessorSpec(
        vendor="NVIDIA",
        category="消費GPU",
        model="RTX 5070 Ti",
        release_date="2026.2",
        process_node="4NP Blackwell",
        cores_threads="8960 CUDA",
        frequency="2.3/2.8GHz",
        cache="N/A",
        tdp="300W",
        ai_tops="N/A",
        ai_pflops="750 TFLOPS",
        memory="16GB GDDR7",
        bandwidth="672 GB/s",
        interconnect="PCIe 5.0",
        positioning="主流遊戲",
        score_local_llm=7,
        score_ai_training=6,
        score_multimodal=7,
        score_edge_ai=5,
        score_ecosystem=10,
        notes="2K144Hz首選, DLSS 4.5"
    ),
    ProcessorSpec(
        vendor="NVIDIA",
        category="消費GPU",
        model="RTX 5070",
        release_date="2026.2",
        process_node="4NP Blackwell",
        cores_threads="6144 CUDA",
        frequency="2.5/2.9GHz",
        cache="N/A",
        tdp="220W",
        ai_tops="N/A",
        ai_pflops="500 TFLOPS",
        memory="12GB GDDR7",
        bandwidth="504 GB/s",
        interconnect="PCIe 5.0",
        positioning="主流遊戲",
        score_local_llm=7,
        score_ai_training=5,
        score_multimodal=6,
        score_edge_ai=5,
        score_ecosystem=10,
        notes="性價比之王, DLSS 4.5"
    ),
    ProcessorSpec(
        vendor="NVIDIA",
        category="數據中心GPU",
        model="GB200 NVL72",
        release_date="2026.Q1",
        process_node="4NP Blackwell",
        cores_threads="N/A",
        frequency="N/A",
        cache="N/A",
        tdp="120kW (整機)",
        ai_tops="N/A",
        ai_pflops="1000+ PFLOPS",
        memory="240GB HBM3e/GPU",
        bandwidth="NVLink 6.0 1.8 TB/s",
        interconnect="NVLink 6.0",
        positioning="AI工廠",
        score_local_llm=10,
        score_ai_training=10,
        score_multimodal=10,
        score_edge_ai=1,
        score_ecosystem=10,
        notes="EFLOPS級算力, 全液冷, Grace CPU + Blackwell GPU"
    ),
    ProcessorSpec(
        vendor="NVIDIA",
        category="數據中心CPU",
        model="Vera Rubin",
        release_date="2026.3",
        process_node="3nm",
        cores_threads="88C Olympus",
        frequency="N/A",
        cache="N/A",
        tdp="N/A",
        ai_tops="N/A",
        ai_pflops="N/A",
        memory="HBM",
        bandwidth="NVLink 7.0 3.6 TB/s",
        interconnect="NVLink 7.0",
        positioning="AI訓練CPU",
        score_local_llm=8,
        score_ai_training=9,
        score_multimodal=7,
        score_edge_ai=2,
        score_ecosystem=9,
        notes="自研ARM架構, 與Rubin GPU協同"
    ),
]

# ============================================================
# 主機板技術數據
# ============================================================

MOTHERBOARD_TRENDS = [
    {"年份": "2026", "功能": "DDR5-8000主流", "PCIe": "PCIe 5.0全面", "供電": "32相AI供電", "接口": "USB4 2.0/25GbE", "AI功能": "AI超頻/散熱"},
    {"年份": "2027", "功能": "DDR5-10000旗艦", "PCIe": "PCIe 6.0導入", "供電": "40相+", "接口": "TB5普及", "AI功能": "自然語言調校"},
]

# ============================================================
# PSU 技術數據
# ============================================================

PSU_TRENDS = [
    {"年份": "2026", "消費功率": "1600W主流", "消費效率": "80+鈦金普及", "數據中心": "12kW/800V", "拓撲": "GaN普及", "AI特性": "動態供電"},
    {"年份": "2027", "消費功率": "2000W雙卡", "消費效率": ">97%效率", "數據中心": "21kW/570kW", "拓撲": "SiC普及", "AI特性": "智能監控"},
]

# ============================================================
# Excel 導出（無需 openpyxl / pandas）
# ============================================================

def export_to_csv(filepath: str):
    """導出所有數據到 CSV"""
    import csv

    all_products = AMD_PRODUCTS + INTEL_PRODUCTS + ARM_PRODUCTS + NVIDIA_PRODUCTS
    fieldnames = [
        "vendor", "category", "model", "release_date", "process_node",
        "cores_threads", "frequency", "cache", "tdp", "ai_tops", "ai_pflops",
        "memory", "bandwidth", "interconnect", "positioning",
        "score_local_llm", "score_ai_training", "score_multimodal",
        "score_edge_ai", "score_ecosystem", "notes"
    ]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in all_products:
            writer.writerow(to_dict(p))

    print(f"[OK] CSV導出: {filepath} ({len(all_products)} 款產品)")

def export_mb_psu_csv(filepath: str):
    """導出主機板和PSU趨勢數據"""
    import csv

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        f.write("=== 主機板技術趨勢 ===\n")
        writer = csv.DictWriter(f, fieldnames=list(MOTHERBOARD_TRENDS[0].keys()))
        writer.writeheader()
        writer.writerows(MOTHERBOARD_TRENDS)

        f.write("\n=== PSU電源技術趨勢 ===\n")
        writer2 = csv.DictWriter(f, fieldnames=list(PSU_TRENDS[0].keys()))
        writer2.writeheader()
        writer2.writerows(PSU_TRENDS)

    print(f"[OK] MB/PSU CSV導出: {filepath}")

# ============================================================
# ASCII 圖表生成
# ============================================================

def draw_radar_chart(name: str, scores: dict, filename: str):
    """生成雷達圖 (ASCII art)"""
    categories = list(scores.keys())
    values = list(scores.values())
    n = len(categories)

    # 雷達圖半徑
    R = 20
    lines = []

    # 計算每個點的位置
    def point(angle, radius):
        x = int(40 + radius * categories.index(name) / n)
        y = int(20 + radius * categories.index(name) / n)
        return x, y

    # 簡化的雷達圖（表格形式）
    bar_chart = f"\n{'='*60}\n{name} - AI滿意度評分\n{'='*60}\n"
    max_val = 10
    for cat, val in zip(categories, values):
        bar = "█" * val + "░" * (max_val - val)
        bar_chart += f"{cat:20s} [{bar}] {val}/10\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(bar_chart)

    print(f"[OK] 雷達圖: {filename}")

def generate_all_charts():
    """生成所有雷達圖"""
    charts = {
        "RTX 5090": {
            "本地LLM": 9, "AI訓練": 8, "多模態": 9, "邊緣AI": 3, "生態成熟度": 10
        },
        "Ryzen AI 9 395X": {
            "本地LLM": 8, "AI訓練": 5, "多模態": 7, "邊緣AI": 7, "生態成熟度": 7
        },
        "GB200 NVL72": {
            "本地LLM": 10, "AI訓練": 10, "多模態": 10, "邊緣AI": 1, "生態成熟度": 10
        },
        "Instinct MI355X": {
            "本地LLM": 9, "AI訓練": 9, "多模態": 9, "邊緣AI": 2, "生態成熟度": 8
        },
        "Core Ultra 9 285K": {
            "本地LLM": 7, "AI訓練": 4, "多模態": 7, "邊緣AI": 7, "生態成熟度": 8
        },
        "Neoverse V3": {
            "本地LLM": 6, "AI訓練": 8, "多模態": 5, "邊緣AI": 6, "生態成熟度": 7
        },
        "Cortex-X925": {
            "本地LLM": 7, "AI訓練": 2, "多模態": 8, "邊緣AI": 9, "生態成熟度": 7
        },
    }

    for name, scores in charts.items():
        safe_name = name.replace(" ", "_").replace("/", "_")
        draw_radar_chart(name, scores, f"chart_{safe_name}.txt")

# ============================================================
# JSON 導出（供網頁/PPT使用）
# ============================================================

def export_to_json(filepath: str):
    """導出完整數據到 JSON"""
    data = {
        "generated_at": datetime.now().isoformat(),
        "report_period": "2025.6-2026.3",
        "vendors": {
            "AMD": [to_dict(p) for p in AMD_PRODUCTS],
            "Intel": [to_dict(p) for p in INTEL_PRODUCTS],
            "ARM": [to_dict(p) for p in ARM_PRODUCTS],
            "NVIDIA": [to_dict(p) for p in NVIDIA_PRODUCTS],
        },
        "motherboard_trends": MOTHERBOARD_TRENDS,
        "psu_trends": PSU_TRENDS,
        "summary": {
            "total_products": len(AMD_PRODUCTS) + len(INTEL_PRODUCTS) + len(ARM_PRODUCTS) + len(NVIDIA_PRODUCTS),
            "amd_count": len(AMD_PRODUCTS),
            "intel_count": len(INTEL_PRODUCTS),
            "arm_count": len(ARM_PRODUCTS),
            "nvidia_count": len(NVIDIA_PRODUCTS),
        }
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] JSON導出: {filepath}")

# ============================================================
# 總結報告
# ============================================================

def print_summary():
    """打印分析總結"""
    total = len(AMD_PRODUCTS) + len(INTEL_PRODUCTS) + len(ARM_PRODUCTS) + len(NVIDIA_PRODUCTS)

    print("\n" + "="*60)
    print("處理器市場分析 - 產品統計")
    print("="*60)
    print(f"AMD:   {len(AMD_PRODUCTS)} 款")
    print(f"Intel: {len(INTEL_PRODUCTS)} 款")
    print(f"ARM:   {len(ARM_PRODUCTS)} 款")
    print(f"NVIDIA:{len(NVIDIA_PRODUCTS)} 款")
    print(f"總計:  {total} 款")
    print("="*60)

    print("\n【AI PC 評估】")
    for p in AMD_PRODUCTS + INTEL_PRODUCTS:
        if "APU" in p.category or "Ultra" in p.model:
            avg = (p.score_local_llm + p.score_edge_ai + p.score_ecosystem) / 3
            print(f"  {p.vendor} {p.model}: AI評分={avg:.1f}/10")

    print("\n【AI 訓練旗艦】")
    for p in NVIDIA_PRODUCTS + AMD_PRODUCTS:
        if "GB200" in p.model or "NVL72" in p.model or "MI355" in p.model:
            print(f"  {p.vendor} {p.model}: {p.ai_pflops or p.ai_tops}")

    print("\n【邊緣 AI 旗艦】")
    for p in ARM_PRODUCTS:
        if p.ai_tops and p.ai_tops != "N/A":
            print(f"  {p.vendor} {p.model}: {p.ai_tops} TOPS")

# ============================================================
# 主入口
# ============================================================

def main():
    print("處理器市場分析自動化腳本")
    print("="*50)

    # CSV導出
    export_to_csv("processor_specs_2025_2026.csv")
    export_mb_psu_csv("mb_psu_trends.csv")

    # JSON導出
    export_to_json("processor_data_2025_2026.json")

    # ASCII雷達圖
    generate_all_charts()

    # 打印總結
    print_summary()

    print("\n[完成] 所有文件已生成:")
    print("  - processor_specs_2025_2026.csv")
    print("  - mb_psu_trends.csv")
    print("  - processor_data_2025_2026.json")
    print("  - chart_*.txt (8個雷達圖)")

if __name__ == "__main__":
    main()
