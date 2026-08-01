import json
import os

from dotenv import load_dotenv

from langfuse import observe
from langfuse.openai import AzureOpenAI

from langfuse_config import langfuse
from prompts import (
    CLASSIFICATION_SYSTEM_PROMPT,
    RESPONSE_SYSTEM_PROMPT,
)

load_dotenv()

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


@observe(name="classify_ticket", as_type="span")
def classify_ticket(ticket_text):

    langfuse.update_current_span(
        metadata={
            "stage": "classification"
        }
    )

    reply = chat(
        [
            {
                "role": "system",
                "content": CLASSIFICATION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": ticket_text,
            },
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(reply)


@observe(name="draft_response", as_type="span")
def draft_response(ticket_text, classification):

    langfuse.update_current_span(
        metadata={
            "stage": "drafting",
            "urgency": classification["urgency"],
            "category": classification["category"],
        }
    )

    return chat(
        [
            {
                "role": "system",
                "content": RESPONSE_SYSTEM_PROMPT,
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


@observe(name="process_ticket")
def process_ticket(ticket_text, ticket_id):

    classification = classify_ticket(ticket_text)

    draft = draft_response(
        ticket_text,
        classification,
    )

    langfuse.update_current_span(
        metadata={
            "ticket_id": ticket_id,
            "urgency": classification["urgency"],
            "category": classification["category"],
        }
    )

    trace_id = langfuse.get_current_trace_id()

    return {
        "urgency": classification["urgency"],
        "category": classification["category"],
        "draft_response": draft,
        "trace_id": trace_id,
        "trace_url": langfuse.get_trace_url(trace_id=trace_id),
    }