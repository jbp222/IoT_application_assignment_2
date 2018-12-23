# wiring of RPi GPIO and PIR from https://maker.pro/raspberry-pi/tutorial/how-to-interface-a-pir-motion-sensor-with-raspberry-pi-gpio

# Phillips hue bridge token generation explanation used from https://www.sitebase.be/generate-phillips-hue-api-token
# Got bridge API from https://www.meethue.com/api/nupnp
# went to API debugger at https://<bridge ip address>/debug/clip.html and used message body {"devicetype":"my_hue_app#hue app"}
# Pressed the button my my bridge and pushed the post butoon on the debugger
# The username is the token used in the code below: "BfZXAjqZucSSHkjv0sS3D2UPvKHtZsR6Kp101K"

# tp-link HS100 smart plug used, code used to access tp-link api used from: itnerd.space/2017/06/19$

# bug in the Kasa api: you have to set a timer via the app once, so that there is a timer id availa$

# itnerd.space blog, step-by-step instructions
# 1. Get the auth token - do a  POST request with the payload inserted into the body, Kasa app down$
#    The terminal UUID bit had to be generated using uuidgenerator.net/version4
# 2. Get endpoint URL and deviceId - use a curl request as per the webiste in the terminal
# 3. Get rule id, this is an id for the timer of the plug

# Not storing any of the keys in this file for security as file will be pushed to public Github account. keys stored locally only in their own file

import RPi.GPIO as GPIO
import time, requests, json, bluetooth, datetime
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
hue_temp_sensor = "/api/" + user + "/sensors/9"
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

twilio_client = Client(account_sid, auth_token)

# tp-link config
plug_body = json.dumps({"method": "login", "params": {"appType": "Kasa_Android", "cloudUserName": "", "cloudPassword": "", "t$
token_response = requests.post("https://wap.tplinkcloud.com", data=plug_body)
token = str(token_response.json()['result']['token'])

url = "https://eu-wap.tplinkcloud.com/?token=" + token
deviceId = ""

postbody = json.dumps({"method": "passthrough", "params": {"deviceId": deviceId, "requestData": "{\"count_down\":{\"get_rules\": null}}"}})
result = requests.post(url, data=postbody)
ruleId = str(json.loads(result.json()['result']['responseData'])['count_down']['get_rules']['rule_list'][0]['id'])

on = False
on_time = 22
off_time = 23

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
            twilio_client.messages.create(body="Julianne is home", from_="MyHomeApp", to=other_num)
            im_home = True
            other_home = False
        elif (my_phone == None and other_phone != None and other_home == False):
            print "SMS sent to me"
            twilio_client.messages.create(body="Darren is home", from_="MyHomeApp", to=my_num)
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

            # Code for smart plug

            # act = 0 = power off | 1 = power on (after the timer)
            # enable = 0 = disable, 1 = enable (the timer)
            # delay = timer of the delay in seconds

            hour = datetime.datetime.today().hour
            temp_resp = requests.get(bridge_url + hue_temp_sensor)
            temp = int(str(temp_resp.json()["state"]["temperature"])[0:2])

            if hour >= on_time and hour <= off_time and not on:
                if temp >= 10:
                    act = 1
                    enable = 1
                    delay = 1
                    timerBody = json.dumps({"method": "passthrough", "params": {"deviceId": deviceId, "requestData": "{\"count_down\":$
                    response = requests.post(url, data=timerBody)
                    time.sleep(5)
                    print "turning plug on..."
                    act = 0
                    enable = 1
                    delay = 360
                    timerBody = json.dumps({"method": "passthrough", "params": {"deviceId": deviceId, "requestData": "{\"count_down\":$
                    response = requests.post(url, data=timerBody)
                    print "1 hour timer set"
                    on = True
            elif hour < on_time and hour > off_time:
                on = False
        time.sleep(1)

except KeyboardInterrupt:
   print "Quit"
   GPIO.cleanup()



