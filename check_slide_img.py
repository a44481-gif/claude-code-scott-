import zipfile, re
from lxml import etree

src1 = r'd:/claude mini max 2.7/storage_market_output/Global_Storage_Market_2025_2030.pptx'

NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'

with zipfile.ZipFile(src1) as z:
    for i in [1, 4, 5]:
        fname = f'ppt/slides/slide{i}.xml'
        print(f"\n=== {fname} ===")
        data = z.read(fname)
        tree = etree.fromstring(data)

        # Find all image references
        for elem in tree.iter():
            # Check for a:blip (image fill)
            if elem.tag.endswith('}blip'):
                embed = elem.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                link = elem.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}link')
                print(f"  blip: embed={embed}, link={link}")

            # Check for pic (picture shape)
            if elem.tag.endswith('}pic'):
                print(f"  pic element found")

        print(f"  Full XML length: {len(data)} bytes")

        # Also check slide rels
        rels_file = f'ppt/slides/_rels/slide{i}.xml.rels'
        rels_data = z.read(rels_file).decode('utf-8')
        print(f"  Rels: {rels_data}")

        # Look for xdr:pic elements with embedded images
        content = data.decode('utf-8')
        # Find embed attributes
        embeds = re.findall(r'embed="([^"]+)"', content)
        links = re.findall(r'link="([^"]+)"', content)
        if embeds:
            print(f"  Embeds: {embeds}")
        if links:
            print(f"  Links: {links}")

        # Check if images are base64 embedded
        if 'image/png' in content or 'base64' in content.lower():
            print(f"  Contains embedded image data!")
