# DocuBot

DocuBot is a small documentation assistant that helps answer developer questions about a codebase.  
It can operate in three different modes:

1. **Naive LLM mode**  
   Sends the entire documentation corpus to a Gemini model and asks it to answer the question.

2. **Retrieval only mode**  
   Uses a simple indexing and scoring system to retrieve relevant snippets without calling an LLM.

3. **RAG mode (Retrieval Augmented Generation)**  
   Retrieves relevant snippets, then asks Gemini to answer using only those snippets.

The docs folder contains realistic developer documents (API reference, authentication notes, database notes), but these files are **just text**. They support retrieval experiments and do not require students to set up any backend systems.

---

## Setup

### 1. Install Python dependencies

    pip install -r requirements.txt

### 2. Configure environment variables

Copy the example file:

    cp .env.example .env

Then edit `.env` to include your Gemini API key:

    GEMINI_API_KEY=your_api_key_here

If you do not set a Gemini key, you can still run retrieval only mode.

---

## Running DocuBot

Start the program:

    python main.py

Choose a mode:

- **1**: Naive LLM (Gemini reads the full docs)  
- **2**: Retrieval only (no LLM)  
- **3**: RAG (retrieval + Gemini)

You can use built in sample queries or type your own.

---

## Running Retrieval Evaluation (optional)

    python evaluation.py

This prints simple retrieval hit rates for sample queries.

---

## Modifying the Project

You will primarily work in:

- `docubot.py`  
  Implement or improve the retrieval index, scoring, and snippet selection.

- `llm_client.py`  
  Adjust the prompts and behavior of LLM responses.

- `dataset.py`  
  Add or change sample queries for testing.

---

## Requirements

- Python 3.9+
- A Gemini API key for LLM features (only needed for modes 1 and 3)
- No database, no server setup, no external services besides LLM calls

---

## Changes

Steps to convert DocuBot into a study bot that accepts user-uploaded study materials (PDF) and supports Q&A and quiz modes.

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
- [ ] Update the README to reflect the new name, modes, and usage instructions

---

## Guardrails

### Already in place
- [x] Rejects non-PDF files or missing file paths at startup
- [x] Warns and disables LLM modes if `GEMINI_API_KEY` is missing
- [x] Returns a safe fallback message if no relevant snippets are retrieved
- [x] Wraps quiz JSON parsing in a try/except so a bad response doesn't crash the app
- [x] Caps PDF context at 8,000 characters before sending to Gemini

### Gaps to fix
- [x] Warn the user immediately if the PDF has no extractable text (e.g. scanned/image-only PDF)
- [x] Prompt the user to re-enter their answer if they type something other than A, B, C, or D
- [x] Handle the case where Gemini returns fewer questions than requested
