from twilio.rest import Client

# Twilio credentials
account_sid = 'account'
auth_token = 'token'
twilio_number = 'phoneno'

# List of recipient numbers
phone_numbers = [
    '+911223xxxxxx',
    '+919212xxxxx'  # your number for testing
]

# Message to send
welcome_message = (
   " 👋 Welcome to AGRI_GUIDE!\n\n"

   "📱 To begin, simply type *hi* and send it to: this phone no\n " 
    "I'm here to assist you every step of the way 😊"

)


client = Client(account_sid, auth_token)


for number in phone_numbers:
    message = client.messages.create(
        body=welcome_message,
        from_=twilio_number,
        to=number
    )
    print(f"✅ Message sent to {number}. SID: {message.sid}")
