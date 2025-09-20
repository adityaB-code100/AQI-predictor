from flask import Flask, render_template, request
import requests
import os,json


# It's best practice to use environment variables for sensitive information like API keys.
# You MUST replace "YOUR_GOOGLE_TRANSLATE_API_KEY" with your actual, working API key.
# This 403 Forbidden error is almost certainly caused by an invalid or restricted key.
# Load API key
with open("config.json") as f:
    config = json.load(f)
API_KEY = config["GOOGLE_TRANSLATE_API_KEY"]["key"]#
URL = "https://translation.googleapis.com/language/translate/v2"


        # Check if both text and target language were provided
def transaltor(text,target):
    text_to_translate=text
    target_language=target
    if text_to_translate and target_language:
            # The API key and query parameters are typically sent via a URL query string.
            # The 'params' argument in requests handles this correctly.
            payload = {
                "q": text_to_translate,
                "target": target_language,
                "key": API_KEY
            }

            try:
                # The requests.post() call is updated to use 'params' for the URL query.
                response = requests.post(URL, params=payload)
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                result = response.json()
                translated_text = result["data"]["translations"][0]["translatedText"]
            except requests.exceptions.HTTPError as e:
                # Handle specific HTTP errors like 403 Forbidden.
                if e.response.status_code == 403:
                    translated_text = "Error: 403 Forbidden. The API key is likely incorrect or not configured for the Google Translation API. Please check your key."
                else:
                    translated_text = f"HTTP Error: {e}"
            except requests.exceptions.RequestException as e:
                # Handle general connection errors or other request issues
                translated_text = f"Error communicating with the translation API: {e}"
            except KeyError:
                # Handle cases where the JSON response is not as expected
                translated_text = "Error: Invalid response from the translation API. Please check your API key."
    else:
            translated_text = "Please enter text and select a target language."

    return translated_text
