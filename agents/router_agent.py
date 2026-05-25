# ============================================================
# FILE: agents/router_agent.py
# PURPOSE: Route submission to correct queue, save to Supabase
# ============================================================

import os, sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from database import save_submission, add_to_queue

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
    coverage = extracted_data.get("coverage_amount", "0")
    try:
        amount = float(str(coverage).replace("$","").replace(",","").strip())
        if amount >= 1000000: return "High"
        elif amount >= 500000: return "Medium"
        else: return "Low"
    except:
        return "Medium"


def route_submission(extracted_result, classifier_result, validation_result):
    line_of_business = classifier_result.get("line_of_business", "Unknown")
    queue_name  = QUEUE_MAPPING.get(line_of_business, "manual_review_queue")
    team_name   = UNDERWRITING_TEAMS.get(queue_name, "Manual Review Team")
    data        = extracted_result.get("data", {})
    priority    = determine_priority(data)
    timestamp   = datetime.now().strftime("%Y%m%d-%H%M%S")
    submission_id = f"CLAIMA-{timestamp}"

    record = {
        "submission_id":         submission_id,
        "timestamp":             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "line_of_business":      line_of_business,
        "queue":                 queue_name,
        "assigned_team":         team_name,
        "priority":              priority,
        "validation_status":     validation_result.get("validation_status", "unknown"),
        "is_complete":           validation_result.get("is_complete", False),
        "missing_fields":        validation_result.get("missing_fields", []),
        "extracted_data":        data,
        "classification_method": classifier_result.get("method", "unknown"),
        "processing_status":     "Pending Review"
    }

    # Save to Supabase — check for duplicate
    save_result = save_submission(record)

    if save_result == "duplicate":
        return {
            "status":   "duplicate",
            "message":  f"This submission already exists in the system. Same applicant and policy type found.",
            "routed_to": team_name,
            "priority":  priority
        }

    add_to_queue(queue_name, submission_id)

    return {
        "status":        "success",
        "submission_id": submission_id,
        "routed_to":     team_name,
        "queue":         queue_name,
        "priority":      priority,
        "message":       f"Submission {submission_id} routed to {team_name} with {priority} priority."
    }