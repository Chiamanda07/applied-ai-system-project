"""
Core StudyBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob
import re

class StudyBot:
    # Minimum number of query words that must appear in a chunk before it
    # is considered meaningful evidence. Applied only when the query has
    # more than two tokens; shorter queries use a threshold of 1.
    _MIN_EVIDENCE_SCORE = 2

    def __init__(self, docs_folder="docs", pdf_path=None, llm_client=None):
        """
        docs_folder: directory containing .md/.txt files (used when pdf_path is None)
        pdf_path:    path to a single PDF study file (takes priority over docs_folder)
        llm_client:  optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.pdf_path = pdf_path
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()  # List of (filename, full_text)

        # Split documents into chunks for retrieval
        self.chunks = self._chunk_documents(self.documents)  # List of (filename, chunk_text)

        # Build a retrieval index over chunks
        self.index = self.build_index(self.chunks)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        If pdf_path is set, returns an empty list (PDF extraction handled in next step).
        Otherwise loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)
        """
        if self.pdf_path is not None:
            return []

        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                docs.append((filename, text))
        return docs

    # -----------------------------------------------------------
    # Chunking
    # -----------------------------------------------------------

    def _chunk_documents(self, documents):
        """
        Split each document into sections at markdown headers (## or ###).
        Returns a list of (filename, chunk_text) tuples — one per section.
        """
        chunks = []
        for filename, text in documents:
            sections = re.split(r'\n(?=#{1,3} )', text)
            for section in sections:
                section = section.strip()
                if len(section) > 20:
                    chunks.append((filename, section))
        return chunks

    # -----------------------------------------------------------
    # Index Construction (Phase 1)
    # -----------------------------------------------------------

    def build_index(self, chunks):
        """
        Build an inverted index mapping lowercase tokens to the list of
        chunk positions (integer indices into self.chunks) where they appear.

        Using positions instead of filenames allows multiple chunks from the
        same file to be indexed and retrieved independently.
        """
        index = {}
        for i, (_, text) in enumerate(chunks):
            for word in text.lower().split():
                token = word.strip(".,!?;:\"'()[]{}-")
                if token:
                    if token not in index:
                        index[token] = []
                    if i not in index[token]:
                        index[token].append(i)
        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval (Phase 1)
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        TODO (Phase 1):
        Return a simple relevance score for how well the text matches the query.

        Suggested baseline:
        - Convert query into lowercase words
        - Count how many appear in the text
        - Return the count as the score
        """
        text_lower = text.lower()
        score = 0
        for word in query.lower().split():
            token = word.strip(".,!?;:\"'()[]{}-")
            if token and token in text_lower:
                score += 1
        return score

    def _has_sufficient_evidence(self, score, query_tokens):
        """
        Returns True if the score represents meaningful evidence for the query.

        Short queries (1-2 tokens) need score >= 1: even a single match covers
        half or more of the query. Longer queries require _MIN_EVIDENCE_SCORE
        matches so that a single coincidental common word cannot pass the filter.
        """
        if not query_tokens:
            return False
        threshold = 1 if len(query_tokens) <= 2 else self._MIN_EVIDENCE_SCORE
        return score >= threshold

    def retrieve(self, query, top_k=3):
        """
        TODO (Phase 1):
        Use the index and scoring function to select top_k relevant document snippets.

        Return a list of (filename, text) sorted by score descending.
        """
        # Find candidate chunk indices using the index
        candidate_indices = set()
        for word in query.lower().split():
            token = word.strip(".,!?;:\"'()[]{}-")
            if token in self.index:
                for idx in self.index[token]:
                    candidate_indices.add(idx)

        # Score each candidate chunk; discard those without sufficient evidence
        query_tokens = [w.strip(".,!?;:\"'()[]{}-") for w in query.lower().split()]
        query_tokens = [t for t in query_tokens if t]

        scored = []
        for idx in candidate_indices:
            filename, text = self.chunks[idx]
            score = self.score_document(query, text)
            if self._has_sufficient_evidence(score, query_tokens):
                scored.append((score, filename, text))

        # Sort by score descending and return (filename, text) tuples
        scored.sort(key=lambda x: x[0], reverse=True)
        return [(filename, text) for _, filename, text in scored][:top_k]

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3):
        """
        Phase 1 retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        formatted = []
        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        Phase 2 RAG mode.
        Uses student retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        return self.llm_client.answer_from_snippets(query, snippets)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive 'generation only' baselines.
        """
        return "\n\n".join(text for _, text in self.documents)
