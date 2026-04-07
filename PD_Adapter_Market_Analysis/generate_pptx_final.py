
# SLIDE 7: Regional Market
def s07(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    hdr(s, "區域市場格局", "Regional Market Share 2025 vs 2030")
    cols = ["區域", "2025份額", "2030份額", "CAGR", "變化/備注"]
    col_x = [Inches(0.4), Inches(2.8), Inches(4.8), Inches(6.8), Inches(9.0)]
    col_w = [Inches(2.2), Inches(1.8), Inches(1.8), Inches(1.8), Inches(3.5)]
    for i, h in enumerate(cols):
        rect(s, col_x[i], Inches(1.1), col_w[i], Inches(0.4), fill=PRIMARY)
        tb(s, col_x[i], Inches(1.15), col_w[i], Inches(0.32), h, sz=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    data = [
        ("中國", "48%", "45%", "13.8%", "-3pp / 市場成熟化", PRIMARY),
        ("北美", "20%", "19%", "14.2%", "-1pp / 穩定增長", CYAN),
        ("歐洲", "17%", "20%", "18.5%", "+3pp / GaN採用領先", GREEN),
        ("東南亞", "8%", "10%", "22.0%", "+2pp / 新興市場爆發", ORANGE),
        ("日韓", "5%", "4%", "12.0%", "-1pp / 成熟市場", PURPLE),
        ("其他", "2%", "2%", "15.0%", "持平", GRAY),
    ]
    for ri, (region, r25, r30, cagr, chg, col) in enumerate(data):
        y = Inches(1.55) + ri * Inches(0.72)
        bg_fill = BG_CARD if ri % 2 == 0 else RGBColor(28, 33, 40)
        rect(s, Inches(0.4), y, Inches(12.5), Inches(0.65), fill=bg_fill, lc=BORDER_COLOR)
        tb(s, col_x[0], y+Inches(0.1), col_w[0], Inches(0.42), region, sz=12, bold=True, color=col)
        for ci, val in enumerate([r25, r30, cagr, chg]):
            c_col = GREEN if ci == 2 else WHITE
            tb(s, col_x[ci+1], y+Inches(0.1), col_w[ci+1], Inches(0.42), val, sz=12, color=c_col, align=PP_ALIGN.CENTER)
    tb(s, Inches(0.4), Inches(6.0), Inches(12.5), Inches(0.5),
       "歐洲CAGR 18.5%為全球最高，受益於環保法規推動GaN快充普及；東南亞CAGR 22.0%受益於智能手機滲透率提升",
       sz=11, color=LIGHT_GRAY)
    ft(s); sn(s, 7); return s

# SLIDE 8: Why Integration
def s08(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    hdr(s, "為何集成是剛需", "Why Integration is a Must-Have")
    cards = [
        ("BOM成本降低", "75-82%", "相比傳統離散方案\n全集成SoC大幅減少\n外圍元件數量", GREEN),
        ("PCB面積減少", "75%", "高功率密度設計\n同等功率下\n尺寸縮小3/4", PRIMARY),
        ("開發週期縮短", "50%", "從晶片選型到\n量產時間減半\n加速產品上市", CYAN),
        ("效率提升", ">95%", "集成優化降低\n開關損耗和\n導通損耗", ORANGE),
    ]
    cw = Inches(2.95)
    for i, (title, val, desc, col) in enumerate(cards):
        lft = Inches(0.4) + i * (cw + Inches(0.12))
        rect(s, lft, Inches(1.1), cw, Inches(4.5), fill=BG_CARD, lc=BORDER_COLOR)
        rect(s, lft, Inches(1.1), cw, Inches(0.45), fill=col)
        tb(s, lft, Inches(1.15), cw, Inches(0.38), title, sz=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tb(s, lft, Inches(1.7), cw, Inches(1.1), val, sz=38, bold=True, color=col, align=PP_ALIGN.CENTER)
        rect(s, lft+Inches(0.3), Inches(2.9), cw-Inches(0.6), Inches(0.03), fill=col)
        tb(s, lft+Inches(0.15), Inches(3.1), cw-Inches(0.3), Inches(2.2), desc, sz=11, color=LIGHT_GRAY, align=PP_ALIGN.CENTER)
    tb(s, Inches(0.4), Inches(5.9), Inches(12.5), Inches(0.6),
       "集成方案核心價值：打破功率密度牆 - 從15W/in3到45W/in3，引領PD適配器進入\"小而美\"時代",
       sz=12, color=LIGHT_GRAY)
    ft(s); sn(s, 8); return s

# SLIDE 9: Four Architectures
def s09(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    hdr(s, "四大集成架構深度解析", "Four Integration Architecture Deep Dive")
    archs = [
        ("PFC+LLC GaN合封", "PI InnoSwitch4-CZ", "220W", ">95%", "代表：Power Integrations\n優勢：超高效率、可靠性強\n挑戰：成本較高", PRIMARY),
        ("ACF單芯片", "DK8607 / FAN6966", "120W", "93-94.5%", "代表：DIODES / onsemi\n優勢：成本最低、性價比高\n挑戰：效率上限", CYAN),
        ("協議+DC-DC SoC", "SC9712 / SW3536", "140W", "92-94%", "代表：南芯 / 智融\n優勢：國產替代首選\n挑戰：PD協議兼容性", GREEN),
        ("全數字功率", "UCC29950 / JW7726", "240W", ">96%", "代表：TI / 杰華特\n優勢：靈活性最強、數字控制\n挑戰：開發難度大", ORANGE),
    ]
    for i, (name, chip, pwr, eff, desc, col) in enumerate(archs):
        row = i // 2
        col_i = i % 2
        lft = Inches(0.4) + col_i * Inches(6.5)
        top = Inches(1.05) + row * Inches(3.0)
        rect(s, lft, top, Inches(6.2), Inches(2.8), fill=BG_CARD, lc=BORDER_COLOR)
        rect(s, lft, top, Inches(6.2), Inches(0.5), fill=col)
        tb(s, lft+Inches(0.12), top+Inches(0.06), Inches(3.5), Inches(0.38), name, sz=13, bold=True, color=WHITE)
        tb(s, lft+Inches(3.7), top+Inches(0.06), Inches(2.3), Inches(0.38), "功率: " + pwr, sz=11, color=WHITE, align=PP_ALIGN.RIGHT)
        tb(s, lft+Inches(0.12), top+Inches(0.58), Inches(3.0), Inches(0.32), "芯片: " + chip, sz=10, color=CYAN)
        tb(s, lft+Inches(3.2), top+Inches(0.58), Inches(2.8), Inches(0.32), "效率: " + eff, sz=11, bold=True, color=GREEN)
        rect(s, lft+Inches(0.12), top+Inches(1.0), Inches(5.96), Inches(0.03), fill=col)
        tb(s, lft+Inches(0.12), top+Inches(1.1), Inches(5.96), Inches(1.6), desc, sz=10.5, color=LIGHT_GRAY)
    ft(s); sn(s, 9); return s

# SLIDE 10: Tech Comparison Table
def s10(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    hdr(s, "四大方案關鍵參數對比", "Technical Parameters Comparison")
    hdrs = ["方案名稱", "代表芯片", "集成度", "最高功率", "效率", "功率密度", "BOM元件", "成本"]
    col_x = [Inches(0.4), Inches(2.1), Inches(3.85), Inches(5.25), Inches(6.55), Inches(7.9), Inches(9.5), Inches(10.9)]
    col_w = [Inches(1.55), Inches(1.6), Inches(1.3), Inches(1.2), Inches(1.2), Inches(1.45), Inches(1.25), Inches(2.1)]
    for i, h in enumerate(hdrs):
        rect(s, col_x[i], Inches(1.1), col_w[i], Inches(0.4), fill=PRIMARY)
        tb(s, col_x[i], Inches(1.15), col_w[i], Inches(0.32), h, sz=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    rows = [
        ("PFC+LLC GaN", "PI InnoSwitch4", "5星", "220W", ">95%", "45W/in3", "15-20", "$$$", PRIMARY),
        ("ACF單芯片", "DK8607", "4星", "120W", "93-94.5%", "35W/in3", "20-25", "$$", CYAN),
        ("協議+DC-DC", "SC9712", "4星", "140W", "92-94%", "30W/in3", "18-22", "$$", GREEN),
        ("全數字功率", "UCC29950", "3星", "240W", ">96%", "40W/in3", "25-30", "$$$", ORANGE),
        ("離散基準", "分立IC組合", "2星", "240W", "88-92%", "15W/in3", "60-80", "$", GRAY),
    ]
    for ri, row in enumerate(rows):
        y = Inches(1.55) + ri * Inches(0.9)
        bg_fill = BG_CARD if ri % 2 == 0 else RGBColor(28, 33, 40)
        for ci, cell in enumerate(row):
            tcol = row[-1] if ci == 0 else (LIGHT_GRAY if ci < len(row)-1 else GREEN)
            rect(s, col_x[ci], y, col_w[ci], Inches(0.82), fill=bg_fill, lc=BORDER_COLOR)
            align = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
            bold_f = ci == 0
            tb(s, col_x[ci]+Inches(0.05), y+Inches(0.2), col_w[ci]-Inches(0.1), Inches(0.42), str(cell), sz=10, bold=bold_f, color=tcol, align=align)
    ft(s); sn(s, 10); return s

# SLIDE 11: Tech Roadmap
def s11(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    hdr(s, "技術路線圖 2025-2030", "Technology Roadmap 2025-2030")
    years = ["2025", "2026", "2027", "2028", "2029", "2030"]
    x_start = Inches(0.6)
    y_line = Inches(2.2)
    step = Inches(12.1) / 5
    rect(s, x_start, y_line, Inches(12.1), Inches(0.04), fill=CYAN)
    for i, yr in enumerate(years):
        x = x_start + i * step
        circ = s.shapes.add_shape(MSO_SHAPE.OVAL, x-Inches(0.18), y_line-Inches(0.16), Inches(0.36), Inches(0.36))
        sf(circ, PRIMARY); sl(circ, PRIMARY)
        tb(s, x-Inches(0.4), y_line+Inches(0.28), Inches(0.8), Inches(0.3), yr, sz=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    ms_data = [
        ("2025", "雙芯片架構", "200-500kHz", "GaN功率級+數字控制器分立", PRIMARY),
        ("2026", "GaN合封方案", "500-1000kHz", "PFC+LLC合封，效率>95%", CYAN),
        ("2027", "單芯片GaN SoC", "1-2MHz", "全集成SoC，140W量產", GREEN),
        ("2028", "全數字功率", "2-3MHz", "數字控制普及，240W標配", ORANGE),
        ("2029", "GaN+SiC混合", "3-5MHz", "SiC用於PFC，GaN用於DC-DC", PURPLE),
        ("2030", "GaN單片集成", "5-10MHz", "CMOS工藝GaN，突破功率密度上限", RGBColor(255, 105, 180)),
    ]
    for i, (yr, tech, freq, desc, col) in enumerate(ms_data):
        x = x_start + i * step
        rect(s, x, y_line-Inches(0.55), Inches(0.04), Inches(0.4), fill=col)
        top = y_line - Inches(3.2)
        rect(s, x-Inches(1.5), top, Inches(3.0), Inches(2.5), fill=BG_CARD, lc=BORDER_COLOR)
        rect(s, x-Inches(1.5), top, Inches(3.0), Inches(0.42), fill=col)
        tb(s, x-Inches(1.5), top+Inches(0.04), Inches(3.0), Inches(0.35), tech, sz=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tb(s, x-Inches(1.4), top+Inches(0.5), Inches(2.8), Inches(0.32), "頻率: " + freq, sz=10, bold=True, color=col)
        tb(s, x-Inches(1.4), top+Inches(0.88), Inches(2.8), Inches(1.5), desc, sz=9.5, color=LIGHT_GRAY)
    ft(s); sn(s, 11); return s

# SLIDE 12: Competitive Landscape
def s12(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    hdr(s, "全球競爭格局全景圖", "Global Competitive Landscape")
    tb(s, Inches(0.4), Inches(1.1), Inches(6.0), Inches(0.4), "國際廠商", sz=16, bold=True, color=PRIMARY)
    intl = [
        ("Power Integrations", "$580M", "A+", "GaN合封先驅，PI InnoSwitch4-CZ市場領先"),
        ("Navitas", "$180M", "B+", "GaN功率IC專家，1000+專利壁壘"),
        ("Infineon", "全平台", "A", "Si/GaN/SiC全覆蓋，汽車級認證"),
        ("TI", "全面", "A", "數字功率控制器的系統級優勢"),
    ]
    for i, (name, rev, grade, desc) in enumerate(intl):
        top = Inches(1.6) + i * Inches(1.3)
        rect(s, Inches(0.4), top, Inches(6.0), Inches(1.15), fill=BG_CARD, lc=BORDER_COLOR)
        rect(s, Inches(0.4), top, Inches(0.12), Inches(1.15), fill=PRIMARY)
        tb(s, Inches(0.62), top+Inches(0.08), Inches(2.8), Inches(0.35), name, sz=12, bold=True, color=WHITE)
        tb(s, Inches(3.5), top+Inches(0.08), Inches(1.2), Inches(0.35), "營收: " + rev, sz=10, color=CYAN)
        tb(s, Inches(4.8), top+Inches(0.08), Inches(1.4), Inches(0.35), "評級: " + grade, sz=10, bold=True, color=GREEN)
        tb(s, Inches(0.62), top+Inches(0.48), Inches(5.6), Inches(0.58), desc, sz=10, color=LIGHT_GRAY)
    tb(s, Inches(6.8), Inches(1.1), Inches(6.0), Inches(0.4), "中國廠商", sz=16, bold=True, color=ORANGE)
    cn = [
        ("南芯半導體", "Pre-IPO", "A-", "PD SoC市場份額領先，SC9712旗艦"),
        ("智融科技", "Pre-IPO", "A-", "多口PD晶片，性價比之王"),
        ("英集芯", "A股", "B+", "USB Hub+PD combo晶片"),
        ("東科半導體", "創業板", "B", "ACF方案，性價比優勢"),
        ("杰華特", "科創板", "B+", "全數字功率方案"),
        ("矽力杰", "A股", "B", "BMS+PD組合方案"),
    ]
    for i, (name, stage, grade, desc) in enumerate(cn):
        col_i = i // 3; row_i = i % 3
        lft = Inches(6.8) + col_i * Inches(3.15)
        top = Inches(1.6) + row_i * Inches(1.8)
        rect(s, lft, top, Inches(3.0), Inches(1.6), fill=BG_CARD, lc=BORDER_COLOR)
        rect(s, lft, top, Inches(3.0), Inches(0.38), fill=ORANGE)
        tb(s, lft, top+Inches(0.04), Inches(3.0), Inches(0.3), name, sz=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tb(s, lft+Inches(0.1), top+Inches(0.48), Inches(1.4), Inches(0.28), stage, sz=9.5, color=CYAN)
        tb(s, lft+Inches(1.6), top+Inches(0.48), Inches(1.2), Inches(0.28), "[" + grade + "]", sz=9.5, bold=True, color=GREEN)
        tb(s, lft+Inches(0.1), top+Inches(0.82), Inches(2.8), Inches(0.65), desc, sz=9.5, color=LIGHT_GRAY)
    ft(s); sn(s, 12); return s

# SLIDE 13: SWOT Analysis
def s13(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    hdr(s, "國際廠商 vs 中國廠商 SWOT", "SWOT Analysis: International vs Chinese Players")
    # International SWOT
    tb(s, Inches(0.4), Inches(1.1), Inches(6.0), Inches(0.4), "國際廠商 (PI / Navitas / Infineon)", sz=13, bold=True, color=PRIMARY)
    intl_swot = [
        ("S優勢", "GaN/SiC工藝領先，專利壁壘深厚", PRIMARY),
        ("W劣勢", "成本高，客戶響應速度慢", ORANGE),
        ("O機會", "汽車/工業市場門檻高，利潤率可觀", GREEN),
        ("T威脅", "中國廠商快速追趕，價格戰壓力", CYAN),
    ]
    for i, (title, desc, col) in enumerate(intl_swot):
        top = Inches(1.55) + i * Inches(1.35)
        rect(s, Inches(0.4), top, Inches(6.0), Inches(1.2), fill=BG_CARD, lc=BORDER_COLOR)
        rect(s, Inches(0.4), top, Inches(0.12), Inches(1.2), fill=col)
        rect(s, Inches(0.52), top+Inches(0.1), Inches(0.75), Inches(0.45), fill=col)
        tb(s, Inches(0.52), top+Inches(0.15), Inches(0.75), Inches(0.38), title, sz=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tb(s, Inches(1.4), top+Inches(0.15), Inches(4.9), Inches(0.9), desc, sz=11, color=WHITE)
    # Chinese SWOT
    tb(s, Inches(6.8), Inches(1.1), Inches(6.0), Inches(0.4), "中國廠商 (南芯 / 智融 / 杰華特)", sz=13, bold=True, color=ORANGE)
    cn_swot = [
        ("S優勢", "性價比極致，供應鏈響應快，本土市場理解深", PRIMARY),
        ("W劣勢", "GaN工藝依賴代工，專利壁壘弱，高端汽車認證不足", ORANGE),
        ("O機會", "消費電子PD SoC市場份額持續擴大，出海加速", GREEN),
        ("T威脅", "內捲嚴重，價格戰持續，國際廠商專利訴訟風險", CYAN),
    ]
    for i, (title, desc, col) in enumerate(cn_swot):
        top = Inches(1.55) + i * Inches(1.35)
        rect(s, Inches(6.8), top, Inches(6.0), Inches(1.2), fill=BG_CARD, lc=BORDER_COLOR)
        rect(s, Inches(6.8), top, Inches(0.12), Inches(1.2), fill=col)
        rect(s, Inches(6.92), top+Inches(0.1), Inches(0.75), Inches(0.45), fill=col)
        tb(s, Inches(6.92), top+Inches(0.15), Inches(0.75), Inches(0.38), title, sz=10, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tb(s, Inches(7.8), top+Inches(0.15), Inches(4.9), Inches(0.9), desc, sz=11, color=WHITE)
    ft(s); sn(s, 13); return s

# SLIDE 14: Competitive Barriers
def s14(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    hdr(s, "核心競爭壁壘與專利格局", "Competitive Barriers & Patent Landscape")
    # Patent data
    tb(s, Inches(0.4), Inches(1.1), Inches(12.5), Inches(0.4), "專利壁壘地圖", sz=16, bold=True, color=WHITE)
    patents = [
        ("Navitas", "1000+", "GaN功率IC核心專利，侵權風險高", PRIMARY),
        ("Power Integrations", "800+", "PowiGaN技術，涵蓋LLC/GaN合封架構", CYAN),
        ("Infineon", "全平台", "Si/GaN/SiC全覆蓋，汽車級專利壁壘", GREEN),
        ("Texas Instruments", "500+", "數字功率控制專利，軟件+硬件生態", ORANGE),
    ]
    for i, (name, count, desc, col) in enumerate(patents):
        top = Inches(1.6) + i * Inches(1.0)
        rect(s, Inches(0.4), top, Inches(12.5), Inches(0.85), fill=BG_CARD, lc=BORDER_COLOR)
        rect(s, Inches(0.4), top, Inches(0.12), Inches(0.85), fill=col)
        tb(s, Inches(0.65), top+Inches(0.08), Inches(2.0), Inches(0.32), name, sz=12, bold=True, color=WHITE)
        rect(s, Inches(2.8), top+Inches(0.1), Inches(1.2), Inches(0.55), fill=col)
        tb(s, Inches(2.8), top+Inches(0.18), Inches(1.2), Inches(0.38), count, sz=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tb(s, Inches(4.2), top+Inches(0.15), Inches(8.5), Inches(0.55), desc, sz=11, color=LIGHT_GRAY)
    tb(s, Inches(0.4), Inches(5.7), Inches(12.5), Inches(0.4), "四大核心壁壘", sz=16, bold=True, color=WHITE)
    barriers = [
        ("專利壁壘", "GaN材料、工藝、驅動架構專利", "Navitas/PI已形成專利網絡", PRIMARY),
        ("工藝壁壘", "GaN-on-Si外延生長良率", "8英寸GaN量產僅少數玩家", CYAN),
        ("認證壁壘", "USB-IF認證/汽車AEC-Q100", "認證周期6-18個月", GREEN),
        ("供應鏈壁壘", "GaN晶圓廠產能集中", "台積電/穩懋佔據70%+份額", ORANGE),
    ]
    for i, (title, desc1, desc2, col) in enumerate(barriers):
        lft = Inches(0.4) + i * Inches(3.15)
        top = Inches(6.15)
        rect(s, lft, top, Inches(3.0), Inches(0.85), fill=BG_CARD, lc=BORDER_COLOR)
        rect(s, lft, top, Inches(3.0), Inches(0.38), fill=col)
        tb(s, lft, top+Inches(0.04), Inches(3.0), Inches(0.3), title, sz=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        tb(s, lft+Inches(0.1), top+Inches(0.42), Inches(2.8), Inches(0.35), desc1, sz=9, color=LIGHT_GRAY)
    ft(s); sn(s, 14); return s

# SLIDE 15: Consumer Electronics
def s15(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg(s)
    hdr(s, "消費電子應用", "Consumer Electronics Applications")
    apps = [
        ("AI PC / 筆電", "140-240W", "$45B", "12%", "蘋果/戴爾/聯想/華為",
         "AI PC標配240W快充，2025年AI PC滲透率預計突破25%，全球筆電PD適配器市場爆發", PRIMARY),
        ("旗艦手機 / 摺疊機", "100-150W", "$38B", "8%",
         "蘋果/三星/小米/OPPO",
         "摺疊手機對便攜性要求高，PD 100W+微型化適配器需求持續攀升", CYAN),
        ("遊戲設備", "45-240W", "$12B", "25%",
         "任天堂/Valve/華碩/索尼",
         "遊戲本適配器功率突破200W，Switch 2和PS5 Pro標配PD快充需求爆發", GREEN),
    ]
    for i, (name, pwr, market, cagr, vendors, desc, col) in enumerate(apps):
        top = Inches(1.1) + i * Inches(2.05)
        rect(s, Inches(0.4), top, Inches(12.5), Inches(1.85), fill=BG_CARD, lc=BORDER_COLOR)
        rect(s, Inches(0.4), top, Inches(0.12), Inches(1.85), fill=col)
        rect(s, Inches(0.4), top, Inches(12.5), Inches(0.5), fill=col)
        tb(s, Inches(0.62), top+Inches(0.06), Inches(4.0), Inches(0.38), name, sz=14, bold=True, color=WHITE)
        tb(s, Inches(4.8), top+Inches(0.06), Inches(2.0), Inches(0.38), "功率: " + pwr, sz=11, color=WHITE)
        tb(s, Inches(6.9), top+Inches(0.06), Inches(2.2), Inches(0.38), "市場: " + market, sz=11, color=WHITE)
        tb(s, Inches(9.2), top+Inches(0.06), Inches(1.5), Inches(0.38), "CAGR: " + cagr, sz=11, bold=True, color=GREEN)
        tb(s, Inches(10.8), top+Inches(0.06), Inches(2.0), Inches(0.38), vendors, sz=10, color=LIGHT_GRAY)
        tb(s, Inches(0.62), top+Inches(0.6), Inches(11.8), Inches(1.1), desc, sz=11, color=LIGHT_GRAY)
    ft(s); sn(s, 15); return s
