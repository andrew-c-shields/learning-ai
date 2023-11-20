# Learned most of this from https://www.youtube.com/watch?v=I4mFqyqFkxg
# Then expanded upon it to combine techniques and build a program that asks for a country and then responds with the capital, the current weather, and some fun facts about the country

import os # Allows us to access OS paths for the .env file

from dotenv import load_dotenv # Used for environment variables
from langchain.llms import OpenAI # Used to initalize an OpenAI LLM for main_v1
from langchain.chat_models import ChatOpenAI # Used in main_v2 for making a ChatOpenAI llm that gives access to newer models
from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate # Allows the use of templates
from pydantic import BaseModel, Field # Needed for Pydantic classes
from langchain.output_parsers import PydanticOutputParser # Allows us to parse the response into a Pydantic object
from langchain.chains.api import open_meteo_docs
from langchain.chains import APIChain

class Country(BaseModel):
    capital: str = Field(description="capital of the country")
    name: str = Field(description="name of the country")

class CountryExpanded(BaseModel):
    capital: str = Field(description="capital of the country")
    name: str = Field(description="name of the country")
    weather: str = Field(description="a report of the current weather right now at the capital of the country")
    funFacts: list[str] = Field(descrption="a list of fun facts about the country")

# Load the Openai API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"

PROMPT_COUNTRY_INFO = """
    Provide information about {country}.
    """

PROMPT_COUNTRY_INFO_V2 = """
    Provide information about {country}. If the country doesn't exist, make up something.
    {format_instructions}
    """

PROMPT_COUNTRY_INFO_V3 = """
    Provide the capital and some fun facts about {country}. If the country doesn't exist, make up something.
    {format_instructions}
    """

# Older ChatGPT model that uses the older style from LangChain
def main_v1():
    llm = OpenAI(openai_api_key=OPENAI_API_KEY)
    result = llm.predict(
        "Give me 5 countries that everyone should visit before they stop traveling."
    )
    print(result)

# Access to newer ChatGPT models
def main_v2():
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL)
    result = llm.predict(
        "Give me 5 countries that everyone should visit before they stop traveling."
    )
    print(result)

# Using templates to sculpt prompts and insert user input
def main_v3():
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL)
    
    country = input("Enter the name of a country: ") # User input

    message = HumanMessagePromptTemplate.from_template(template=PROMPT_COUNTRY_INFO)
    chat_prompt = ChatPromptTemplate.from_messages(messages=[message]) # Allows us to handle multiple messages and format them all in a single call
    chat_prompt_with_values = chat_prompt.format_prompt(country=country)

    response = llm(chat_prompt_with_values.to_messages())
    print(response) # This will just print a raw string object with the response in the content field

# Using templates to sculpt prompts and insert user input while returning JSON
def main_v4():
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL)
    parser = PydanticOutputParser(pydantic_object=Country)
    
    country = input("Enter the name of a country: ") # User input

    message = HumanMessagePromptTemplate.from_template(template=PROMPT_COUNTRY_INFO_V2)
    chat_prompt = ChatPromptTemplate.from_messages(messages=[message]) # Allows us to handle multiple messages and format them all in a single call
    chat_prompt_with_values = chat_prompt.format_prompt(country=country, format_instructions=parser.get_format_instructions())

    response = llm(chat_prompt_with_values.to_messages())
    data = parser.parse(response.content) # this will give us a response of type Country
    print(f"The capital of {data.name} is {data.capital}.")

# Combine getting user input, weather data, and fun facts into a single response for the user
def main_v5():
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL)
    parser = PydanticOutputParser(pydantic_object=CountryExpanded)
    country = input("Enter the name of a country: ") # User input

    message = HumanMessagePromptTemplate.from_template(template=PROMPT_COUNTRY_INFO_V3)
    chat_prompt = ChatPromptTemplate.from_messages(messages=[message]) # Allows us to handle multiple messages and format them all in a single call
    chat_prompt_with_values = chat_prompt.format_prompt(country=country, format_instructions=parser.get_format_instructions())
    response = llm(chat_prompt_with_values.to_messages())
    data = parser.parse(response.content) # this will give us a response of type CountryExpanded
    
    # Now check the weather
    chain_new = APIChain.from_llm_and_api_docs(
        llm,
        open_meteo_docs.OPEN_METEO_DOCS,
        verbose=False,
        limit_to_domains=["https://api.open-meteo.com/"]
    )

    result = chain_new.run(
        f"What is the weather like right now in {data.capital}, {data.name} in degrees Farenhiet?"
    )
    data.weather = result

    print(f'The capital of {data.name} is {data.capital} and {data.weather}. Some fun facts about {data.name} are: {" ".join(str(x) for x in data.funFacts)}')

if __name__ == "__main__": # Main guard
    main_v5()