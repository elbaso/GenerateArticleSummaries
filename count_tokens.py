import os
import argparse
from pathlib import Path
from PyPDF2 import PdfReader
import tiktoken

# Use GPT-4-compatible tokenizer
encoding = tiktoken.encoding_for_model("gpt-4")

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)

def count_tokens(text):
    return len(encoding.encode(text))

def main(pdf_folder):
    pdf_dir = Path(pdf_folder)
    if not pdf_dir.exists() or not pdf_dir.is_dir():
        print(f"❌ Folder not found: {pdf_dir}")
        return

    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print("📂 No PDF files found in the specified folder.")
        return

    total_tokens = 0

    for pdf in pdf_files:
        text = extract_text(pdf)
        tokens = count_tokens(text)
        total_tokens += tokens
        print(f"{tokens:,} tokens - {pdf.name}")

    print("\n🧮 Total tokens across all PDFs:", f"{total_tokens:,}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count tokens in PDF files using GPT-4 tokenizer.")
    parser.add_argument(
        "folder",
        nargs="?",
        default="pdfs",
        help="Path to the folder containing PDF files (default: ./pdfs)"
    )
    args = parser.parse_args()
    main(args.folder)