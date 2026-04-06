# -*- coding: utf-8 -*-
"""
PPT合併腳本 - 使用ZIP底層合併，完整保留所有圖片和媒體資源
"""

import zipfile, shutil, os, re
from lxml import etree

SRC1 = r"d:/claude mini max 2.7/storage_market_output/Global_Storage_Market_2025_2030.pptx"
SRC2 = r"d:/李總項目/CCS集成母排与线束技术整合市场分析报告.pptx"
OUTPUT = r"d:/claude mini max 2.7/storage_market_output/CCS_全球储能市场综合报告_2025-2030_FINAL.pptx"
WORK = r"d:/claude mini max 2.7/storage_market_output/_merge_work"

NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG = "http://schemas.openxmlformats.org/package/2006/content-types"
ET_NS_P = f"{{{NS_P}}}"
ET_NS_R = f"{{{NS_R}}}"

def nsmap(el):
    return dict(el.nsmap)

def make_cover_slide_xml():
    """生成深色綜合封面XML"""
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="{NS_P}" xmlns:r="{NS_R}" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:cSld>
    <p:bg>
      <p:bgPr>
        <a:solidFill>
          <a:srgbClr val="0A295E"/>
        </a:solidFill>
        <a:effectLst/>
      </p:bgPr>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="12192000" cy="6858000"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="12192000" cy="6858000"/>
        </a:xfrm>
      </p:grpSpPr>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="2" name="Title"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="457200" y="1371600"/>
            <a:ext cx="11277600" cy="2286000"/>
          </a:xfrm>
          <a:prstGeom prst="rect">
            <a:avLst/>
          </a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square" rtlCol="0"/>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="ctr"/>
            <a:r>
              <a:rPr lang="zh-CN" sz="4000" b="1">
                <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
                <a:latin typeface="Microsoft YaHei"/>
                <a:ea typeface="Microsoft YaHei"/>
              </a:rPr>
              <a:t>CCS集成母排 × 全球储能市场</a:t>
            </a:r>
          </a:p>
          <a:p>
            <a:pPr algn="ctr"/>
            <a:r>
              <a:rPr lang="zh-CN" sz="3200" b="1">
                <a:solidFill><a:srgbClr val="FFD700"/></a:solidFill>
                <a:latin typeface="Microsoft YaHei"/>
                <a:ea typeface="Microsoft YaHei"/>
              </a:rPr>
              <a:t>综合分析报告 2025-2030</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="3" name="Subtitle"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="457200" y="3810000"/>
            <a:ext cx="11277600" cy="1094400"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"/>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="ctr"/>
            <a:r>
              <a:rPr lang="zh-CN" sz="1800" b="0">
                <a:solidFill><a:srgbClr val="CCD9EC"/></a:solidFill>
                <a:latin typeface="Microsoft YaHei"/>
                <a:ea typeface="Microsoft YaHei"/>
              </a:rPr>
              <a:t>CCS集成母排与线束技术整合市场分析报告</a:t>
            </a:r>
          </a:p>
          <a:p>
            <a:pPr algn="ctr"/>
            <a:r>
              <a:rPr lang="zh-CN" sz="1600">
                <a:solidFill><a:srgbClr val="99AACC"/></a:solidFill>
                <a:latin typeface="Microsoft YaHei"/>
                <a:ea typeface="Microsoft YaHei"/>
              </a:rPr>
              <a:t>全球储能及新能源关联市场经济规模分析</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="4" name="Date"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="457200" y="5029200"/>
            <a:ext cx="11277600" cy="457200"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"/>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="ctr"/>
            <a:r>
              <a:rPr lang="zh-CN" sz="1400">
                <a:solidFill><a:srgbClr val="7788AA"/></a:solidFill>
                <a:latin typeface="Microsoft YaHei"/>
                <a:ea typeface="Microsoft YaHei"/>
              </a:rPr>
              <a:t>2026年4月  |  内部研究资料</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr>
    <a:masterClrMapping/>
  </p:clrMapOvr>
