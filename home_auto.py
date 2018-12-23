# wiring of RPi GPIO and PIR from https://maker.pro/raspberry-pi/tutorial/how-to-interface-a-pir-motion-sensor-with-raspberry-pi-gpio

# Phillips hue bridge token generation explanation used from https://www.sitebase.be/generate-phillips-hue-api-token
# Got bridge API from https://www.meethue.com/api/nupnp
# went to API debugger at https://<bridge ip address>/debug/clip.html and used message body {"devicetype":"my_hue_app#hue app"}
# Pressed the button my my bridge and pushed the post butoon on the debugger
# The username is the token used in the code below: "BfZXAjqZucSSHkjv0sS3D2UPvKHtZsR6Kp101K"


import RPi.GPIO as GPIO
import time, requests, json, bluetooth
from twilio.rest import Client

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# PIR & Hue configs
pin = 17
GPIO.setup(pin, GPIO.IN)
bridge_url = "http://192.168.1.78"
body = {}
user = ""
# GET
sitting_room_light = "/api/" + user + "/lights/3"
# PUT
sitting_room_light_state = "/api/" + user + "/lights/3/state"
start_time = time.time()
current_state = 0
previous_state = 0

# Twilio account details
account_sid = ""
auth_token = ""
my_num = ""
other_num = ""
im_home = False
other_home = False

client = Client(account_sid, auth_token)

try:
    print "Waiting for PIR to settle..."
    while GPIO.input(pin) == 1:
        current_state = 0
    print "Ready"
    while True:
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

        # This code is responsible for checking for motion with the PIR & then turning on / off a light
        if im_home or other_home:
            current_state = GPIO.input(pin)
            if current_state == 1 and previous_state == 0:
                print "Motion detected!"
                previous_state = 1
                resp = requests.get(bridge_url + sitting_room_light)
                if not resp.json()['state']['on']:
                    print "Light turned on"
                    body = json.dumps({"on": True})
                    req = requests.put(bridge_url + sitting_room_light_state, data=body)
                start_time = time.time()
            elif current_state == 0 and previous_state == 1:
                previous_state = 0
            else:
                resp = requests.get(bridge_url + sitting_room_light)
                if resp.json()['state']['on']:
                    print str(900 - (time.time() - start_time)) + " seconds left untill the lights turn off"
                if time.time() - start_time >= 900 and resp.json()['state']['on']:
                    print "60 seconds are up and the light will be turned off now"
                    body = json.dumps({"on": False})
                    req = requests.put(bridge_url + sitting_room_light_state, data = body)
                    start_time = time.time()
        time.sleep(1)

except KeyboardInterrupt:
   print "Quit"
   GPIO.cleanup()
