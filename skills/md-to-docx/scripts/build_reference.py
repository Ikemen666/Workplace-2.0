"""
Build (or rebuild) the pandoc reference.docx used by convert.sh.

Output: <skill>/assets/reference.docx (or a path passed as argv[1])

Default style choices (good for briefings, memos, reports, research docs):
- Font: Aptos Display (covers ascii + east-asia)
- Body: 12pt, line spacing 1.0, pure black
- Title: 16pt bold centered
- Subtitle: 13pt italic centered
- Heading 1 / 2 / 3: 14 / 13 / 12 pt bold black, tight space-before/after
- Block quote (Block Text): 12pt italic, indented 0.4in
- Footnote text: 10pt
- Compact (pandoc's tight-list style): space_after=2pt for clean bullet rhythm

Tweak the constants and tune() calls below for a different house style.
"""

import os
import subprocess
import sys
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

FONT = 'Aptos Display'
BLACK = RGBColor(0, 0, 0)

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(SKILL_DIR, 'assets', 'reference.docx')


def fetch_pandoc_default():
    """Run pandoc to produce its built-in default reference.docx in a temp file."""
    tmp = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
    tmp.close()
    subprocess.run(
        ['pandoc', '-o', tmp.name, '--print-default-data-file=reference.docx'],
        check=True,
    )
    return tmp.name


def set_font(style, font_name=FONT):
    style.font.name = font_name
    style.font.color.rgb = BLACK
    rPr = style._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rFonts.set(qn('w:eastAsia'), font_name)


def tune(doc, style_name, *, size=None, bold=None, italic=None,
         line_spacing=1.0, space_before=0, space_after=4,
         alignment=None, left_indent=None):
    try:
        s = doc.styles[style_name]
    except KeyError:
        return
    set_font(s)
    if size is not None:
        s.font.size = Pt(size)
    if bold is not None:
        s.font.bold = bold
    if italic is not None:
        s.font.italic = italic
    pf = s.paragraph_format
    pf.line_spacing = line_spacing
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    if alignment is not None:
        pf.alignment = alignment
    if left_indent is not None:
        pf.left_indent = left_indent


def build(out_path):
    default_ref = fetch_pandoc_default()
    doc = Document(default_ref)

    # Body styles — Aptos Display 12pt, tight rhythm
    tune(doc, 'Normal',          size=12, space_after=4)
    tune(doc, 'Body Text',       size=12, space_after=4)
    tune(doc, 'First Paragraph', size=12, space_after=4)
    tune(doc, 'Compact',         size=12, space_before=0, space_after=2)

    # Title block
    tune(doc, 'Title',    size=16, bold=True,
         alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
    tune(doc, 'Subtitle', size=13, italic=True,
         alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    tune(doc, 'Author',   size=12)
    tune(doc, 'Date',     size=12, italic=True)

    # Headings
    tune(doc, 'Heading 1', size=14, bold=True, space_before=18, space_after=6)
    tune(doc, 'Heading 2', size=13, bold=True, space_before=12, space_after=4)
    tune(doc, 'Heading 3', size=12, bold=True, space_before=8,  space_after=2)
    tune(doc, 'Heading 4', size=12, bold=True, space_before=6,  space_after=2)
    tune(doc, 'Heading 5', size=12, bold=True, italic=True,
         space_before=4, space_after=2)
    tune(doc, 'Heading 6', size=12, italic=True)

    # Block quote and special
    tune(doc, 'Block Text', size=12, italic=True,
         left_indent=Inches(0.4), space_before=4, space_after=4)

    # Footnotes — slightly smaller, still legible
    tune(doc, 'Footnote Text',       size=10, space_after=2)
    tune(doc, 'Footnote Block Text', size=10, space_after=2)

    # Captions
    tune(doc, 'Caption',       size=11, italic=True, space_after=4)
    tune(doc, 'Table Caption', size=11, italic=True, space_after=4)

    # Bibliography
    tune(doc, 'Bibliography', size=11, space_after=2)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc.save(out_path)
    os.unlink(default_ref)
    print(f'✅  Reference docx saved to {out_path}')


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    build(out)
