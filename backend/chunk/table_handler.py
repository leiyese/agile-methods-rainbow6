from pathlib import Path
import json
import camelot

PDF_PATH = Path("rag_docs/02914-ettsak-villkor-olycksfall-sjuk.pdf")
OUT_DIR  = Path("rag_docs/tables")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def run_flavor(flavor: str, pdf_path: str):
    try:
        tbls = camelot.read_pdf(
            str(pdf_path),
            flavor=flavor,      # 'stream' or 'lattice'
            pages="all",
            strip_text="\n",
        )
        return tbls
    except Exception as e:
        print(f"[WARN] {flavor} failed: {e}")
        return None
    
def to_preview_cells(df, max_cols=6):
    cols = list(df.columns[:max_cols])
    # If df.columns are numeric indices, convert to str
    cols = [str(c) for c in cols]
    header = cols
    first = [str(x) for x in df.iloc[0].values[:max_cols]] if len(df) else []
    return {"header": header, "first_row": first}

if __name__ == "__main__":
    manifest = {"pdf": str(PDF_PATH), "tables": []}
    counts = {}

    for flavor in ("stream", "lattice"):
        tables = run_flavor(flavor, PDF_PATH)
        n = tables.n if tables else 0
        counts[flavor] = n
        print(f"[INFO] {flavor}: detected {n} tables")

        if not tables:
            continue

        for i, t in enumerate(tables):
            # robust filename
            page = getattr(t, "page", "unknown")
            csv_path = OUT_DIR / f"page-{page:0>3}_table-{i+1}_{flavor}.csv"
            try:
                t.to_csv(str(csv_path))
            except Exception as e:
                print(f"[WARN] Could not save table {i+1} on page {page}: {e}")
                continue

            # Try to get a bbox if Camelot exposes it (not always public)
            bbox = getattr(t, "_bbox", None)
            df = t.df
            preview = to_preview_cells(df)

            manifest["tables"].append({
                "page": page,
                "index": i + 1,
                "flavor": flavor,
                "csv": str(csv_path),
                "shape": list(df.shape),
                "preview": preview,
                "bbox": bbox if isinstance(bbox, (list, tuple)) else None,
            })

    man_path = OUT_DIR / "tables_manifest.json"
    man_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n[SUMMARY]")
    print(json.dumps(counts, indent=2))
    print(f"[OK] Wrote manifest → {man_path}")