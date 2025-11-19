from qwop import Game, GameWindow
import pyglet
import time
import dill
import queue
import numpy as np
import copy

################# HELPER FUNCTIONS #################
# Saves results to a dill file
def saveResults(set, name="qwop-backtracking-{}.dill"):
    with open(name.format(time.strftime("%Y%m%d-%H%M%S")), "wb") as f:
        dill.dump([set], f)

# Loads results from a dill file
def loadResults(fileName):
    with open(fileName, "rb") as f:
        set = dill.load(f)
        
    return set


################# OBJECTIVE FUNCTION FOR MINIMIZATION, PENALTY AND SIMULATION #################
# Penalty example considering the character's head angle
def characterHeadAnglePenalty(game : Game):
    # angle between head and torso in radians
    headAngle = np.arctan2(game.character.head.position[1]-game.character.torso.position[1], game.character.head.position[0]-game.character.torso.position[0])
    
    headBobTol = np.pi/4 # 45 degrees tolerance for head bobbing
    if headAngle < (np.pi/2 - headBobTol) or headAngle > (np.pi/2 + headBobTol):
        return True
    else:
        return False

# Objective function for minimization
# Returns meters walked by character as a scalar
# Input is a numpy array of n x 4 limb force inputs, where n is the amount of steps in the simulation
def simulate(x):
    game = Game()
        
    lastPos = game.get_character_position()*1.25/200

    for action in x:
        for _ in range(6): # period for movement, 60ms for each action
            match action:
                case 0:
                    game.character.move_thighL(9000)
                    game.character.move_thighR(-9000)
                case 1:
                    game.character.move_thighL(-9000)
                    game.character.move_thighR(9000)
                case 2:
                    game.character.move_calfL(9000)
                    game.character.move_calfR(-9000)
                case 3:
                    game.character.move_calfL(-9000)
                    game.character.move_calfR(9000)
                case _:
                    print('ERROR UNKNOWN ACTION ', action)
                    exit(0)
            
            game.step()
            
        curPos = game.get_character_position()*1.25/200
        headAngle = np.arctan2(game.character.head.position[1]-game.character.torso.position[1], game.character.head.position[0]-game.character.torso.position[0])
        headAngleError = (headAngle - np.pi/2)
        """
            Menor penalidade para pequenos erros de ângulo
            Maior recompensa para andar mais longe em menos passos
        """
        # if headAngleError < 0:
        #     if headAngleError > -np.pi/6:
        #         headAngleError = 0 
        if abs(headAngleError) < np.pi/6:
            headAngleError /= 2 
        if characterHeadAnglePenalty(game):
            return -20*(curPos/(len(x)))**2 + headAngleError**2, True, curPos, headAngleError
        
        if (curPos - lastPos) < 0:
            return -20*(curPos/(len(x)))**2 + headAngleError**2, True, curPos, headAngleError
        
            
    
    return -20*(curPos/len(x))**2 + headAngleError**2, False, curPos, headAngleError

class Solution:
    def __init__(self, x : list):
        self.x = x
        
        self.score, self.constraint, self.distance, self.headAngleError = simulate(self.x)
    
    def children(self):
        actions = [0, 1, 2, 3]
    
        children = [self.x + [a] for a in actions]
        
        solutions = [Solution(child) for child in children]
        
        return solutions
    
    def reject(self):        
        if self.constraint:
            return True
        else:
            return False
    
    def accept(self):
        if len(self.x) >= 100: # ~500 STEPS IN SIMULATION, 80*6 actions
            return True
        else:
            return False
        
def saveAllResults(openSet, finalSolutionSet):
    saveResults(openSet, "qwop-backtracking-open-{}.dill")
    saveResults(finalSolutionSet, "qwop-backtracking-final-{}.dill")

    print('========================================================================')
    print('{} Open solutions | {} Final solutions'.format(openSet.qsize(), finalSolutionSet.qsize()))
    
    if not openSet.empty():
        score, solution = openSet.queue[0]
        
        print('\nBest OPEN solution size: {} score: {}'.format(len(solution.x), solution.score))
        print('distance: {} head angle error: {} constraint: {}'.format(solution.distance, solution.headAngleError, solution.constraint))
        print('x: ', solution.x)
    
    if not finalSolutionSet.empty():
        score, solution = finalSolutionSet.queue[0]
        
        print('\nBest CLOSED solution size: {} score: {}'.format(len(solution.x), solution.score))
        print('distance: {} head angle error: {} constraint: {}'.format(solution.distance, solution.headAngleError, solution.constraint))
        print('x: ', solution.x)
        
    print('========================================================================\n')
        
    
