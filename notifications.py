from twilio.rest import Client
import os
# from dotenv import load_dotenv

# load_dotenv()

# Your Account SID from twilio.com/console
account_sid = os.getenv('ACCOUNT_SID')
# "AC31c262395aaef2cc582c6eb4ef1de1a8"
# Your Auth Token from twilio.com/console
auth_token  = os.getenv('AUTH_TOKEN')
# "ca2a25e6f1924da875e868f2a3a59eea"
client = Client(account_sid, auth_token)
twilio_no = os.getenv('TWILIO_NUM')

def send_message(number, msg):

    # client.messages.create(
    #     to="+1" + number, 
    #     from_=twilio_no,
    #     body=msg)
    
    client.messages.create(
        to="+1" + number, 
        from_=twilio_no,
        body=msg)

# def verify_acct (name, number):
#     client.validation_requests \
#                            .create(
#                                 friendly_name=name,
#                                 phone_number='+1' + number
#                             )


