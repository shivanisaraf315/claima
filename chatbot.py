# ============================================================
# FILE: chatbot.py
# PURPOSE: Conversational chatbot that lets users ask about
#          their submission status using natural language
# LIBRARY USED:
#   - google-generativeai → Gemini AI for understanding questions
#   - json, os            → Read submissions from JSON file (built-in)
# ============================================================

import google.genai as genai   # NEW official Google AI SDK
import json
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Path to submissions data file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBMISSIONS_FILE = os.path.join(BASE_DIR, "data", "submissions.json")


def load_submissions():
    """
    Load all submissions from the JSON file.
    Returns an empty list if file doesn't exist or is empty.
    """
    try:
        if os.path.exists(SUBMISSIONS_FILE):
            with open(SUBMISSIONS_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        return []
    except Exception:
        return []


def find_submission_by_id(submission_id, submissions):
    """
    Search for a submission by its ID.
    .upper() makes the search case-insensitive.
    Returns the submission dict if found, None if not.
    """
    for sub in submissions:
        if sub.get("submission_id", "").upper() == submission_id.upper():
            return sub
    return None


def find_submissions_by_name(name, submissions):
    """
    Search for submissions by applicant name (partial match).
    .lower() makes it case-insensitive.
    Returns a list of all matching submissions.
    """
    name_lower = name.lower()
    matches = []
    for sub in submissions:
        # Get the applicant name from extracted data
        applicant = sub.get("extracted_data", {}).get("applicant_name", "")
        business  = sub.get("extracted_data", {}).get("business_name", "")

        # Check if the search name appears in applicant or business name
        if name_lower in str(applicant).lower() or name_lower in str(business).lower():
            matches.append(sub)
    return matches


def format_submission_summary(sub):
    """
    Convert a submission dictionary into a clean readable summary string.
    This gets sent to Gemini so it can answer naturally.
    """
    data = sub.get("extracted_data", {})
    return f"""
Submission ID     : {sub.get('submission_id', 'N/A')}
Applicant Name    : {data.get('applicant_name', 'N/A')}
Business Name     : {data.get('business_name', 'N/A')}
Line of Business  : {sub.get('line_of_business', 'N/A')}
Policy Type       : {data.get('policy_type', 'N/A')}
Coverage Amount   : {data.get('coverage_amount', 'N/A')}
Effective Date    : {data.get('effective_date', 'N/A')}
Expiration Date   : {data.get('expiration_date', 'N/A')}
Assigned Team     : {sub.get('assigned_team', 'N/A')}
Priority          : {sub.get('priority', 'N/A')}
Validation Status : {sub.get('validation_status', 'N/A')}
Processing Status : {sub.get('processing_status', 'N/A')}
Missing Fields    : {', '.join(sub.get('missing_fields', [])) or 'None'}
Submitted On      : {sub.get('timestamp', 'N/A')}
"""


def get_all_submissions_summary(submissions):
    """
    Create a brief summary of all submissions for context.
    Gemini needs this to answer general questions like
    'How many submissions are pending?'
    """
    if not submissions:
        return "No submissions have been processed yet."

    lines = [f"Total Submissions: {len(submissions)}\n"]
    for sub in submissions:
        name = sub.get("extracted_data", {}).get("applicant_name", "Unknown")
        lines.append(
            f"- {sub.get('submission_id')} | {name} | "
            f"{sub.get('line_of_business')} | "
            f"Priority: {sub.get('priority')} | "
            f"Validation: {sub.get('validation_status')}"
        )
    return "\n".join(lines)


def chat(user_message, chat_history=None):
    """
    MAIN CHATBOT FUNCTION
    Takes the user's message and returns a helpful response.

    HOW IT WORKS:
    1. Load all submissions from JSON
    2. Try to find relevant submission(s) based on user message
    3. Build a context string with submission data
    4. Send user message + context to Gemini
    5. Return Gemini's natural language response

    INPUT:  user_message  → what the user typed (string)
            chat_history  → list of previous messages (for context)
    OUTPUT: response string from Gemini
    """

    submissions = load_submissions()

    # ----------------------------------------------------------
    # Try to extract a submission ID from the user's message
    # CLAIMA IDs look like: CLAIMA-20241215-143022
    # We scan each word to find one that starts with "CLAIMA-"
    # ----------------------------------------------------------
    words = user_message.upper().split()
    found_id = None
    for word in words:
        # Clean punctuation from the word before checking
        clean_word = word.strip(".,?!:;")
        if clean_word.startswith("CLAIMA-"):
            found_id = clean_word
            break

    # ----------------------------------------------------------
    # Build context based on what we found
    # ----------------------------------------------------------
    context = ""

    if found_id:
        # User mentioned a specific submission ID
        sub = find_submission_by_id(found_id, submissions)
        if sub:
            context = f"Here is the submission data the user is asking about:\n{format_submission_summary(sub)}"
        else:
            context = f"No submission found with ID: {found_id}"

    else:
        # Try to find by name — extract potential names from message
        # We look for capitalized words as potential names
        potential_names = [w for w in user_message.split() if len(w) > 3 and w[0].isupper()]

        matched_subs = []
        for name in potential_names:
            matches = find_submissions_by_name(name, submissions)
            matched_subs.extend(matches)

        # Remove duplicates (same submission matched multiple times)
        seen_ids = set()
        unique_subs = []
        for sub in matched_subs:
            sid = sub.get("submission_id")
            if sid not in seen_ids:
                seen_ids.add(sid)
                unique_subs.append(sub)

        if unique_subs:
            context = "Here are the relevant submissions:\n"
            for sub in unique_subs:
                context += format_submission_summary(sub)
        else:
            # No specific submission found — give overview of all
            context = f"All submissions overview:\n{get_all_submissions_summary(submissions)}"

    # ----------------------------------------------------------
    # Build the full prompt for Gemini
    # ----------------------------------------------------------
    system_context = f"""
You are CLAIMA Assistant — a helpful, professional AI chatbot for an 
insurance submission processing system called CLAIMA.

Your job is to help users track their insurance submissions, understand 
their status, and answer questions about the processing pipeline.

Be concise, friendly, and professional. Use the submission data below 
to answer accurately. If data is not available, say so politely.

{context}
"""

    # Build message history for Gemini (multi-turn conversation)
    messages = []

    # Add previous conversation turns if any
    if chat_history:
        for turn in chat_history:
            messages.append({
                "role": turn["role"],
                "parts": [turn["content"]]
            })

    # Add the current user message
    messages.append({
        "role": "user",
        "parts": [f"{system_context}\n\nUser Question: {user_message}"]
    })

    try:
        full_prompt = f"{system_context}\n\nUser Question: {user_message}"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        return response.text.strip()

    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try again."


# -------------------------------------------------------
# HOW TO EXPLAIN THIS IN INTERVIEW:
# "The chatbot uses Gemini AI to answer natural language
#  questions about submission status. It first loads all
#  submissions from the JSON file, then tries to find
#  the relevant one — by submission ID if the user
#  mentions it, or by name matching otherwise. It then
#  builds a context string with that submission's data
#  and sends it to Gemini along with the user's question.
#  Gemini responds in natural language. This is called
#  Retrieval-Augmented Generation or RAG — we retrieve
#  relevant data and give it to the AI as context."
# -------------------------------------------------------