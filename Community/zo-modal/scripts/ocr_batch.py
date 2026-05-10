#!/usr/bin/env python3
"""Modal GPU-accelerated OCR — process scanned PDFs via Tesseract.

Usage:
    python3 ocr_batch.py --dir /path/to/pdf/dropzone
    python3 ocr_batch.py --pdf /path/to/scanned.pdf
    python3 ocr_batch.py --warm  # pre-warm OCR container (no processing)
"""
import modal, os, sys, json, argparse
from pathlib import Path

def build_ocr_image():
    return (
        modal.Image.debian_slim()
        .apt_install("tesseract-ocr", "ghostscript", "libpoppler-cpp-dev")
        .pip_install("pytesseract", "pdf2image", "pillow")
    )

def main():
    parser = argparse.ArgumentParser(description="Modal GPU OCR")
    parser.add_argument("--dir", default="", help="Directory of PDFs to process")
    parser.add_argument("--pdf", default="", help="Single PDF to process")
    parser.add_argument("--max-pages", default=5, type=int, help="Max pages per PDF")
    parser.add_argument("--warm", action="store_true", help="Warm container only")
    parser.add_argument("--output", default="/home/workspace/ocr_results.json", help="Output path")
    args = parser.parse_args()

    app = modal.App("zo-ocr")

    @app.function(image=build_ocr_image(), gpu="T4", timeout=600,
                  retries=modal.Retries(max_retries=2), cpu=2.0)
    def ocr_process(pdf_paths: list) -> dict:
        import pytesseract
        from pdf2image import convert_from_path

        results = {}
        for pdf_path in pdf_paths:
            try:
                if not os.path.exists(pdf_path):
                    results[os.path.basename(pdf_path)] = {"status": "not_found"}
                    continue
                images = convert_from_path(pdf_path, dpi=300,
                    first_page=1, last_page=args.max_pages)
                text = ""
                for img in images:
                    text += pytesseract.image_to_string(img, lang='eng') + "\n"
                results[os.path.basename(pdf_path)] = {
                    "status": "success",
                    "text": text[:5000],
                    "pages": len(images)
                }
            except Exception as e:
                results[os.path.basename(pdf_path)] = {"status": "failed", "error": str(e)[:200]}
        return {"results": results, "total": len(pdf_paths)}

    if args.warm:
        print("Warming OCR container...")
        ocr_process.remote(["/nonexistent.pdf"])
        print("Warm complete.")
        return

    pdfs = []
    if args.pdf:
        if not os.path.exists(args.pdf):
            print(f"ERROR: {args.pdf} not found")
            sys.exit(1)
        pdfs = [os.path.abspath(args.pdf)]
    elif args.dir:
        p = Path(args.dir)
        if not p.exists():
            print(f"ERROR: {args.dir} not found")
            sys.exit(1)
        pdfs = [str(f) for f in p.glob("*.pdf")[:20]]
        if not pdfs:
            print(f"No PDFs found in {args.dir}")
            return
    else:
        print("Specify --dir or --pdf")
        sys.exit(1)

    print(f"Processing {len(pdfs)} PDFs on Modal T4 GPU...")
    result = ocr_process.remote(pdfs)
    
    success = sum(1 for v in result["results"].values() if v.get("status") == "success")
    print(f"Done: {success}/{result['total']} successful")

    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Results: {args.output}")

if __name__ == "__main__":
    main()
