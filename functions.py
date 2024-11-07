from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import load_dotenv, find_dotenv
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from typing import Optional
from langchain.chains.openai_functions import (
    create_openai_fn_chain,
    create_structured_output_chain,
)
from langchain.schema import HumanMessage, SystemMessage

load_dotenv(find_dotenv())

invoice_schema = {
    "type": "object",
    "properties": {
        "recipient_email": {
            "type": "string",
            "description": "Email of invoice recipient.",
        },
        "items": {
            "type": "array",
            "description": "Array of invoice items being charged to recipient",
            "item": {
                "type": "object",
                "description": "Information about one type of invoice item",
                "properties": {
                    "quantity": {
                        "type": "number",
                        "description": "The number of invoice items of this type in the invoice",
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the invoice item",
                    },
                    "price": {
                        "type": "number",
                        "description": "Price of the invoice item",
                    },
                    "currency": {
                        "type": "string",
                        "description": "Payment currency the item is priced in",
                    },
                },
            },
        },
    },
}


def draft_invoice(user_input):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt_msgs = [
        SystemMessage(
            content="You are a world class algorithm for extracting inovice information in a structured format."
        ),
        HumanMessage(
            content="Use the given format to extract information from the following input:"
        ),
        HumanMessagePromptTemplate.from_template("{input}"),
        HumanMessage(content="Tips: Make sure to answer in the correct format"),
    ]
    prompt = ChatPromptTemplate(messages=prompt_msgs)
    chain = create_structured_output_chain(invoice_schema, llm, prompt, verbose=True)
    print("Waiting response")
    response = chain.run(user_input)
    print("Got response")
    return response


def draft_email(user_input, name="John"):
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)

    template = """

  You are a helpful assistant that drafts an email reply based on a new email.
  Your goal is to help the user quickly create a perfect email reply by.

  Keep your reply short and to the point and mimic the style of the email to match the tone.

  Make sure to sign of with {signature}
  """

    signature = "Kind regards, \n\nDarko"
    system_message_prompt = SystemMessagePromptTemplate.from_template(template=template)

    human_template = "Here's the email to reply to and consider any other comments from the user fo reply as well: {user_input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    response = chain.run(user_input=user_input, signature=signature)
    return response


def try_invoice(user_input):
    chat = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, verbose=True)

    system_message_prompt = SystemMessage(
        content="You are a world class algorithm for extracting inovice information in the following format: {invoice_schema}"
    )
    human_template = "Use the given format to extract information from the following input: {user_input}"

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    response = chain.run(user_input=user_input, invoice_schema=invoice_schema)
    return response
