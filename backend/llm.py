import json
import os

from dotenv import load_dotenv

from prompts import (
    CLASSIFICATION_PROMPT,
    RESPONSE_PROMPT,
)



load_dotenv()

from langfuse.openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version=os.getenv(
        "AZURE_CHAT_API_VERSION",
        "2025-01-01-preview",
    ),
)

MODEL = os.getenv(
    "AZURE_CHAT_DEPLOYMENT",
    "gpt-4.1-mini",
)


def chat(messages, response_format=None):

    kwargs = {
        "model": MODEL,
        "messages": messages,
    }

    if response_format:
        kwargs["response_format"] = response_format

    response = client.chat.completions.create(**kwargs)

    return response.choices[0].message.content


def classify_ticket(ticket_text):

    reply = chat(
        [
            {
                "role": "system",
                "content": CLASSIFICATION_PROMPT,
            },
            {
                "role": "user",
                "content": ticket_text,
            },
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(reply)


def draft_response(ticket_text, classification):

    return chat(
        [
            {
                "role": "system",
                "content": RESPONSE_PROMPT,
            },
            {
                "role": "user",
                "content": f"""
Ticket:

{ticket_text}

Urgency:
{classification["urgency"]}

Category:
{classification["category"]}
""",
            },
        ]
    )


def process_ticket(ticket_text, ticket_id):

    classification = classify_ticket(ticket_text)

    draft = draft_response(
        ticket_text,
        classification,
    )

    return {
        "urgency": classification["urgency"],
        "category": classification["category"],
        "draft_response": draft,
        "trace_id": None,
        "trace_url": None,
    }
