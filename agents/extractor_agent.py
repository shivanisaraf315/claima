# ============================================================
# FILE: agents/extractor_agent.py
# PURPOSE: Send the raw PDF text to Gemini AI and get back
#          structured insurance data (name, policy type, etc.)
# LIBRARY USED: google-generativeai
#   - This is Google's official Python library to talk to
#     the Gemini AI model using your API key.
# ============================================================

import google.generativeai as genai  # Google's Gemini AI library
import json                           # Built-in Python library to handle JSON data
import os                             # Built-in Python library to read environment variables
from dotenv import load_dotenv        # Reads your API key from the .env file

# Load the .env file so we can access GEMINI_API_KEY
load_dotenv()

# Configure Gemini with your API key
# os.getenv() reads the value from your .env file safely
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create a Gemini model instance
# "gemini-1.5-flash" is free tier, fast, and good enough for this project
model = genai.GenerativeModel("gemini-1.5-flash")


def extract_information(parsed_result):
    """
    WHAT THIS FUNCTION DOES:
    - Takes the output from parser_agent (the raw text)
    - Builds a detailed prompt asking Gemini to extract fields
    - Sends that prompt to Gemini AI
    - Gets back a JSON response with structured insurance data
    - Returns that structured data as a Python dictionary

    INPUT:  parsed_result → the dictionary returned by parser_agent
    OUTPUT: Dictionary with all extracted insurance fields
    """

    # First check if parsing was successful
    # If parser failed, we don't even call Gemini
    if parsed_result["status"] != "success":
        return {
            "status": "error",
            "message": "Cannot extract — document parsing failed.",
            "data": {}
        }

    # Get the raw text from the parser result
    raw_text = parsed_result["text"]

    # -------------------------------------------------------
    # THE PROMPT — This is the most important part
    # We are telling Gemini exactly what to find and how to
    # return the answer (in JSON format)
    # -------------------------------------------------------
    prompt = f"""
    You are an expert insurance document analyst.
    Read the following insurance document text carefully.
    Extract the following fields and return ONLY a valid JSON object.
    Do not add any explanation. Do not add markdown. Just raw JSON.

    Fields to extract:
    - applicant_name: Full name of the person or company applying
    - policy_type: Type of insurance (Commercial Auto, Property, General Liability)
    - coverage_amount: The total coverage amount in dollars
    - effective_date: Policy start date
    - expiration_date: Policy end date
    - agent_name: Name of the insurance agent
    - contact_email: Email address found in the document
    - contact_phone: Phone number found in the document
    - business_name: Name of the business (if applicable)
    - location: Address or location mentioned
    - number_of_vehicles: Number of vehicles (for Auto policies, else null)
    - property_value: Value of property (for Property policies, else null)
    - liability_limit: Liability limit amount (for GL policies, else null)
    - loss_history: Any mention of previous claims or losses
    - submission_notes: Any special notes or remarks in the document

    If a field is not found in the document, set its value to null.

    Document Text:
    {raw_text}
    """

    try:
        # Send the prompt to Gemini and get a response
        response = model.generate_content(prompt)

        # response.text gives us the text Gemini replied with
        raw_response = response.text.strip()

        # Sometimes Gemini wraps JSON in ```json ``` markdown blocks
        # We clean that up before parsing
        if raw_response.startswith("```"):
            raw_response = raw_response.split("```")[1]  # Remove opening ```
            if raw_response.startswith("json"):
                raw_response = raw_response[4:]          # Remove the word 'json'

        # json.loads() converts the JSON string into a Python dictionary
        extracted_data = json.loads(raw_response)

        return {
            "status": "success",       # Extraction worked
            "data": extracted_data     # The structured insurance data
        }

    except json.JSONDecodeError:
        # This happens if Gemini didn't return valid JSON
        return {
            "status": "error",
            "message": "Gemini response was not valid JSON.",
            "data": {}
        }

    except Exception as e:
        # Any other error (API limit, network issue, etc.)
        return {
            "status": "error",
            "message": f"Extraction failed: {str(e)}",
            "data": {}
        }


# -------------------------------------------------------
# HOW TO EXPLAIN THIS IN INTERVIEW:
# "The extractor agent takes the raw text from the parser,
#  builds a structured prompt telling Gemini exactly which
#  insurance fields to find, sends it to the Gemini API,
#  and parses the JSON response back into a Python dictionary.
#  If Gemini returns invalid JSON, we handle that error
#  gracefully without crashing the system."
# -------------------------------------------------------