# ============================================================
# FILE: agents/router_agent.py
# PURPOSE: Assign the processed submission to the correct
#          underwriting queue based on its line of business
# LIBRARY USED: json, os (both built-in Python — no install needed)
#   - json  → read and write JSON files
#   - os    → check if files exist, get file paths
#   - datetime → get current date and time (built-in)
# ============================================================

import json      # Built-in: read/write JSON files
import os        # Built-in: file path operations
from datetime import datetime   # Built-in: get current timestamp


# Path to our data files
# os.path.dirname(__file__) gets the folder where THIS file is
# os.path.join builds the correct path for any operating system
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBMISSIONS_FILE = os.path.join(BASE_DIR, "data", "submissions.json")
QUEUES_FILE = os.path.join(BASE_DIR, "data", "queues.json")


# -------------------------------------------------------
# QUEUE DEFINITIONS
# Each line of business has its own underwriting team queue
# Priority is assigned based on coverage amount
# -------------------------------------------------------
QUEUE_MAPPING = {
    "Commercial Auto":   "auto_underwriting_queue",
    "Property":          "property_underwriting_queue",
    "General Liability": "liability_underwriting_queue",
    "Unknown":           "manual_review_queue"
}

UNDERWRITING_TEAMS = {
    "auto_underwriting_queue":      "Commercial Auto Underwriting Team",
    "property_underwriting_queue":  "Property Underwriting Team",
    "liability_underwriting_queue": "General Liability Underwriting Team",
    "manual_review_queue":          "Manual Review Team"
}


def determine_priority(extracted_data):
    """
    Determines submission priority based on coverage amount.
    High coverage = High priority (gets reviewed first)

    Returns: "High", "Medium", or "Low"
    """
    coverage = extracted_data.get("coverage_amount", "0")

    # Convert coverage to a number for comparison
    # We remove $ and commas before converting
    try:
        # str(coverage) converts it to string first
        # replace() removes $ signs and commas
        # float() converts string to a decimal number
        amount = float(str(coverage).replace("$", "").replace(",", "").strip())

        if amount >= 1000000:    # 1 million or more → High priority
            return "High"
        elif amount >= 500000:   # 500k to 1 million → Medium priority
            return "Medium"
        else:                    # Below 500k → Low priority
            return "Low"
    except:
        # If we can't convert (e.g., coverage is "Not specified")
        return "Medium"          # Default to medium


def load_json_file(filepath, default):
    """
    Helper function to safely load a JSON file.
    If file doesn't exist or is empty, returns the default value.
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read().strip()
                if content:                  # File has content
                    return json.loads(content)
        return default                       # File empty or missing
    except:
        return default


def save_json_file(filepath, data):
    """
    Helper function to save data to a JSON file.
    json.dumps() converts Python dictionary to JSON string
    indent=4 makes it nicely formatted (readable)
    """
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def route_submission(extracted_result, classifier_result, validation_result):
    """
    WHAT THIS FUNCTION DOES:
    - Gets the line of business from classifier
    - Determines priority based on coverage amount
    - Creates a unique submission ID
    - Saves the complete submission to submissions.json
    - Adds it to the correct queue in queues.json
    - Returns routing confirmation

    INPUT:  extracted_result   → from extractor_agent
            classifier_result  → from classifier_agent
            validation_result  → from validator_agent
    OUTPUT: Dictionary with routing details and submission ID
    """

    # Get the line of business from classifier
    line_of_business = classifier_result.get("line_of_business", "Unknown")

    # Get the correct queue name for this line of business
    queue_name = QUEUE_MAPPING.get(line_of_business, "manual_review_queue")

    # Get the team name for this queue
    team_name = UNDERWRITING_TEAMS.get(queue_name, "Manual Review Team")

    # Get extracted data
    data = extracted_result.get("data", {})

    # Determine priority
    priority = determine_priority(data)

    # -------------------------------------------------------
    # CREATE SUBMISSION ID
    # Format: CLAIMA-YYYYMMDD-HHMMSS
    # Example: CLAIMA-20241215-143022
    # datetime.now() gets current date and time
    # strftime() formats it as a string
    # -------------------------------------------------------
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    submission_id = f"CLAIMA-{timestamp}"

    # -------------------------------------------------------
    # BUILD THE COMPLETE SUBMISSION RECORD
    # This is everything we know about this submission
    # -------------------------------------------------------
    submission_record = {
        "submission_id":      submission_id,
        "timestamp":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "line_of_business":   line_of_business,
        "queue":              queue_name,
        "assigned_team":      team_name,
        "priority":           priority,
        "validation_status":  validation_result.get("validation_status", "unknown"),
        "is_complete":        validation_result.get("is_complete", False),
        "missing_fields":     validation_result.get("missing_fields", []),
        "extracted_data":     data,
        "classification_method": classifier_result.get("method", "unknown"),
        "processing_status":  "Pending Review"   # Initial status
    }

    # -------------------------------------------------------
    # SAVE TO submissions.json
    # Load existing submissions, add new one, save back
    # -------------------------------------------------------
    submissions = load_json_file(SUBMISSIONS_FILE, [])  # Default: empty list
    submissions.append(submission_record)               # Add new submission
    save_json_file(SUBMISSIONS_FILE, submissions)       # Save updated list

    # -------------------------------------------------------
    # UPDATE queues.json
    # Each queue is a list of submission IDs
    # -------------------------------------------------------
    queues = load_json_file(QUEUES_FILE, {
        "auto_underwriting_queue":      [],
        "property_underwriting_queue":  [],
        "liability_underwriting_queue": [],
        "manual_review_queue":          []
    })

    # Add this submission ID to the correct queue
    if queue_name not in queues:
        queues[queue_name] = []
    queues[queue_name].append(submission_id)

    save_json_file(QUEUES_FILE, queues)

    return {
        "status":          "success",
        "submission_id":   submission_id,
        "routed_to":       team_name,
        "queue":           queue_name,
        "priority":        priority,
        "message":         f"Submission {submission_id} successfully routed to {team_name} with {priority} priority."
    }


# -------------------------------------------------------
# HOW TO EXPLAIN THIS IN INTERVIEW:
# "The router agent takes the results from all previous
#  agents and creates a complete submission record. It
#  assigns a unique ID using the current timestamp,
#  determines priority based on coverage amount, and
#  saves the submission to a JSON file. It also updates
#  the queue file so each underwriting team can see their
#  pending submissions. I chose JSON files instead of a
#  database to keep the project simple and portable —
#  no database setup is needed to run it."
# -------------------------------------------------------