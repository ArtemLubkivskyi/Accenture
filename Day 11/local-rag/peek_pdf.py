"""Print one PDF page as the extractor sees it, in plain and layout mode.

uv run python peek_pdf.py product_guide.pdf 14
"""
import sys
from pathlib import Path

from pypdf import PdfReader

import config

name = sys.argv[1]
page_no = int(sys.argv[2])  # 1-based, like the PDF viewer

page = PdfReader(Path(config.DOCS_DIR) / name).pages[page_no - 1]
for mode in ["plain", "layout"]:
    print(f"===== {name} page {page_no}, mode={mode} =====")
    print(page.extract_text(extraction_mode=mode))
    print()
