import numpy as np
#from multiprocessing import shared_memory
#from multiprocessing.managers import SharedMemoryManager
from multiprocessing.shared_memory import ShareableList
from multiprocessing import resource_tracker
from src.Command import Command

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

remove_shm_from_resource_tracker()
shm_robot = ShareableList(name='robot_smm')

command = Command()
command.horizontal_velocity = np.array([shm_robot[0], shm_robot[1]])
command.yaw_rate = shm_robot[2]
command.height = shm_robot[3]
command.pitch = shm_robot[4]
command.roll = shm_robot[5]
command.activation = shm_robot[6]
command.hop_event = shm_robot[7]
command.trot_event = shm_robot[8]
command.activate_event = shm_robot[9]

try:
    user_input = ''
    while True:
        user_input = input('Robot> ')
        parsed = user_input.lower().split()
        if parsed[0] == 'quit':
            break
        elif parsed[0] == 'activate':
            command.activate_event = not command.activate_event
            print('ActivateEvent', command.activate_event)
        elif parsed[0] == 'hop':
            command.hop = not command.hop
            print('Hop', command.hop)
        elif parsed[0] == 'trot':
            command.trot = not command.trot
            print('Trot', command.trot)
        elif parsed[0] == 'velocity':
            if (parsed.count == 3):
                command.horizontal_velocity = np.array([parsed[1], parsed[2]]).astype(np.float32)
                print('Horizontal velocity', command.horizontal_velocity)
            else:
                print('ERROR: Horizontal velocity requires 2 arguments')
        elif parsed[0] == 'yaw':
            if (parsed.count == 2):
                command.yaw_rate = float(parsed[1])
                print('Yaw rate', command.yaw_rate)
            else:
                print('ERROR: Yaw rate requires 1 argument')
        elif parsed[0] == 'height':
            if (parsed.count == 2):
                command.height = float(parsed[1])
                print('Height', command.height)
            else:
                print('ERROR: Height requires 1 argument')
        elif parsed[0] == 'pitch':
            if (parsed.count == 2):
                command.pitch = float(parsed[1])
                print('Pitch', command.pitch)
            else:
                print('ERROR: Pitch requires 1 argument')
        elif parsed[0] == 'roll':
            if (parsed.count == 2):
                command.roll = float(parsed[1])
                print('Roll', command.roll)
            else:
                print('ERROR: Roll requires 1 argument')
        elif parsed[0] == 'activation':
            if (parsed.count == 2):
                command.activation = int(parsed[1])
                print('Activation', command.activation)
            else:
                print('ERROR: Activation requires 1 argument')
        elif parsed[0] == 'status':
            print('Status', command)
        else:
            print('Unknown command')

except (KeyboardInterrupt, SystemExit):
    pass

print("Going away...")
shm_robot.shm.close()