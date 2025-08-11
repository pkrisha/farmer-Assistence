from flask import Flask, request, render_template, Response
from twilio.twiml.messaging_response import MessagingResponse
import requests
import mysql.connector
import re  
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename


app = Flask(__name__, template_folder="templates")


OPENWEATHER_API_KEY = "784f5def8f7fa2ca1966b061ef80c2fe"

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'krisha#17',
    'database': 'twilio'
}

@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body").strip().lower()
    print(f"Received: {incoming_msg}")

    response = MessagingResponse()
    msg = response.message()

    #  Main Menu
    if incoming_msg in ["hi", "hello", "menu"]:
        msg.body(
            "👋 *Welcome to AgriChat* — Your Farm Assistant 🤖\n\n"
            "*You can send the following messages:*\n"
            "1️⃣ *weather in <city>* – Get live weather updates 🌦️\n"
            "2️⃣ *loan <Loan_ID>* – Check your loan status and details 💰\n"
            "3️⃣ *help* – Show this guide again ❓\n\n"
            
        )

    # Weather
    elif incoming_msg.startswith("weather in"):
        city = incoming_msg.replace("weather in", "").strip()
        if city:
            msg.body(get_weather(city))
        else:
            msg.body("⚠️ Please enter the city like: *weather in Mumbai*")

    #  Loan
    elif incoming_msg.startswith("loan"):
        loan_id = incoming_msg.replace("loan", "").strip().upper()
        if loan_id:
            msg.body(get_loan_info(loan_id))
        else:
            msg.body("⚠️ Please enter your loan ID like: *loan xqd20111216*")

    # Help
    elif incoming_msg == "help":
        msg.body(
            "🆘 *Help Guide:*\n\n"
            "📍 *Check Weather:*\n"
            "→ Type: *weather in <city>*\n"
            "→ Example: *weather in Delhi*\n\n"
            "📍 *Check Loan Info:*\n"
            "→ Type: *loan <Loan_ID>*\n"
            "→ Example: *loan xqd20111216*\n\n"
            "📍 *See Menu:*\n"
            "→ Type: *menu* or *hi*"
        )

    # Invalid Input
    else:
        msg.body(
            "❌ Sorry, I didn't understand that.\n\n"
            "📖 *Here's what you can do:*\n"
            "- *weather in <city>* → Get weather updates\n"
            "- *loan <Loan_ID>* → Check your loan status\n"
            "- *help* → Get help menu\n\n"
            "ℹ️ Example: *loan xqd20111216*"
        )

    return str(response)

#  Weather Info
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url)
        data = res.json()
        if data["cod"] != 200:
            return f"⚠️ Couldn't find weather for '{city}'."
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"].title()
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        return (
            f"🌤️ *Weather in {city.title()}*\n"
            f"🌡️ Temp: {temp}°C\n"
            f"☁️ Condition: {desc}\n"
            f"💧 Humidity: {humidity}%\n"
            f"🌬️ Wind: {wind} m/s"
        )
    except:
        return "❌ Error fetching weather. Try again later."

