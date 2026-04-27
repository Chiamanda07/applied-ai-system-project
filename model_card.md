# StudyBot Model Card

---

## 1. System Overview

**What is StudyBot trying to do?**

StudyBot is an AI-powered study assistant that lets students upload a PDF of their study material and interact with it in two ways: asking questions and generating a multiple choice quiz. The goal is to turn passive reading into active learning by grounding every response in the student's own uploaded material.

**What inputs does StudyBot take?**

- A PDF file path provided by the user at startup
- A natural language question (Ask mode) or a requested number of quiz questions (Quiz mode)
- A Gemini API key set in the `.env` file

**What outputs does StudyBot produce?**

- A focused answer drawn from retrieved chunks of the PDF (Ask mode)
- A multiple choice quiz with 4 options per question, correct answer tracking, and a final score (Quiz mode)

---

## 2. Retrieval Design

**How does the retrieval system work?**

- **Indexing:** The PDF text is split into ~1,000 character chunks using paragraph breaks. An inverted keyword index maps each token to the list of chunk positions where it appears.
- **Scoring:** Each candidate chunk is scored by counting how many query words appear in it.
- **Selection:** The top 3 highest-scoring chunks are returned as context for Gemini.

**What tradeoffs did you make?**

Keyword retrieval is fast and requires no external APIs or vector databases, but it misses paraphrased questions — if the student asks something in different words than the source material uses, relevant chunks may not be retrieved. Semantic embeddings would improve this but add significant cost and complexity. The 1,000 character chunk size balances retrieval precision against context richness; smaller chunks improve precision but lose surrounding context.

---

## 3. Use of the LLM (Gemini)

**When does StudyBot call Gemini and when does it not?**

- **Ask mode:** Gemini is called once per question, receiving the top 3 retrieved chunks as context. The retrieval step (keyword index search) does not use Gemini.
- **Quiz mode:** Gemini is called once per session, receiving the first 8,000 characters of the PDF and returning a JSON array of multiple choice questions.

**What instructions do you give the LLM to keep it grounded?**

For Ask mode, the prompt instructs Gemini to answer using only the provided excerpts, not to add outside knowledge, and to reply with a specific fallback message if the excerpts are insufficient. For Quiz mode, the prompt requires a strict JSON format, exactly 4 options per question labeled A–D, and instructs Gemini to test understanding of key concepts rather than surface definitions.

---

## 4. Experiments and Comparisons

StudyBot replaces the original three DocuBot modes with two study-focused modes. The table below reflects observations from testing Ask mode (RAG) against the kind of questions a student would actually ask.

| Query | RAG: helpful or not? | Notes |
|-------|----------------------|-------|
| What is the main topic of this chapter? | Helpful | Retrieves relevant intro chunks accurately |
| What are the differences between X and Y? | Partially helpful | Depends on whether both concepts appear in the same chunk |
| Define [term not in the PDF] | Safe refusal | Returns fallback message correctly |
| Vague question with no keywords | Not helpful | Keyword index finds no candidates; returns fallback |

**What patterns did you notice?**

RAG works best when the question uses words that appear in the material. Vague or paraphrased questions expose the weakness of keyword retrieval — the index finds nothing and Gemini correctly refuses rather than guessing. Quiz mode performs better on dense, concept-rich material than on PDFs with mostly diagrams or tables.

---

## 5. Failure Cases and Guardrails

**Failure case 1: Scanned/image-based PDF**
- Question: User uploads a scanned textbook page
- What happened: `pdfplumber` extracted no text; the bot loaded silently with no content and returned fallback messages for every question
- What should happen: Immediate error message at startup — now fixed with a `ValueError` if extracted text is empty

**Failure case 2: Gemini returns malformed JSON for quiz**
- Question: Generate 5 quiz questions
- What happened: Gemini wrapped the JSON array in markdown code fences (` ```json ... ``` `), causing `json.loads` to throw an exception
- What should happen: Strip code fences before parsing — now fixed with regex preprocessing

**When should StudyBot say it doesn't know?**

- When no chunks are retrieved because the question keywords don't match anything in the PDF
- When the retrieved chunks exist but don't contain enough information to answer confidently

**What guardrails are implemented?**

- Rejects non-PDF files and missing paths at startup
- Raises a clear error if the PDF has no extractable text
- Caps quiz context at 8,000 characters to avoid token limit errors
- Wraps quiz JSON parsing in try/except to prevent crashes on malformed responses
- Prompts the user to re-enter if their quiz answer is not A, B, C, or D
- Warns and disables LLM modes if `GEMINI_API_KEY` is missing

---

## 6. Limitations and Future Improvements

**Current limitations**

1. Keyword retrieval misses paraphrased questions — if the student's wording differs from the PDF's wording, relevant chunks are not found
2. Quiz generation only uses the first 8,000 characters, so content from later pages is never tested
3. No memory between questions — each Ask query is independent with no conversation history
4. Quality depends entirely on the PDF; poorly formatted or scanned documents produce poor results

**Future improvements**

1. Replace keyword retrieval with semantic embeddings (e.g. sentence-transformers) for better handling of paraphrased questions
2. Expand quiz context by sampling chunks from across the whole document rather than just the first 8,000 characters
3. Add conversation memory so follow-up questions can reference previous answers

---

## 7. Responsible Use

**Where could this system cause real-world harm if used carelessly?**

StudyBot answers only from the provided material, which limits hallucination risk but introduces a new one: if the uploaded PDF contains incorrect or biased information, StudyBot will reflect it without warning. Additionally, the system could be misused to generate quiz questions from exam papers or copyrighted textbooks, facilitating academic dishonesty rather than genuine learning.

**Guidelines for safe use**

- Always verify important answers against the original source — StudyBot is a study aid, not an authority
- Only upload materials you own or have permission to use
- Do not rely on StudyBot for high-stakes decisions; treat its answers as a starting point for further review
- Be aware that scanned or image-heavy PDFs will produce no output — use text-based PDFs only
