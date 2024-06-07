# Imports and load API key
import os
import openai
from dotenv import load_dotenv

# Load the Openai API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# OpenAI function to talk to gpt-3.5-turbo
def compute():
  response = openai.ChatCompletion.create(
    model = "gpt-3.5-turbo",
    messages = prompts
  )
  if response["choices"][0]["finish_reason"] != "stop":
    return
  prompts.append({
      "role": "assistant",
      "content": response["choices"][0]["message"]["content"]
  })
  print(response["choices"][0]["message"]["content"])

# Define the system message
system_msg = 'Acting as the best DnD writer'

prompts = []

# Start a loop that will run until the user enters 'quit'.
prompts.append({
    "role": "system",
    "content": system_msg
})
while True:
  prompt = input("Enter your prompt, or 'quit': ")
  if prompt == 'quit':
    break
  prompts.append({
      "role": "user",
      "content": prompt
  })
  compute()
