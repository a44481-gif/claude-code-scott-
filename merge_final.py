# -*- coding: utf-8 -*-
"""
PPT合併 - ZIP底層合併
以CCS PPTX（5.8MB，完整圖片）為基礎，加入新頁面PPT的幻燈片內容
"""
import zipfile, os, re
from lxml import etree

CCS = r'd:/claude mini max 2.7/storage_market_output/ccs_base.pptx'
NEW_PPTX = r'd:/claude mini max 2.7/storage_market_output/CCS_Global_IFPCS_Final_Report.pptx'
OUTPUT = r'd:/claude mini max 2.7/storage_market_output/CCS_Global_IFPCS_MERGED.pptx'

NS_P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS_PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS_CT = 'http://schemas.openxmlformats.org/package/2006/content-types'

def qn_p(t): return f'{{{NS_P}}}{t}'
def qn_r(t): return f'{{{NS_R}}}{t}'

print("=== 分析源文件 ===")
with zipfile.ZipFile(CCS) as z:
    ccs_files = sorted(z.namelist())
    ccs_slides = sorted([f for f in ccs_files if re.match(r'ppt/slides/slide\d+\.xml$', f)])
    ccs_media = [f for f in ccs_files if f.startswith('ppt/media/')]
    ccs_pres = z.read('ppt/presentation.xml')
    ccs_pres_rels = z.read('ppt/_rels/presentation.xml.rels')
    ccs_ct = z.read('[Content_Types].xml')
    existing_media = set(f for f in z.namelist() if f.startswith('ppt/media/'))

with zipfile.ZipFile(NEW_PPTX) as z:
    new_files_list = sorted(z.namelist())
    new_slides_list = sorted([f for f in new_files_list if re.match(r'ppt/slides/slide\d+\.xml$', f)])
    new_pres = z.read('ppt/presentation.xml')
    new_pres_rels = z.read('ppt/_rels/presentation.xml.rels')
    new_pres_tree = etree.fromstring(new_pres)
    new_pres_rels_tree = etree.fromstring(new_pres_rels)
    # 建立 rid -> target 映射
    new_rid_to_target = {}
    for rel in new_pres_rels_tree:
        new_rid_to_target[rel.get('Id','')] = rel.get('Target','')

    # 讀取所有新 slides 內容
    new_slide_data = {}
    for f in new_slides_list:
        new_slide_data[f] = z.read(f)

    # 讀取所有新 slide rels
    new_slide_rels_data = {}
    for f in new_files_list:
        if re.match(r'ppt/slides/_rels/slide\d+\.xml\.rels', f):
            new_slide_rels_data[f] = z.read(f)

    # 讀取所有新 media
    new_media_data = {}
    for f in new_files_list:
        if f.startswith('ppt/media/'):
            new_media_data[f] = z.read(f)

print(f"CCS: {len(ccs_slides)} slides, {len(ccs_media)} media")
print(f"新PPT: {len(new_slides_list)} slides, {len(new_media_data)} media")

# 解析CCS結構
pres_tree = etree.fromstring(ccs_pres)
pres_rels_tree = etree.fromstring(ccs_pres_rels)
ct_tree = etree.fromstring(ccs_ct)

# 最大ID
def max_id(tree, tag):
    vals = [int(el.get('id')) for el in tree.iter(qn_p(tag)) if el.get('id','0').isdigit()]
    return max(vals) if vals else 0

def max_rid(tree):
    vals = []
    for el in tree:
        rid = el.get('Id','')
        if rid.startswith('rId'):
            try: vals.append(int(rid[3:]))
            except: pass
    return max(vals) if vals else 0

max_sld_id = max_id(pres_tree, 'sldId')
max_pres_rid = max_rid(pres_rels_tree)
ccs_max_snum = max(int(re.search(r'slide(\d+)',f).group(1)) for f in ccs_slides if re.search(r'slide(\d+)',f))
print(f"max_sld_id={max_sld_id}, max_rId={max_pres_rid}, max_slide_num={ccs_max_snum}")

# 取新PPT的 sldIdLst（只要第2張起的幻燈片，即新增的數據頁）
new_sldIdLst = new_pres_tree.find(qn_p('sldIdLst'))
new_slide_info = []
for sldId in new_sldIdLst:
    new_slide_info.append({'id': sldId.get('id'), 'rId': sldId.get(qn_r('id'))})

# 建立幻燈片映射
sldIdLst = pres_tree.find(qn_p('sldIdLst'))
next_sld_id = max_sld_id + 1
next_rid = max_pres_rid + 1
next_snum = ccs_max_snum + 1

new_slide_map = {}  # old_slide_f -> new_slide_f

for info in new_slide_info:
    old_rid = info['rId']
    old_target = new_rid_to_target.get(old_rid, '')
    m = re.search(r'slides/(slide\d+\.xml)', old_target)
    if not m: continue
    old_slide_f = f"ppt/slides/{m.group(1)}"
    if old_slide_f not in new_slide_data: continue

    new_rid = f'rId{next_rid}'
    new_slide_f = f"ppt/slides/slide{next_snum}.xml"
    new_slide_map[old_slide_f] = (new_slide_f, new_rid)

    # 加入 sldIdLst
    el = etree.SubElement(sldIdLst, qn_p('sldId'))
    el.set('id', str(next_sld_id))
    el.set(qn_r('id'), new_rid)

    # 加入 pres rels
    relEl = etree.SubElement(pres_rels_tree, 'Relationship')
    relEl.set('Id', new_rid)
    relEl.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide')
    relEl.set('Target', f'slides/slide{next_snum}.xml')

    next_sld_id += 1
    next_rid += 1
    next_snum += 1

