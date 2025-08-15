#!/usr/bin/env python3

import google.generativeai as genai
import os
import sys

# get API key
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
    else:
        f.close()

# NOTE: I would like to also support getting an API key from gnome keyring.  That would be an exercise for later

# help caller if they don't seem to have a key set up
if google_api_key is None:
    print("Error: please specify your Google API key using the \"GOOGLE_API_KEY\" environment variable or the ~/.config/gemini.token file.")
    sys.exit(1)

# Configure API key
genai.configure(api_key=google_api_key)

# show model name
model_name = "gemini-2.5-flash"
print(f"# Using {model_name} .")

model = genai.GenerativeModel(model_name)
response = model.generate_content("Generate a haiku about nature.")
print(response.text)
