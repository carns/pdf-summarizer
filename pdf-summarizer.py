#!/usr/bin/env python3

import google.generativeai as genai
import os
import sys
import PyPDF2

def get_google_api_key() -> str:
    """
    Find Google API key to use
    """

    # let environment variable take precedence, but if not set, then look for a file in ~/.config/
    file_path = os.path.expanduser("~/.config/gemini.token")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key is None:
        try:
            with open(file_path, 'r') as f:
                google_api_key = f.read().strip()
        except FileNotFoundError:
            google_api_key = None
        except Exception as e:
            google_api_key = None

    # NOTE: I would like to also support getting an API key from gnome keyring.  That would be an exercise for later

    # help caller if they don't seem to have a key set up
    if google_api_key is None:
        print("Error: please specify your Google API key using the \"GOOGLE_API_KEY\" environment variable or the ~/.config/gemini.token file.")

    return google_api_key


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a given PDF file.
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
        return text
    except FileNotFoundError:
        print(f"Error: PDF file not found at '{pdf_path}'")
        return ""
    except Exception as e:
        print(f"An error occurred while reading the PDF: {e}")
        return ""


def main():
    """
    Main routine for summarizing a pdf file name specified on the command line
    """

    # check for file name
    if len(sys.argv) != 2:
        print("Usage: {} <filename>".format(sys.argv[0]))
        sys.exit(1)

    file_name = sys.argv[1]

    if not os.path.exists(file_name):
        print("Error: File '{}' does not exist.".format(file_name))
        sys.exit(1)

    google_api_key = get_google_api_key()

    # Configure API key
    genai.configure(api_key=google_api_key)

    # show model name
    model_name = "gemini-2.5-flash"
    print(f"# Using {model_name} to produce a summary of {file_name}.")
    model = genai.GenerativeModel(model_name)

    # read contents of pdf
    print(f"# Reading contents of {file_name}...")
    document_text = extract_text_from_pdf(file_name)

    # debugging
    # print(document_text)
    # sys.exit(0)

    print(f"# Quering model for a summary...")
    # prompt = f"Summarize the following document in a single paragraph for a computer science audience:\n\n{document_text}"
    prompt = f"""Summarize the following document in markdown format.  The heading should be the title of the document.  After the heading,
    list the document authors.  After the document authors, generate a concise paragraph that summarizes the document for a computer
    science audience.:\n\n{document_text}"""
    response = model.generate_content(prompt)
    print(response.text)

if __name__ == "__main__":
    main()
