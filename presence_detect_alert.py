import bluetooth
import time
from twilio.rest import Client

# Twilio account details
account_sid = ""
auth_token = ""
client = Client(account_sid, auth_token)

my_num = ""
other_num = ""
im_home = False
other_home = False

while True:
    print "Checking " + time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())

    # My iphone MAC Address
    my_phone = bluetooth.lookup_name('D0:2B:20:7A:DF:F6', timeout=5)
    # Other iphone MAC Address
    other_phone = bluetooth.lookup_name('80:B0:3D:DD:84:FC', timeout=5)

    if (my_phone != None and other_phone != None):
        print "Everyone is home"
        im_home = True
        other_home = True
    elif (my_phone == None and other_phone == None):
        print "Everone is away"
        im_home = False
        other_home = False
    elif (my_phone != None and other_phone == None and im_home == False):
        print "SMS sent to Darren"
        client.messages.create(body="Julianne is home", from_="MyHomeApp", to=other_num)
        im_home = True
        other_home = False
    elif (my_phone == None and other_phone != None and other_home == False):
        print "SMS sent to me"
        client.messages.create(body="Darren is home", from_="MyHomeApp", to=my_num)
        im_home = False
        other_home = True
    elif (my_phone != None and other_phone == None and im_home == True):
         print "I am still home and Darren is away"
        im_home = True
        other_home = False
    elif (my_phone == None and other_phone != None and other_home == True):
        print "Darren is still home and I am away"
        im_home = False
        other_home = True

    # sleep timer used 350 secs in the flow chart
    time.sleep(60)

