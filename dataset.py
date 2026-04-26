"""
Optional helper module containing:
- SAMPLE_QUERIES used during the activity
- FALLBACK_DOCS, an in memory documentation corpus used if the docs/ folder
  is missing or cannot be loaded
"""

# -----------------------------------------------------------
# Sample queries used throughout Phase 0, 1, and 2
# -----------------------------------------------------------

SAMPLE_QUERIES = [
    "What are the main concepts covered in this material?",
    "Can you summarize the key points of this topic?",
    "What is the definition of the main term introduced here?",
    "How does the process described here work step by step?",
    "What are the differences between the two ideas mentioned?",
    "Why is this concept important?",
    "What examples are given to explain this topic?",
    "What are the key takeaways from this section?",
]

# -----------------------------------------------------------
# Optional fallback documentation corpus
# Used only if docs/ directory is missing.
# -----------------------------------------------------------

FALLBACK_DOCS = {
    "AUTH.md": """
# Authentication Guide

Tokens are created by the generate_access_token function inside auth_utils.py.
They are signed using the AUTH_SECRET_KEY environment variable.

Clients authenticate by sending a POST request to /api/login. They receive
a token which must be included in the Authorization header for all future
requests.

A token can be refreshed using POST /api/refresh.
""",

    "API_REFERENCE.md": """
# API Reference

GET /api/users returns all users. Requires a valid Authorization token.
GET /api/users/<user_id> returns data for a specific user.
GET /api/projects/<project_id> returns detailed project info.

POST /api/login validates credentials and returns an access token.
""",

    "DATABASE.md": """
# Database Guide

The users table contains:
- user_id
- email
- password_hash
- joined_at

The projects table contains:
- project_id
- name
- description
- status
- owner_id
""",

    "SETUP.md": """
# Setup Guide

Set DATABASE_URL and AUTH_SECRET_KEY before running the application.
Install dependencies with pip install -r requirements.txt.
Run the server using python app.py.
"""
}


def load_fallback_documents():
    """
    Returns FALLBACK_DOCS as a list of (filename, text) tuples.
    Provided as a helper for environments where no docs/ folder is available.
    """
    return list(FALLBACK_DOCS.items())
