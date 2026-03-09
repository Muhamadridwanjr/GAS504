import os
import google.generativeai as genai
from google.oauth2 import service_account

CRED_PATH = "/app/credentials/google_credentials.json"

if os.path.exists(CRED_PATH):
    try:
        # Some versions of google-generativeai can't use service accounts directly easily
        # But let's see if we can at least list models or if it needs an API Key.
        print("Initial testing of genai SDK in container...")
        # Note: Usually genai needs an API KEY. 
        # But let's try to list models and see the error.
        models = [m for m in genai.list_models()]
        for m in models:
            print(f"Model: {m.name}")
    except Exception as e:
        print(f"genai SDK failed: {str(e)}")
else:
    print("No credentials in container.")
