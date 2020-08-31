from google.cloud import translate
# GOOGLE_APPLICATION_CREDENTIALS or explicitly create credentials and re-run the application.
# For more information, please see https://cloud.google.com/docs/authentication/getting-started

translate_client = translate.Client()

text = 'Hello, world!'
target_lang = 'fr'

translation = translate_client.translate(text, target_language=target_lang)
