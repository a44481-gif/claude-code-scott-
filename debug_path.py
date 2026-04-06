import zipfile, re, os
from lxml import etree

src2 = r'd:/claude mini max 2.7/storage_market_output/CCS_Global_Storage_2025_2030.pptx'

with zipfile.ZipFile(src2) as z:
    files = z.namelist()
    slides = sorted([f for f in files if re.match(r'ppt/slides/slide\d+\.xml$', f)])

    slide_file = slides[0]
    slide_dir = '/'.join(slide_file.split('/')[:-1])  # ppt/slides
    slide_num = re.search(r'slide(\d+)\.xml', slide_file).group(1)
    rels_file = f'ppt/slides/_rels/slide{slide_num}.xml.rels'

    print(f"slide_file: {slide_file}")
    print(f"slide_dir: {slide_dir}")
    print(f"rels_file: {rels_file}")
    print(f"rels exists: {rels_file in files}")

    rels_data = z.read(rels_file)
    rels_tree = etree.fromstring(rels_data)
    for rel in rels_tree:
        rel_type = rel.get('Type', '')
        rel_id = rel.get('Id')
        target = rel.get('Target', '')
        if 'image' in rel_type.lower():
            # Simulate path resolution
            img_path = target
            if target.startswith('../'):
                parts = target.split('/')
                slide_parts = slide_dir.split('/')
                for p in parts:
                    if p == '..':
                        if slide_parts:
                            slide_parts.pop()
                    elif p and p != '.':
                        slide_parts.append(p)
                img_path = '/'.join(slide_parts)
            print(f"  image: {rel_id} -> target={target} -> img_path={img_path}")
            print(f"  img_path in files: {img_path in files}")
