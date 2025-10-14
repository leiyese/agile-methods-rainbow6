from pathlib import Path
import fitz

def import_document(pdf_path: Path):
    try: 
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF '{pdf_path}': {e}")
    return doc

def save_text(text, output_path: Path): 
    out = output_path.with_suffix(".txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"Saved cleaned text to: {out}  |  Chars: {len(text):,}")
    print("\nPreview:\n", text[:800])