</p:sld>"""
    return etree.fromstring(xml.encode('utf-8'))


def make_divider_slide_xml(part_num, title_line1, title_line2=""):
    """生成分隔页XML"""
    line2_xml = f"""<a:p>
            <a:pPr algn="ctr"/>
            <a:r>
              <a:rPr lang="zh-CN" sz="2400" b="1">
                <a:solidFill><a:srgbClr val="FFD700"/></a:solidFill>
                <a:latin typeface="Microsoft YaHei"/>
                <a:ea typeface="Microsoft YaHei"/>
              </a:rPr>
              <a:t>{title_line2}</a:t>
            </a:r>
          </a:p>""" if title_line2 else ""

    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="{NS_P}" xmlns:r="{NS_R}" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:cSld>
    <p:bg>
      <p:bgPr>
        <a:solidFill>
          <a:srgbClr val="1A5CBF"/>
        </a:solidFill>
        <a:effectLst/>
      </p:bgPr>
    </p:bg>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="12192000" cy="6858000"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="12192000" cy="6858000"/>
        </a:xfrm>
      </p:grpSpPr>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="2" name="PartNum"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="457200" y="1828800"/>
            <a:ext cx="11277600" cy="914400"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"/>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="ctr"/>
            <a:r>
              <a:rPr lang="en-US" sz="2000" b="1">
                <a:solidFill><a:srgbClr val="FFD700"/></a:solidFill>
                <a:latin typeface="Arial"/>
              </a:rPr>
              <a:t>PART {part_num}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="3" name="Title"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="457200" y="2590800"/>
            <a:ext cx="11277600" cy="1828800"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
          <a:noFill/>
        </p:spPr>
        <p:txBody>
          <a:bodyPr wrap="square"/>
          <a:lstStyle/>
          <a:p>
            <a:pPr algn="ctr"/>
            <a:r>
              <a:rPr lang="zh-CN" sz="3600" b="1">
                <a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>
                <a:latin typeface="Microsoft YaHei"/>
                <a:ea typeface="Microsoft YaHei"/>
              </a:rPr>
              <a:t>{title_line1}</a:t>
            </a:r>
          </a:p>
          {line2_xml}
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr>
    <a:masterClrMapping/>
  </p:clrMapOvr>
</p:sld>"""
    return etree.fromstring(xml.encode('utf-8'))


