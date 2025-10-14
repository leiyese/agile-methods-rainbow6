import re

def extract_text(doc: object) -> str:
    parts = [page.get_text("text") for page in doc]
    text = "\n".join(parts)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()