from flask import Flask, request, jsonify, render_template
from chatbot_app import FinancialAdvisorBot
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend requests from different origins
bot = FinancialAdvisorBot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    user_query = data.get("query", "")
    response = bot.process_query(user_query)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)