# Loan Info from MySQL
def get_loan_info(loan_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM krishi_loan WHERE Loan_ID = %s", (loan_id,))
        loan = cursor.fetchone()
        conn.close()

        if not loan:
            return f"❌ No loan found with ID '{loan_id}'."

        return (
            f"📋 *Loan Details:*\n"
            f"📌 Loan ID: {loan['Loan_ID']}\n"
            f"💼 Status: {loan['loan_status']}\n"
            f"💰 Principal: ₹{loan['Principal']}\n"
            f"📆 Terms: {loan['terms']} days\n"
            f"🗓️ Effective: {loan['effective_date']}\n"
            f"📅 Due: {loan['due_date']}\n"
            f"⏱️ Paid Off: {loan['paid_off_time']}\n"
            f"⚠️ Overdue: {loan['past_due_days']} days\n"
            f"👤 Borrower Age: {loan['age']}"
        )
    except Exception as e:
        print("DB Error:", e)
        return "❌ Could not fetch loan info. Please try again later."




@app.route("/test", methods=["GET", "POST"])
def test():
    reply = ""
    if request.method == "POST":
        form_msg = request.form.get("Body")
        with app.test_request_context('/sms', method='POST', data={'Body': form_msg}):
            xml_response = sms_reply()
            body_match = re.search(r'<Body>(.*?)</Body>', xml_response, re.DOTALL)
            if body_match:
                reply = body_match.group(1)
            else:
                reply = "Error processing response"
    return render_template("test.html", reply=reply)

@app.route('/finance', methods=['GET', 'POST'])
def finance():
    result = None
    eligible = None
    recommendation = None
    recommended_banks = []
    
    if request.method == 'POST':
        # Get form data
        farm_size = float(request.form.get('farm_size', 0))
        annual_income = float(request.form.get('annual_income', 0))
        years_farming = int(request.form.get('years_farming', 0))
        credit_score = int(request.form.get('credit_score', 0))
        existing_debt = float(request.form.get('existing_debt', 0))
        crop_type = request.form.get('crop_type', '')
        collateral_value = float(request.form.get('collateral_value', 0))
        
        # Calculate debt-to-income ratio
        debt_to_income = (existing_debt / annual_income) if annual_income > 0 else float('inf')
        
        # Calculate eligibility score (0-100)
        score = 0
        
        # Credit score impact (0-25 points)
        if credit_score >= 750:
            score += 25
        elif credit_score >= 700:
            score += 20
        elif credit_score >= 650:
            score += 15
        elif credit_score >= 600:
            score += 10
        elif credit_score >= 550:
            score += 5
        
        # Farming experience (0-20 points)
        if years_farming >= 10:
            score += 20
        elif years_farming >= 5:
            score += 15
        elif years_farming >= 3:
            score += 10
        elif years_farming >= 1:
            score += 5
        
        # Debt-to-income ratio (0-25 points)
        if debt_to_income <= 0.2:
            score += 25
        elif debt_to_income <= 0.3:
            score += 20
        elif debt_to_income <= 0.4:
            score += 15
        elif debt_to_income <= 0.5:
            score += 10
        elif debt_to_income <= 0.6:
            score += 5
        
        # Farm size relative to income (0-15 points)
        income_per_acre = annual_income / farm_size if farm_size > 0 else 0
        if income_per_acre >= 2000:
            score += 15
        elif income_per_acre >= 1500:
            score += 12
        elif income_per_acre >= 1000:
            score += 9
        elif income_per_acre >= 500:
            score += 6
        elif income_per_acre > 0:
            score += 3
        
        # Collateral adequacy (0-15 points)
        collateral_ratio = collateral_value / existing_debt if existing_debt > 0 else float('inf')
        if collateral_ratio >= 2.0:
            score += 15
        elif collateral_ratio >= 1.5:
            score += 12
        elif collateral_ratio >= 1.0:
            score += 9
        elif collateral_ratio >= 0.75:
            score += 6
        elif collateral_ratio > 0:
            score += 3
        
        # Set result
        result = score
        
        # Determine eligibility status and bank recommendations
        if score >= 80:
            eligible = "Highly Eligible"
            recommendation = "You have a strong application. Consider applying for premium loan products with favorable terms."
            recommended_banks = [
                {
                    "name": "AgriBank Premier",
                    "description": "Offers premium agricultural loans with low interest rates and flexible terms for high-quality applicants.",
                    "interest_rate": "3.2% - 4.5%",
                    "max_loan": "$1,500,000",
                    "special_features": "No prepayment penalties, harvest-time payment schedules, interest-only periods available"
                },
                {
                    "name": "FarmCredit Elite",
                    "description": "Specialized in large-scale agricultural financing with competitive rates and personalized service.",
                    "interest_rate": "3.5% - 4.8%",
                    "max_loan": "$2,000,000",
                    "special_features": "Equipment financing, land acquisition loans, operating lines of credit"
                },
                {
                    "name": "Rural Development Bank",
                    "description": "Government-backed loans with some of the best terms available for qualified farmers.",
                    "interest_rate": "2.9% - 4.2%",
                    "max_loan": "$1,750,000",
                    "special_features": "Extended repayment terms, drought/disaster relief programs, beginning farmer incentives"
                }
            ]
        elif score >= 60:
            eligible = "Eligible"
            recommendation = "You qualify for standard agricultural loans. Submit your application with complete documentation."
            recommended_banks = [
                {
                    "name": "Heartland Farm Credit",
                    "description": "Offers solid loan products designed for established farming operations.",
                    "interest_rate": "4.5% - 6.0%",
                    "max_loan": "$750,000",
                    "special_features": "Seasonal payment schedules, equipment financing, refinancing options"
                },
                {
                    "name": "Community Agricultural Bank",
                    "description": "Local lender with good understanding of regional farming needs and challenges.",
                    "interest_rate": "4.8% - 6.2%",
                    "max_loan": "$500,000",
                    "special_features": "Local decision-making, flexible collateral options, personalized service"
                },
                {
                    "name": "Farm Service Agency",
                    "description": "Government-backed loans with reasonable terms for qualified farmers.",
                    "interest_rate": "3.5% - 5.5%",
                    "max_loan": "$600,000",
                    "special_features": "Low down payments, longer terms, targeted programs for specific needs"
                }
            ]
        elif score >= 40:
            eligible = "Conditionally Eligible"
            recommendation = "You may qualify with additional collateral or a co-signer. Consider government-backed loan programs."
            recommended_banks = [
                {
                    "name": "Farm Service Agency - Beginning Farmer Program",
                    "description": "Specialized government program designed to help farmers with limited financial resources.",
                    "interest_rate": "4.0% - 6.0%",
                    "max_loan": "$300,000",
                    "special_features": "Down payment assistance, extended terms, training/mentorship programs"
                },
                {
                    "name": "Rural Credit Union",
                    "description": "Member-owned financial institution with more flexible lending standards.",
                    "interest_rate": "5.5% - 7.5%",
                    "max_loan": "$250,000",
                    "special_features": "Member benefits, smaller loans available, financial education resources"
                },
                {
                    "name": "Community Development Financial Institution",
                    "description": "Mission-driven lender focused on underserved agricultural communities.",
                    "interest_rate": "5.0% - 7.0%",
                    "max_loan": "$200,000",
                    "special_features": "Technical assistance, flexible terms, focus on sustainable agriculture"
                }
            ]
        else:
            eligible = "Not Currently Eligible"
            recommendation = "Work on improving your credit score and reducing existing debt before applying. Consider consulting with an agricultural financial advisor."
            recommended_banks = [
                {
                    "name": "Farm Credit Counseling Services",
                    "description": "Not a lender, but offers financial counseling to help improve eligibility for future loan applications.",
                    "interest_rate": "N/A",
                    "max_loan": "N/A",
                    "special_features": "Credit repair strategies, debt management plans, business planning assistance"
                },
                {
                    "name": "USDA Farm Service Agency - Microloans",
                    "description": "Small loan program with more accessible requirements for beginning farmers.",
                    "interest_rate": "5.0% - 7.0%",
                    "max_loan": "$50,000",
                    "special_features": "Simplified application process, mentoring and financial training"
                }
            ]
    
    return render_template('finance.html', result=result, eligible=eligible, recommendation=recommendation, recommended_banks=recommended_banks)


# the website routes 
@app.route('/')
def index():
    """Route for the home page"""
    return render_template('index.html', title='Home')

@app.route('/about')
def about():
    """Route for the about page"""
    return render_template('about.html', title='About')





@app.route('/weather')
def weather():
    return render_template('weather.html')

@app.route('/fertilizer')
def fertilizer():
    return render_template('fertilizer.html')






  
# Run the application
if __name__ == "__main__":
    app.run(port=5000, debug=True)