import zipfile, re

src1 = r'd:/claude mini max 2.7/storage_market_output/Global_Storage_Market_2025_2030.pptx'
src2 = r'd:/claude mini max 2.7/storage_market_output/CCS_Global_Storage_2025_2030.pptx'

for name, path in [('Storage', src1), ('CCS', src2)]:
    with zipfile.ZipFile(path) as z:
        files = sorted(z.namelist())
        slides = [f for f in files if re.match(r'ppt/slides/slide\d+\.xml$', f)]
        media = [f for f in files if f.startswith('ppt/media/')]
        slide_rels = [f for f in files if re.match(r'ppt/slides/_rels/slide\d+\.xml\.rels$', f)]
        print(f"\n{name} PPTX:")
        print(f"  Slides: {len(slides)}")
        print(f"  Media: {len(media)}")
        print(f"  Slide rels: {len(slide_rels)}")

        # Check first storage slide's rels
        if name == 'Storage':
            for rel_file in slide_rels[:3]:
                print(f"\n  {rel_file}:")
                data = z.read(rel_file).decode('utf-8')
                print(f"  {data[:500]}")
