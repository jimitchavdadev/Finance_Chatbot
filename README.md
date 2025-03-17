# Finance Chatbot Web App

## 📌 Objective

The **Finance Chatbot Web App** is a Flask-based interactive chatbot designed to provide financial advice, stock data, loan calculations, and budget analysis. It enables users to ask financial questions and receive AI-driven responses in a user-friendly web interface. The chatbot can:

- Explain financial concepts in simple terms.
- Retrieve real-time stock market data.
- Perform loan payment and investment calculations.
- Provide budgeting and saving insights.

---

## 🛠️ How It Works

### 1️⃣ **Backend (Flask & Python)**

- The Flask server (`app.py`) serves the frontend and processes chatbot queries.
- `Finance_Chatbot.py` contains the **FinancialAdvisorBot**, which handles financial-related queries.
- The bot interacts with external APIs (e.g., Yahoo Finance) for real-time stock data.
- Flask exposes an API endpoint (`/query`) where the frontend sends user queries.

### 2️⃣ **Frontend (HTML, CSS, JavaScript)**

- `index.html` provides a chat-based UI.
- `style.css` ensures a clean, modern, and responsive design.
- `script.js` manages user interactions, sends queries to the backend, and formats chatbot responses.

### 3️⃣ **Chat Flow**

1. User types a question into the input field.
2. The JavaScript code (`script.js`) sends the question to the Flask backend via an API request.
3. The backend processes the query using `Finance_Chatbot.py`, performs necessary calculations, or fetches stock data.
4. The chatbot responds, and the UI displays the formatted message.

---

## 🚀 How to Run the Code

### **Prerequisites**

Ensure you have **Python 3.8+** installed and **pip** (Python package manager).

### **1️⃣ Clone the Repository**

```bash
git clone https://github.com/jimitchavdadev/Finance_Chatbot/
cd Finance_Chatbot
```

### **2️⃣ Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3️⃣ Set Up Environment Variables**

Create a `.env` file in the project root and add your API keys (if required). Example:

```
GROQ_API_KEY=your_api_key_here
```

### **4️⃣ Run the Flask App**

```bash
python app.py
```

The app will start on `http://127.0.0.1:5000/`.

### **5️⃣ Open in Browser**

Visit `http://127.0.0.1:5000/` to use the chatbot.

---

## ✨ Features

✅ AI-powered finance chatbot  
✅ Real-time stock data retrieval  
✅ Loan, investment, and budget calculations  
✅ User-friendly web interface  
✅ Secure API-based backend

---

## 🤝 Contributing

1. Fork the repository.
2. Create a new branch (`feature-new`).
3. Commit your changes (`git commit -m "Added new feature"`).
4. Push to the branch (`git push origin feature-new`).
5. Submit a **Pull Request**.

---

## 📜 License

This project is licensed under the **MIT License**.

---
