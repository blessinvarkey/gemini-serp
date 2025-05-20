# Groq-SERP Chatbot

A Streamlit-based chatbot that demonstrates a multi-step flow without using LangChain:

1. **External Search** via Serper REST API
2. **LLM Inference** via GROQ's Python client (OpenAI-compatible)
3. **Streamlit UI** showing only the latest query and response

---

## 🚀 Features

* **Serper Search**: Fetch real-time search results from Serper’s REST API
* **GROQ LLM**: Use `llama-3.3-70b-versatile` via GROQ’s Chat Completion endpoint
* **Plain Python**: No LangChain dependency—full control over orchestration
* **Streamlit**: Interactive web UI with minimal boilerplate

## 📦 Requirements

List the dependencies in your `requirements.txt`:

```text
streamlit
requests
groq
```

## 🔑 Configuration

Set your API keys as Streamlit secrets (preferred) or environment variables:

```
GROQ_API_KEY = "<your-groq-api-key>"
SERPER_API_KEY = "<your-serper-key>"
```

> In Streamlit Cloud, add these under **Settings → Secrets**. Otherwise, export in your shell:
>
> ```bash
> export GROQ_API_KEY="..."
> export SERPER_API_KEY="..."
> ```

## 📄 Project Structure

```
├── app.py         # Main Streamlit application
├── requirements.txt
└── README.md      # This documentation
```

## ⚙️ Usage

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
2. **Run the app**:

   ```bash
   streamlit run app.py
   ```
3. **Ask a question** in the text box and click **Send**.

## 🛠️ How It Works

1. **User submits** a query via `st.text_input` and clicks **Send**.
2. **`serp_search()`** calls Serper's REST API to fetch JSON search results.
3. A **combined prompt** is built, embedding those results.
4. **`call_llm()`** sends the prompt to GROQ’s `llama-3.3-70b-versatile` model.
5. The **response** is displayed in the Streamlit app under **Answer**.
6. Streamlit **session state** retains only the latest query and response.

## ☁️ Deployment on Streamlit Cloud

1. Push this repo to GitHub.
2. In Streamlit Cloud, create a new app pointing to this repo and the `app.py` file.
3. Add **GROQ\_API\_KEY** and **SERPER\_API\_KEY** to the app’s **Secrets**.
4. Deploy 

