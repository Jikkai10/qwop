from qwop import Game, GameWindow
import pyglet
import numpy as np
import gym
from gym.spaces import Tuple,Box,Discrete,MultiDiscrete

import threading
import time

class QWOPEnv(gym.Env):
    def __init__(self, screen=False):
        super().__init__()
        
        self.screen = screen
        self.createGame()
        
        # Possible movements are activations for all 4 limbs (thighL, thighR, calfL, calfR)
        self.action_space = Tuple(( Box(-1,1), Box(-1,1), Box(-1,1), Box(-1,1) ))

        # matches getInputs()
        self.observation_space = Tuple((
            Box(-np.inf, np.inf),   # 0  character x position
            Box(-np.inf, np.inf),   # 1  character y position
            Box(-np.inf, np.inf),   # 2  head x position
            Box(-np.inf, np.inf),   # 3  head y position
            Box(-np.inf, np.inf),   # 4  torso x position
            Box(-np.inf, np.inf),   # 5  torso y position
            Box(-np.inf, np.inf),   # 6  left foot x position
            Box(-np.inf, np.inf),   # 7  left foot y position
            Box(-np.inf, np.inf),   # 8  right foot x position
            Box(-np.inf, np.inf)    # 9  right foot y position
        ))
        
        # It's suggested to scale position by 1.25/200
        self.startPos = self.game.get_character_position()*1.25/200
        
        ### These are not included in the observation space but can be used for your solution
        
        # Head angle relative to torso in radians
        # headAngle = np.arctan2(game.character.head.position[1]-game.character.torso.position[1], game.character.head.position[0]-game.character.torso.position[0])
        
        # Positional difference between feet
        #legDeltaX = [game.character.footR.position[0] - game.character.footL.position[0]]
        #legDeltaY = [game.character.footR.position[1] - game.character.footL.position[1]]
        
        # Distance between head and feet
        #headToRightFoot = np.linalg.norm(game.character.head.position - game.character.footR.position)
        #headToLeftFoot = np.linalg.norm(game.character.head.position - game.character.footL.position)
        
        # Maximum body length
        #bodyDelta = max(headToRightFoot, headToLeftFoot)

            
    def step(self, x):
        #obs = None
        reward = 0
        done = False
        truncated = False
        info = {}
        
        x = np.array(x)
        x = np.clip(x, -1, 1) # clip to acceptable range of [-1, 1] muscle activations
        x *= 9000             # scale to the maximum value of the thigh/calf movement
        
        self.game.character.move_thighL(x[0])
        self.game.character.move_thighR(x[1])
        self.game.character.move_calfL(x[2])
        self.game.character.move_calfR(x[3])
        self.game.step()

        # Naive reward is the horizontal movement of the character
        curPos = self.game.get_character_position()*1.25/200
        reward = curPos - self.startPos
        
        # update observation
        obs = self.getInputs()

        self.steps +=1

        return obs, reward, done, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # use same parameters from last game
        self.createGame()
        self.steps = 0

        obs = self.getInputs()
        info = {}

        return obs, info

    def render(self):
        if not self.screen:
            return
        
    def createGame(self):
        self.steps = 0
        
        self.game = Game()
        
        if self.screen:
            self.gameWindow = GameWindow(self.game)
            
    def getInputs(self):
        inputs = []
        inputs += [self.game.character.get_position()[0]]
        inputs += [self.game.character.get_position()[1]]
        inputs += [self.game.character.head.position[0]]
        inputs += [self.game.character.head.position[1]]
        inputs += [self.game.character.torso.position[0]]
        inputs += [self.game.character.torso.position[1]]
        inputs += [self.game.character.footL.position[0]]
        inputs += [self.game.character.footL.position[1]]
        inputs += [self.game.character.footR.position[0]]
        inputs += [self.game.character.footR.position[1]]

        return inputs
