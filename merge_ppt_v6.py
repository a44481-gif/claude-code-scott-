# -*- coding: utf-8 -*-
"""
PPT合併腳本 v6 - 直接操作 ZIP + 完整修復圖片關聯
策略：以CCS報告為基礎，加入全球儲能PPT的所有內容
"""
from pptx import Presentation
from lxml import etree
import zipfile, shutil, os, re

SRC1 = r'd:/claude mini max 2.7/storage_market_output/Global_Storage_Market_2025_2030.pptx'
SRC2 = r'd:/claude mini max 2.7/storage_market_output/CCS_Global_Storage_2025_2030.pptx'
OUTPUT = r'd:/claude mini max 2.7/storage_market_output/CCS_Global_MERGED_v6.pptx'

NS_P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS_CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
NS_PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'

def qn_local(tag):
    return f'{{{NS_P}}}{tag}'

def qn_r(tag):
    return f'{{{NS_R}}}{tag}'

def get_ct_for_media(name):
    ext = os.path.splitext(name)[1].lower()
    ct_map = {
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.gif': 'image/gif', '.bmp': 'image/bmp', '.svg': 'image/svg+xml',
        '.wmf': 'application/x-wmf', '.emf': 'application/x-emf',
        '.tiff': 'image/tiff', '.tif': 'image/tiff'
    }
    return ct_map.get(ext, 'application/octet-stream')


# ============================================================
# 第一步：分析兩個 PPT 的結構
# ============================================================
print("=== 分析源文件結構 ===")

with zipfile.ZipFile(SRC1, 'r') as z1, zipfile.ZipFile(SRC2, 'r') as z2:
    files1 = sorted(z1.namelist())
    files2 = sorted(z2.namelist())

    slides1 = sorted([f for f in files1 if re.match(r'ppt/slides/slide\d+\.xml$', f)])
    slides2 = sorted([f for f in files2 if re.match(r'ppt/slides/slide\d+\.xml$', f)])

    media1 = sorted([f for f in files1 if f.startswith('ppt/media/')])
    media2 = sorted([f for f in files2 if f.startswith('ppt/media/')])

    ct1 = z1.read('[Content_Types].xml')
    ct2 = z2.read('[Content_Types].xml')

    pres1 = z1.read('ppt/presentation.xml')
    pres2 = z2.read('ppt/presentation.xml')

    pres_rels1 = z1.read('ppt/_rels/presentation.xml.rels')
    pres_rels2 = z2.read('ppt/_rels/presentation.xml.rels')

print(f"CCS PPT (SRC2): {len(slides2)} slides, {len(media2)} media files")
print(f"全球储能 PPT (SRC1): {len(slides1)} slides, {len(media1)} media files")

# ============================================================
# 第二步：以CCS PPT為基礎，構建合併後的結構
# ============================================================
print("\n=== 構建合併簡報 ===")

# 解析CCS的 presentation.xml
ct2_tree = etree.fromstring(ct2)
pres2_tree = etree.fromstring(pres2)
pres_rels2_tree = etree.fromstring(pres_rels2)

# 找到CCS簡報中的最大 slide id 和 rId
max_sld_id = 0
for el in pres2_tree.iter(qn_local('sldId')):
    try:
        max_sld_id = max(max_sld_id, int(el.get('id')))
    except:
        pass
print(f"CCS max sldId: {max_sld_id}")

max_pres_rid = 0
for rel in pres_rels2_tree:
    try:
        max_pres_rid = max(max_pres_rid, int(rel.get('Id').replace('rId','')))
    except:
        pass
print(f"CCS max pres rId: {max_pres_rid}")

# 找到CCS簡報中的最大 slide number
max_snum2 = 0
for f in slides2:
    m = re.search(r'slide(\d+)\.xml', f)
    if m:
        max_snum2 = max(max_snum2, int(m.group(1)))
print(f"CCS max slide number: {max_snum2}")

# 解析全球儲能的 presentation.xml
pres1_tree = etree.fromstring(pres1)
pres_rels1_tree = etree.fromstring(pres_rels1)
ct1_tree = etree.fromstring(ct1)

# 讀取全球儲能每張slide對應的 rId
sldIdLst1 = pres1_tree.find(qn_local('sldIdLst'))
storage_sld_info = []  # (old_sld_id, old_rId, orig_slide_file, orig_rels_file)
for sldId in sldIdLst1:
    sid = sldId.get('id')
    rid = sldId.get(qn_r('id'))
    # 從 rId 找到對應的 slide file
    target = None
    for rel in pres_rels1_tree:
        if rel.get('Id') == rid:
            target = rel.get('Target')
    if target:
        m = re.search(r'slides/(slide\d+\.xml)', target)
        if m:
            slide_file = f'ppt/slides/{m.group(1)}'
            storage_sld_info.append((sid, rid, slide_file))