print(f"新增slides: {len(new_slide_map)}")

# 更新 [Content_Types]
def add_ct(ov_el, pn, ct_):
    ex = ov_el.find(f'{{{NS_CT}}}Override[@PartName="{pn}"]')
    if ex is None:
        ov = etree.SubElement(ov_el, f'{{{NS_CT}}}Override')
        ov.set('PartName', pn); ov.set('ContentType', ct_)

for old_f, (new_f, _) in new_slide_map.items():
    add_ct(ct_tree, f'/{new_f}', 'application/vnd.openxmlformats-officedocument.presentationml.slide+xml')
    add_ct(ct_tree, f'/{new_f.replace("slides/","slides/_rels/")}.rels',
           'application/vnd.openxmlformats-officedocument.presentationml.slide.related+xml')

# 處理 slides 和 media
final_slides = {}
final_slide_rels = {}
final_media = {}

for old_slide_f, (new_slide_f, _) in new_slide_map.items():
    old_rels_f = old_slide_f.replace('.xml','.xml.rels').replace('slides/','slides/_rels/')
    old_rels_xml = new_slide_rels_data.get(old_rels_f, b'')
    old_rels_tree = etree.fromstring(old_rels_xml) if old_rels_xml else \
                     etree.Element(f'{{{NS_PKG}}}Relationships')

    slide_xml = new_slide_data[old_slide_f]
    slide_tree = etree.fromstring(slide_xml)

    # rid -> new media name
    rid_to_new_media = {}
    new_rels_list = []  # (new_rid, type, target)

    # 固定 rId1 為 slideLayout6
    new_rels_list.append(('rId1','http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout','../slideLayouts/slideLayout6.xml'))

    rid_counter = 2000
    for rel in old_rels_tree:
        rid = rel.get('Id','')
        target = rel.get('Target','')
        reltype = rel.get('Type','')
        if 'image' in reltype.lower() or 'media' in target.lower():
            media_name = target.replace('../media/','ppt/media/')
            if not media_name.startswith('ppt/media/'): media_name = f'ppt/media/{os.path.basename(target)}'
            if media_name in new_media_data:
                # 分配新名稱
                ext = os.path.splitext(media_name)[1]
                new_media_name = f'ppt/media/media_{rid_counter}{ext}'
                rid_counter += 1
                while new_media_name in existing_media or new_media_name in final_media:
                    new_media_name = f'ppt/media/media_{rid_counter}{ext}'
                    rid_counter += 1
                final_media[new_media_name] = new_media_data[media_name]
                existing_media.add(new_media_name)
                rid_to_new_media[rid] = new_media_name
                new_rels_list.append((f'rId{rid_counter-1}', reltype, new_media_name.replace('ppt/media/','')))

    # 更新 slide XML 中的 rid 引用
    def fix_rids(elem, rid_map):
        for child in elem.iter():
            for attr, val in list(child.attrib.items()):
                if val in rid_map:
                    child.attrib[attr] = rid_map[val]
    fix_rids(slide_tree, rid_to_new_media)

    # 建立新的 slide rels
    new_rels_root = etree.Element(f'{{{NS_PKG}}}Relationships')
    for nr, nrt, nt in new_rels_list:
        rel_el = etree.SubElement(new_rels_root, 'Relationship')
        rel_el.set('Id', nr); rel_el.set('Type', nrt); rel_el.set('Target', nt)

    final_slides[new_slide_f] = etree.tostring(slide_tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    final_slide_rels[new_slide_f.replace('slides/','slides/_rels/')+'.rels'] = \
        etree.tostring(new_rels_root, xml_declaration=True, encoding='UTF-8', standalone=True)

print(f"最終: {len(final_slides)} slides, {len(final_media)} media")

# 寫入
print("寫入合併PPTX...")
ct_updated = False
with zipfile.ZipFile(CCS) as z_ccs, \
     zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as zout:

    # 更新核心文件
    zout.writestr('ppt/presentation.xml', etree.tostring(pres_tree, xml_declaration=True, encoding='UTF-8', standalone=True))
    zout.writestr('ppt/_rels/presentation.xml.rels', etree.tostring(pres_rels_tree, xml_declaration=True, encoding='UTF-8', standalone=True))
    zout.writestr('[Content_Types].xml', etree.tostring(ct_tree, xml_declaration=True, encoding='UTF-8', standalone=True))
    ct_updated = True

    # 複製CCS全部
    for f in ccs_files:
        zout.writestr(f, z_ccs.read(f))

    # 寫入新 slides
    for f, data in final_slides.items():
        zout.writestr(f, data)

    # 寫入新 slide rels
    for f, data in final_slide_rels.items():
        zout.writestr(f, data)

    # 寫入新 media 並更新 CT
    for f, data in final_media.items():
        zout.writestr(f, data)
        ext = os.path.splitext(f)[1].lower()
        ct_map = {'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg',
                  '.gif':'image/gif','.svg':'image/svg+xml','.bmp':'image/bmp'}
        add_ct(ct_tree, f'/{f}', ct_map.get(ext,'application/octet-stream'))

    # 重新寫入含media的CT
    if not ct_updated:
        zout.writestr('[Content_Types].xml', etree.tostring(ct_tree, xml_declaration=True, encoding='UTF-8', standalone=True))

size = os.path.getsize(OUTPUT)
print(f"\n=== 完成 ===")
print(f"文件: {OUTPUT}")
print(f"大小: {size/1024/1024:.2f} MB")
print(f"新增slides: {len(final_slides)}, 新增media: {len(final_media)}")
