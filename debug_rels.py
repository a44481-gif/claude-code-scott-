import zipfile, re
from lxml import etree

src2 = r'd:/claude mini max 2.7/storage_market_output/CCS_Global_Storage_2025_2030.pptx'

with zipfile.ZipFile(src2) as z:
    files = z.namelist()
    slides = sorted([f for f in files if re.match(r'ppt/slides/slide\d+\.xml$', f)])
    print(f"Total slides: {len(slides)}")
    print(f"Sample slide: {slides[0]}")

    rels_file = slides[0].replace('ppt/slides/', 'ppt/slides/_rels/').replace('.xml', '.xml.rels')
    print(f"Checking rels: {rels_file}")
    print(f"Rels exists: {rels_file in files}")

    rels_data = z.read(rels_file)
    print(f"Rels size: {len(rels_data)} bytes")
    print(f"Rels content:\n{rels_data.decode('utf-8')}")

    # Try different type patterns
    rels_tree = etree.fromstring(rels_data)
    for rel in rels_tree:
        rel_type = rel.get('Type', '')
        rel_id = rel.get('Id')
        target = rel.get('Target')
        print(f"  Rel: Id={rel_id}, Type={rel_type}, Target={target}")
        print(f"    'image' in Type: {'image' in rel_type.lower()}")