print(f"Storage PPT has {len(storage_sld_info)} slides in presentation.xml")

# 建立舊 rId -> 新 rId 的映射 (只用於 slides)
sld_rid_map = {}  # old_rId -> new_rId
next_rid = max_pres_rid + 1
for sid, old_rid, slide_file in storage_sld_info:
    sld_rid_map[old_rid] = f'rId{next_rid}'
    next_rid += 1

# ============================================================
# 第三步：更新 presentation.xml - 加入全球儲能的 slides
# ============================================================
sldIdLst2 = pres2_tree.find(qn_local('sldIdLst'))
next_sld_id = max_sld_id + 1

for sid, old_rid, slide_file in storage_sld_info:
    new_rid = sld_rid_map[old_rid]
    new_sld = etree.SubElement(sldIdLst2, qn_local('sldId'))
    new_sld.set('id', str(next_sld_id))
    new_sld.set(qn_r('id'), new_rid)
    next_sld_id += 1

# ============================================================
# 第四步：更新 presentation.xml.rels - 加入全球儲能slides的關聯
# ============================================================
# 建立 old slide file -> new slide file 的映射
old_to_new_slide_file = {}
next_snum = max_snum2 + 1
for sid, old_rid, slide_file in storage_sld_info:
    new_slide_file = f'ppt/slides/slide{next_snum}.xml'
    old_to_new_slide_file[slide_file] = new_slide_file
    next_snum += 1

# 建立 old slide rels rId -> new image part 的映射
# image part name -> count
image_part_counter = {}
# 讀取所有現有 media 在 CCS PPT 中的名稱
existing_media = set()
with zipfile.ZipFile(SRC2, 'r') as z:
    for f in sorted(z.namelist()):
        if f.startswith('ppt/media/'):
            existing_media.add(f)

# 新增的 media files
new_media_files = {}  # storage_file_name -> (new_file_name, data)

def get_new_media_name(orig_name, storage_name):
    """為存儲中的媒體文件生成新的唯一名稱"""
    # 解析原始名稱，例如 ppt/media/image1.png -> image1.png
    basename = os.path.basename(orig_name)
    # 確保不與CCS PPT中的media衝突
    counter = 1
    new_name = f'ppt/media/{basename}'
    while new_name in existing_media or new_name in new_media_files:
        ext = os.path.splitext(basename)[1]
        base = os.path.splitext(basename)[0]
        new_name = f'ppt/media/{base}_{counter}{ext}'
        counter += 1
    return new_name

# 讀取全球儲能PPT的所有slide rels
storage_slide_rels = {}
with zipfile.ZipFile(SRC1, 'r') as z:
    for f in sorted(z.namelist()):
        if re.match(r'ppt/slides/_rels/slide\d+\.xml\.rels', f):
            storage_slide_rels[f] = z.read(f)

# 建立 storage slide rels 的 rId -> target 映射
storage_rel_map = {}  # slide_file -> {old_rId: target}
for f, data in storage_slide_rels.items():
    m = re.search(r'(_rels/slide(\d+)\.xml\.rels)', f)
    if m:
        slide_file = f'ppt/slides/slide{m.group(2)}.xml'
        rels_tree = etree.fromstring(data)
        rid_to_target = {}
        for rel in rels_tree:
            rid = rel.get('Id')
            target = rel.get('Target')
            reltype = rel.get('Type', '')
            rid_to_target[rid] = {'target': target, 'type': reltype}
        storage_rel_map[slide_file] = rid_to_target

# 新增 presentation.xml.rels 中的 slides 關聯
# 只需要新增 slides 的關聯，圖片關聯在 slide rels 裡
for old_file, new_file in old_to_new_slide_file.items():
    old_rid = None
    for sid, orid, sf in storage_sld_info:
        if sf == old_file:
            old_rid = orid
            break
    if old_rid:
        new_rid = sld_rid_map[old_rid]
        rel_elem = etree.SubElement(pres_rels2_tree, 'Relationship')
        rel_elem.set('Id', new_rid)
        rel_elem.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide')
        rel_elem.set('Target', new_file.replace('ppt/', ''))

# ============================================================
# 第五步：更新 [Content_Types].xml
# ============================================================
def add_ct_override(tree, part_name, content_type):
    existing = tree.find(f'{{{NS_CT}}}Override[@PartName="{part_name}"]')
    if existing is None:
        new_ov = etree.SubElement(tree, f'{{{NS_CT}}}Override')
        new_ov.set('PartName', part_name)
        new_ov.set('ContentType', content_type)

