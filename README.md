# Smart Home IoT implementation (IoT application assignment 2)

### Author: Julianne Daly, WIT
### Student ID: 20082215
### Proposal document link: https://github.com/jdaly222/IoT_application_assignment_2/blob/master/proposal.md

## Brief overview of project:
* Smart home IoT application using physical devices and sensors incorptorating connected device architecture
* Technologies and tools used to implement the project include Python, Bash, REST api's, Bluetooth, IoT Cloud Platform Twilio, PIR sensor, RPi 3, Smart plug, smart bulb, smart motion sensor with temperature sensor,
  mobile phones
* Functionalities include:
..* bluetooth location based messaging and MAC address identification
..* location and sensor based activation of an electronic device (bluetooth and temperature sensor with smart plug & electic blanket)
..* location and sensor based illumination of light bulb

## Differences between proposal document and final implementation:
* SenseHAT sensor was not used for this project as some GPIO pins were taken up by PIR sensor already
* Temperature instead was measured from a Philips Hue motion sensor which happened to also provide temperature
* Although not explicitly stated on the proposal, initial idea was to identify the MAC address of the mobile phones through the router, however after further research online, mostly via stack overflow, there were issues
  when the phone was inactive (on lock screen for example) that it may not show up as 'home'. Bluetooth was chosen instead as it is more relaible at identiyting the phone device, however it does have it's own limitations 
  in terms of proximity
* Twilio was not implemented via Wia as it turned out that it's implemetation was stright forward without having to use Wia

