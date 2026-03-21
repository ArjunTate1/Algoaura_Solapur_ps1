# 🚦 GenAI-Powered Indian Traffic Law Assistant

This is a simple yet effective Streamlit-based GenAI app that helps users query Indian traffic laws in natural language. It uses LangChain, OpenAI embeddings, and FAISS for intelligent search from a PDF version of the Motor Vehicles Act.

---

## 📁 Project Structure

```
genai-traffic-law-assistant/
├── app.py                # Main Streamlit application
├── .env                  # API keys (not pushed to GitHub)
├── .env.example          # Sample env file format
├── requirements.txt      # Python dependencies
├── 2202011053641.pdf     # Law document used as data source
├── .gitignore            # Hides .env, .venv, etc.
└── README.md             # Project guide 
```

---

##  What This Project Does

- Loads traffic law PDF using PyPDF2.
- Splits the content into chunks using LangChain’s `RecursiveCharacterTextSplitter`.
- Embeds those chunks using OpenAI embeddings.
- Stores the vectors in a FAISS vector database.
- Creates a retriever + LLM chain to give context-aware answers.
- Runs everything on a simple Streamlit UI.

---

##  How to Run This Project

### 1. Clone the Repo

```bash
git clone https://github.com/MallikarjunSonna/genai-traffic-law-assistant.git
cd genai-traffic-law-assistant
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Add Your API Key

Create a `.env` file in the root directory and add your OpenAI key like this:

```
OPENAI_API_KEY=sk-your-openai-api-key
```

Refer to `.env.example` for reference.

### 4. Run the App

```bash
streamlit run app.py
```

That’s it — now you can ask questions from Indian traffic law like a pro.

---

##  Example Questions to Ask

- What is the fine for not wearing a helmet?
- Is drunk driving punishable by jail?
- What does Section 129 talk about?
- What's the penalty for not using a seatbelt?
- What are the rules for underage drivers?

---

##  Want to Deploy Online?

Use [Streamlit Cloud](https://streamlit.io/cloud). Here's how:

1. Move your `.env` values into `.streamlit/secrets.toml`
2. Format:
```
[general]
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxx"
```

---

##  Tech Stack

- LangChain
- OpenAI Embeddings
- FAISS
- PyPDF
- Streamlit

---

##  Important

- Don’t forget to keep your API keys safe.

---

## 👨‍💻 About the Author

This project was built by [Mallikarjun Sonna](https://github.com/MallikarjunSonna) to practically explore how GenAI can be used to solve real-world legal problems using natural language interfaces.

Suggestions and contributions are always welcome!

---

## 📫 Contact

If you have ideas, suggestions, or want to contribute, feel free to open an issue or reach out through GitHub.