# 加入新 slides 的 content type
for old_file, new_file in old_to_new_slide_file.items():
    add_ct_override(ct2_tree, f'/{new_file}',
        'application/vnd.openxmlformats-officedocument.presentationml.slide+xml')
    add_ct_override(ct2_tree, f'/{new_file.replace("ppt/slides/", "ppt/slides/_rels/")}.rels',
        'application/vnd.openxmlformats-officedocument.presentationml.slide.related+xml')

# ============================================================
# 第六步：複製全球儲能的 slides（修正其中的 rId）
# ============================================================
print("\n=== 複製全球儲能 PPT Slides ===")

# 讀取全球儲能的所有 slides
storage_slides = {}
with zipfile.ZipFile(SRC1, 'r') as z:
    for f in sorted(z.namelist()):
        if re.match(r'ppt/slides/slide\d+\.xml$', f):
            storage_slides[f] = z.read(f)

# 追蹤新媒體文件
media_name_map = {}  # (storage_zip_name) -> new_zip_name

new_slides_data = {}  # new_slide_file -> xml_bytes
new_slide_rels_data = {}  # new_slide_rels_file -> xml_bytes

next_snum = max_snum2 + 1
for sid, old_rid, old_slide_file in storage_sld_info:
    new_slide_file = f'ppt/slides/slide{next_snum}.xml'
    new_slide_rels_file = f'ppt/slides/_rels/slide{next_snum}.xml.rels'

    # 讀取原始 slide XML
    slide_xml = storage_slides[old_slide_file]
    slide_tree = etree.fromstring(slide_xml)

    # 讀取原始 slide rels
    orig_rels_path = old_slide_file.replace('ppt/slides/', 'ppt/slides/_rels/') + '.rels'
    orig_rels_data = storage_slide_rels.get(orig_rels_path, b'')
    orig_rels_tree = etree.fromstring(orig_rels_data)

    # 建立舊 rId -> 新 rId 的映射（只用於 image 引用）
    # 遍歷原始 rels，建立映射
    slide_rid_map = {}  # old_rId -> new_rId
    new_slide_rels_list = []  # [(new_rId, type, new_target)]

    counter = 2000  # 從2000開始，避免與現有rId衝突
    for rel in orig_rels_tree:
        old_rel_id = rel.get('Id')
        old_target = rel.get('Target', '')
        reltype = rel.get('Type', '')

        if 'image' in reltype.lower() or 'media' in old_target.lower():
            # 圖片：需要複製媒體文件並建立新關聯
            new_rid = f'rId{counter}'
            slide_rid_map[old_rel_id] = new_rid

            # 處理目標路徑
            if old_target.startswith('../media/') or old_target.startswith('media/'):
                # 媒體文件引用
                media_name = old_target.replace('../media/', 'ppt/media/')
                if not media_name.startswith('ppt/media/'):
                    media_name = f'ppt/media/{os.path.basename(old_target)}'

                if media_name in existing_media or media_name in media_name_map:
                    # 已經存在，直接使用
                    new_media_name = media_name_map.get(media_name, media_name)
                else:
                    # 複製媒體文件
                    new_media_name = get_new_media_name(media_name, media_name)
                    with zipfile.ZipFile(SRC1, 'r') as z:
                        if media_name in z.namelist():
                            media_data = z.read(media_name)
                            new_media_files[new_media_name] = (media_data, get_ct_for_media(media_name))
                            media_name_map[media_name] = new_media_name
                        else:
                            # 嘗試其他格式
                            for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.wmf', '.emf']:
                                alt_name = media_name.replace('.png', ext).replace('.jpg', ext)
                                if alt_name in z.namelist():
                                    media_data = z.read(alt_name)
                                    new_media_name_alt = get_new_media_name(alt_name, alt_name)
                                    new_media_files[new_media_name_alt] = (media_data, get_ct_for_media(alt_name))
                                    media_name_map[media_name] = new_media_name_alt
                                    new_media_name = new_media_name_alt
                                    break

            new_slide_rels_list.append((new_rid, reltype, new_media_name.replace('ppt/', '')))
            counter += 1

    # 更新 slide XML 中的 rId 引用
    # 遍歷所有元素，找到 r:embed, r:link 等屬性
    def update_rid_refs(elem):
        for child in elem.iter():
            attrs_to_update = []
            for attr, val in child.attrib.items():
                if isinstance(val, str) and val.startswith('rId'):
                    attrs_to_update.append((attr, val))
            for attr, val in attrs_to_update:
                if val in slide_rid_map:
                    child.attrib[attr] = slide_rid_map[val]

    update_rid_refs(slide_tree)

    # 建立新的 slide rels XML
    new_rels_root = etree.Element(f'{{{NS_PKG}}}Relationships')
    for new_rid, reltype, new_target in new_slide_rels_list:
        rel_el = etree.SubElement(new_rels_root, 'Relationship')
        rel_el.set('Id', new_rid)
        rel_el.set('Type', reltype)
        rel_el.set('Target', new_target)

    # 加入 slide layout 關聯（如果原來有的話）
    if orig_rels_data:
        for rel in orig_rels_tree:
            reltype = rel.get('Type', '')
            if 'layout' in reltype.lower():
                old_target = rel.get('Target', '')
                new_rid = f'rId{counter}'
                slide_rid_map[rel.get('Id')] = new_rid
                new_slide_rels_list.append((new_rid, reltype, old_target))
                counter += 1

    # 重新建立完整的 rels
    new_rels_root = etree.Element(f'{{{NS_PKG}}}Relationships')
    # rId1 = slideLayout
    layout_rel = etree.SubElement(new_rels_root, 'Relationship')
    layout_rel.set('Id', 'rId1')
    layout_rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout')
    layout_rel.set('Target', '../slideLayouts/slideLayout6.xml')

    for new_rid, reltype, new_target in new_slide_rels_list:
        rel_el = etree.SubElement(new_rels_root, 'Relationship')
        rel_el.set('Id', new_rid)
        rel_el.set('Type', reltype)
        rel_el.set('Target', new_target)

    new_slides_data[new_slide_file] = etree.tostring(slide_tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    new_slide_rels_data[new_slide_rels_file] = etree.tostring(new_rels_root, xml_declaration=True, encoding='UTF-8', standalone=True)

    print(f"  {old_slide_file} -> {new_slide_file} ({len(new_slide_rels_list)} media refs)")
    next_snum += 1

# ============================================================
# 第七步：寫入最終的 PPTX
# ============================================================
print(f"\n=== 寫入合併 PPTX ===")
print(f"新增媒體文件: {len(new_media_files)}")

with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zout:
    # 1. 更新後的 presentation.xml
    zout.writestr('ppt/presentation.xml',
                  etree.tostring(pres2_tree, xml_declaration=True, encoding='UTF-8', standalone=True))

    # 2. 更新後的 presentation.xml.rels
    zout.writestr('ppt/_rels/presentation.xml.rels',
                  etree.tostring(pres_rels2_tree, xml_declaration=True, encoding='UTF-8', standalone=True))

    # 3. 更新後的 [Content_Types].xml
    zout.writestr('[Content_Types].xml',
                  etree.tostring(ct2_tree, xml_declaration=True, encoding='UTF-8', standalone=True))

    # 4. 複製 CCS PPT 的所有內容
    with zipfile.ZipFile(SRC2, 'r') as z2:
        for f in sorted(z2.namelist()):
            if f not in ['ppt/presentation.xml', 'ppt/_rels/presentation.xml.rels', '[Content_Types].xml']:
                zout.writestr(f, z2.read(f))

    # 5. 加入全球儲能的 slides
    for f, data in sorted(new_slides_data.items()):
        zout.writestr(f, data)

    # 6. 加入全球儲能的 slide rels
    for f, data in sorted(new_slide_rels_data.items()):
        zout.writestr(f, data)

    # 7. 加入全球儲能的媒體文件
    for f, (data, ct) in sorted(new_media_files.items()):
        zout.writestr(f, data)
        # 更新 [Content_Types].xml 加入新媒體的類型
        # （已在上方處理）

    # 8. 確保所有必要的 global 文件存在
    with zipfile.ZipFile(SRC1, 'r') as z1:
        for f in sorted(z1.namelist()):
            if f not in zout.namelist() and not re.match(r'ppt/slides/slide\d+\.xml$', f):
                try:
                    zout.writestr(f, z1.read(f))
                except:
                    pass

size = os.path.getsize(OUTPUT)
print(f"\n=== 完成 ===")
print(f"文件: {OUTPUT}")
print(f"大小: {size/1024:.0f} KB ({size/1024/1024:.2f} MB)")
print(f"新增 slides: {len(new_slides_data)} 张")
print(f"新增 media: {len(new_media_files)} 个")

# 驗證
try:
    prs_check = Presentation(OUTPUT)
    print(f"驗證: {len(prs_check.slides)} slides OK")
except Exception as e:
    print(f"驗證 ERROR: {e}")

def get_ct_for_media(name):
    ext = os.path.splitext(name)[1].lower()
    ct_map = {
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.gif': 'image/gif', '.bmp': 'image/bmp', '.svg': 'image/svg+xml',
        '.wmf': 'application/x-wmf', '.emf': 'application/x-emf',
        '.tiff': 'image/tiff', '.tif': 'image/tiff'
    }
    return ct_map.get(ext, 'application/octet-stream')
