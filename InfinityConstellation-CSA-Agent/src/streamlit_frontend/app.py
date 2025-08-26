import streamlit as st
import requests
import time

# Defaults
API_BASE = st.secrets.get("API_URL", "http://localhost:8000/api")
STREAM_URL = f"{API_BASE}/chat/stream"
SYNC_URL = f"{API_BASE}/chat/sync"

st.set_page_config(page_title="Infinity CSA - Data Intelligence", layout="wide")

st.title("Infinity CSA — Research & Lead Generation")

with st.sidebar:
    st.header("Interactive Controls")
    model_choice = st.selectbox("Model hint (optional)", options=["auto", "gpt5", "claude", "mistral", "gemini"], index=0)
    verbosity = st.selectbox("Verbosity", options=["minimal", "balanced", "verbose"], index=0)
    task_type = st.selectbox("Task type", options=["research_query", "lead_generation", "structured_data_extraction", "customer_support"], index=0)
    run_mode = st.radio("Run mode", options=["stream", "sync"], index=0)
    st.markdown("---")
    st.markdown("**Notes:**\n- `minimal` favors fast first token and short answers.\n- `verbose` produces long, detailed reasoning.")

prompt = st.text_area("Enter a research or business query", height=150)

col1, col2 = st.columns([3,1])

with col2:
    if st.button("Submit"):
        if not prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            # Prepare params
            params = {"prompt": prompt, "verbosity": verbosity, "task_type": task_type}
            if model_choice != "auto":
                params["model"] = model_choice

            if run_mode == "stream":
                # Streaming mode — read line-by-line from the streaming endpoint
                st.info("Streaming mode — real-time responses below.")
                placeholder = st.empty()
                # Use requests stream in a blocking manner — acceptable in Streamlit context
                with st.spinner("Contacting orchestrator..."):
                    try:
                        resp = requests.get(STREAM_URL, params=params, stream=True, timeout=120)
                        result_text = ""
                        for chunk in resp.iter_lines():
                            if chunk:
                                # decode bytes to str
                                text = chunk.decode("utf-8")
                                result_text += text
                                # update the UI incrementally
                                placeholder.text_area("CSA Response (streaming)", value=result_text, height=400)
                                # tiny sleep to let UI render
                                time.sleep(0.01)
                    except Exception as e:
                        st.error(f"Streaming error: {e}")
            else:
                # Sync mode — single request, aggregated response
                st.info("Sync mode — waiting for aggregated response.")
                try:
                    r = requests.post(SYNC_URL, json={"prompt": prompt, "model": params.get("model"), "verbosity": verbosity, "task_type": task_type}, timeout=120)
                    if r.status_code == 200:
                        data = r.json()
                        st.text_area("CSA Response (sync)", value=data.get("response", ""), height=400)
                    else:
                        st.error(f"Error: {r.status_code} - {r.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")