import numpy as np
import time
from src.IMU import IMU
from src.Controller import Controller
#from src.JoystickInterface import JoystickInterface
from src.State import State
from src.Command import Command
from pupper.HardwareInterface import HardwareInterface
from pupper.Config import Configuration
from pupper.Kinematics import four_legs_inverse_kinematics
from multiprocessing.shared_memory import ShareableList
from multiprocessing import resource_tracker

def remove_shm_from_resource_tracker():
    """Monkey-patch multiprocessing.resource_tracker so SharedMemory won't be tracked

    More details at: https://bugs.python.org/issue38119
    """

    def fix_register(name, rtype):
        if rtype == "shared_memory":
            return
        return resource_tracker._resource_tracker.register(name, rtype)
    resource_tracker.register = fix_register

    def fix_unregister(name, rtype):
        if rtype == "shared_memory":
            return
        return resource_tracker._resource_tracker.unregister(name, rtype)
    resource_tracker.unregister = fix_unregister

    if "shared_memory" in resource_tracker._CLEANUP_FUNCS:
        del resource_tracker._CLEANUP_FUNCS["shared_memory"]

def read_command(shm_interface):
    command = Command()
    command.horizontal_velocity = np.array([shm_interface[0], shm_interface[1]])
    command.yaw_rate = shm_interface[2]
    command.height = shm_interface[3]
    command.pitch = shm_interface[4]
    command.roll = shm_interface[5]
    command.activation = shm_interface[6]
    command.hop_event = shm_interface[7]
    command.trot_event = shm_interface[8]
    command.activate_event = shm_interface[9]
    return command

def ischanged(newcommand, oldcommand):
    if newcommand.horizontal_velocity[0] != oldcommand.horizontal_velocity[0]:
        return True
    if newcommand.horizontal_velocity[1] != oldcommand.horizontal_velocity[1]:
        return True
    if newcommand.yaw_rate != oldcommand.yaw_rate:
        return True
    if newcommand.height != oldcommand.height:
        return True
    if newcommand.pitch != oldcommand.pitch:
        return True
    if newcommand.roll != oldcommand.roll:
        return True
    if newcommand.activation != oldcommand.activation:
        return True
    if newcommand.hop_event != oldcommand.hop_event:
        return True
    if newcommand.trot_event != oldcommand.trot_event:
        return True
    if newcommand.activate_event != oldcommand.activate_event:
        return True
    return False

def main(use_imu=False):
    """Main program
    """

    # Create config
    config = Configuration()
    hardware_interface = HardwareInterface()

    # Create imu handle
    if use_imu:
        imu = IMU(port="/dev/ttyACM0")
        imu.flush_buffer()

    # Create controller and user input handles
    controller = Controller(
        config,
        four_legs_inverse_kinematics,
    )
    state = State()
    #print("Creating joystick listener...")
    #joystick_interface = JoystickInterface(config)
    #print("Done.")
    print("Creating SHM reader...")
    remove_shm_from_resource_tracker()
    shm_interface = ShareableList([0.0, 0.0, 0.0, -0.16, 0.0, 0.0, 0, False, False, False], name='robot_smm')

    print("Done.")

    last_loop = time.time()

    print("Summary of gait parameters:")
    print("overlap time: ", config.overlap_time)
    print("swing time: ", config.swing_time)
    print("z clearance: ", config.z_clearance)
    print("x shift: ", config.x_shift)

    # prime the pump
    oldcommand = read_command(shm_interface)

    try:
        # Wait until the activate button has been pressed
        while True:
            print("Waiting for L1 to activate robot.")
            while True:
                #command = joystick_interface.get_command(state)
                #joystick_interface.set_color(config.ps4_deactivated_color)
                command = read_command(shm_interface)
                if ischanged(command, oldcommand):
                    print('Command', command.horizontal_velocity, command.yaw_rate, command.height, command.pitch, command.roll, command.activation, command.hop_event, command.trot_event, command.activate_event)
                oldcommand = command
                if command.activate_event == True:
                    shm_interface[9] = False # so we don't loop
                    command.activate_event = False
                    break
                time.sleep(0.1)
            print("Robot activated.")
            #joystick_interface.set_color(config.ps4_color)

            while True:
                now = time.time()
                if now - last_loop < config.dt:
                    continue
                last_loop = time.time()

                # Parse the udp joystick commands and then update the robot controller's parameters
                #command = joystick_interface.get_command(state)
                command = read_command(shm_interface)
                if ischanged(command, oldcommand):
                    print('Command', command.horizontal_velocity, command.yaw_rate, command.height, command.pitch, command.roll, command.activation, command.hop_event, command.trot_event, command.activate_event)
                oldcommand = command
                if command.activate_event == True:
                    print("Deactivating Robot")
                    break

                # Read imu data. Orientation will be None if no data was available
                quat_orientation = (
                    imu.read_orientation() if use_imu else np.array([1, 0, 0, 0])
                )
                state.quat_orientation = quat_orientation

                # Step the controller forward by dt
                controller.run(state, command)

                # Update the pwm widths going to the servos
                hardware_interface.set_actuator_postions(state.joint_angles)
    except (KeyboardInterrupt, SystemExit):
        print("Going away...")
        shm_interface.shm.close()
        shm_interface.shm.unlink()  # Free and release the shared memory block at the very end

main()
