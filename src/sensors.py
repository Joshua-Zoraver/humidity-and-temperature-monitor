import time
import threading
import math

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
        #TODO replace above with proper error handling when no longer testing without RPi
        # raise RuntimeError("No Sense HAT / RPi available")

    #Get actual values from sensors
    humidity = sense.get_humidity()
    temperature = sense.get_temperature()
    
    #Filter invalid values and replace with None
    return {
        "humidity": humidity if isinstance(humidity, (int, float)) and not math.isnan(humidity) else None,
        "temperature": temperature if isinstance(temperature, (int, float)) and not math.isnan(temperature) else None
    }


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
        
