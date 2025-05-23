# 📘 RAG PDF Assistant

**RAG PDF Assistant** is a smart question-answering tool that allows you to ask questions about the content of a PDF or text file. It uses Retrieval-Augmented Generation (RAG) with OpenAI embeddings and Claude-3 Haiku (via Flotorch Gateway) to provide accurate, context-based answers strictly from the provided document.

---

## 🔧 Features

- 📄 Supports `.pdf` and `.txt` documents
- 🔍 Answers questions using only the content of the file (no external knowledge)
- 🧠 Can summarize the document on request
- 🤖 Uses OpenAI Embeddings and Claude-3 Haiku
- ⚡ Fast and lightweight, runs from command line

---

## 📁 Project Structure
```
rag-pdf-assistant/
│
├── app/
│ ├── generator.py 
│ ├── retriever.py 
│ └── docs/ 
│
├── main.py 
├── .env 
├── requirements.txt
└── README.md 
```

## ⚙️ Setup Instructions

**Clone this repository**:
   git clone https://github.com/your-username/rag-pdf-assistant.git
   cd rag-pdf-assistant
## ✅ Requirements

- Python 3.8 or higher  
- [OpenAI API key](https://platform.openai.com/)  
- [Flotorch Gateway API key](https://flotorch.ai/)  
- Your Flotorch Gateway `BASE_URL`  

## Install the required Python libraries:
```bash
pip install -r requirements.txt
```
## Add your API keys in a .env file in the root folder:
   ```
   OPENAI_API_KEY=your-openai-key
   API_KEY=your-flotorch-api-key
   BASE_URL=https://your-flotorch-url.com
   ```

## Add your document:
- Place the .pdf or .txt file in the app/docs/ directory.

## Run the assistant:
   ```
   python main.py
   ```






