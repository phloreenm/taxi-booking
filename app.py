from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from bson import ObjectId
from mailing import Mailer
from database import MongoDB
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)


# Set a secret key for the session
app.secret_key = os.getenv('SECRET_KEY')


# Configure Flask app for email
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=int(os.getenv('MAIL_PORT')),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS') == 'True',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
)

# Initialize Mailer
mailer = Mailer(app)

# Initialize MongoDB connection
mongo_uri = os.getenv('MONGO_URI')
mongo_db_name = 'taxi_booking'  # Change as necessary
mongodb = MongoDB(mongo_uri, mongo_db_name)
mongodb.test_connection()  # Optional: to test MongoDB connection at startup


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        mongodb.insert_document('taxi_booking', form_data)  # Use the correct collection name

        # Prepare your email content
        subject = 'Booking Confirmation'
        sender = app.config['MAIL_USERNAME']
        recipients = [form_data['email']]
        text_body = "Your booking has been confirmed, " + form_data['name'] + "! Thank you for choosing us!"
        html_body = """
        <html>
            <body>
                <h1>Booking Confirmed</h1>
                <p>Your booking has been successfully confirmed, {name}! Thank you for choosing us!</p>
                <p>Booking details:</p>
                <ul>
                    <li>Name: {name}</li>
                    <li>Email: {email}</li>
                    <li>Phone: {pickup}</li>
                    <li>Date: {destination}</li>
            </body>
        </html>
        """.format(name=form_data['name'], email=form_data['email'], pickup=form_data['pickup'], destination=form_data['destination'])

        try:
            # Send the confirmation email to the client
            mailer.send_email(subject, sender, recipients, text_body, html=html_body)

            # Optionally, send booking details to the driver
            mailer.send_email('New Booking',
                              app.config['MAIL_USERNAME'],
                              ['premiertaxissalisbury@gmail.com'],
                              f"New booking details: {form_data}")
            # session['booking_details'] = form_data  # Save booking details to session
            # Redirect to the success page if the email is sent successfully
            return redirect(url_for('success'))
        except Exception as e:
            print(f"Failed to send email: {e}")
            # Instead of redirecting, return the booking page with a JavaScript alert
            error_message = "Failed to send email. Please try again later."
            return render_template('booking.html', error_message=error_message)

    return render_template('booking.html')


@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    mongodb.test_connection()  # Test the MongoDB connection
    app.run(debug=True)
