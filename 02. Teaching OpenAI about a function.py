import os
import openai
from dotenv import load_dotenv
import json

# Load the Openai API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Sample function to tell OpenAI about
def computeHash(a: int, b: int):
  """Computes a hash based on two given values"""
  return a + b

# OpenAI function to talk to gpt-3.5-turbo
def run_conversation(message: str):
  # Step 1: send the conversation and available functions to GPT
  messages = [{"role": "system", "content": "Acting as a data scientist"}]
  messages.append({"role": "user", "content": message})
  functions = [{
    "name": "computeHash",
    "description": "Computes a hash based on two given values",
    "parameters": {
        "type": "object",
        "properties":{
            "a": {
                "type": "integer",
                "description": "A whole number, e.g. 1, 2, 3"
            },
            "b": {
                "type": "integer",
                "description": "A whole number, e.g. 4, 5, 6"
            }
        },
        "required": ["a","b"]
    }
  }]

  response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = messages,
    functions = functions
  )
  response_message = response["choices"][0]["message"]

  # Step 2: check if GPT wanted to call a function
  if response_message.get("function_call"):
    # Step 3: call the function
    available_functions = {
        "computeHash": computeHash
    }
    function_name = response_message["function_call"]["name"]
    function_to_call = available_functions[function_name]
    function_args = json.loads(response_message["function_call"]["arguments"])
    function_response = function_to_call(
        a=function_args.get("a"),
        b=function_args.get("b"),
    )

     # Step 4: send the info on the function call and function response to GPT
    messages.append(response_message)  # extend conversation with assistant's reply
    messages.append({
        "role": "function",
        "name": function_name,
        "content": str(function_response),
    })  # extend conversation with function response

    second_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
    )  # get a new response from GPT where it can see the function response
    return second_response["choices"][0]["message"]["content"]

while True:
  prompt = input("Ask for a hash such as: Can you compute the hash of 5 and 9?, or 'quit': ")
  if prompt == 'quit':
    break
  print(run_conversation(prompt))

