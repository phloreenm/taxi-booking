from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from mailing import Mailer
from database import MongoDB
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

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
        mongodb.insert_document('taxi_booking', form_data)  # Change collection name as necessary

        # Send confirmation email to client
        mailer.send_email('Booking Confirmation',
                          app.config['MAIL_USERNAME'],
                          [form_data['email']],
                          "Your booking has been confirmed.")

        # Send booking details to driver
        mailer.send_email('New Booking',
                          app.config['MAIL_USERNAME'],
                          ['anthimosm@yahoo.com'],  # Change this to the actual driver's email
                          f"New booking details: {form_data}")

        return redirect(url_for('index'))
    return render_template('booking.html')

if __name__ == '__main__':
    mongodb.test_connection()  # Test the MongoDB connection
    app.run(debug=True)
