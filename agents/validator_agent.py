# ============================================================
# FILE: agents/validator_agent.py
# PURPOSE: Check the extracted data for missing required fields
#          and flag any incomplete submissions
# LIBRARY USED: None (pure Python only — no external libraries)
#   - This agent uses only basic Python: lists, loops, and
#     dictionary operations. No installation needed.
# ============================================================


# These are the fields that MUST be present in every submission
# If any of these are missing or null, the submission is incomplete
REQUIRED_FIELDS = [
    "applicant_name",
    "policy_type",
    "coverage_amount",
    "effective_date",
    "expiration_date",
    "contact_email",
    "contact_phone"
]

# These fields are specific to each policy type
# If the policy is Auto, number_of_vehicles must be present
# If Property, property_value must be present
# If General Liability, liability_limit must be present
POLICY_SPECIFIC_FIELDS = {
    "Commercial Auto":       ["number_of_vehicles"],
    "Property":              ["property_value", "location"],
    "General Liability":     ["liability_limit"]
}


def validate_submission(extracted_result):
    """
    WHAT THIS FUNCTION DOES:
    - Takes the output from extractor_agent
    - Checks every required field is present and not null
    - Also checks policy-specific fields based on policy type
    - Returns a validation report with missing fields listed

    INPUT:  extracted_result → dictionary from extractor_agent
    OUTPUT: Dictionary with validation status and missing fields
    """

    # If extraction failed, skip validation
    if extracted_result["status"] != "success":
        return {
            "status": "error",
            "message": "Cannot validate — extraction failed.",
            "missing_fields": [],
            "is_complete": False
        }

    # Get the actual data dictionary
    data = extracted_result["data"]

    missing_fields = []   # We will collect all missing fields here
    warnings = []         # Non-critical issues go here

    # -------------------------------------------------------
    # STEP 1: Check all required fields
    # -------------------------------------------------------
    for field in REQUIRED_FIELDS:

        # Check if field is missing from data entirely
        # OR if its value is None/null
        # OR if its value is an empty string ""
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)  # Add to missing list

    # -------------------------------------------------------
    # STEP 2: Check policy-specific fields
    # -------------------------------------------------------
    policy_type = data.get("policy_type", "")  # Get policy type safely

    # .get() is used instead of data["policy_type"] because
    # if "policy_type" doesn't exist, .get() returns "" instead of crashing

    if policy_type in POLICY_SPECIFIC_FIELDS:
        # Get the list of required fields for this policy type
        specific_fields = POLICY_SPECIFIC_FIELDS[policy_type]

        for field in specific_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(f"{field} (required for {policy_type})")

    # -------------------------------------------------------
    # STEP 3: Basic data quality checks (warnings only)
    # -------------------------------------------------------

    # Check if email looks like a real email (has @ symbol)
    email = data.get("contact_email", "")
    if email and "@" not in str(email):
        warnings.append("contact_email does not look valid")

    # Check if effective date comes before expiration date
    # We keep this simple — just check both exist
    eff = data.get("effective_date")
    exp = data.get("expiration_date")
    if eff and exp and eff == exp:
        warnings.append("effective_date and expiration_date are the same")

    # -------------------------------------------------------
    # STEP 4: Decide overall validation status
    # -------------------------------------------------------

    # If no fields are missing → submission is complete
    is_complete = len(missing_fields) == 0

    if is_complete:
        validation_status = "passed"
        message = "All required fields are present. Submission is complete."
    else:
        validation_status = "failed"
        message = f"{len(missing_fields)} required field(s) are missing."

    return {
        "status": "success",                  # Validator itself ran fine
        "validation_status": validation_status, # "passed" or "failed"
        "is_complete": is_complete,            # True or False
        "missing_fields": missing_fields,      # List of what's missing
        "warnings": warnings,                  # Non-blocking issues
        "message": message                     # Human readable summary
    }


# -------------------------------------------------------
# HOW TO EXPLAIN THIS IN INTERVIEW:
# "The validator agent checks the extracted data against
#  a predefined list of required fields. It also checks
#  policy-specific fields — for example, Auto submissions
#  must have number of vehicles, Property must have
#  property value. It returns a clear pass or fail result
#  with a list of exactly which fields are missing,
#  so the user knows what to fix."
# -------------------------------------------------------