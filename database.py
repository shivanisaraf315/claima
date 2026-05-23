# ============================================================
# FILE: database.py
# PURPOSE: Connects CLAIMA to Supabase database
# LIBRARY: supabase (free Python client)
# Install: pip install supabase
#
# WHY SUPABASE INSTEAD OF JSON FILES:
# - Data is stored in the cloud, not your local PC
# - Works when deployed on Streamlit Cloud
# - Multiple people can use the app simultaneously
# - Data persists even if you restart the app
# ============================================================

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# ── CONNECTION ───────────────────────────────────────────────
# These values come from your .env file
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create the Supabase client — this is the connection object
# All database operations go through this client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ── SUBMISSIONS ──────────────────────────────────────────────

def save_submission(record: dict):
    """
    Save a new submission to the Supabase submissions table.
    Called by router_agent after processing is complete.
    """
    try:
        data = {
            "id":                    record.get("submission_id"),
            "timestamp":             record.get("timestamp"),
            "line_of_business":      record.get("line_of_business"),
            "assigned_team":         record.get("assigned_team"),
            "priority":              record.get("priority"),
            "validation_status":     record.get("validation_status"),
            "is_complete":           record.get("is_complete"),
            "missing_fields":        record.get("missing_fields", []),
            "extracted_data":        record.get("extracted_data", {}),
            "processing_status":     record.get("processing_status", "Pending Review"),
            "classification_method": record.get("classification_method", "unknown"),
            "queue":                 record.get("queue")
        }
        supabase.table("submissions").insert(data).execute()
        return True
    except Exception as e:
        print(f"DB save_submission error: {e}")
        return False


def get_all_submissions():
    """
    Load all submissions from the database.
    Returns a list of submission dictionaries.
    Used by the UI to display the submissions tab.
    """
    try:
        response = supabase.table("submissions").select("*").execute()
        rows = response.data or []

        # Convert back to the format our UI expects
        result = []
        for row in rows:
            result.append({
                "submission_id":         row["id"],
                "timestamp":             row["timestamp"],
                "line_of_business":      row["line_of_business"],
                "assigned_team":         row["assigned_team"],
                "priority":              row["priority"],
                "validation_status":     row["validation_status"],
                "is_complete":           row["is_complete"],
                "missing_fields":        row["missing_fields"] or [],
                "extracted_data":        row["extracted_data"] or {},
                "processing_status":     row["processing_status"],
                "classification_method": row["classification_method"],
                "queue":                 row["queue"]
            })
        return result
    except Exception as e:
        print(f"DB get_all_submissions error: {e}")
        return []


def get_submission_by_id(submission_id: str):
    """
    Get a single submission by its ID.
    Used by the chatbot to answer status queries.
    """
    try:
        response = supabase.table("submissions")\
            .select("*")\
            .eq("id", submission_id)\
            .execute()
        if response.data:
            row = response.data[0]
            return {
                "submission_id":     row["id"],
                "timestamp":         row["timestamp"],
                "line_of_business":  row["line_of_business"],
                "assigned_team":     row["assigned_team"],
                "priority":          row["priority"],
                "validation_status": row["validation_status"],
                "is_complete":       row["is_complete"],
                "missing_fields":    row["missing_fields"] or [],
                "extracted_data":    row["extracted_data"] or {},
                "processing_status": row["processing_status"]
            }
        return None
    except Exception as e:
        print(f"DB get_submission_by_id error: {e}")
        return None


# ── QUEUES ───────────────────────────────────────────────────

def get_queues():
    """
    Load all queue data from the database.
    Returns a dict like: {"auto_underwriting_queue": ["CLAIMA-123", ...], ...}
    """
    try:
        response = supabase.table("queues").select("*").execute()
        result = {}
        for row in response.data or []:
            result[row["queue_name"]] = row["submission_ids"] or []
        return result
    except Exception as e:
        print(f"DB get_queues error: {e}")
        return {
            "auto_underwriting_queue":      [],
            "property_underwriting_queue":  [],
            "liability_underwriting_queue": [],
            "manual_review_queue":          []
        }


def add_to_queue(queue_name: str, submission_id: str):
    """
    Add a submission ID to the correct underwriting queue.
    First loads the current list, then appends, then saves back.
    """
    try:
        # Get current queue contents
        response = supabase.table("queues")\
            .select("submission_ids")\
            .eq("queue_name", queue_name)\
            .execute()

        if response.data:
            current_ids = response.data[0]["submission_ids"] or []
            current_ids.append(submission_id)

            # Update queue with new list
            supabase.table("queues")\
                .update({"submission_ids": current_ids})\
                .eq("queue_name", queue_name)\
                .execute()
        return True
    except Exception as e:
        print(f"DB add_to_queue error: {e}")
        return False