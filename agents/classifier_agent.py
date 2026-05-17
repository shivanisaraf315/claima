# ============================================================
# FILE: agents/classifier_agent.py
# PURPOSE: Identify which line of business this submission
#          belongs to — Auto, Property, or General Liability
# LIBRARY USED: None (pure Python — keyword matching + logic)
#   - We use simple keyword detection first (fast & free)
#   - Gemini is used as a fallback if keywords don't match
# ============================================================

import google.genai as genai   # NEW official Google AI SDK
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# -------------------------------------------------------
# KEYWORD DICTIONARY
# These are words commonly found in each type of insurance document
# If we find these words in the text, we can classify without AI
# This saves API calls and is faster
# -------------------------------------------------------
CLASSIFICATION_KEYWORDS = {
    "Commercial Auto": [
        "vehicle", "automobile", "auto", "truck", "fleet",
        "driver", "driving", "motor", "car", "van", "commercial vehicle",
        "number of vehicles", "vin", "vehicle identification"
    ],
    "Property": [
        "property", "building", "structure", "real estate",
        "premises", "location", "square feet", "construction",
        "roof", "fire protection", "dwelling", "warehouse", "office building"
    ],
    "General Liability": [
        "liability", "bodily injury", "property damage", "occurrence",
        "aggregate", "general liability", "premises liability",
        "products liability", "completed operations", "personal injury"
    ]
}


def classify_submission(extracted_result, raw_text=""):
    """
    WHAT THIS FUNCTION DOES:
    - First checks if policy_type was already extracted by Gemini
    - If yes, validates it is one of our 3 known types
    - If not found or unclear, uses keyword matching on raw text
    - If still unclear, asks Gemini directly to classify
    - Returns the final classified line of business

    INPUT:  extracted_result → dictionary from extractor_agent
            raw_text         → original PDF text (for keyword matching)
    OUTPUT: Dictionary with the classified insurance line
    """

    if extracted_result["status"] != "success":
        return {
            "status": "error",
            "message": "Cannot classify — extraction failed.",
            "line_of_business": "Unknown"
        }

    data = extracted_result["data"]
    known_types = list(CLASSIFICATION_KEYWORDS.keys())
    # known_types = ["Commercial Auto", "Property", "General Liability"]

    # -------------------------------------------------------
    # METHOD 1: Use what Gemini already extracted
    # -------------------------------------------------------
    policy_type = data.get("policy_type", "")

    if policy_type in known_types:
        # Gemini already correctly identified the type
        return {
            "status": "success",
            "line_of_business": policy_type,
            "method": "extracted_field",   # How we classified it
            "confidence": "high"
        }

    # -------------------------------------------------------
    # METHOD 2: Keyword matching on raw text
    # Count how many keywords from each category appear in text
    # Whichever category has the most matches wins
    # -------------------------------------------------------
    if raw_text:
        text_lower = raw_text.lower()  # Convert to lowercase for comparison
        scores = {}                     # Store keyword match count per category

        for category, keywords in CLASSIFICATION_KEYWORDS.items():
            # Count how many keywords from this category appear in the text
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            scores[category] = score

        # Find the category with the highest score
        best_match = max(scores, key=lambda x: scores[x])
        best_score = scores[best_match]

        # Only use keyword match if we found at least 2 matching keywords
        # This avoids wrong classification from just 1 accidental word
        if best_score >= 2:
            return {
                "status": "success",
                "line_of_business": best_match,
                "method": "keyword_matching",
                "confidence": "medium",
                "keyword_scores": scores   # Useful for debugging
            }

    # -------------------------------------------------------
    # METHOD 3: Ask Gemini directly (fallback)
    # Used when neither of the above methods worked
    # -------------------------------------------------------
    try:
        prompt = f"""
        You are an insurance classification expert.
        Based on the following extracted insurance data, classify this submission
        into exactly ONE of these three categories:
        - Commercial Auto
        - Property
        - General Liability

        Return ONLY the category name. Nothing else. No explanation.

        Extracted Data:
        {data}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        classified = response.text.strip()

        # Validate that Gemini returned one of our known types
        if classified in known_types:
            return {
                "status": "success",
                "line_of_business": classified,
                "method": "gemini_fallback",
                "confidence": "medium"
            }
        else:
            # Gemini returned something unexpected
            return {
                "status": "success",
                "line_of_business": "General Liability",  # Safe default
                "method": "default_fallback",
                "confidence": "low",
                "note": f"Gemini returned unexpected value: {classified}"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Classification failed: {str(e)}",
            "line_of_business": "Unknown"
        }


# -------------------------------------------------------
# HOW TO EXPLAIN THIS IN INTERVIEW:
# "The classifier uses a three-level strategy. First it
#  checks if Gemini already extracted the policy type.
#  If not, it does keyword matching — counting how many
#  Auto, Property, or Liability keywords appear in the
#  document text. If that also fails, it asks Gemini
#  directly to classify. This layered approach is faster
#  and more reliable than always calling the API."
# -------------------------------------------------------