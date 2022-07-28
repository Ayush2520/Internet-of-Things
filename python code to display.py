import serial
import wiotp.sdk.device
import time
import random
from datetime import datetime
from datetime import date
import requests


myConfig = { 
    "identity": {
        "orgId": "d7luey",
        "typeId": "SmartParking",
        "deviceId":"12345"
    },
    "auth": {
        "token": "1234567890"
    }
}
vehicles = {"DB:F0:55:22":{"name":"AYUSH KUMAR AGARWAL","mobileno":"9110100868","status":"","in_time":"","out_time":"","slot":""} ,
            "D9:05:6C:99":{"name":"AYUSH KUMAR SINGH","mobileno":"9304352553","status":"","in_time":"","out_time":"","slot":""}
            }

slotsBooked = {"slot1":"NO","slot2":"NO","slot1rfid":"NONE","slot2rfid":"NONE"}


slot1 = "EMPTY"
slot2 = "EMPTY"
recentActivity = ""
booking = 0



def checkBookingTimings():
    global slot1
    global slot2
    global booking
    global recentActivity
    print('mai idhar h')
    s1 = slotsBooked["slot1rfid"]
    s2 = slotsBooked["slot2rfid"]
    a = []
    a = list(vehicles.keys())
    if(s1 != "NONE"):
        if s1 in a:
            timebooked = vehicles[s1]["in_time"]
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            time_delta = (datetime.strptime(current_time,'%d/%m/%Y %H:%M:%S') - datetime.strptime(timebooked,'%d/%m/%Y %H:%M:%S'))
            total_seconds = time_delta.total_seconds()
            print(total_seconds)
            if(total_seconds >=120):
                slot1 = "EMPTY"
                vehicles[s1]["in_time"] = ""
                vehicles[s1]["status"] = ""
                vehicles[s1]["slot"] = ""
                booking = booking -1
                recentActivity = "Booking for slot 1 is cancelled"
                nm = vehicles[s1]["name"]
                mn = vehicles[s1]["mobileno"]
                sendSms(nm,mn,recentActivity)
    if(s2 != "NONE"):
        if s2 in a:
            timebooked = vehicles[s2]["in_time"]
            now = datetime.now()
            current_time = now.strftime("%d/%m/%Y %H:%M:%S")
            time_delta = (datetime.strptime(current_time,'%d/%m/%Y %H:%M:%S') - datetime.strptime(timebooked,'%d/%m/%Y %H:%M:%S'))
            total_seconds = time_delta.total_seconds()
            if(total_seconds >=10):
                slot1 = "EMPTY"
                vehicles[s2]["in_time"] = ""
                vehicles[s2]["status"] = ""
                vehicles[s2]["slot"] = ""
                booking = booking -1
                recentActivity = "Booking for slot 2 is cancelled"
                nm = vehicles[s1]["name"]
                mn = vehicles[s1]["mobileno"]
                sendSms(nm,mn,recentActivity)
                
            
            
    

def bookingSlot(slno,rfidno):
    global booking
    global slot1
    global slot2
    a =[]
    a= list(vehicles.keys())
    if rfidno in a:
        vehicles[rfidno]["status"] = "booked"
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        vehicles[rfidno]["in_time"] = current_time
        vehicles[rfidno]["slot"] = slno
        if(slno == '1'):
            slotsBooked["slot1"]= "BOOKED"
            slotsBooked["slot1rfid"] = rfidno
            slot1 = "BOOKED"
            recentActivity = "Slot 1 is Booked"
        elif(slno == '2'):
            slotsBooked["slot2"]= "BOOKED"
            slotsBooked["slot2rfid"] = rfidno
            slot2 = "BOOKED"
        nm = vehicles[rfidno]["name"]
        mn = vehicles[rfidno]["mobileno"]
        recentActivity = "Booking done for slot "+slno
        sendSms(nm,mn,recentActivity)
        booking = booking + 1
        checkSlotStatus(3)

def myCommandCallback(cmd):
    print("Message received from IBM IoT Platform: %s" % cmd.data['command'])
    m=cmd.data['command']
    sl = m[0]
    rn = m[1:len(m)]
    bookingSlot(sl,rn)
    

        

serial1 = serial.Serial('COM4',9600)
client = wiotp.sdk.device.DeviceClient(config=myConfig, logHandlers=None)
client.connect()


def sendSms(nameID,number,msgtype):
        url = 'https://www.fast2sms.com/dev/bulkV2'
        message = 'Hello '+nameID+' '+msgtype
        numbers = number
        payload = f'sender_id=TXTIND&message={message}&route=v3&language=english&numbers={numbers}'
        headers = {
            'authorization':'XZi0uN3hcxTtUnkD7sl9gEo2VARfrjQwGbOW1IvyaP68pL54dJvsR8TQ3mw7N4aCx2dhVOtqEL5KADBp',
            'Content-Type':'application/x-www-form-urlencoded'
            }
        response = requests.request("POST",url=url,data=payload, headers=headers)
        print(response.text)
            

