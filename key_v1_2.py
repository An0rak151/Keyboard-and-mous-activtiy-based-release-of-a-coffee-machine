#Autor: Maximilian Mantel
#Date:  2021_06_08

#Python Script to Start a Coffee machine with Tinkerforge Hardware
#if the floating APM value over the laste 3 mins lower than product of the threshold and the
#APM value of the first 30 mins.


import sys
import time
import keyboard
import threading
from pynput import mouse
from tinkerforge.ip_connection import IPConnection
from tinkerforge.brick_master import BrickMaster
from tinkerforge.bricklet_distance_ir_v2 import BrickletDistanceIRV2
from tinkerforge.bricklet_industrial_dual_relay import BrickletIndustrialDualRelay

#TinkerForge
HOST = "192.168.0.25"   #Ersetzen Durch Ipadresse der Wlan-Masterextension
PORT = 4223             #Muss Port der Wlan-Masterextension entsprechen
UID_mb = "XXYYZZ"       #UID des MasterBrick eingeben
UID_idr = "XXYYZZ"      #UID des BrickletIndustrialDualRelay eingeben
UID_dir = "XXYYZZ"      #UID des BrickletDistanceIRV2 eingeben
Max_Distance = 50       #Maximale Distanz zwischen Tasse und Sensor in mm als Ganzzahl
Press_Time = 1          #Zeit in Sec in der die Taste "gedrückt" werden soll
Threshold = 0.5         #Schwelle: Kaffe wenn Aktifität der letzen 3 minute kleiner als Trashold mal Durchschnit erster 30min ist.

#Klassen und Funktions Definitionen
class Kaffemaschine(object):
    def __init__(self, uid_mb, uid_idr, uid_dir, max_distance, press_time):
        self.min_distance = max_distance
        self.press_time = press_time
        self.ipcon = IPConnection() # Create IP connection
        self.master = BrickMaster(uid_mb, self.ipcon) # Create device object
        self.idr = BrickletIndustrialDualRelay(uid_idr, self.ipcon) # Create device object
        self.dir = BrickletDistanceIRV2(uid_dir, self.ipcon) # Create device object
        self.ipcon.connect(HOST, PORT) # Connect to brickd
        self.idr.set_value(False, False)

    def macht_kaffe(self):
        print('/nZeit fuer Kaffe/n')
        if(self.dir.get_distance()>self.max_distance):
            print('Kaffe Tasse richtig unter die Kaffemaschine stellen:/n')
        while(self.dir.get_distance()>self.max_distance):
            pass    #Macht nichts wartet bis Tasse erkannt wird.
        self.idr.set_value(True, False)
        print('Kaffe wird gemacht./n')
        time.sleep(self.press_time)
        self.idr.set_value(False, False)

    def __del__(self):
        self.ipcon.disconnect()

def count_key_strokes():
    #Variablen und Objekte mit global inerhalb der Funktion bekannt machen
    global falue
    while True:
        b = keyboard.read_key()
        #print (b)
        falue+=1

def on_click(x, y, button, pressed):
    #Variablen und Objekte mit global inerhalb der Funktion bekannt machen
    global falue
    #print('clicked')
    falue+=1

def apm():
    #Variablen und Objekte mit global inerhalb der Funktion bekannt machen
    global falue
    global Meinekaffemaschine
    global Threshold
    history_sec=[]
    falue_old=0
    while True:
        time.sleep(1)
        history_sec.append(falue/2) #Geteilt durch zwei weil das loslasen der tasten/Buttons auch als aktion erkannt wird.
        falue=0
        #print((sum(history_sec[-15:]))/15)
        sys.stdout.write('\r' + 'APM:' +str((sum(history_sec[-15:]))*4))
        sys.stdout.flush()
        if(len(history_sec)>1800):
            if ((sum(history_sec[-180:])/3)<Threshold*((sum(history_sec[:1800]))/30)):
                Meinekaffemaschine.macht_kaffe()
                history_sec.clear()
                falue=0

#Hauptprogramm
falue=0
Meinekaffemaschine = Kaffemaschine(UID_mb, UID_idr, UID_dir, Max_Distance, Press_Time)

thread1 = threading.Thread(target=apm)
thread1.daemon = True
thread1.start()

thread2 = threading.Thread(target=count_key_strokes)
thread2.daemon = True
thread2.start()

with mouse.Listener(on_click=on_click) as listener:
    listener.join()

thread1.join()
thread2.join()

del Meinekaffemaschine
