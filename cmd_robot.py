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

try:
    user_input = ''
    command = Command()
    while True:
        command.horizontal_velocity = np.array([shm_robot[0], shm_robot[1]])
        command.yaw_rate = shm_robot[2]
        command.height = shm_robot[3]
        command.pitch = shm_robot[4]
        command.roll = shm_robot[5]
        command.activation = shm_robot[6]
        command.hop_event = shm_robot[7]
        command.trot_event = shm_robot[8]
        command.activate_event = shm_robot[9]

        user_input = input('Robot> ')
        parsed = user_input.lower().split()
        if parsed[0] == 'quit' or parsed[0] == 'exit':
            break
        elif parsed[0] == 'help' or parsed[0] == '?':
            print('\tactivate')
            print('\thop')
            print('\ttrot')
            print('\tvelocity <x> <y>')
            print('\tyaw <angle>')
            print('\theight <m>')
            print('\tpitch <angle>')
            print('\troll <angle>')
            print('\tactivation <a>')
        elif parsed[0] == 'activate':
            shm_robot[9] = not shm_robot[9]
            print('Activate', shm_robot[9])
        elif parsed[0] == 'hop':
            shm_robot[7] = not shm_robot[7]
            print('Hop', shm_robot[7])
        elif parsed[0] == 'trot':
            shm_robot[8] = not shm_robot[8]
            print('Trot', shm_robot[8])
        elif parsed[0] == 'velocity':
            if (len(parsed) == 3):
                shm_robot[0] = float(parsed[1])
                shm_robot[1] = float(parsed[2])
                print('Horizontal velocity', shm_robot[0], ',', shm_robot[1])
            else:
                print('ERROR: Horizontal velocity requires 2 arguments')
        elif parsed[0] == 'yaw':
            if (len(parsed) == 2):
                shm_robot[2] = float(parsed[1])
                print('Yaw rate', shm_robot[2])
            else:
                print('ERROR: Yaw rate requires 1 argument')
        elif parsed[0] == 'height':
            if (len(parsed) == 2):
                shm_robot[3] = float(parsed[1])
                print('Height', shm_robot[3])
            else:
                print('ERROR: Height requires 1 argument')
        elif parsed[0] == 'pitch':
            if (len(parsed) == 2):
                shm_robot[4] = float(parsed[1])
                print('Pitch', shm_robot[4])
            else:
                print('ERROR: Pitch requires 1 argument')
        elif parsed[0] == 'roll':
            if (len(parsed) == 2):
                shm_robot[5] = float(parsed[1])
                print('Roll', shm_robot[5])
            else:
                print('ERROR: Roll requires 1 argument')
        elif parsed[0] == 'activation':
            if (len(parsed) == 2):
                shm_robot[6] = int(parsed[1])
                print('Activation', shm_robot[6])
            else:
                print('ERROR: Activation requires 1 argument')
        elif parsed[0] == 'status':
            print('Command', command.horizontal_velocity, command.yaw_rate, command.height, command.pitch, command.roll, command.activation, command.hop_event, command.trot_event, command.activate_event)
        else:
            print('Unknown command')

except (KeyboardInterrupt, SystemExit):
    pass

print("Going away...")
shm_robot.shm.close()