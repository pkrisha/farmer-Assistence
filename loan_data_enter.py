from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Database config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'krisha17',
    'database': 'twilio'
}

@app.route("/")
def loan_form():
    return render_template("loan_form.html")

@app.route("/submit-loan", methods=["POST"])
def submit_loan():
    data = request.form

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
        INSERT INTO krishi_loan (Loan_ID, loan_status, Principal, terms, effective_date, due_date, paid_off_time, past_due_days, age)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data['Loan_ID'],
            data['loan_status'],
            int(data['Principal']),
            data['terms'],
            data['effective_date'],
            data['due_date'],
            data['paid_off_time'] if data['paid_off_time'] else None,
            int(data['past_due_days']) if data['past_due_days'] else None,
            int(data['age'])
        )

        cursor.execute(query, values)
        conn.commit()

        return "✅ Loan data submitted successfully!"

    except Exception as e:
        return f"❌ Error: {e}"

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(debug=True, port=3000)  
