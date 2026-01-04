# Nexus AI - Advanced RAG System

Nexus AI is a modern, production-ready Retrieval-Augmented Generation (RAG) system built with Flask, PostgreSQL (`pgvector`), and LangChain. It enables fast, context-aware AI interactions grounded in your specific documents and web content.
(The name is Nexus is only for demonstration purposes)


## 🚀 Features

- **Multi-Source Ingestion**:
  - 📄 **PDF Support**: Batch upload and process local PDF documents.
  - 🌐 **Web Scraping**: Recursive ingestion of websites and their sub-tabs with depth control.
- **Smart Retrieval**: Uses semantic similarity search powered by `pgvector` for hyper-relevant context retrieval.
- **Modern UI/UX**:
  - 💬 **Refined Chat Interface**: Glassmorphism design, smooth animations, and beige/dark-brown aesthetic.
  - 🛠️ **Admin Dashboard**: Centralized management for document ingestion and system monitoring.
- **Performant Backend**: Leveraging **Groq** (`llama-3.3-70b-versatile`) for near-instant responses.

## 🛠️ Technical Stack

- **Framework**: Flask
- **LLM Orchestration**: LangChain
- **Language Models**: Groq (Llama 3.3) / OpenAI (Embeddings)
- **Vector Database**: PostgreSQL with `pgvector`
- **Data Processing**: BeautifulSoup4 (Web), PyPDF (Documents)
- **Styling**: Vanilla CSS (Modern UI)

## 🏗️ Getting Started

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- API Keys:
  - [Groq API Key](https://console.groq.com/)
  - [OpenAI API Key](https://platform.openai.com/) (for embeddings)

### 1. Setup Environment

Create a `.env` file in the `rag/` directory with the following variables:

```env
# LLM Configuration
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key

# Database Configuration
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/nexus_db
```

### 2. Launch Database

Start the PostgreSQL database with `pgvector` using Docker Compose:

```bash
cd rag
docker-compose up -d
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Applications

**Launch the Admin Dashboard (for data ingestion):**
```bash
python admin_app.py
```
*Access via: `http://127.0.0.1:5001`*

**Launch the Chat Application:**
```bash
python chat_app.py
```
*Access via: `http://127.0.0.1:5000`*

## 📂 Project Structure

- `rag/admin_app.py`: Flask app for administration and document management.
- `rag/chat_app.py`: Main user-facing chat application.
- `rag/assistant.py`: Core RAG logic and response generation.
- `rag/database.py`: Database connection and vector store utilities.
- `rag/prompts.py`: System prompts and assistant identity.
- `rag/templates/`: HTML templates for the web interfaces.
- `rag/static/`: CSS and static assets.

## 🛡️ License

Distributed under the MIT License. See `LICENSE` for more information.