def merge_ppts():
    """合併兩個PPTX檔案"""
    # 清理工作目錄
    if os.path.exists(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    work_pptx = os.path.join(WORK, "merged.pptx")

    # 同時打開兩個源文件
    with zipfile.ZipFile(SRC1, 'r') as z1, \
         zipfile.ZipFile(SRC2, 'r') as z2, \
         zipfile.ZipFile(work_pptx, 'w', zipfile.ZIP_DEFLATED) as zout:

        all_files_1 = set(z1.namelist())
        all_files_2 = set(z2.namelist())
        all_files = all_files_1 | all_files_2

        print(f"SRC1 ({SRC1.split('/')[-1]}) files: {len(all_files_1)}")
        print(f"SRC2 ({SRC2.split('/')[-1]}) files: {len(all_files_2)}")

        # 讀取所有內容
        content1 = {f: z1.read(f) for f in all_files_1}
        content2 = {f: z2.read(f) for f in all_files_2}

        # ===== 分析現有slide關係 =====
        # [Content_Types].xml
        ct1 = content1.get('[Content_Types].xml', b'')
        ct2 = content2.get('[Content_Types].xml', b'')
        ct_out = merge_content_types(ct1, ct2)

        # [Relationships].xml
        rel1 = content1.get('_rels/.rels', b'')
        rel2 = content2.get('_rels/.rels', b'')

        # presentation.xml
        pres1_xml = content1.get('ppt/presentation.xml', b'')
        pres2_xml = content2.get('ppt/presentation.xml', b'')

        # slideMasters / slideLayouts
        sm1 = sorted([f for f in all_files_1 if f.startswith('ppt/slideMasters/') and f.endswith('.xml')])
        sm2 = sorted([f for f in all_files_2 if f.startswith('ppt/slideMasters/') and f.endswith('.xml')])
        sl1 = sorted([f for f in all_files_1 if f.startswith('ppt/slideLayouts/') and f.endswith('.xml')])
        sl2 = sorted([f for f in all_files_2 if f.startswith('ppt/slideLayouts/') and f.endswith('.xml')])

        # 確定現有slide數量
        slides1 = sorted([f for f in all_files_1 if re.match(r'ppt/slides/slide\d+\.xml', f)])
        slides2 = sorted([f for f in all_files_2 if re.match(r'ppt/slides/slide\d+\.xml', f)])
        print(f"Slides in SRC1: {len(slides1)}")
        print(f"Slides in SRC2: {len(slides2)}")

        # 新slideID起點
        # 解析pres1.xml取得現有sldIdLst
        pres1_tree = etree.fromstring(pres1_xml)
        sldIdLst = pres1_tree.find(f'{{{NS_P}}}sldIdLst')
        existing_ids = [int(el.get('id')) for el in sldIdLst]
        next_id = max(existing_ids) + 1 if existing_ids else 256
        print(f"Starting slide ID: {next_id}")

        # 計算新的rId
        # 讀取presentation.xml.rels
        pres1_rels_xml = content1.get('ppt/_rels/presentation.xml.rels', b'')
        pres1_rels_tree = etree.fromstring(pres1_rels_xml)
        existing_rids = []
        for rel in pres1_rels_tree:
            try:
                existing_rids.append(int(rel.get('Id').replace('rId','')))
            except:
                pass
        next_rid = max(existing_rids) + 1 if existing_rids else 1

        # ===== 構建合併後的 presentation.xml =====
        merged_tree = etree.fromstring(pres1_xml)
        merged_rels_tree = etree.fromstring(pres1_rels_xml)

        # 找到 sldIdLst
        merged_sldIdLst = merged_tree.find(f'{{{NS_P}}}sldIdLst')

        # --- 新增封面 slide (new slide 0) ---
        new_slide_xml_cover = make_cover_slide_xml()
        new_slide_rels_cover = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout6.xml"/>
</Relationships>"""
        cover_slide_name = "ppt/slides/slide_new_cover.xml"
        cover_rels_name = "ppt/slides/_rels/slide_new_cover.xml.rels"

        # --- Part1 分隔頁 ---
        div1_xml = make_divider_slide_xml(1, "CCS集成母排与线束技术整合", "市场分析报告")
        div1_rels = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout6.xml"/>
</Relationships>"""
        div1_name = "ppt/slides/slide_new_div1.xml"
        div1_rels_name = "ppt/slides/_rels/slide_new_div1.xml.rels"

        # --- Part2 分隔頁 ---
        div2_xml = make_divider_slide_xml(2, "全球储能及新能源关联市场经济规模", "2025-2030")
        div2_rels = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout6.xml"/>
</Relationships>"""
        div2_name = "ppt/slides/slide_new_div2.xml"
        div2_rels_name = "ppt/slides/_rels/slide_new_div2.xml.rels"

        # --- 加入到sldIdLst (順序：封面、CCS報告、储能報告、分隔頁) ---
        def add_sldId(parent, slide_name, rid_num):
            sldId = etree.SubElement(parent, f'{{{NS_P}}}sldId')
            sldId.set('id', str(next_id))
            sldId.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', f'rId{rid_num}')
            return next_id + 1, rid_num + 1

        # 先加入封面
        next_id, next_rid = add_sldId(merged_sldIdLst, cover_slide_name, next_rid)

        # CCS報告的slides (使用SRC2)
        for s in slides2:
            m = re.search(r'slide(\d+)\.xml', s)
            src2_slide_num = m.group(1)
            new_slide_name = f"ppt/slides/slide_new_ccs_{src2_slide_num}.xml"
            # 直接從SRC2複製
            slide_xml = content2[s]
            # 加入到列表
            next_id, next_rid = add_sldId(merged_sldIdLst, new_slide_name, next_rid)
            # 同時寫入（後面統一寫）

        # 分隔頁2 (Part2)
        next_id, next_rid = add_sldId(merged_sldIdLst, div2_name, next_rid)

        # 全球储能報告的slides (使用SRC1)
        for s in slides1:
            m = re.search(r'slide(\d+)\.xml', s)
            src1_slide_num = m.group(1)
            new_slide_name = f"ppt/slides/slide_new_storage_{src1_slide_num}.xml"
            slide_xml = content1[s]
            next_id, next_rid = add_sldId(merged_sldIdLst, new_slide_name, next_rid)

        # 更新presentation.xml.rels - 加入所有新slide的關聯
        def add_pres_rel(tree, rid, target, rel_type):
            rel = etree.SubElement(tree, 'Relationship')
            rel.set('Id', f'rId{rid}')
            rel.set('Type', rel_type)
            rel.set('Target', target)

        # 分隔頁
        add_pres_rel(merged_rels_tree, next_rid - 4, 'slides/slide_new_cover.xml',
                     'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide')
        rid_ccs_start = next_rid - 3
        rid_storage_start = next_rid - 3 + len(slides2) + 1  # +1 for div2
        add_pres_rel(merged_rels_tree, next_rid - 3 + len(slides2),
                     'slides/slide_new_div2.xml',
                     'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide')

        # CCS slides
        for i, s in enumerate(slides2):
            m = re.search(r'slide(\d+)\.xml', s)
            add_pres_rel(merged_rels_tree, rid_ccs_start + i,
                        f'slides/slide_new_ccs_{m.group(1)}.xml',
                        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide')

        # 储能 slides
        for i, s in enumerate(slides1):
            m = re.search(r'slide(\d+)\.xml', s)
            add_pres_rel(merged_rels_tree, rid_storage_start + i,
                        f'slides/slide_new_storage_{m.group(1)}.xml',
                        'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide')

        # ===== 更新[Content_Types].xml =====
        ct_tree = etree.fromstring(ct_out)
        ct_ns = 'http://schemas.openxmlformats.org/package/2006/content-types'
        override_ns = 'http://schemas.openxmlformats.org/package/2006/relationships'

        def ensure_ct(tree, part_name, content_type):
            existing = tree.find(f'{{{ct_ns}}}Override[@PartName="{part_name}"]')
            if existing is None:
                ov = etree.SubElement(tree, f'{{{ct_ns}}}Override')
                ov.set('PartName', part_name)
                ov.set('ContentType', content_type)

        # 新增的slide需要override
        ensure_ct(ct_tree, '/ppt/slides/slide_new_cover.xml',
                  'application/vnd.openxmlformats-officedocument.presentationml.slide+xml')
        ensure_ct(ct_tree, '/ppt/slides/slide_new_div1.xml',
                  'application/vnd.openxmlformats-officedocument.presentationml.slide+xml')
        ensure_ct(ct_tree, '/ppt/slides/slide_new_div2.xml',
                  'application/vnd.openxmlformats-officedocument.presentationml.slide+xml')
        for i in range(1, len(slides2) + 1):
            ensure_ct(ct_tree, f'/ppt/slides/slide_new_ccs_{i}.xml',
                      'application/vnd.openxmlformats-officedocument.presentationml.slide+xml')
        for i in range(1, len(slides1) + 1):
            ensure_ct(ct_tree, f'/ppt/slides/slide_new_storage_{i}.xml',
                      'application/vnd.openxmlformats-officedocument.presentationml.slide+xml')

        # ===== 寫入所有檔案到新的ZIP =====
        # 1. [Content_Types].xml
        zout.writestr('[Content_Types].xml',
                      etree.tostring(ct_tree, xml_declaration=True, encoding='UTF-8', standalone=True))

        # 2. _rels/.rels
        zout.writestr('_rels/.rels', content1.get('_rels/.rels', content2.get('_rels/.rels', b'')))

        # 3. _rels/presentation.xml.rels (更新後)
        zout.writestr('ppt/_rels/presentation.xml.rels',
                      etree.tostring(merged_rels_tree, xml_declaration=True, encoding='UTF-8', standalone=True))

        # 4. presentation.xml (更新後)
        zout.writestr('ppt/presentation.xml',
                      etree.tostring(merged_tree, xml_declaration=True, encoding='UTF-8', standalone=True))

        # 5. app.xml (如果存在)
        if 'docProps/app.xml' in content1:
            zout.writestr('docProps/app.xml', content1['docProps/app.xml'])

        # 6. Core (如果存在)
        if 'docProps/core.xml' in content1:
            zout.writestr('docProps/core.xml', content1['docProps/core.xml'])

        # 7. 新增的封面、分隔頁
        zout.writestr('ppt/slides/slide_new_cover.xml',
                      etree.tostring(new_slide_xml_cover, xml_declaration=True, encoding='UTF-8', standalone=True))
        zout.writestr('ppt/slides/_rels/slide_new_cover.xml.rels', new_slide_rels_cover)
        zout.writestr('ppt/slides/slide_new_div1.xml',
                      etree.tostring(div1_xml, xml_declaration=True, encoding='UTF-8', standalone=True))
        zout.writestr('ppt/slides/_rels/slide_new_div1.xml.rels', div1_rels)
        zout.writestr('ppt/slides/slide_new_div2.xml',
                      etree.tostring(div2_xml, xml_declaration=True, encoding='UTF-8', standalone=True))
        zout.writestr('ppt/slides/_rels/slide_new_div2.xml.rels', div2_rels)

        # 8. 複製CCS報告的所有slides (需要修正relationships中的target)
        for s in slides2:
            m = re.search(r'slide(\d+)\.xml', s)
            new_name = f"ppt/slides/slide_new_ccs_{m.group(1)}.xml"
            # 修正slide rels中的相對路徑
            slide_xml = content2[s]
            zout.writestr(new_name, slide_xml)
            # 複製對應的rels
            rel_path = f"ppt/slides/_rels/{m.group(0)}.rels"
            if rel_path in content2:
                zout.writestr(f"ppt/slides/_rels/slide_new_ccs_{m.group(1)}.xml.rels",
                            content2[rel_path])

        # 9. 複製全球储能報告的所有slides
        for s in slides1:
            m = re.search(r'slide(\d+)\.xml', s)
            new_name = f"ppt/slides/slide_new_storage_{m.group(1)}.xml"
            zout.writestr(new_name, content1[s])
            rel_path = f"ppt/slides/_rels/{m.group(0)}.rels"
            if rel_path in content1:
                zout.writestr(f"ppt/slides/_rels/slide_new_storage_{m.group(1)}.xml.rels",
                            content1[rel_path])

        # 10. 複製所有共用資源
        # slideLayouts (from src1)
        for sl in sl1:
            if sl not in zout.namelist():
                zout.writestr(sl, content1[sl])
        for sl in sl2:
            name = sl.split('/')[-1]
            if f'ppt/slideLayouts/{name}' not in zout.namelist():
                zout.writestr(f'ppt/slideLayouts/{name}', content2[sl])
        # slideMasters
        for sm in sm1:
            if sm not in zout.namelist():
                zout.writestr(sm, content1[sm])
        for sm in sm2:
            name = sm.split('/')[-1]
            if f'ppt/slideMasters/{name}' not in zout.namelist():
                zout.writestr(f'ppt/slideMasters/{name}', content2[sm])
        # theme
        for f in all_files:
            if f.startswith('ppt/theme/') and f not in zout.namelist():
                src = content1 if f in content1 else content2
                zout.writestr(f, src[f])
        # slideLayout rels
        for f in all_files:
            if re.match(r'ppt/slideLayouts/_rels/.+\.xml\.rels', f) and f not in zout.namelist():
                src = content1 if f in content1 else content2
                zout.writestr(f, src[f])
        # slideMaster rels
        for f in all_files:
            if re.match(r'ppt/slideMasters/_rels/.+\.xml\.rels', f) and f not in zout.namelist():
                src = content1 if f in content1 else content2
                zout.writestr(f, src[f])
        # 所有的media (圖片)
        media_count = 0
        for f in all_files:
            if f.startswith('ppt/media/'):
                if f not in zout.namelist():
                    src = content1 if f in content1 else content2
                    zout.writestr(f, src[f])
                    media_count += 1
        print(f"Media files copied: {media_count}")

        # 確保所有必要文件
        for f in all_files:
            if f not in zout.namelist() and not f.startswith('ppt/slides/'):
                src = content1 if f in content1 else content2
                zout.writestr(f, src[f])

    # 複製到最終路徑
    shutil.copy2(work_pptx, OUTPUT)
    size = os.path.getsize(OUTPUT)
    print(f"\nFile size: {size/1024:.0f} KB ({size/1024/1024:.2f} MB)")
    print(f"Total slides: 1 cover + {len(slides2)} CCS + 1 divider + {len(slides1)} storage + 1 divider = {2 + len(slides2) + len(slides1)}")
    print(f"Output: {OUTPUT}")
    return size


def merge_content_types(ct1_bytes, ct2_bytes):
    """合併兩個[Content_Types].xml"""
    if not ct1_bytes:
        return ct2_bytes
    if not ct2_bytes:
        return ct1_bytes
    tree1 = etree.fromstring(ct1_bytes)
    tree2 = etree.fromstring(ct2_bytes)
    ns = 'http://schemas.openxmlformats.org/package/2006/content-types'
    for override in tree2.findall(f'{{{ns}}}Override'):
        existing = tree1.find(f'{{{ns}}}Override[@PartName="{override.get("PartName")}"]')
        if existing is None:
            tree1.append(override)
    return etree.tostring(tree1, xml_declaration=True, encoding='UTF-8', standalone=True)


if __name__ == '__main__':
    print("=" * 60)
    print("  PPT合并 - ZIP底层合并方式")
    print("=" * 60)
    size = merge_ppts()
    print("\nDone!")
