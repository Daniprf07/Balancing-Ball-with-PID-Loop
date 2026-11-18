import board
import adafruit_vl53l4cd
import pwmio
import time
from adafruit_motor import servo

####################   Setting Rate of Measurements    ######################
frequency_servo = 50    # Measured in Hz  
period_sensor = 20      # Measured in ms (20ms = 50Hz)   


####################   Creating objects     ######################

#Servo connected to pin A2 
pwm = pwmio.PWMOut(board.A2, duty_cycle=2 ** 15, frequency= frequency_servo)
servo = servo.Servo(pwm)

#Sensor connected with QT cable 
i2c = board.I2C() 
sensor = adafruit_vl53l4cd.VL53L4CD(i2c)
sensor.timing_budget = period_sensor


####################   Global Constants    ######################
    
MIN_ANGLE = 10
MAX_ANGLE = 170

FLAT_ANGLE = 90        # 90 (degrees) for maximum range of motion

DEADZONE_DISTANCE = 0.6    # cm
SETTLE_TIME = 0.1         # seconds

'''
Set point values 
Green: ??  Blue: ??  (cm)  [red ball]
Green: ??  B: ??  (cm)  [yellow ball]	
'''
SET_POINT  = 12.8

LOOP_TIME = 0.02  #ms

####################      PID Adjustable Gains      ####################

kp = 3.720        
kd =3.72
ki = 1.3

####################      Initializing Variables          ####################

sensor.start_ranging()

filtered_distance = sensor.distance

last_distance = =sensor.distance

integral = 0
 
timer = time.monotonic()

settle_start = None


####################      Main Loop           ####################

while True:
    
    loop_start = time.monotonic()
    
    if sensor.data_ready:
        distance = sensor.distance
        sensor.clear_interrupt()
    else:
        continue
    
    
    current_time = time.monotonic()           # Sets current time with as reference
    
    # EMWA for input distance
    
    filtered_distance = distance*0.2 + filtered_distance*0.8
   
    
    # Proportional term
    
    error = SET_POINT - filtered_distance  
    
    p_term = -kp * error # Negative to oppose the error
    
    
    # Derivative term
        
    derivative = (filtered_distance-last_distance)  / LOOP_TIME # Uses constant time to increase consistency
    
    d_term = kd * derivative
    
    
    # Integral term
    
    decay = 0.90   # Decaying factor to smooth integral term
     
    integral = (integral*decay)  +  (error * LOOP_TIME)
    
    i_term = -ki * integral
    
    
    # The sum of the terms determines the change from the flat angle
    
    output = FLAT_ANGLE + p_term + d_term + i_term 
    
    
    # If ball remains in deadzone at leat settle time, the angle is kept at 90
    
    if (abs(error) < DEADZONE_DISTANCE ):        

        if settle_start is None:
            settle_start = current_time

        elif current_time - settle_start > SETTLE_TIME:
            output=90
            print(current_time-timer)
            
    else:
        settle_start = None
            
            
    # Sends the output to the servo 
    servo.angle = max(min(output, MAX_ANGLE),MIN_ANGLE)
     
     
    # Updates last error

    last_distance = filtered_distance
    
    
    # Prints  important info for testing
    print(
        f"D={noLowDistance:.2f} "
        f"E={error:.2f} "
        f"V={derivative:.2f} "
        f"A={output:.2f}"
    )
    
    # Waits if the loop took less time than LOOP_TIME
    
    elapsed = time.monotonic() - loop_start    
        
    if elapsed < LOOP_TIME s:
        time.sleep(LOOP_TIME - elapsed)
