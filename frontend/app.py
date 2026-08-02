
import requests
import streamlit as st

BACKEND_URL = "http://backend:8000/v1/triage-ticket"

st.set_page_config(
    page_title="Support Ticket Triage",
    page_icon="🎫",
    layout="centered",
)

st.title("🎫 Support Ticket Triage")

st.write(
    "Paste a customer support ticket below. "
    "The application will classify its urgency and category, then generate a suggested first response."
)

ticket = st.text_area(
    "Support Ticket",
    height=220,
    placeholder="Example:\nI updated my password and now I can't log in. I have an important meeting in 20 minutes...",
)

if st.button("Analyze Ticket", use_container_width=True):

    if not ticket.strip():
        st.warning("Please enter a support ticket.")
        st.stop()

    with st.spinner("Analyzing ticket..."):

        try:
            response = requests.post(
                BACKEND_URL,
                json={"ticket": ticket},
                timeout=60,
            )

            response.raise_for_status()

            result = response.json()

        except requests.exceptions.RequestException as e:
            st.error(f"Backend request failed:\n\n{e}")
            st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Urgency",
            value=result["urgency"].capitalize(),
        )

    with col2:
        st.metric(
            label="Category",
            value=result["category"].capitalize(),
        )

    st.divider()
    st.subheader("Suggested First Response")
    st.write(result["draft_response"])
    st.divider()
    st.subheader("Langfuse Trace")
    st.code(result["trace_id"])
    if result.get("trace_url"):
        st.link_button(
            "Open Trace in Langfuse",
            result["trace_url"],
        )