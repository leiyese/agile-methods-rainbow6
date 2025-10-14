import sys, re
from pathlib import Path
import fitz

PDF_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("./rag_docs/02914-ettsak-villkor-olycksfall-sjuk.pdf")

def extract_pdf_text(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    parts = [page.get_text("text") for page in doc]
    text = "\n".join(parts)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

if __name__ == "__main__":
    text = extract_pdf_text(PDF_PATH)
    out = PDF_PATH.with_suffix(".txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"Saved cleaned text to: {out}  |  Chars: {len(text):,}")
    print("\nPreview:\n", text[:800])
