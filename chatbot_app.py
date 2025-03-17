import requests
import json
import os
import time
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FinancialAdvisorBot:
    def __init__(self):
        # Get API key from environment variables
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("No Groq API key found. Please set the GROQ_API_KEY environment variable.")
        
        # API URL
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Define the system prompt for the financial advisor persona
        self.system_prompt = """
        You are a knowledgeable financial advisor chatbot with access to real-time financial data. Your goal is to provide helpful, 
        accurate, and ethical financial advice. You can:
        
        - Explain financial concepts in simple terms
        - Provide general investment strategies and principles
        - Offer budgeting and saving tips
        - Explain tax concepts at a high level
        - Discuss retirement planning approaches
        - Calculate loan payments, interest, and investment returns
        - Analyze real-time stock market data
        
        Remember to:
        - Clarify that you're providing general advice, not personalized financial recommendations
        - Suggest consulting with a licensed financial advisor for specific investment decisions
        - Never recommend specific stocks, funds, or investment products
        - Be transparent about the limitations of your knowledge
        - Ask clarifying questions when needed to provide better advice

        For numeric data, showcase calculations step-by-step to help users understand the reasoning.
        """
        
        # Initialize conversation history
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
    
    def get_stock_data(self, ticker, period="1d"):
        """
        Get real-time stock data using yfinance.
        
        Args:
            ticker (str): Stock ticker symbol
            period (str): Time period for historical data
            
        Returns:
            dict: Stock data information
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period=period)
            
            # Create a dictionary with relevant information
            stock_data = {
                "name": info.get("shortName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
                "previous_close": info.get("previousClose", "N/A"),
                "open": info.get("open", "N/A"),
                "day_low": info.get("dayLow", "N/A"),
                "day_high": info.get("dayHigh", "N/A"),
                "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
                "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "volume": info.get("volume", "N/A"),
                "avg_volume": info.get("averageVolume", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A") * 100 if info.get("dividendYield", "N/A") != "N/A" else "N/A",
                "historical_data": history.to_dict() if not history.empty else {}
            }
            
            return {
                "status": "success",
                "data": stock_data
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to retrieve stock data: {str(e)}"
            }
    
    def calculate_loan_payment(self, principal, interest_rate, years):
        """
        Calculate monthly loan payment for mortgage or other loans.
        
        Args:
            principal (float): Loan amount
            interest_rate (float): Annual interest rate (as a percentage)
            years (int): Loan term in years
            
        Returns:
            dict: Loan payment information
        """
        try:
            # Convert annual interest rate to monthly decimal rate
            monthly_rate = interest_rate / 100 / 12
            
            # Total number of payments
            n_payments = years * 12
            
            # Calculate monthly payment using the loan formula
            if monthly_rate == 0:
                monthly_payment = principal / n_payments
            else:
                monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
            
            # Calculate total interest paid
            total_cost = monthly_payment * n_payments
            total_interest = total_cost - principal
            
            # Generate amortization schedule
            schedule = []
            balance = principal
            
            for i in range(1, n_payments + 1):
                interest_payment = balance * monthly_rate
                principal_payment = monthly_payment - interest_payment
                
                balance -= principal_payment
                
                if i <= 12 or i % 12 == 0 or i == n_payments:  # First year, yearly thereafter, and last payment
                    schedule.append({
                        'payment_number': i,
                        'payment_amount': monthly_payment,
                        'principal_paid': principal_payment,
                        'interest_paid': interest_payment,
                        'remaining_balance': max(0, balance)  # Ensure balance doesn't go below zero
                    })
            
            return {
                "status": "success",
                "data": {
                    "monthly_payment": monthly_payment,
                    "total_payments": n_payments,
                    "total_cost": total_cost,
                    "total_interest": total_interest,
                    "interest_rate_monthly": monthly_rate,
                    "schedule": schedule[:10]  # Return first 10 entries for brevity
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to calculate loan payment: {str(e)}"
            }
    
    def calculate_investment_growth(self, initial_investment, monthly_contribution, annual_return, years):
        """
        Calculate compound investment growth over time.
        
        Args:
            initial_investment (float): Initial investment amount
            monthly_contribution (float): Monthly contribution amount
            annual_return (float): Expected annual return rate (as a percentage)
            years (int): Investment time horizon in years
            
        Returns:
            dict: Investment growth information
        """
        try:
            # Convert annual rate to monthly
            monthly_rate = annual_return / 100 / 12
            
            # Total number of months
            n_months = years * 12
            
            # Initialize arrays for tracking values
            balances = []
            contributions = []
            interests = []
            
            # Initial balance
            balance = initial_investment
            total_contribution = initial_investment
            total_interest = 0
            
            # Calculate month by month
            for i in range(1, n_months + 1):
                # Add monthly contribution
                balance += monthly_contribution
                total_contribution += monthly_contribution
                
                # Add interest
                interest = balance * monthly_rate
                balance += interest
                total_interest += interest
                
                # Store values at yearly intervals
                if i % 12 == 0:
                    year = i // 12
                    balances.append((year, balance))
                    contributions.append((year, total_contribution))
                    interests.append((year, total_interest))
            
            return {
                "status": "success",
                "data": {
                    "final_balance": balance,
                    "total_contributions": total_contribution,
                    "total_interest": total_interest,
                    "yearly_balances": balances,
                    "yearly_contributions": contributions,
                    "yearly_interests": interests
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to calculate investment growth: {str(e)}"
            }
    
    def calculate_retirement_needs(self, current_age, retirement_age, life_expectancy, annual_expenses, inflation_rate, current_savings, monthly_contribution, expected_return):
        """
        Calculate retirement needs and savings plan.
        
        Args:
            current_age (int): Current age
            retirement_age (int): Expected retirement age
            life_expectancy (int): Expected life expectancy
            annual_expenses (float): Current annual expenses
            inflation_rate (float): Expected inflation rate (as a percentage)
            current_savings (float): Current retirement savings
            monthly_contribution (float): Monthly contribution to retirement savings
            expected_return (float): Expected annual return on investments (as a percentage)
            
        Returns:
            dict: Retirement planning information
        """
        try:
            # Calculate years until retirement and years in retirement
            years_to_retirement = retirement_age - current_age
            years_in_retirement = life_expectancy - retirement_age
            
            # Calculate future annual expenses accounting for inflation
            future_annual_expenses = annual_expenses * ((1 + inflation_rate / 100) ** years_to_retirement)
            
            # Calculate total needed in retirement
            # Using the 4% rule as a simple approximation
            retirement_corpus_needed = future_annual_expenses * 25
            
            # Calculate how current savings will grow
            monthly_rate = expected_return / 100 / 12
            n_months = years_to_retirement * 12
            
            # Future value of current savings
            future_value_current_savings = current_savings * ((1 + monthly_rate) ** n_months)
            
            # Future value of monthly contributions
            future_value_contributions = monthly_contribution * ((1 + monthly_rate) ** n_months - 1) / monthly_rate * (1 + monthly_rate)
            
            # Total future value
            total_future_value = future_value_current_savings + future_value_contributions
            
            # Calculate shortfall or surplus
            shortfall = retirement_corpus_needed - total_future_value
            
            # Calculate required monthly contribution to meet retirement goal
            if shortfall > 0:
                required_monthly = monthly_contribution + (shortfall * monthly_rate) / ((1 + monthly_rate) ** n_months - 1)
            else:
                required_monthly = monthly_contribution
            
            return {
                "status": "success",
                "data": {
                    "years_to_retirement": years_to_retirement,
                    "years_in_retirement": years_in_retirement,
                    "future_annual_expenses": future_annual_expenses,
                    "retirement_corpus_needed": retirement_corpus_needed,
                    "future_value_current_savings": future_value_current_savings,
                    "future_value_contributions": future_value_contributions,
                    "total_future_value": total_future_value,
                    "shortfall_or_surplus": -shortfall if shortfall < 0 else shortfall,
                    "is_surplus": shortfall < 0,
                    "required_monthly_contribution": required_monthly
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to calculate retirement needs: {str(e)}"
            }
    
    def analyze_budget(self, income, expenses_dict):
        """
        Analyze a budget based on income and expense categories.
        
        Args:
            income (float): Monthly income
            expenses_dict (dict): Dictionary of expense categories and amounts
            
        Returns:
            dict: Budget analysis information
        """
        try:
            # Calculate total expenses
            total_expenses = sum(expenses_dict.values())
            
            # Calculate savings
            savings = income - total_expenses
            savings_rate = (savings / income) * 100 if income > 0 else 0
            
            # Calculate percentage for each category
            category_percentages = {category: (amount / income) * 100 if income > 0 else 0 
                                   for category, amount in expenses_dict.items()}
            
            # Standard recommendations based on 50/30/20 rule
            # 50% needs, 30% wants, 20% savings/debt
            needs_categories = ['housing', 'utilities', 'groceries', 'healthcare', 'insurance', 'transportation']
            wants_categories = ['entertainment', 'dining', 'shopping', 'hobbies', 'subscriptions', 'travel']
            savings_categories = ['savings', 'investments', 'debt_payment']
            
            # Calculate actual percentages
            needs_total = sum(expenses_dict.get(cat, 0) for cat in needs_categories if cat in expenses_dict)
            wants_total = sum(expenses_dict.get(cat, 0) for cat in wants_categories if cat in expenses_dict)
            savings_debt_total = sum(expenses_dict.get(cat, 0) for cat in savings_categories if cat in expenses_dict) + savings
            
            needs_percentage = (needs_total / income) * 100 if income > 0 else 0
            wants_percentage = (wants_total / income) * 100 if income > 0 else 0
            savings_debt_percentage = (savings_debt_total / income) * 100 if income > 0 else 0
            
            # Check if budget follows 50/30/20 rule
            rule_assessment = {
                "needs": {
                    "actual": needs_percentage,
                    "recommended": 50,
                    "difference": needs_percentage - 50
                },
                "wants": {
                    "actual": wants_percentage,
                    "recommended": 30,
                    "difference": wants_percentage - 30
                },
                "savings_debt": {
                    "actual": savings_debt_percentage,
                    "recommended": 20,
                    "difference": savings_debt_percentage - 20
                }
            }
            
            # Generate improvement suggestions
            suggestions = []
            
            if savings < 0:
                suggestions.append("Your expenses exceed your income. Consider reducing expenses or increasing income.")
            
            if needs_percentage > 50:
                suggestions.append("Your essential expenses are higher than recommended. Consider finding ways to reduce housing, transportation, or other necessary costs.")
            
            if wants_percentage > 30:
                suggestions.append("Your discretionary spending is higher than recommended. Consider cutting back on entertainment, dining out, or other non-essential expenses.")
            
            if savings_debt_percentage < 20:
                suggestions.append("You're saving less than recommended. Aim to increase your savings rate to at least 20% of your income.")
            
            # Top expense categories
            sorted_expenses = sorted(expenses_dict.items(), key=lambda x: x[1], reverse=True)
            top_expenses = sorted_expenses[:3]
            
            return {
                "status": "success",
                "data": {
                    "income": income,
                    "total_expenses": total_expenses,
                    "savings": savings,
                    "savings_rate": savings_rate,
                    "category_percentages": category_percentages,
                    "rule_assessment": rule_assessment,
                    "top_expenses": top_expenses,
                    "suggestions": suggestions
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to analyze budget: {str(e)}"
            }
    
    def parse_financial_query(self, query):
        """
        Parse a financial query to identify financial functions to execute.
        
        Args:
            query (str): User's financial query
            
        Returns:
            dict: Parsed query information and function calls
        """
        try:
            # Add the user's query to conversation history
            self.conversation_history.append({"role": "user", "content": query})
            
            # Send query to LLM to analyze and determine which financial function to call
            payload = {
                "model": "llama3-70b-8192",
                "messages": self.conversation_history,
                "temperature": 0.2,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
            response_data = response.json()
            
            # Extract assistant's response
            if "choices" in response_data and len(response_data["choices"]) > 0:
                assistant_response = response_data["choices"][0]["message"]["content"]
                self.conversation_history.append({"role": "assistant", "content": assistant_response})
                
                # Try to identify if there's a function call needed based on the query
                function_call = None
                
                # Check for stock data request
                if any(keyword in query.lower() for keyword in ["stock", "ticker", "share price", "stock price"]):
                    ticker_symbols = self._extract_ticker_symbols(query)
                    if ticker_symbols:
                        function_call = {
                            "function": "get_stock_data",
                            "parameters": {"ticker": ticker_symbols[0]}
                        }
                
                # Check for loan calculation
                elif any(keyword in query.lower() for keyword in ["loan", "mortgage", "payment", "interest"]):
                    loan_params = self._extract_loan_parameters(query)
                    if loan_params:
                        function_call = {
                            "function": "calculate_loan_payment",
                            "parameters": loan_params
                        }
                
                # Check for investment growth calculation
                elif any(keyword in query.lower() for keyword in ["invest", "compound", "growth", "return"]):
                    investment_params = self._extract_investment_parameters(query)
                    if investment_params:
                        function_call = {
                            "function": "calculate_investment_growth",
                            "parameters": investment_params
                        }
                
                # Check for retirement calculation
                elif any(keyword in query.lower() for keyword in ["retire", "retirement", "401k", "pension"]):
                    retirement_params = self._extract_retirement_parameters(query)
                    if retirement_params:
                        function_call = {
                            "function": "calculate_retirement_needs",
                            "parameters": retirement_params
                        }
                
                # Check for budget analysis
                elif any(keyword in query.lower() for keyword in ["budget", "spending", "expense", "income"]):
                    budget_params = self._extract_budget_parameters(query)
                    if budget_params:
                        function_call = {
                            "function": "analyze_budget",
                            "parameters": budget_params
                        }
                
                return {
                    "status": "success",
                    "query": query,
                    "response": assistant_response,
                    "function_call": function_call
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to get response from language model"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to parse financial query: {str(e)}"
            }

    def _extract_ticker_symbols(self, query):
        """Extract stock ticker symbols from a query"""
        # Simple regex-free extraction for common patterns
        words = query.upper().split()
        potential_tickers = []
        
        for word in words:
            # Clean up any punctuation
            word = ''.join(c for c in word if c.isalnum())
            
            # Check if word is a potential ticker (1-5 capital letters)
            if word.isalpha() and len(word) <= 5 and word == word.upper():
                potential_tickers.append(word)
        
        return potential_tickers
    
    def _extract_loan_parameters(self, query):
        """Extract loan calculation parameters from a query"""
        try:
            # Send to LLM to extract parameters
            extraction_prompt = f"""
            Extract loan calculation parameters from this query: "{query}"
            
            Return ONLY a JSON object with these fields (use null if not found):
            - principal: (numeric loan amount)
            - interest_rate: (annual interest rate as a percentage)
            - years: (loan term in years)
            
            JSON object:
            """
            
            extraction_messages = [
                {"role": "system", "content": "You extract structured data from text. Respond with JSON only."},
                {"role": "user", "content": extraction_prompt}
            ]
            
            payload = {
                "model": "llama3-70b-8192",
                "messages": extraction_messages,
                "temperature": 0.1,
                "max_tokens": 200
            }
            
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
            response_data = response.json()
            
            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"].strip()
                # Extract the JSON part if there's any other text
                if '{' in content and '}' in content:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    content = content[start:end]
                
                params = json.loads(content)
                
                # Validate parameters
                if params.get("principal") and params.get("interest_rate") and params.get("years"):
                    return {
                        "principal": float(params["principal"]),
                        "interest_rate": float(params["interest_rate"]),
                        "years": int(params["years"])
                    }
            
            return None
        
        except Exception:
            return None
    
    def _extract_investment_parameters(self, query):
        """Extract investment calculation parameters from a query"""
        try:
            # Similar approach as loan parameters
            extraction_prompt = f"""
            Extract investment growth parameters from this query: "{query}"
            
            Return ONLY a JSON object with these fields (use null if not found):
            - initial_investment: (numeric initial amount)
            - monthly_contribution: (numeric monthly amount)
            - annual_return: (expected annual return percentage)
            - years: (investment horizon in years)
            
            JSON object:
            """
            
            extraction_messages = [
                {"role": "system", "content": "You extract structured data from text. Respond with JSON only."},
                {"role": "user", "content": extraction_prompt}
            ]
            
            payload = {
                "model": "llama3-70b-8192",
                "messages": extraction_messages,
                "temperature": 0.1,
                "max_tokens": 200
            }
            
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
            response_data = response.json()
            
            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"].strip()
                if '{' in content and '}' in content:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    content = content[start:end]
                
                params = json.loads(content)
                
                # Validate parameters
                if (params.get("initial_investment") is not None and 
                    params.get("monthly_contribution") is not None and 
                    params.get("annual_return") is not None and 
                    params.get("years") is not None):
                    return {
                        "initial_investment": float(params["initial_investment"]),
                        "monthly_contribution": float(params["monthly_contribution"]),
                        "annual_return": float(params["annual_return"]),
                        "years": int(params["years"])
                    }
            
            return None
        
        except Exception:
            return None
    
    def _extract_retirement_parameters(self, query):
        """Extract retirement calculation parameters from a query"""
        try:
            extraction_prompt = f"""
            Extract retirement planning parameters from this query: "{query}"
            
            Return ONLY a JSON object with these fields (use null if not found):
            - current_age: (numeric current age)
            - retirement_age: (numeric retirement age)
            - life_expectancy: (numeric life expectancy)
            - annual_expenses: (numeric annual expenses)
            - inflation_rate: (numeric inflation rate percentage)
            - current_savings: (numeric current retirement savings)
            - monthly_contribution: (numeric monthly contribution)
            - expected_return: (numeric expected annual return percentage)
            
            JSON object:
            """
            
            extraction_messages = [
                {"role": "system", "content": "You extract structured data from text. Respond with JSON only."},
                {"role": "user", "content": extraction_prompt}
            ]
            
            payload = {
                "model": "llama3-70b-8192",
                "messages": extraction_messages,
                "temperature": 0.1,
                "max_tokens": 300
            }
            
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
            response_data = response.json()
            
            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"].strip()
                if '{' in content and '}' in content:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    content = content[start:end]
                
                params = json.loads(content)
                
                # Use default values for missing parameters
                return {
                    "current_age": int(params.get("current_age", 30)),
                    "retirement_age": int(params.get("retirement_age", 65)),
                    "life_expectancy": int(params.get("life_expectancy", 90)),
                    "annual_expenses": float(params.get("annual_expenses", 50000)),
                    "inflation_rate": float(params.get("inflation_rate", 2.5)),
                    "current_savings": float(params.get("current_savings", 0)),
                    "monthly_contribution": float(params.get("monthly_contribution", 500)),
                    "expected_return": float(params.get("expected_return", 7))
                }
            
            return None
        
        except Exception:
            return None
    
    def _extract_budget_parameters(self, query):
        """Extract budget analysis parameters from a query"""
        try:
            extraction_prompt = f"""
            Extract budget analysis parameters from this query: "{query}"
            
            Return ONLY a JSON object with these fields:
            - income: (numeric monthly income)
            - expenses: (object with expense categories as keys and amounts as values)
            
            Example:
            {{
                "income": 5000,
                "expenses": {{
                    "housing": 1500,
                    "utilities": 200,
                    "groceries": 500,
                    "transportation": 300,
                    "entertainment": 300,
                    "dining": 200,
                    "savings": 500
                }}
            }}
            
            JSON object:
            """
            
            extraction_messages = [
                {"role": "system", "content": "You extract structured data from text. Respond with JSON only."},
                {"role": "user", "content": extraction_prompt}
            ]
            
            payload = {
                "model": "llama3-70b-8192",
                "messages": extraction_messages,
                "temperature": 0.1,
                "max_tokens": 400
            }
            
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
            response_data = response.json()
            
            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"].strip()
                if '{' in content and '}' in content:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    content = content[start:end]
                
                params = json.loads(content)
                
                # Validate parameters
                if params.get("income") and params.get("expenses"):
                    return {
                        "income": float(params["income"]),
                        "expenses_dict": params["expenses"]
                    }
            
            return None
        
        except Exception:
            return None
    
    def process_query(self, query):
        """
        Process a financial query and execute any identified function calls.
        
        Args:
            query (str): User's financial query
            
        Returns:
            dict: Query response with any function results
        """
        # Parse the query
        parsed_result = self.parse_financial_query(query)
        
        if parsed_result["status"] == "error":
            return parsed_result
        
        # Execute function call if identified
        function_result = None
        if parsed_result.get("function_call"):
            function_name = parsed_result["function_call"]["function"]
            parameters = parsed_result["function_call"]["parameters"]
            
            if function_name == "get_stock_data":
                function_result = self.get_stock_data(**parameters)
            elif function_name == "calculate_loan_payment":
                function_result = self.calculate_loan_payment(**parameters)
            elif function_name == "calculate_investment_growth":
                function_result = self.calculate_investment_growth(**parameters)
            elif function_name == "calculate_retirement_needs":
                function_result = self.calculate_retirement_needs(**parameters)
            elif function_name == "analyze_budget":
                function_result = self.analyze_budget(**parameters)
        
        # If function was executed, add result to conversation and get updated response
        if function_result:
            # Add function result to conversation history
            result_message = f"Function {parsed_result['function_call']['function']} returned: {json.dumps(function_result)}"
            self.conversation_history.append({"role": "system", "content": result_message})
            
            # Get updated response with function results incorporated
            payload = {
                "model": "llama3-70b-8192",
                "messages": self.conversation_history,
                "temperature": 0.2,
                "max_tokens": 1000
            }
            
            response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))
            response_data = response.json()
            
            if "choices" in response_data and len(response_data["choices"]) > 0:
                updated_response = response_data["choices"][0]["message"]["content"]
                # Update the last assistant message
                for i in range(len(self.conversation_history) - 1, -1, -1):
                    if self.conversation_history[i]["role"] == "assistant":
                        self.conversation_history[i]["content"] = updated_response
                        break
                else:
                    # If no assistant message found, add new one
                    self.conversation_history.append({"role": "assistant", "content": updated_response})
                
                return {
                    "status": "success",
                    "query": query,
                    "response": updated_response,
                    "function_result": function_result
                }
        
        # Return the original response if no function was executed
        # Return the original response if no function was executed
        return {
            "status": "success",
            "query": query,
            "response": parsed_result["response"]
        }
    
    def generate_investment_chart(self, investment_result):
        """
        Generate a chart for investment growth projection.
        
        Args:
            investment_result (dict): Result from calculate_investment_growth
            
        Returns:
            str: Base64 encoded image
        """
        try:
            if investment_result["status"] != "success":
                return None
            
            data = investment_result["data"]
            
            # Extract data points
            years = [year for year, _ in data["yearly_balances"]]
            balances = [balance for _, balance in data["yearly_balances"]]
            contributions = [contrib for _, contrib in data["yearly_contributions"]]
            interests = [interest for _, interest in data["yearly_interests"]]
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            
            # Plot lines
            plt.plot(years, balances, 'b-', linewidth=2, label='Total Balance')
            plt.plot(years, contributions, 'g-', linewidth=2, label='Contributions')
            plt.plot(years, interests, 'r-', linewidth=2, label='Interest Earned')
            
            # Fill areas
            plt.fill_between(years, 0, contributions, color='g', alpha=0.3)
            plt.fill_between(years, contributions, [contributions[i] + interests[i] for i in range(len(contributions))], color='r', alpha=0.3)
            
            # Labels and formatting
            plt.title('Investment Growth Projection', fontsize=16)
            plt.xlabel('Years', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend()
            
            # Format y-axis as currency
            from matplotlib.ticker import FuncFormatter
            def currency_formatter(x, pos):
                if x >= 1000000:
                    return '${:,.1f}M'.format(x / 1000000)
                elif x >= 1000:
                    return '${:,.0f}K'.format(x / 1000)
                else:
                    return '${:,.0f}'.format(x)
            
            plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_formatter))
            
            # Save to a bytes buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            plt.close()
            
            # Encode the image to base64
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            return None
    
    def generate_retirement_chart(self, retirement_result):
        """
        Generate a chart for retirement planning.
        
        Args:
            retirement_result (dict): Result from calculate_retirement_needs
            
        Returns:
            str: Base64 encoded image
        """
        try:
            if retirement_result["status"] != "success":
                return None
            
            data = retirement_result["data"]
            
            # Create data for visualization
            years_to_retirement = data["years_to_retirement"]
            years_in_retirement = data["years_in_retirement"]
            
            # Create data points for accumulation phase
            accumulation_years = list(range(years_to_retirement + 1))
            savings_growth = [data["current_savings"] * ((1 + data["required_monthly_contribution"] / data["current_savings"]) ** year) 
                             for year in accumulation_years]
            
            # Create the plot (two subplots)
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            
            # Accumulation phase plot
            ax1.plot(accumulation_years, savings_growth, 'b-', linewidth=2)
            ax1.set_title('Retirement Savings Accumulation Phase', fontsize=14)
            ax1.set_xlabel('Years until Retirement', fontsize=12)
            ax1.set_ylabel('Projected Savings ($)', fontsize=12)
            ax1.grid(True, linestyle='--', alpha=0.7)
            
            # Add target line
            ax1.axhline(y=data["retirement_corpus_needed"], color='r', linestyle='--', label='Required Amount')
            ax1.legend()
            
            # Distribution phase plot - simple drawdown visualization
            retirement_years = list(range(years_in_retirement + 1))
            annual_withdrawal = data["future_annual_expenses"]
            
            # Simple linear drawdown model
            starting_balance = data["total_future_value"]
            withdrawals = [starting_balance - (annual_withdrawal * year) for year in retirement_years]
            # Ensure no negative values
            withdrawals = [max(0, w) for w in withdrawals]
            
            ax2.plot(retirement_years, withdrawals, 'g-', linewidth=2)
            ax2.set_title('Retirement Distribution Phase', fontsize=14)
            ax2.set_xlabel('Years in Retirement', fontsize=12)
            ax2.set_ylabel('Remaining Savings ($)', fontsize=12)
            ax2.grid(True, linestyle='--', alpha=0.7)
            
            # Format y-axis as currency for both plots
            from matplotlib.ticker import FuncFormatter
            def currency_formatter(x, pos):
                if x >= 1000000:
                    return '${:,.1f}M'.format(x / 1000000)
                elif x >= 1000:
                    return '${:,.0f}K'.format(x / 1000)
                else:
                    return '${:,.0f}'.format(x)
            
            ax1.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
            ax2.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to a bytes buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            plt.close()
            
            # Encode the image to base64
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            return None
    
    def generate_budget_chart(self, budget_result):
        """
        Generate a chart for budget analysis.
        
        Args:
            budget_result (dict): Result from analyze_budget
            
        Returns:
            str: Base64 encoded image
        """
        try:
            if budget_result["status"] != "success":
                return None
            
            data = budget_result["data"]
            
            # Extract data for visualization
            categories = list(data["category_percentages"].keys())
            percentages = list(data["category_percentages"].values())
            
            # Sort by percentage (descending)
            sorted_data = sorted(zip(categories, percentages), key=lambda x: x[1], reverse=True)
            categories = [item[0] for item in sorted_data]
            percentages = [item[1] for item in sorted_data]
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
            
            # Pie chart of expense categories
            ax1.pie(percentages, labels=categories, autopct='%1.1f%%', startangle=90, 
                   shadow=False, explode=[0.1 if i == 0 else 0 for i in range(len(categories))])
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            ax1.set_title('Expense Distribution', fontsize=14)
            
            # 50/30/20 rule comparison chart
            rule_labels = ['Needs', 'Wants', 'Savings/Debt']
            actual_values = [data["rule_assessment"]["needs"]["actual"], 
                            data["rule_assessment"]["wants"]["actual"], 
                            data["rule_assessment"]["savings_debt"]["actual"]]
            recommended_values = [data["rule_assessment"]["needs"]["recommended"], 
                                 data["rule_assessment"]["wants"]["recommended"], 
                                 data["rule_assessment"]["savings_debt"]["recommended"]]
            
            x = np.arange(len(rule_labels))
            width = 0.35
            
            ax2.bar(x - width/2, actual_values, width, label='Actual', color='skyblue')
            ax2.bar(x + width/2, recommended_values, width, label='Recommended', color='lightgreen')
            
            ax2.set_ylabel('Percentage of Income', fontsize=12)
            ax2.set_title('50/30/20 Rule Comparison', fontsize=14)
            ax2.set_xticks(x)
            ax2.set_xticklabels(rule_labels)
            ax2.legend()
            
            # Add percentage labels on bars
            for i, v in enumerate(actual_values):
                ax2.text(i - width/2, v + 1, f"{v:.1f}%", ha='center', fontsize=9)
            
            for i, v in enumerate(recommended_values):
                ax2.text(i + width/2, v + 1, f"{v:.1f}%", ha='center', fontsize=9)
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to a bytes buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            plt.close()
            
            # Encode the image to base64
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            return None
    
    def generate_loan_chart(self, loan_result):
        """
        Generate a chart for loan payments.
        
        Args:
            loan_result (dict): Result from calculate_loan_payment
            
        Returns:
            str: Base64 encoded image
        """
        try:
            if loan_result["status"] != "success":
                return None
            
            data = loan_result["data"]
            
            # Extract amortization schedule
            schedule = data["schedule"]
            payment_numbers = [item["payment_number"] for item in schedule]
            principal_payments = [item["principal_paid"] for item in schedule]
            interest_payments = [item["interest_paid"] for item in schedule]
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
            
            # Pie chart of total cost breakdown
            labels = ['Principal', 'Interest']
            sizes = [data["monthly_payment"] * data["total_payments"] - data["total_interest"], data["total_interest"]]
            explode = (0, 0.1)  # only "explode" the interest slice
            
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                   shadow=False, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            ax1.set_title('Total Loan Cost Breakdown', fontsize=14)
            
            # Bar chart showing principal vs interest over time
            width = 0.35
            
            ax2.bar(payment_numbers, principal_payments, width, label='Principal')
            ax2.bar(payment_numbers, interest_payments, width, bottom=principal_payments, label='Interest')
            
            ax2.set_xlabel('Payment Number', fontsize=12)
            ax2.set_ylabel('Payment Amount ($)', fontsize=12)
            ax2.set_title('Principal vs Interest Payments', fontsize=14)
            ax2.legend()
            
            # Format y-axis as currency
            from matplotlib.ticker import FuncFormatter
            def currency_formatter(x, pos):
                return '${:,.0f}'.format(x)
            
            ax2.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
            
            # Adjust layout
            plt.tight_layout()
            
            # Save to a bytes buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            plt.close()
            
            # Encode the image to base64
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            return None
    
    def generate_stock_chart(self, stock_result):
        """
        Generate a chart for stock data.
        
        Args:
            stock_result (dict): Result from get_stock_data
            
        Returns:
            str: Base64 encoded image
        """
        try:
            if stock_result["status"] != "success":
                return None
            
            data = stock_result["data"]
            
            # Check if we have historical data
            if not data["historical_data"] or "Close" not in data["historical_data"]:
                return None
            
            # Extract historical data
            close_data = data["historical_data"]["Close"]
            dates = list(close_data.keys())
            prices = list(close_data.values())
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            
            # Plot line
            plt.plot(dates, prices, 'b-', linewidth=2)
            
            # Add markers for starting and ending points
            plt.plot(dates[0], prices[0], 'go', markersize=8)  # starting point
            plt.plot(dates[-1], prices[-1], 'ro', markersize=8)  # ending point
            
            # Calculate percent change
            percent_change = ((prices[-1] - prices[0]) / prices[0]) * 100
            
            # Labels and formatting
            plt.title(f'{data["name"]} ({data["sector"]}) - Price History', fontsize=16)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Price ($)', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Add text annotation for percent change
            text_color = 'green' if percent_change >= 0 else 'red'
            plt.figtext(0.15, 0.85, f"Change: {percent_change:.2f}%", 
                       fontsize=12, color=text_color, 
                       bbox=dict(facecolor='white', alpha=0.8, boxstyle='round'))
            
            # Format y-axis as currency
            from matplotlib.ticker import FuncFormatter
            def currency_formatter(x, pos):
                return '${:,.2f}'.format(x)
            
            plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_formatter))
            
            # Format x-axis dates
            plt.gcf().autofmt_xdate()
            
            # Save to a bytes buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            plt.close()
            
            # Encode the image to base64
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            return None
        
def main():
    print("Welcome to the Financial Advisor Chatbot!")
    print("Type 'exit' to end the conversation.")
    
    bot = FinancialAdvisorBot()
    
    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in ["exit", "quit"]:
            print("Goodbye! Have a great day!")
            break
        
        response = bot.process_query(user_query)
        
        if response["status"] == "success":
            print("\nBot:", response["response"])
            
            # If there's a function result, display it
            if "function_result" in response and response["function_result"]:
                print("\n[Function Output]")
                print(json.dumps(response["function_result"], indent=4))
        else:
            print("\nBot: Sorry, I couldn't process your request.")

if __name__ == "__main__":
    main()
