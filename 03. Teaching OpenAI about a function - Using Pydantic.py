import os # Allows us to access OS paths for the .env file
import openai # Imports all the openai functions
import json # Allows us to manipulate JSON objects
from dotenv import load_dotenv # Used for environment variables
from pydantic import validate_arguments # Validate_arguments allows for setting validate functions per instance of an openai_function

# Load the Openai API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Copied here as a way to create a simple decorator @openai_function that allows for passing it to OpenAI
from functools import wraps
from typing import Any, Callable

class openai_function:
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, func: Callable) -> None:
        self.func = func
        self.validate_func = validate_arguments(func)
        self.function_name = self.func.__name__
        if self.func.__doc__ is None:
            self.func.__doc__ = ""
        self.function_description = self.func.__doc__.replace("inbound_file_tool", "")
        self.inbound_file_tool = "inbound_file_tool" in self.func.__doc__
        self.schema = {
            "name": self.func.__name__,
            "description": self.func.__doc__.replace("inbound_file_tool", ""),
            "parameters": self.validate_func.model.schema(),
        }
        self.model = self.validate_func.model

    def openai_schema(self):
        sc = self.schema
        arr_to_remove = []
        shared_memory_check = False
        for key, value in self.schema["parameters"]["properties"].items():
            if key not in self.schema["parameters"]["required"]:
                arr_to_remove.append(key)
            else:
                if isinstance(value, dict):
                    if "$ref" in value:
                        if "definitions" in value["$ref"]:
                            sc["parameters"]["properties"][key] = self.schema[
                                "parameters"
                            ]["definitions"][value["$ref"].split("#/definitions/")[1]]
                            del sc["parameters"]["properties"][key]["description"]
                            del sc["parameters"]["properties"][key]["title"]
                            sc["parameters"]["properties"][key]["type"] = "string"

        for key in arr_to_remove:
            del sc["parameters"]["properties"][key]
            if "definitions" in sc["parameters"]:
                del sc["parameters"]["definitions"]

        return sc

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            return self.validate_func(*args, **kwargs)

        return wrapper(*args, **kwargs)

    def from_response(self, completion, throw_error=True, shared_memory=None):
        """Execute the function from the response of an openai chat completion"""
        message = completion.choices[0].message

        if throw_error:
            assert "function_call" in message, "No function call detected"
            assert (
                message["function_call"]["name"] == self.schema["name"]
            ), "Function name does not match"

        function_call = message["function_call"]
        arguments = json.loads(function_call["arguments"])
        return self.validate_func(**arguments)

# Sample function to tell OpenAI about
@openai_function
def computeHash(a: int, b: int) -> int:
  """Computes a hash based on two given values and returns that hash"""
  return a + b

# OpenAI function to talk to gpt-3.5-turbo
def run_conversation(message: str):
  messages = [{"role": "system", "content": "Acting as a data scientist"}]
  messages.append({"role": "user", "content": message})
  functions = [computeHash.openai_schema()]

  completion = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = messages,
    functions = functions
  )
  result = computeHash.from_response(completion)
  return result

# Basic main method that asks for input
while True:
  prompt = input("Ask for a hash such as: Can you compute the hash of 5 and 9?, or 'quit': ")
  if prompt == 'quit':
    break
  print(run_conversation(prompt))