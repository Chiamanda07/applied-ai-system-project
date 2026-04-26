"""
CLI runner for StudyBot.

Supports two modes:
1. Ask a question — answers using the RAG pipeline over your study material
2. Generate quiz  — Gemini creates multiple choice questions from your material
"""

import os

from dotenv import load_dotenv
load_dotenv()

from studybot import StudyBot
from llm_client import GeminiClient


def get_pdf_path():
    """
    Prompts the user for a PDF file path and validates it exists.
    Loops until a valid path is entered.
    """
    print("Enter the path to your PDF study material.")
    print("Tip: For best results keep the PDF under 50 pages (~150,000 characters).")
    print("Longer files may slow down loading and reduce answer quality.\n")
    while True:
        path = input("PDF path: ").strip().strip('"').strip("'")
        if not path.lower().endswith(".pdf"):
            print("File must be a .pdf. Try again.\n")
            continue
        if not os.path.isfile(path):
            print(f"File not found: {path}. Try again.\n")
            continue
        return path


def try_create_llm_client():
    """
    Tries to create a GeminiClient.
    Returns (llm_client, has_llm: bool).
    """
    try:
        client = GeminiClient()
        return client, True
    except RuntimeError as exc:
        print("Warning: LLM features are disabled.")
        print(f"Reason: {exc}")
        print("A GEMINI_API_KEY is required for both modes.\n")
        return None, False


def choose_mode(has_llm):
    """
    Asks the user which mode to run.
    Returns "1", "2", or "q".
    """
    print("Choose a mode:")
    if has_llm:
        print("  1) Ask a question")
        print("  2) Generate quiz")
    else:
        print("  1) Ask a question  (unavailable — no GEMINI_API_KEY)")
        print("  2) Generate quiz   (unavailable — no GEMINI_API_KEY)")
    print("  q) Quit")

    choice = input("Enter choice: ").strip().lower()
    return choice


def run_ask_mode(bot, has_llm):
    """
    Mode 1: user types a question, StudyBot answers using the RAG pipeline.
    """
    if not has_llm or bot.llm_client is None:
        print("\nAsk mode requires a GEMINI_API_KEY.\n")
        return

    question = input("\nAsk a question about your material: ").strip()
    if not question:
        print("No question entered.\n")
        return

    print()
    print("=" * 60)
    answer = bot.answer_rag(question)
    print("Answer:")
    print(answer)
    print()


def run_quiz_mode(bot, has_llm):
    """
    Mode 2: Gemini generates multiple choice questions, user answers each one,
    and a final score is shown at the end.
    """
    if not has_llm or bot.llm_client is None:
        print("\nQuiz mode requires a GEMINI_API_KEY.\n")
        return

    try:
        num = input("\nHow many questions? (press Enter for 5): ").strip()
        num_questions = int(num) if num.isdigit() and int(num) > 0 else 5
    except ValueError:
        num_questions = 5

    print(f"\nGenerating {num_questions} questions from your material...\n")

    # Cap context at 8000 chars to stay within Gemini's prompt limits
    context = bot.full_corpus_text()[:8000]

    try:
        questions = bot.llm_client.generate_quiz(context, num_questions)
    except Exception as e:
        print(f"Failed to generate quiz: {e}\n")
        return

    if not questions:
        print("No questions were generated. Try a different PDF.\n")
        return

    if len(questions) < num_questions:
        print(f"Note: only {len(questions)} question(s) could be generated from this material (you requested {num_questions}).\n")

    score = 0
    for i, q in enumerate(questions, 1):
        print("=" * 60)
        print(f"Question {i} of {len(questions)}: {q['question']}\n")
        for letter, option_text in q["options"].items():
            print(f"  {letter}) {option_text}")

        while True:
            answer = input("\nYour answer (A/B/C/D): ").strip().upper()
            if answer in ("A", "B", "C", "D"):
                break
            print("Invalid input. Please enter A, B, C, or D.")
        correct = q["answer"].upper()

        if answer == correct:
            print("Correct!\n")
            score += 1
        else:
            print(f"Incorrect. The correct answer was {correct}.\n")

    print("=" * 60)
    print(f"Quiz complete! You scored {score}/{len(questions)}.\n")


def main():
    print("StudyBot")
    print("========\n")

    pdf_path = get_pdf_path()
    llm_client, has_llm = try_create_llm_client()
    try:
        bot = StudyBot(pdf_path=pdf_path, llm_client=llm_client)
    except ValueError as e:
        print(f"\nError: {e}\n")
        return
    print(f"\nLoaded: {os.path.basename(pdf_path)}\n")

    while True:
        choice = choose_mode(has_llm)

        if choice == "q":
            print("\nGoodbye.")
            break
        elif choice == "1":
            run_ask_mode(bot, has_llm)
        elif choice == "2":
            run_quiz_mode(bot, has_llm)
        else:
            print("\nUnknown choice. Please pick 1, 2, or q.\n")


if __name__ == "__main__":
    main()
