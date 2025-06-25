# GenerateArticleSummaries

This Python tool summarizes academic PDF articles using OpenAI's GPT-4.1 model. It supports large files via a two-pass summarization strategy and outputs clean, structured Markdown summaries. Ideal for research, coursework, and knowledge management.

## ✨ Features

- ✅ Summarizes each article into a single `.md` file (even for long PDFs)
- ✅ Two-pass process:
  - Splits large documents into manageable chunks
  - Summarizes each chunk
  - Merges the chunk summaries into a single unified summary
- ✅ Outputs structured Markdown based on your academic prompt
- ✅ Logs any failures (with timestamps) to `summary_failures.log`

---

## 📁 Folder Structure

```
GenerateArticleSummaries/
├── summarizer_two_pass.py
├── .env
├── prompts/
│   └── default_prompt.txt
├── pdfs/                # Input folder for PDFs
├── summaries/           # Output folder for Markdown summaries
├── summary_failures.log # Auto-generated log of failed files
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Install Python dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Create your `.env` file

```env
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4.1
MAX_TOKENS=4096
TEMPERATURE=0.3
```

### 3. Add your prompt

Save your preferred Markdown prompt format in:

```
prompts/default_prompt.txt
```

Include `{{FILENAME}}` as a placeholder that will be replaced automatically.

---

## 🚀 Usage

```bash
python3 summarizer_two_pass.py /path/to/pdf/folder -o /path/to/output/folder
```

Example:

```bash
python3 summarizer_two_pass.py ./pdfs -o ./summaries
```

---

## 🧠 Notes

- Large PDFs are chunked into 20,000-token blocks to stay under API limits
- If any chunk fails, the entire file is skipped
- A unified final summary is generated using a second summarization pass
- All failures are logged in `summary_failures.log` with timestamps and chunk info

---

## 📚 License

MIT License

---

## 🙋‍♂️ Author

Developed by Bassam Islam  
Senior Sales Engineer · UCLA Anderson MBA  
[GitHub Profile](https://github.com/elbaso)
