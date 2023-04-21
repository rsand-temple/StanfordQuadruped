#import pigpio
from pupper.Config import ServoParams, PWMParams

import board
import busio
import numpy as np
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from adafruit_servokit import ServoKit

class HardwareInterface:
    def __init__(self):
        #self.pi = pigpio.pi()
        # Create the I2C bus interface.
        self.i2c_bus = busio.I2C(board.SCL, board.SDA)

        # Create a simple PCA9685 class instance.
        self.pca = PCA9685(self.i2c_bus)

        # ServoKit
        self.kit = ServoKit(channels=16)

        self.pwm_params = PWMParams()
        self.servo_params = ServoParams()
        #initialize_pwm(self.pi, self.pwm_params)
        #initialize_pwm(self.pca, self.pwm_params)
        initialize_pwm(self.kit, self.pwm_params)

    def set_actuator_postions(self, joint_angles):
        #send_servo_commands(self.pi, self.pwm_params, self.servo_params, joint_angles)
        #send_servo_commands(self.pca, self.pwm_params, self.servo_params, joint_angles)
        send_servo_commands(self.kit, self.pwm_params, self.servo_params, joint_angles)
    
    def set_actuator_position(self, joint_angle, axis, leg):
        #send_servo_command(self.pi, self.pwm_params, self.servo_params, joint_angle, axis, leg)
        #send_servo_command(self.pca, self.pwm_params, self.servo_params, joint_angle, axis, leg)
        send_servo_command(self.kit, self.pwm_params, self.servo_params, joint_angle, axis, leg)


def pwm_to_duty_cycle(pulsewidth_micros, pwm_params):
    """Converts a pwm signal (measured in microseconds) to a corresponding duty cycle on the gpio pwm pin
    Parameters
    ----------
    pulsewidth_micros : float
        Width of the pwm signal in microseconds
    pwm_params : PWMParams
        PWMParams object
    Returns
    -------
    float
        PWM duty cycle corresponding to the pulse width
    """
    return int(pulsewidth_micros / 1e6 * pwm_params.freq * pwm_params.range)


def angle_to_pwm(angle, servo_params, axis_index, leg_index):
    """Converts a desired servo angle into the corresponding PWM command
    Parameters
    ----------
    angle : float
        Desired servo angle, relative to the vertical (z) axis
    servo_params : ServoParams
        ServoParams object
    axis_index : int
        Specifies which joint of leg to control. 0 is abduction servo, 1 is inner hip servo, 2 is outer hip servo.
    leg_index : int
        Specifies which leg to control. 0 is front-right, 1 is front-left, 2 is back-right, 3 is back-left.
    Returns
    -------
    float
        PWM width in microseconds
    """
    angle_deviation = (
        #angle - servo_params.neutral_angles[axis_index, leg_index]
        90 + angle - servo_params.neutral_angles[axis_index, leg_index]
    ) * servo_params.servo_multipliers[axis_index, leg_index]
    pulse_width_micros = (
        servo_params.neutral_position_pwm
        + servo_params.micros_per_rad * angle_deviation
    )
    return pulse_width_micros


def angle_to_duty_cycle(angle, pwm_params, servo_params, axis_index, leg_index):
    return pwm_to_duty_cycle(
        angle_to_pwm(angle, servo_params, axis_index, leg_index), pwm_params
    )


#def initialize_pwm(pi, pwm_params):
#def initialize_pwm(pca, pwm_params):
def initialize_pwm(kit, pwm_params):
    #pca.frequency = pwm_params.freq
    for leg_index in range(4):
        for axis_index in range(3):
            #pi.set_PWM_frequency(pwm_params.pins[axis_index, leg_index], pwm_params.freq)
            #pi.set_PWM_range(pwm_params.pins[axis_index, leg_index], pwm_params.range)
            #pca.channels[pwm_params.pins[axis_index, leg_index]].duty_cycle = pwm_params.min
            print('Initializing servo', pwm_params.pins[axis_index, leg_index])
            #theservo = servo.Servo(pca.channels[pwm_params.pins[axis_index, leg_index]], pwm_params.min, pwm_params.range)
            #theservo = servo.Servo(pca.channels[pwm_params.pins[axis_index, leg_index]])
            #theservo.angle = 90
            kit.servo[pwm_params.pins[axis_index, leg_index]].angle = 90



#def send_servo_commands(pi, pwm_params, servo_params, joint_angles):
#def send_servo_commands(pca, pwm_params, servo_params, joint_angles):
def send_servo_commands(kit, pwm_params, servo_params, joint_angles):
    for leg_index in range(4):
        for axis_index in range(3):
            #duty_cycle = angle_to_duty_cycle(
            #    joint_angles[axis_index, leg_index],
            #    pwm_params, servo_params, axis_index, leg_index,
            #)
            #pi.set_PWM_dutycycle(pwm_params.pins[axis_index, leg_index], duty_cycle)
            #pca.channels[pwm_params.pins[axis_index, leg_index]].duty_cycle = duty_cycle
            send_servo_command(kit, pwm_params, servo_params, joint_angles[axis_index, leg_index])
            #kit.servo[pwm_params.pins[axis_index, leg_index]].angle = joint_angles[axis_index, leg_index]

#def send_servo_command(pi, pwm_params, servo_params, joint_angle, axis, leg):
#def send_servo_command(pca, pwm_params, servo_params, joint_angle, axis, leg):
def send_servo_command(kit, pwm_params, servo_params, joint_angle, axis, leg):
    #duty_cycle = angle_to_duty_cycle(joint_angle, pwm_params, servo_params, axis, leg)
    #pi.set_PWM_dutycycle(pwm_params.pins[axis, leg], duty_cycle)
    #pca.channels[pwm_params.pins[axis, leg]].duty_cycle = duty_cycle
    ja_degrees = (180 * joint_angle / np.pi) + 90 # servokit goes 0-180 not -90,90 
    print('Settings servo {} to angle {} deg'.format(pwm_params.pins[axis, leg], ja_degrees))
    kit.servo[pwm_params.pins[axis, leg]].angle = ja_degrees

#def deactivate_servos(pi, pwm_params):
def deactivate_servos(pca, pwm_params):
    for leg_index in range(4):
        for axis_index in range(3):
            pca.channels[pwm_params.pins[axis_index, leg_index]].duty_cycle = 0