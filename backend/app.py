from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from llm import process_ticket

app = FastAPI()


class TicketRequest(BaseModel):
    ticket: str


@app.post("/v1/triage-ticket")
def triage_ticket(request: TicketRequest):

    return process_ticket(
        ticket_text=request.ticket,
        ticket_id=str(uuid4()),
    )