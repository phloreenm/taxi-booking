from flask_mail import Message, Mail

class Mailer:
    def __init__(self, app):
        self.mail = Mail(app)

    def send_email(self, subject, sender, recipients, body, html=None):
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = body
        if html:
            msg.html = html
        self.mail.send(msg)
