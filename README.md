# 📬 Organization Email Alert System

A Python-based AI agent that monitors your Gmail inbox for domain-specific emails (e.g., `@acropolis.in`) and sends Telegram alerts if the email remains unread for more than 2 minutes. The system also uses **Gemini 1.5 Pro** (Google Generative AI) to auto-summarize the email content and format alerts using **Markdown** for clean readability.

---

## 🚀 Features

- 📥 Monitors Gmail inbox in real-time for unseen emails from a specific domain
- ⏰ Triggers Telegram alert if the email is unread after 2 minutes
- 🤖 Uses **Google Gemini 1.5 Pro** to generate concise summaries of the email content
- 📲 Sends formatted Telegram messages using **Telegram Bot API**
- ✅ Reliable delivery using `IMAPClient`, `Pyzmail`, and `requests`

---

## 🧠 Tech Stack

**Languages:**  
- Python

**Libraries/Tools Used:**  
- `IMAPClient` – for connecting and interacting with Gmail
- `Pyzmail` – to parse email content
- `requests` – to interact with the Telegram API
- `google.generativeai` – to access Gemini 1.5 Pro for summarization
- `dotenv` – for managing environment variables

**APIs & Services:**  
- **Gmail (IMAP)**
- **Telegram Bot API**
- **Google Gemini (Generative AI)**

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/madhuvan567/Organization-email-alert-system
cd Organization-email-alert-system
