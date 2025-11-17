import numpy as np

# Example of solution
#
# This bot has precalculated limb actions.
# Each limb movement is performed in opposites, if the left thigh is moved forwards, the right thigh goes backwards.
# Each movement action is held for a period of time allowing the character to move.

class Bot:
    def __init__(self, env):
        self.env = env
        self.obs = None
        
        # Example solution 1: step and fumble
        #solution = [2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 0, 3, 2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 3, 3, 3, 0, 0, 1, 1, 0, 0, 1, 3, 3, 1, 3, 3, 2, 0, 3]
        
        
        #solution = [2, 2, 2, 2, 1, 1, 1, 2, 2, 0, 2, 2, 1, 1, 2, 1, 1, 2, 2, 3, 0, 2, 0, 3, 1, 3, 3, 0, 3, 3, 0, 1, 3, 3, 0, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3, 3, 0, 3, 3, 2, 2, 2, 2, 2, 2, 2, 0, 3, 2, 2, 3, 2, 1, 2, 0, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3]
        
        solution = [2, 2, 2, 2, 1, 1, 1, 2, 2, 0, 2, 2, 1, 1, 2, 1, 1, 2, 2, 3, 0, 2, 0, 3, 1, 3, 3, 0, 3, 3, 0, 1, 3, 3, 0, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 3, 3, 0, 3, 3, 2, 2, 2, 2, 2, 2, 2, 0, 3, 2, 2, 3, 2, 1, 3, 2, 3, 3, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 2, 1, 3, 3, 3, 3, 3, 0, 3, 1, 3, 3, 2, 2, 2, 2, 2, 2]
        
        solution = []
        
        MOVEMENT_PERSIST = 6 # holds the limb configuration for this amount of steps
        
        # Decode solution into forces
        n = len(solution)*MOVEMENT_PERSIST             # 60ms for each action
        x = np.zeros((n, 4))
        
        for (i, action) in zip(range(n), solution):
            match action:
                case 0:
                    x[i*MOVEMENT_PERSIST:i*MOVEMENT_PERSIST+MOVEMENT_PERSIST, 0] = 1
                    x[i*MOVEMENT_PERSIST:i*MOVEMENT_PERSIST+MOVEMENT_PERSIST, 1] = -1
                case 1:
                    x[i*MOVEMENT_PERSIST:i*MOVEMENT_PERSIST+MOVEMENT_PERSIST, 0] = -1
                    x[i*MOVEMENT_PERSIST:i*MOVEMENT_PERSIST+MOVEMENT_PERSIST, 1] = 1
                case 2:
                    x[i*MOVEMENT_PERSIST:i*MOVEMENT_PERSIST+MOVEMENT_PERSIST, 2] = 1
                    x[i*MOVEMENT_PERSIST:i*MOVEMENT_PERSIST+MOVEMENT_PERSIST, 3] = -1
                case 3:
                    x[i*MOVEMENT_PERSIST:i*MOVEMENT_PERSIST+MOVEMENT_PERSIST, 2] = -1
                    x[i*MOVEMENT_PERSIST:i*MOVEMENT_PERSIST+MOVEMENT_PERSIST, 3] = 1
                case _:
                    print('ERROR UNKNOWN ACTION ', action)
                    exit(0)
        
        # store the limb configuration for each step  
        self.x = x
        
        self.step = 0
        
    def act(self):
        if self.step < len(self.x):
            action = self.x[self.step]
            self.step += 1
        else:
            action = self.env.action_space.sample()
            
        return action
    
    def observe(self, obs):
        self.obs = obs