def main():
    # Backtracking without considering solution quality
    '''openSet = queue.Queue()
    finalSolutionSet = queue.Queue()
    
    for action in [0, 1, 2, 3]:
        sol = Solution([action])
        openSet.put(sol)
    
    while not openSet.empty():
        solution = openSet.get()
        print(openSet.qsize(), len(solution.x), solution.x)
        
        if solution.reject():
            print('YOU\'RE FIRED!')
            continue
        elif solution.accept():
            print('GOOD JOB!')
            finalSolutionSet.put(solution)
        else:
            solutions = solution.children()
            
            for partial in solutions:
                openSet.put(partial)'''
 
    # Backtracking with solution minimization
    openSet = queue.PriorityQueue()                # stores solutions to be checked
    finalSolutionSet = queue.PriorityQueue()       # stores solutions accepted as final
    
    # Timer for saving results
    t0 = time.time()
    maxTime = 10*60 # 10 minutes
    
    # Initialize open set with initial partial solutions
    # 0: move_thighL
    # 1: move_thighR
    # 2: move_calfL
    # 3: move_calfR
    for action in [0, 1, 2, 3]:
        sol = Solution([action])
        openSet.put((sol.score, sol))
    
    # Process the open set
    while not openSet.empty():
        # Best first solution of priority queue
        score, solution = openSet.get()
        
        # Save partial results every maxTime
        if (time.time() - t0) >= maxTime:
            t0 = time.time()
            saveAllResults(openSet, finalSolutionSet)
        
        # Eliminate invalid partial solutions, save final solutions and create children of valid partial solutions
        if solution.reject():
            #print('YOU\'RE FIRED!')
            continue
        elif solution.accept():
            #print('GOOD JOB!')
            finalSolutionSet.put((score, solution))
        else:
            solutions = solution.children()
            
            for partial in solutions:
                openSet.put((partial.score, partial))
                
    # Save final results
    saveAllResults(openSet, finalSolutionSet)
    print('*** BACKTRACKING DONE! ***')
    
    
# Loads an optimization trial from fileName and displays the results
def mainGraphicsLoadResults(fileName):
    game = Game()
    gameWindow = GameWindow(game)
    
    # results vector 'x' has shape (n,4) but is saved as (1,n*4)
    set = loadResults(fileName)[0]
    
    # Best first solution of priority queue
    score, solution = set.get()
    
    # Decode solution into forces
    n = len(solution.x)*6             # 60ms for each action
    x = np.zeros((n, 4))
    print('Decoded solution length: ', solution.x)
    for (i, action) in zip(range(n), solution.x):
        match action:
            case 0:
                x[i*6:i*6+6, 0] = 9000
                x[i*6:i*6+6, 1] = -9000
            case 1:
                x[i*6:i*6+6, 0] = -9000
                x[i*6:i*6+6, 1] = 9000
            case 2:
                x[i*6:i*6+6, 2] = 9000
                x[i*6:i*6+6, 3] = -9000
            case 3:
                x[i*6:i*6+6, 2] = -9000
                x[i*6:i*6+6, 3] = 9000
            case _:
                print('ERROR UNKNOWN ACTION ', action)
                exit(0)
        
    
    print('===== LOADED RESULT =====')
    print(x)
    
    updateGame = lambda dt: gameWindow.updateBot(dt, game, x)
    
    pyglet.clock.schedule_interval(updateGame, 0.01)
    pyglet.app.run()
    
    
if __name__ == "__main__":
    main()
    
    #mainGraphicsLoadResults('qwop-backtracking-final-20250517-225853.dill')


