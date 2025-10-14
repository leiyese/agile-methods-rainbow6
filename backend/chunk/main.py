from pathlib import Path
import sys
from utils import import_document, save_text
from pdf_text_extractor import extract_text

PDF_PATH = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else Path("./rag_docs/02914-ettsak-villkor-olycksfall-sjuk.pdf")
)


def main():
    doc = import_document(PDF_PATH)
    text = extract_text(doc)
    save_text(text=text, output_path=PDF_PATH)
    return doc


if __name__ == "__main__":
    main()
