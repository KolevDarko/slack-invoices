from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import load_dotenv, find_dotenv
from langchain.prompts.chat import (
  ChatPromptTemplate,
  SystemMessagePromptTemplate,
  HumanMessagePromptTemplate
)

load_dotenv(find_dotenv())

def draft_email(user_input, name='John'):
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