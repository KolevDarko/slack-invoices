import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, request
from functions import draft_email

load_dotenv(find_dotenv())

# Set Slack API credentials
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]

# Init slack app
app = App(token=SLACK_BOT_TOKEN)

# Initialize the Flask app
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

def get_bot_user_id():
  # Gets bot user id via slack Api
  try:
    slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    response = slack_client.auth_test()
    return response["user_id"]
  except SlackApiError as e:
    print(f"Error: {e}")


def my_function(text):
    """
    Custom function to process the text and return a response.
    In this example, the function converts the input text to uppercase.

    Args:
        text (str): The input text to process.

    Returns:
        str: The processed text.
    """
    response = text.upper()
    return response


@app.event("app_mention")
def handle_mentions(body, say):
    """
    Event listener for mentions in Slack.
    When the bot is mentioned, this function processes the text and sends a response.

    Args:
        body (dict): The event data received from Slack.
        say (callable): A function for sending a response to the channel.
    """
    text = body["event"]["text"]

    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()
    say("Sure, I'll get right on that")

    response = draft_email(text)
    say(response)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    Route for handling Slack events.
    This function passes the incoming HTTP request to the SlackRequestHandler for processing.

    Returns:
        Response: The result of handling the request.
    """
    # Check if the request is a challenge request
    data = request.json
    if 'challenge' in data:
        print("hi challenge")
        return jsonify({"challenge": data["challenge"] or ""})
    if data["type"] == "url_verification":
       return jsonify({"challenge": data["challenge"] or ""})
    
    return handler.handle(request)

# Run the Flask app
if __name__ == "__main__":
    flask_app.run(port=5005, debug=True)
