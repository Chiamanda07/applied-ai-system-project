# StudyBot

## Original Project: [DocuBot](https://github.com/Chiamanda07/ai110-docubot-starter)

This project was originally built as **DocuBot**, a developer documentation assistant created during Modules 1–3. DocuBot answered questions about a codebase by loading markdown files from a `docs/` folder and supporting three modes: naive LLM generation, keyword-based retrieval only, and Retrieval Augmented Generation (RAG). It was designed to help developers quickly find answers across technical documentation without reading through every file manually.

---

## Title and Summary

**StudyBot** is an AI-powered study assistant that lets students upload any PDF and interact with it in two ways:

1. **Ask a question** — get a focused answer drawn directly from your material
2. **Generate a quiz** — receive multiple choice questions to test your understanding

StudyBot matters because reading is passive. Asking questions and taking quizzes are active learning strategies that improve retention. By combining PDF text extraction, keyword retrieval, and Gemini's language understanding, StudyBot turns any document into an interactive study session.

---

## Architecture Overview

![System Diagram](assets/system_design.png)

StudyBot is built around a **RAG (Retrieval Augmented Generation)** pipeline:

1. **PDF Loader** — `pdfplumber` extracts raw text from each page of the uploaded PDF
2. **Chunker** — text is split into ~1,000 character chunks using paragraph breaks, so no single piece overwhelms the LLM
3. **Index Builder** — an inverted keyword index is built over all chunks and stored in memory
4. **Retriever** — when the user asks a question, the top 3 most relevant chunks are retrieved from the index
5. **Gemini (RAG)** — the retrieved chunks and the question are sent to Gemini, which answers using only that context
6. **Gemini (Quiz)** — the first 8,000 characters of the PDF are sent to Gemini, which returns a JSON array of multiple choice questions
7. **Quiz Loop** — each question is displayed to the user, their answer is collected, and a final score is shown

Human interaction happens at three points: uploading the PDF, asking questions, and answering quiz questions. Unit tests (pytest) verify that the PDF path is correctly stored on the bot instance.

---

## Setup Instructions

### 1. Clone the repository

```
git clone https://github.com/Chiamanda07/applied-ai-system-project
cd applied-ai-system-project
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Add your Gemini API key

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

Get a free key at [aistudio.google.com](https://aistudio.google.com) → **Get API key**.

### 4. Run StudyBot

```
python main.py
```

You will be prompted to enter the path to a PDF file (under 50 pages recommended), then choose a mode.

### 5. Run the tests (optional)

```
python -m pytest tests/ -v
```

---

## Sample Interactions

### Ask a Question

```
PDF path: C:\Users\karen\notes\biology_ch3.pdf

Loaded: biology_ch3.pdf

Choose a mode:
  1) Ask a question
  2) Generate quiz
  q) Quit
Enter choice: 1

Ask a question about your material: What is the role of mitochondria?

Answer:
According to the material, mitochondria are responsible for producing ATP
through cellular respiration. They are often called the "powerhouse of the
cell" because they generate most of the cell's energy supply.
```

### Generate a Quiz

```
Enter choice: 2

How many questions? (press Enter for 5):

Generating 5 questions from your material...

============================================================
Question 1 of 5: What process do mitochondria use to produce ATP?

  A) Photosynthesis
  B) Cellular respiration
  C) Fermentation
  D) Osmosis

Your answer (A/B/C/D): B
Correct!

============================================================
Question 2 of 5: Where is DNA stored in a eukaryotic cell?

  A) Mitochondria
  B) Ribosome
  C) Nucleus
  D) Vacuole

Your answer (A/B/C/D): C
Correct!

============================================================
Quiz complete! You scored 2/2.
```

### Invalid PDF (scanned/image-based)

```
PDF path: C:\Users\karen\notes\scanned_textbook.pdf

