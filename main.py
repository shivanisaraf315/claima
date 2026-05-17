# ============================================================
# FILE: main.py
# PURPOSE: Master orchestrator — runs all 5 agents in order
#          for a given PDF file and returns the full result
# HOW IT WORKS:
#   1. parser_agent   → reads PDF text
#   2. extractor_agent → sends to Gemini, gets structured data
#   3. validator_agent → checks for missing fields
#   4. classifier_agent → identifies line of business
#   5. router_agent   → assigns queue, saves to JSON
# ============================================================

from agents.parser_agent     import parse_document
from agents.extractor_agent  import extract_information
from agents.validator_agent  import validate_submission
from agents.classifier_agent import classify_submission
from agents.router_agent     import route_submission


def process_submission(file_path):
    """
    WHAT THIS FUNCTION DOES:
    - Takes a PDF file path as input
    - Runs all 5 agents in sequence
    - Returns a complete result dictionary with every agent's output
    - If any agent fails, it stops and returns the error immediately

    INPUT:  file_path → path to the PDF file (string)
    OUTPUT: Dictionary with results from all agents + final status
    """

    print(f"\n{'='*55}")
    print(f"  CLAIMA — Processing Submission")
    print(f"  File: {file_path}")
    print(f"{'='*55}")

    # ----------------------------------------------------------
    # STEP 1: PARSE — Read the PDF and extract raw text
    # ----------------------------------------------------------
    print("\n[1/5] Parser Agent → Reading PDF...")
    parsed = parse_document(file_path)

    if parsed["status"] != "success":
        print(f"  ERROR: {parsed['message']}")
        return {"status": "error", "stage": "parsing", "details": parsed}

    print(f"  OK — Extracted {len(parsed['text'])} characters of text")

    # ----------------------------------------------------------
    # STEP 2: EXTRACT — Send text to Gemini, get structured data
    # ----------------------------------------------------------
    print("\n[2/5] Extractor Agent → Sending to Gemini AI...")
    extracted = extract_information(parsed)

    if extracted["status"] != "success":
        print(f"  ERROR: {extracted['message']}")
        return {"status": "error", "stage": "extraction", "details": extracted}

    print(f"  OK — Extracted {len(extracted['data'])} fields from document")

    # ----------------------------------------------------------
    # STEP 3: VALIDATE — Check for missing required fields
    # ----------------------------------------------------------
    print("\n[3/5] Validator Agent → Checking completeness...")
    validated = validate_submission(extracted)

    if validated["validation_status"] == "passed":
        print(f"  OK — All required fields present")
    else:
        missing = validated["missing_fields"]
        print(f"  WARNING — {len(missing)} field(s) missing: {missing}")

    # Note: We continue even if validation fails
    # The submission is routed with a "incomplete" flag

    # ----------------------------------------------------------
    # STEP 4: CLASSIFY — Identify line of business
    # ----------------------------------------------------------
    print("\n[4/5] Classifier Agent → Identifying line of business...")
    classified = classify_submission(extracted, parsed["text"])

    print(f"  OK — Classified as: {classified['line_of_business']}")
    print(f"       Method used: {classified.get('method', 'unknown')}")

    # ----------------------------------------------------------
    # STEP 5: ROUTE — Assign to underwriting queue
    # ----------------------------------------------------------
    print("\n[5/5] Router Agent → Assigning to queue...")
    routed = route_submission(extracted, classified, validated)

    if routed["status"] != "success":
        print(f"  ERROR: {routed['message']}")
        return {"status": "error", "stage": "routing", "details": routed}

    print(f"  OK — {routed['message']}")

    # ----------------------------------------------------------
    # FINAL RESULT — Combine everything into one dictionary
    # ----------------------------------------------------------
    print(f"\n{'='*55}")
    print(f"  SUBMISSION COMPLETE")
    print(f"  ID       : {routed['submission_id']}")
    print(f"  Team     : {routed['routed_to']}")
    print(f"  Priority : {routed['priority']}")
    print(f"  Status   : {'Complete' if validated['is_complete'] else 'Incomplete — missing fields'}")
    print(f"{'='*55}\n")

    return {
        "status":          "success",
        "submission_id":   routed["submission_id"],
        "line_of_business": classified["line_of_business"],
        "routed_to":       routed["routed_to"],
        "priority":        routed["priority"],
        "validation":      validated,
        "extracted_data":  extracted["data"],
        "classification":  classified,
        "routing":         routed
    }


# -------------------------------------------------------
# This block runs only when you execute main.py directly
# Example: python main.py
# It will test the system with all 3 sample documents
# -------------------------------------------------------
if __name__ == "__main__":
    test_files = [
        "sample_docs/sample_auto.pdf",
        "sample_docs/sample_property.pdf",
        "sample_docs/sample_liability.pdf"
    ]

    for file in test_files:
        result = process_submission(file)
        if result["status"] == "success":
            print(f"Processed: {result['submission_id']} → {result['line_of_business']}\n")
        else:
            print(f"Failed at stage: {result['stage']}\n")


# -------------------------------------------------------
# HOW TO EXPLAIN THIS IN INTERVIEW:
# "main.py is the orchestrator — it imports all 5 agents
#  and runs them in sequence. Each agent returns a
#  dictionary with a status field. If any agent fails,
#  we stop immediately and return the error. This is
#  called a pipeline architecture — each step's output
#  becomes the next step's input. The final result
#  contains outputs from all 5 agents combined."
# -------------------------------------------------------