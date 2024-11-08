from functools import wraps
import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, abort, jsonify, request
from functions import extract_invoice_data
from invoice import create_invoice

load_dotenv()

# Set Slack API credentials
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Init slack app
app = App(token=SLACK_BOT_TOKEN)

# Initialize the Flask app
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


def get_bot_user_id():
    # Gets bot user id via slack Api
    try:
        slack_client = WebClient(token=SLACK_BOT_TOKEN)
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"Error: {e}")


signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)


def require_slack_verification(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not verify_slack_request():
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def verify_slack_request():
    # Get the request headers
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    # Check if the timestamp is within five minutes of the current time
    current_timestamp = int(time.time())
    if abs(current_timestamp - int(timestamp)) > 60 * 5:
        return False

    # Verify the request signature
    return signature_verifier.is_valid(
        body=request.get_data().decode("utf-8"),
        timestamp=timestamp,
        signature=signature,
    )


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
    say("Sure, extracting invoice data")

    response = extract_invoice_data(text)
    print(f"Got response, {response}")
    invoice_id = create_invoice(response)
    invoice_link = f"https://app.request.finance/draft/{invoice_id}"
    say(f"Invoice created: {invoice_link}")


@flask_app.route("/slack/events", methods=["POST"])
@require_slack_verification
def slack_events():
    """
    Route for handling Slack events.
    This function passes the incoming HTTP request to the SlackRequestHandler for processing.

    Returns:
        Response: The result of handling the request.
    """
    # Check if the request is a challenge request
    data = request.json
    if "challenge" in data:
        print("hi challenge")
        return jsonify({"challenge": data["challenge"] or ""})
    if data["type"] == "url_verification":
        return jsonify({"challenge": data["challenge"] or ""})

    return handler.handle(request)


@flask_app.route("/")
def hello():
    return "Hello World!"


# Run the Flask app
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8000)
