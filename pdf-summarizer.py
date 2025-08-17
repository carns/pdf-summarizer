#!/usr/bin/env python3

import google.generativeai as genai
import os
import sys
import PyPDF2
import argparse
import json
import crossref

# --- Module-level Constants ---
GEMINI_MODEL_NAME = "gemini-2.5-flash" # Gemini model to use
GEMINI_API_KEY_FILE = "~/.config/gemini.token" # file to read token from
GEMINI_API_KEY_ENVVAR = "GOOGLE_API_KEY" # environment variable to get token from

class GoogleAPIKeyError(Exception):
    """Custom exception raised when the Google API key cannot be found."""
    pass

def generate_summary(document_text:str, model_name:str) -> dict:
    """
    Generate summary of document_text

    Args:
        document_text (str): complete document to summarize
        model_name (str): name of the Gemini model to use

    Returns:
        dict: dictionary with summary information about document
    """

    model = genai.GenerativeModel(model_name)

    prompt = f"""Summarize the following document and provide the
    information in a JSON object.

    The JSON object should have the following keys.  If any cannot be
    determined, then leave the value empty.
    - "title": (string) The title of the document.
    - "authors": (array of strings) A list of the authors of the document
    - "synopsis": A concise paragraph summarizing the document for a computer
      science audience

    Here is the document:
    \n\n{document_text}"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )

        # Parse the JSON string from the response
        # The 'response.text' attribute will contain the JSON string
        summary = json.loads(response.text)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        print(f"Raw response text: {response.text}")
    except Exception as e:
        print(f"An error occurred during content generation: {e}")

    return summary


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
            return google_api_key
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

    Args:
        pdf_path (str): path to the PDF file to parse

    Returns:
        str: contents of the PDF in string form
    """
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def main():
    """
    Main routine for summarizing a pdf file name specified on the command line
    """

    parser = argparse.ArgumentParser(
        description="Summarize a PDF file using Google's Gemini API.",
        formatter_class=argparse.RawTextHelpFormatter # Useful for multiline descriptions/help
    )
    parser.add_argument("filename",
                        help="Path to the PDF file to be summarized.")
    parser.add_argument("-o", "--output",
                        dest="output_filename",
                        help="Specify the name of the output file. If not provided, defaults to the input filename with '.md' appended.")

    args = parser.parse_args() # This handles sys.argv automatically

    filename = args.filename
    if args.output_filename:
        output_filename = args.output_filename
    else:
        output_filename = filename + ".md"

    # read contents of pdf
    print(f"Reading contents of {filename}...")
    try:
        document_text = extract_text_from_pdf(filename)
    except FileNotFoundError:
        print(f"Error: PDF file not found at '{filename}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unabe to read PDF '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

    # get api key
    print(f"Getting API key...")
    try:
        api_key = get_google_api_key()
    except GoogleAPIKeyError as e:
        print(f"Error: could not ackquire API key: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    # configure API key
    genai.configure(api_key=api_key)

    # generate summary
    print(f"Using {GEMINI_MODEL_NAME} to generate summary...")
    try:
        summary = generate_summary(document_text=document_text,
                                   model_name=GEMINI_MODEL_NAME)
    except Exception as e:
        print(f"Error: unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    # write summary
    with open(output_filename, 'wt') as file:
        file.write(f"## {summary['title']}\n\n")
        file.write(f"### Authors\n")
        file.write(f"{', '.join(summary['authors'])}\n\n")
        file.write(f"### Synopsis\n")
        file.write(f"{summary['synopsis']}\n\n")
        file.write(f"### Significance\n")

if __name__ == "__main__":
    main()
