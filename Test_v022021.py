from smbus import SMBus
import sys
sys.path.append('/home/pi/ADI_Project/dependencies/mlx90614/')
from mlx90614 import MLX90614
import time
import evdev
from evdev import categorize, ecodes
import csv
import os.path
from os import path

dataIn = 0
IDnum = ""
temp = ""
bus = SMBus(1)
sensor = MLX90614(bus, address=0x5A)
Employee = ""
isReg = 0
isDup = 0
T1 = 0
isHighTemp = 0;
Remarks = ""
fileMade = 0

########Manifesto File Name Edits#############
Shuttle_route = "Dasma_Bayan1"
named_tuple = time.localtime()
Time = time.strftime("%H:%M:%S", named_tuple)
Date = time.strftime("%m_%d_%Y", named_tuple)
filename = Shuttle_route + "_" + Date +".csv"
##############################################


class Device():
    name = 'USB Reader USB Reader'
 
    @classmethod
    def list(cls, show_all=False):
        # list the available devices
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        if show_all:
            for device in devices:
                print("event: " + device.fn, "name: " + device.name, "hardware: " + device.phys)
        return devices
 
    @classmethod
    def connect(cls):
        # connect to device if available
        try:
            device = [dev for dev in cls.list() if cls.name in dev.name][0]
            device = evdev.InputDevice(device.fn)
            return device
        except IndexError:
            print("Device not found.\n - Check if it is properly connected. \n - Check permission of /dev/input/ (see README.md)")
            exit()
 
    @classmethod
    def run(cls):
        device = cls.connect()
        container = []
        global dataIn
        global temp
        try:
            device.grab()
            # bind the device to the script
            for event in device.read_loop():
                    # enter into an endeless read-loop
                    if event.type == ecodes.EV_KEY and event.value == 1:
                        digit = evdev.ecodes.KEY[event.code]
                        if digit == 'KEY_ENTER':
                            # create and dump the tag
                            dataIn = 1
                            tag = "".join(i.strip('KEY_') for i in container)
                            #print("RFID Number: " + tag)
                            temp = tag
                            container = []
                            break
                        else:
                            container.append(digit)
        except:
            # catch all exceptions to be able release the device
            device.ungrab()
            print('Quitting.')
            
def getTemp():
    global T1
    global isHighTemp
    global Remarks
    
    T1 = sensor.get_object_1()
    T1 = round(T1,2)
    if T1> 37.50:
        isHighTemp = 1
        Remarks = "Above normal Temperature"
    else:
        isHighTemp = 0
        Remarks = "Normal Temperature"

def checkEmployee():
    global Employee
    global IDnum
    global temp
    global isReg
    temp = temp.lstrip("0")
    with open('/home/pi/ADI_Project/employees.csv') as csv_file:
        csv_read = csv.reader(csv_file, delimiter=',')
        for row in csv_read:
            #print(row)
            if temp in row[0]:
                Employee = row[3] + " " + row[4] + ". " + row[2]
                IDnum = row[1]
                isReg = 1
                break
            else:
                isReg = 0
                Employee = "Unregistered Employee"
                IDnum = "Unregistered ID"
    
def checkDuplicate():
    global IDnum
    global filename
    global isDup
    if os.path.isfile(filename):
        with open(filename) as csv_file:
            csv_read = csv.reader(csv_file, delimiter=',')
            for row in csv_read:
                #print(row)
                if IDnum in row[0]:
                    isDup = 1
                    break
                else:
                    isDup = 0
     
def writeAttendance():
    global IDnum
    global T1
    global Remarks
    global Time
    if path.exists(filename) == False:
        with open(filename, mode='w') as csv_file:
            header = ['ID Number', 'Temperature', 'Time in', 'Remarks'] 
            writer = csv.DictWriter(csv_file, fieldnames = header) 
          
            # writing data row-wise into the csv file 
            writer.writeheader() 
            writer.writerow({'ID Number': IDnum,
                             'Temperature': T1,
                             'Time in': Time,
                             'Remarks': Remarks})
            csv_file.close()
    else:
        with open(filename, mode='a+') as csv_file:
            header = ['ID Number', 'Temperature', 'Time in', 'Remarks'] 
            writer = csv.DictWriter(csv_file, fieldnames = header) 
          
            # writing data row-wise into the csv file 
            #writer.writeheader() 
            writer.writerow({'ID Number': IDnum,
                             'Temperature': T1,
                             'Time in': Time,
                             'Remarks': Remarks})
            csv_file.close()
while 1:            
    Device.run()
    if dataIn == 1:
        getTemp()
        checkEmployee()
        checkDuplicate()
        if isDup == 1:
            print("Error: Tap Duplicate")
            print()
        if isReg == 1 and isHighTemp == 0 and isDup == 0:
            print("Name: " + Employee)
            print("ID Number: " + IDnum)
            print ("Body Temperature:", T1)
            print("Remarks: Cleared")
            print()
            writeAttendance()
        if isReg == 1 and isHighTemp == 1 and isDup == 0:
            print("Name: " + Employee)
            print("ID Number: " + IDnum)
            print ("Body Temperature:", T1)
            print("Remarks: Advised to go home and seek medical advice.")
            print()
            writeAttendance()
        if isReg == 0:
            print("Unregistered ID")
            print ("Body Temperature:", T1)
            print()
        dataIn = 0
        Employee = ""
        T1 = 0
        IDnum = ""
        
        

        

