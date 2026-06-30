import os
os.environ["GEMINI_API_KEY"] = "dummy"

import ai_helper

class DummyResponse:
    def __init__(self, text):
        self.text = text

class DummyModels:
    def generate_content(self, model, contents):
        return DummyResponse("Dummy response")

class DummyClient:
    def __init__(self, api_key):
        self.models = DummyModels()

ai_helper.client = DummyClient("dummy")

print(ai_helper.suggest_tone_indicator('test'))
