from app import mail

def send_email(recipients, title, body):
    time.sleep(0.5)
    if type(recipients) is not list:
        recipients = [recipients]
    msg = Message(title,
            sender=os.getenv('MAIL_USERNAME', 'user@gmail.com'),
            recipients = recipients)
    msg.body = body
    print(body)
    #mail.send(msg)
