"""
Fence Tables Utility

Inserts [TABLE] ... [/TABLE] markers into extracted PDF text
based on table bounding boxes from Camelot manifest.
"""

import json
import re
from pathlib import Path
import fitz  # PyMuPDF

# Adjusted paths for backend layout
BASE_DIR = Path(__file__).resolve().parents[1]  # -> backend/
PDF_PATH = BASE_DIR / "rag_docs" / "02914-ettsak-villkor-olycksfall-sjuk.pdf"
MANIFEST_PATH = BASE_DIR / "rag_docs" / "tables" / "tables_manifest.json"
OUT_PATH = BASE_DIR / "rag_docs" / "02914-ettsak-villkor-olycksfall-sjuk.fenced.txt"

FLAGS = fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fence_page_text(page, page_text: str, tables_for_page: list[dict]) -> tuple[str, int]:
    """Replace table regions on a page with fenced blocks."""
    fenced_count = 0
    text_raw = page_text

    for t in sorted(tables_for_page, key=lambda x: (x.get("bbox") or [0, 0, 0, 0])[1]):
        bbox = t.get("bbox")
        if not bbox:
            continue
        rect = fitz.Rect(*bbox)
        clip_txt = page.get_text("text", flags=FLAGS, clip=rect)
        if not clip_txt.strip():
            rect = fitz.Rect(rect.x0 - 2, rect.y0 - 2, rect.x1 + 2, rect.y1 + 2)
            clip_txt = page.get_text("text", flags=FLAGS, clip=rect)

        if not clip_txt.strip():
            # fallback: insert empty fenced block
            text_raw += f"\n\n[TABLE page={page.number + 1} idx={t['index']} flavor={t['flavor']}]\n[/TABLE]\n"
            fenced_count += 1
            continue

        where = text_raw.find(clip_txt)
        if where >= 0:
            before = text_raw[:where]
            after = text_raw[where + len(clip_txt):]
            text_raw = before + f"\n[TABLE]\n{clip_txt.strip()}\n[/TABLE]\n" + after
            fenced_count += 1
        else:
            # fallback if text can't be located
            text_raw += f"\n\n[TABLE page={page.number + 1} idx={t['index']} flavor={t['flavor']}]\n{clip_txt.strip()}\n[/TABLE]\n"
            fenced_count += 1

    return text_raw, fenced_count


def main():
    manifest = json.loads(Path(MANIFEST_PATH).read_text(encoding="utf-8"))
    pdf_path = PDF_PATH
    doc = fitz.open(pdf_path)
    by_page = {}
    for t in manifest["tables"]:
        p = int(t["page"])
        by_page.setdefault(p, []).append(t)

    all_pages = []
    total_fenced = 0
    for pno in range(1, doc.page_count + 1):
        page = doc.load_page(pno - 1)
        page_text = page.get_text("text", flags=FLAGS)
        tables = by_page.get(pno, [])
        fenced_text, n = fence_page_text(page, page_text, tables)
        total_fenced += n
        all_pages.append(fenced_text.strip())

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n\n==== PAGE BREAK ====\n\n".join(all_pages), encoding="utf-8")
    print(f"[OK] Wrote fenced text → {OUT_PATH}")
    print(f"[OK] Fenced tables: {total_fenced}")


if __name__ == "__main__":
    main()
