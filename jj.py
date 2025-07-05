import google.generativeai as genai

genai.configure(api_key="AIzaSyDF8EbndZGEqHBw75PK2Nr2vugNqtUk-HQ")

models = genai.list_models()
print(models)
