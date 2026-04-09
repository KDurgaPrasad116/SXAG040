# 📄 AI Legal Document Action Agent

## 🧠 Introduction

The **AI Legal Document Action Agent** is a full-stack application that
simulates an intelligent pipeline of specialized AI agents to process
and analyze legal documents. It extracts insights, identifies risks, and
recommends actions using AI-driven workflows.

------------------------------------------------------------------------

## 📚 Table of Contents

-   Features
-   Tech Stack
-   Project Structure
-   Installation
-   Usage
-   API Endpoints
-   Testing
-   Configuration
-   Examples
-   Troubleshooting
-   Contributors

------------------------------------------------------------------------

## ✨ Features

-   Legal document parsing using PyMuPDF
-   AI-powered summarization
-   Clause extraction
-   Risk analysis
-   Action recommendations
-   Full-stack implementation
-   JWT Authentication
-   SQLite database

------------------------------------------------------------------------

## 🛠 Tech Stack

### Frontend

-   React (Vite)
-   Tailwind CSS
-   Framer Motion
-   Axios

### Backend

-   FastAPI
-   SQLAlchemy
-   PyMuPDF
-   OpenAI API
-   PyJWT

------------------------------------------------------------------------

## 📁 Project Structure

    SXAG040/
    ├── server/
    ├── src/
    ├── public/
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

## ⚙️ Installation

### Backend

    cd server
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python seed_data.py
    export OPENAI_API_KEY="your-api-key"
    uvicorn main:app --reload --port 8000

### Frontend

    npm install
    npm run dev

------------------------------------------------------------------------

## 🚀 Usage

1.  Start backend and frontend
2.  Upload a legal document
3.  View AI-generated insights

------------------------------------------------------------------------

## 🔌 API Endpoints

-   GET /docs
-   POST /upload
-   GET /analyze
-   POST /auth

------------------------------------------------------------------------

## 🧪 Testing

    cd server
    pytest test_main.py

------------------------------------------------------------------------

## ⚙️ Configuration

    OPENAI_API_KEY=your_key

------------------------------------------------------------------------

## 💡 Examples

-   Upload contract → Extract clauses → Analyze risks → Get
    recommendations

------------------------------------------------------------------------

## 🛠 Troubleshooting

-   Ensure API key is set
-   Backend running on port 8000
-   Dependencies installed

------------------------------------------------------------------------

## 👥 Contributors

-   K Durga Prasad
-   Darshan A
-   Md Sairin Saidath
-   Himanshu Saho
------------------------------------------------------------------------
