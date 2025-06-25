import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import tiktoken
from openai import OpenAI
from datetime import datetime

# Load environment config
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.3))

client = OpenAI(api_key=OPENAI_API_KEY)
encoding = tiktoken.get_encoding("cl100k_base")
CHUNK_TOKEN_LIMIT = 20000  # Safe limit to avoid request token caps

def load_prompt():
    with open("prompts/default_prompt.txt", "r", encoding="utf-8") as f:
        return f.read()

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)

def count_tokens(text):
    return len(encoding.encode(text))

def chunk_text(text, max_tokens=CHUNK_TOKEN_LIMIT):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if count_tokens(' '.join(current_chunk)) > max_tokens:
            current_chunk.pop()
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def summarize_text(text, prompt):
    full_prompt = prompt + "\n\n" + text
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return None

def log_failure(pdf_path, chunk_number=None, total_chunks=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reason = f"chunk {chunk_number} of {total_chunks}" if chunk_number else "full document"
    log_line = f"[{timestamp}] Failed to summarize {pdf_path.name} ({reason})\n"
    with open("summary_failures.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_line)

def merge_chunk_summaries(chunk_summaries, pdf_filename):
    merge_prompt = f"""You are given several partial summaries of one academic article. Synthesize them into one unified Markdown summary using the structure below.

Put the article title in Heading level 1.
Put the label Summary in Heading level 2, and add a 2-3 sentence high-level summary.
Put the label Authors in Heading level 2, and format author names like [[@John Smith]].
Put the label Publication Date in Heading level 2.
Put the label File Name in Heading level 2, and insert: `{pdf_filename}`
Put the label Keywords in Heading level 2 using #tag format.
Put the label Overview in Heading level 2.
Put the label Key Concepts in Heading level 2 as 7–10 bullet points.
Put the label My Notes in Heading level 2, and leave it blank.
Add a '---' separator and end with a Heading level 1 labeled 'Article Highlights'.

Here are the partial summaries:
""" + "\n\n".join(chunk_summaries)

    return summarize_text("", merge_prompt)

def process_pdf(pdf_path, output_dir, base_prompt):
    print(f"\n📘 Processing: {pdf_path.name}")
    text = extract_text_from_pdf(pdf_path)
    num_tokens = count_tokens(text)
    print(f"   🔢 Token count: {num_tokens:,} tokens")

    prompt_with_filename = base_prompt.replace("{{FILENAME}}", pdf_path.name)

    if num_tokens > CHUNK_TOKEN_LIMIT:
        print(f"⚠️ Large file. Splitting into {CHUNK_TOKEN_LIMIT}-token chunks.")
        chunks = chunk_text(text)
        chunk_summaries = []

        for i, chunk in enumerate(chunks):
            print(f"   ✂️  Summarizing chunk {i+1} of {len(chunks)}...")
            summary = summarize_text(chunk, prompt_with_filename)
            if summary:
                chunk_summaries.append(summary)
            else:
                print(f"❌ Chunk {i+1} failed. Skipping file.")
                log_failure(pdf_path, chunk_number=i+1, total_chunks=len(chunks))
                return
        print("🔁 Merging chunk summaries into one unified summary...")
        full_summary = merge_chunk_summaries(chunk_summaries, pdf_path.name)
        if not full_summary:
            print("❌ Final merge failed. Skipping file.")
            log_failure(pdf_path)
            return
    else:
        full_summary = summarize_text(text, prompt_with_filename)
        if not full_summary:
            print("❌ Summarization failed. Skipping file.")
            log_failure(pdf_path)
            return

    output_path = output_dir / f"{pdf_path.stem}.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_summary)
    print(f"✅ Summary saved to: {output_path.name}")

def main():
    parser = argparse.ArgumentParser(description="Summarize each PDF into a Markdown file using OpenAI GPT.")
    parser.add_argument("folder", help="Path to the folder containing PDF files")
    parser.add_argument("-o", "--output", default="summaries", help="Output folder for Markdown summaries")
    args = parser.parse_args()

    pdf_folder = Path(args.folder)
    output_folder = Path(args.output)
    output_folder.mkdir(parents=True, exist_ok=True)
    base_prompt = load_prompt()

    for pdf_file in sorted(pdf_folder.glob("*.pdf")):
        process_pdf(pdf_file, output_folder, base_prompt)

if __name__ == "__main__":
    main()
