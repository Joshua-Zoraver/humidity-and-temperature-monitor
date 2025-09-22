import time
import threading

try:
    from sense_hat import SenseHat
    sense = SenseHat()
except ImportError:
    #If not using RPi, make fake one (testing)
    sense = None

def read_values():
    if sense is None:
        #Return fake values if RPi isnt available (testing)
        return {"humidity": 50.0, "temperature": 22.0}
    #Return actual values from 
    return {"humidity": sense.get_humidity(), "temperature": sense.get_temperature()}

class SensorReader(threading.Thread):
    def __init__(self, interval = 10, callback = None):
        super().__init__()
        self.interval = interval
        self.callback = callback #Function to call with sensor data after each reading
        self.running = False #Flag to control the thread's loop

    #Reads sensor data repeatedly until stopped
    def run(self):
        self.running = True
        while self.running:
            data = read_values() #Get humidity and temperature
            if self.callback:
                self.callback(data) #Call the callback function
            time.sleep(self.interval) #Wait

    def stop(self):
        self.running = False
        
