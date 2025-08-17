#!/usr/bin/env python3

import google.generativeai as genai
import os
import sys
import PyPDF2

# --- Module-level Constants ---
GEMINI_MODEL_NAME = "gemini-2.5-flash" # Gemini model to use
GEMINI_API_KEY_FILE = "~/.config/gemini.token" # file to read token from
GEMINI_API_KEY_ENVVAR = "GOOGLE_API_KEY" # environment variable to get token from

class GoogleAPIKeyError(Exception):
    """Custom exception raised when the Google API key cannot be found."""
    pass

def get_google_api_key() -> str:
    """
    Find Google API key to use.

    Tries multiple methods, starting with environment variable then a configuration file

    Raises:
        GoogleAPIKeyError: If the Google API key cannot be found.

    Returns:
        str: The found Google API key.
    """

    # try environment variable first
    google_api_key = os.getenv(GEMINI_API_KEY_ENVVAR)
    if google_api_key:
        return google_api_key

    # try file next, continue if not found
    try:
        file_path = os.path.expanduser(GEMINI_API_KEY_FILE)
        with open(file_path, 'r') as f:
            google_api_key = f.read().strip()
            return(google_api_key)
    except FileNotFoundError:
        # File doesn't exist, which is expected if not configured this way.
        pass
    # don't catch other exceptions; those would be unexpected

    # NOTE: I would like to also support getting an API key from gnome keyring.  That would be an exercise for later.

    # raise an exception if we get this far without finding an API key
    if google_api_key is None:
        raise GoogleAPIKeyError(
                f"could not find Google API key in ${GEMINI_API_KEY_ENVVAR} or '{GEMINI_API_KEY_FILE}'"
        )

    return google_api_key


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a given PDF file.
    """
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def main():
    """
    Main routine for summarizing a pdf file name specified on the command line
    """

    # check for file name that we are supposed to process
    if len(sys.argv) != 2:
        print("Usage: {} <filename>".format(sys.argv[0]))
        sys.exit(1)
    file_name = sys.argv[1]

    # read contents of pdf
    print(f"# Reading contents of {file_name}...")
    try:
        document_text = extract_text_from_pdf(file_name)
    except FileNotFoundError:
        print(f"Error: PDF file not found at '{file_name}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unabe to read PDF '{file_name}': {e}")
        sys.exit(1)

    # get api key
    try:
        api_key = get_google_api_key()
        print("# Found API key")
    except GoogleAPIKeyError as e:
        print(f"Error: could not ackquire API key: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: unexpected error: {e}")
        sys.exit(1)

    # Configure API key
    genai.configure(api_key=api_key)

    # show model name
    print(f"# Using {GEMINI_MODEL_NAME} to produce a summary of {file_name}.")
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)

    print(f"# Querying model for a summary...")
    # prompt = f"Summarize the following document in a single paragraph for a computer science audience:\n\n{document_text}"
    prompt = f"""Summarize the following document in markdown format.  The heading should be the title of the document.  After the heading,
    list the document authors.  After the document authors, generate a concise paragraph that summarizes the document for a computer
    science audience.:\n\n{document_text}"""
    response = model.generate_content(prompt)
    print(response.text)

if __name__ == "__main__":
    main()