def databaseCheck(rfidno):
    global recentActivity
    a =[]
    a= list(vehicles.keys())
    if rfidno in a:
        print('got it')
        sta = vehicles[rfidno]["status"]
        if(sta == "parked"):
            checkSlotStatus(2)
            now = datetime.now()
            time_out = now.strftime("%d/%m/%Y %H:%M:%S")
            time_in = vehicles[rfidno]["in_time"]
            vehicles[rfidno]["status"] = ""
            vehicles[rfidno]["slot"] = ""
            totalBill = calculateBill(time_in,time_out)
            print('thankyou for using our services and your bill is ', totalBill)
            recAct(rfidno,'left',time_out)
            msg = "thankyou for using our services and your bill is Rs. "+ str(totalBill)
            sendSms(vehicles[rfidno]["name"],vehicles[rfidno]["mobileno"],msg)
            checkSlotStatus(3)
        elif(sta == "denied"):
            print('you cannot enter')
            now = datetime.now()
            timeX = now.strftime("%d/%m/%Y %H:%M:%S")
            recAct(rfidno,'denied',timeX)
            nm = vehicles[rfidno]["name"]
            mn = vehicles[rfidno]["mobileno"]
            sendsms(nm,mn,"YOUR ID IS BLOCKED.. YOU CANNOT ENTER")
        else:
            a = getSlot()
            if(a == "NO SPACE"):
                msg = "sorry parking is full.. try again later"
                sendSms(vehicles[rfidno]["name"],vehicles[rfidno]["mobileno"],msg)
            else:
                now = datetime.now()
                current_time = now.strftime("%d/%m/%Y %H:%M:%S")
                vehicles[rfidno]["in_time"] = current_time
                vehicles[rfidno]["status"] = "parked"
                vehicles[rfidno]["slot"] = a
                print('welcome in')
                checkSlotStatus(1)
                recAct(rfidno,'entered',current_time)
                msg = "Welcome. you have been alloted slot no. "+str(a)+"for your vehicle"
                sendSms(vehicles[rfidno]["name"],vehicles[rfidno]["mobileno"],msg)
                
    else:
        print('no such id exists')
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        recAct(rfidno,'not found in database',current_time)
        
    


def recAct(rNo,oper,time):
    global recentActivity
    recentActivity = "Vehicle NO: "+rNo+" "+oper+" on "+time
    

    
def checkSlotStatus(oper):
    if(oper == 3):
        serial1.write(b'space check')
        ser = serial1.readline().decode()
        checkValue(ser)
    elif(oper == 1):
        serial1.write(b"open gate 1")
        ser = serial1.readline().decode()
        checkValue(ser)
        
    elif(oper == 2):
        serial1.write(b"open gate 2")
        ser = serial1.readline().decode()
        checkValue(ser)
        
def getSlot():
    global slot1
    global slot2
    if (slot1 == "EMPTY"):
        slot1 = "FULL"
        return 1
    elif(slot2 == "EMPTY"):
        slot2 = "FULL"
        return 2
    else:
        return "NO SPACE"

def calculateBill(intime,outtime):
    #rate per second =  Rs. 0.001
    rate = 0.01
    time_delta = (datetime.strptime(outtime,'%d/%m/%Y %H:%M:%S') - datetime.strptime(intime,'%d/%m/%Y %H:%M:%S'))
    total_seconds = time_delta.total_seconds()
    price = total_seconds*rate
    return round(price,2)
    
    	
def checkValue(servalue):
    global slot1
    global slot2
    l = len(servalue)
    abc = servalue[0:l-2]
    
    if (abc == "Both slots are full"):
        slot1 = "FULL"
        slot2 = "FULL"
    elif(abc == "SLOT 1 is full"):
        if(slot2 != "BOOKED"):
            slot1 = "FULL"
            slot2 = "EMPTY"
        else:
            slot1 = "FULL"
    elif(abc == "SLOT 2 is full"):
        if(slot1 != "BOOKED"):
            slot1 = "EMPTY"
            slot2 = "FULL"
        else:
            slot2 = "FULL"
        
    elif(abc == "Both slots are empty"):
        if(slot1 != "BOOKED"):
            slot1 = "EMPTY"
        if(slot2 != "BOOKED"):
            slot2 = "EMPTY"
    elif(servalue[2]==":"):
        databaseCheck(abc)
    elif(abc == "band kar de bhai gate 1 ho gaya"):
        print("Gate 1 is closed")
    elif(abc == "band kar de bhai gate 2 ho gaya"):
        print("Gate 2 is closed")

def receiveValue1():
    ser = serial1.readline().decode()
    checkValue(ser)
    #time.sleep(1)
    
def publishdata():
    myData={'slot1status':slot1,'slot2status':slot2,'recentact':recentActivity}
    client.publishEvent(eventId="status", msgFormat="json", data=myData, qos=0, onPublish=None)
    print("Published data Successfully: %s", myData)
    client.commandCallback = myCommandCallback


while True:
    #checkBookingTimings()
    receiveValue1()
    publishdata()
