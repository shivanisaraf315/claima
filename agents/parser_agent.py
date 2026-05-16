# ============================================================
# FILE: agents/parser_agent.py
# PURPOSE: Read a PDF file and extract all the raw text from it
# LIBRARY USED: pdfplumber
#   - pdfplumber is a free Python library that opens PDF files
#     and lets you read the text inside them, page by page.
# ============================================================

import pdfplumber  # This library reads PDF files and extracts text


def parse_document(file_path):
    """
    WHAT THIS FUNCTION DOES:
    - Takes the path of a PDF file as input
    - Opens the PDF using pdfplumber
    - Reads every page one by one
    - Collects all the text from all pages
    - Returns the full text as one single string

    INPUT:  file_path → example: "sample_docs/sample_auto.pdf"
    OUTPUT: A long string containing all text from the PDF
    """

    all_text = ""  # Start with an empty string to collect text

    try:
        # pdfplumber.open() opens the PDF file safely
        # 'with' keyword ensures the file is closed after reading (good practice)
        with pdfplumber.open(file_path) as pdf:

            # pdf.pages gives us a list of all pages in the PDF
            # We loop through each page one by one
            for page in pdf.pages:

                # page.extract_text() reads all text on that page
                text = page.extract_text()

                # Sometimes a page has no text (like a blank page)
                # 'if text' checks it's not empty before adding
                if text:
                    all_text += text + "\n"  # Add page text + a new line

        # If we successfully got text, return it
        if all_text.strip():  # .strip() removes extra spaces/newlines
            return {
                "status": "success",          # Tells other agents: parsing worked
                "text": all_text.strip(),     # The actual extracted text
                "file": file_path             # Which file was parsed
            }
        else:
            # PDF opened but had no readable text
            return {
                "status": "error",
                "message": "No text found in the document. It may be a scanned image PDF.",
                "file": file_path
            }

    except FileNotFoundError:
        # This error happens if the file path is wrong
        return {
            "status": "error",
            "message": f"File not found: {file_path}",
            "file": file_path
        }

    except Exception as e:
        # This catches any other unexpected error
        return {
            "status": "error",
            "message": f"Failed to parse document: {str(e)}",
            "file": file_path
        }


# -------------------------------------------------------
# HOW TO EXPLAIN THIS IN INTERVIEW:
# "The parser agent uses pdfplumber to open a PDF file,
#  loop through each page, extract the text, and return
#  it as a structured dictionary with a status field.
#  If the file is missing or unreadable, it returns an
#  error message instead of crashing the whole system."
# -------------------------------------------------------