from pptx import Presentation
import zipfile, re

# Check the structure of a pic element
src1 = r'd:/claude mini max 2.7/storage_market_output/Global_Storage_Market_2025_2030.pptx'
with zipfile.ZipFile(src1) as z:
    data = z.read('ppt/slides/slide4.xml').decode('utf-8')
    print(data)
