import zipfile, re
from lxml import etree
from pptx import Presentation

merged = r'd:/claude mini max 2.7/storage_market_output/CCS_Global_MERGED_v6.pptx'

with zipfile.ZipFile(merged) as z:
    files = sorted(z.namelist())
    slides = [f for f in files if re.match(r'ppt/slides/slide\d+\.xml$', f)]
    media = [f for f in files if f.startswith('ppt/media/')]
    print(f"Total slides in merged: {len(slides)}")
    print(f"Total media in merged: {len(media)}")
    print(f"Media files: {media}")

    # Check slide 23 (first storage slide)
    s = 'ppt/slides/slide23.xml'
    if s in files:
        data = z.read(s).decode('utf-8')
        print(f"\nSlide 23 has image refs: {'embed=' in data}")
        if 'embed=' in data:
            embeds = re.findall(r'embed="([^"]+)"', data)
            print(f"  Embeds: {embeds}")

    # Check if slide rels for slide23 exist
    rels = 'ppt/slides/_rels/slide23.xml.rels'
    if rels in files:
        rels_data = z.read(rels).decode('utf-8')
        print(f"\nSlide 23 rels: {rels_data}")
    else:
        print(f"\nSlide 23 rels: NOT FOUND")
