from vetted_secrets import GOOGLE_API_KEY
import google.generativeai as genai
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content('hey just testing if you are able to receive this')
print((response.text.split('**')))