Error: No text could be extracted from 'scanned_textbook.pdf'. This usually
means the PDF is scanned or image-based. Try a PDF with a real text layer.
```

---

## Design Decisions

**Why RAG instead of sending the full PDF to Gemini?**
Sending an entire textbook to an LLM would be slow, expensive, and likely exceed token limits. RAG retrieves only the 3 most relevant chunks per question, keeping prompts small and answers grounded in the actual material.

**Why keyword retrieval instead of embeddings?**
A simple inverted keyword index requires no external API, no vector database, and no additional cost. For a study bot working on focused academic material, keyword matching is fast and effective enough. Semantic embeddings would improve results on paraphrased questions but add significant complexity.

**Why cap chunks at 1,000 characters?**
Large chunks hurt retrieval precision (a chunk matching on one word but containing irrelevant content scores well) and risk hitting Gemini's prompt token limit when multiple chunks are combined. 1,000 characters balances context size with retrieval accuracy.

**Why cap quiz context at 8,000 characters?**
Quiz generation sends content directly without retrieval, so a hard cap prevents token limit errors on long PDFs. 8,000 characters covers roughly 5–8 pages, enough for meaningful question generation.

---

## Testing Summary

**What worked:**
- PDF extraction with `pdfplumber` worked reliably on standard text-based PDFs
- The quiz JSON parsing was robust after adding regex to strip Gemini's markdown code fences
- Input validation (PDF path, answer re-entry) caught edge cases cleanly

**What didn't work initially:**
- Chunking by markdown headers (`##`) produced one giant chunk on PDFs since they have no headers — fixed by falling back to paragraph splitting
- Paths with spaces failed when users pasted them with surrounding quotes — fixed by stripping quotes from input
- Gemini occasionally wrapped JSON responses in code fences, breaking `json.loads` — fixed with regex preprocessing

**What I learned:**
- LLM outputs need defensive parsing. Even well-prompted models add unexpected formatting
- Retrieval quality depends heavily on chunk size; too large and precision drops, too small and context is lost
- Guardrails need to be designed upfront, not added after; silent failures (empty PDF, no API key) are harder to debug than loud ones

---

## Reflection

Building StudyBot taught me that AI applications are less about the model and more about the **pipeline around it**. Gemini is powerful, but without good chunking, retrieval, and prompt design, it either hallucinates or fails to use the provided material at all.

StudyBot is a tool, so depending on who is using it, it could be misused. It could be used to generate quiz questions from exam papers or copyrighted textbooks, effectively helping students cheat rather than learn. A future safeguard could be limiting the bot to materials the user explicitly marks as their own notes rather than published works.

Collaborating with AI during this project was genuinely useful but required critical judgment. One helpful suggestion was using `pdfplumber` for PDF extraction and switching from markdown header splitting to paragraph-based chunking for PDF text. One suggestion that was flawed was the initial quiz prompt design: the AI suggested asking Gemini to "generate questions from the document," which produced vague, surface-level questions. It took several prompt iterations, adding explicit instructions to test understanding rather than definitions, and requiring strict JSON formatting to get reliable, useful output.

---

## Requirements

- Python 3.9+
- A Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))
- No database or server setup required

---

## Changes

Steps taken to convert DocuBot into StudyBot:

- [x] Rename the project from DocuBot to StudyBot and update references across all files
- [x] Add `pdfplumber` to `requirements.txt` for PDF text extraction
- [x] Update `main.py` to accept a PDF file path as input at startup instead of loading from `docs/`
- [x] Update `studybot.py` to extract and chunk text from the uploaded PDF using `pdfplumber` instead of reading a folder of docs
- [x] Replace the three existing modes with two new modes: **Ask a question** and **Generate quiz**
- [x] In Ask mode, use the existing RAG pipeline to answer questions about the uploaded study material
- [x] In Quiz mode, prompt Gemini to generate multiple choice questions (with 4 options and a correct answer) from the retrieved content
- [x] Add a quiz loop in `main.py` that displays each question, collects the user's answer, and shows whether it was correct
- [x] Update `dataset.py` to replace dev-focused sample queries with generic study-style sample questions
- [x] Update `llm_client.py` with a new prompt template for quiz generation (separate from the Q&A prompt)
- [x] Update the README to reflect the new name, modes, and usage instructions

---

## Guardrails

### Already in place
- [x] Rejects non-PDF files or missing file paths at startup
- [x] Warns and disables LLM modes if `GEMINI_API_KEY` is missing
- [x] Returns a safe fallback message if no relevant snippets are retrieved
- [x] Wraps quiz JSON parsing in a try/except so a bad response doesn't crash the app
- [x] Caps PDF context at 8,000 characters before sending to Gemini
- [x] Warn the user immediately if the PDF has no extractable text (e.g. scanned/image-only PDF)
- [x] Prompt the user to re-enter their answer if they type something other than A, B, C, or D
- [x] Handle the case where Gemini returns fewer questions than requested.
