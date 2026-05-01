import os
import openai
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

# openai.api_key = os.environ['OpenAIKey']

class OpenAIAPI:
    def __init__(self, can_schema):
        self.schema = can_schema
        self.client = OpenAI()

    def get_completion(
        self,
        messages,
        model="gpt-5.4-nano",
        temperature=0,
        max_tokens=700
    ):
        response = self.client.responses.create(
            model=model,
            input=messages,
            temperature=temperature,
            max_output_tokens=max_tokens,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "canonical_invoice",
                    "schema": self.schema,
                    "strict": True
                }
            }
        )
        
        return response.output_text

