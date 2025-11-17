import pyglet
import numpy as np
from envqwop import QWOPEnv
from bot import Bot
import threading
import time

def runLoop(env):
    bot = Bot(env)
    
    # Simulate for 10 seconds
    for _ in range(1000):
        action = bot.act()
        
        obs, reward, done, truncated, info = env.step(action)
        
        bot.observe(obs)
        
        print('REWARD: ', reward)
        time.sleep(0.01)

def main():
    env = QWOPEnv(screen=True)
    
    # Create separate thread for logic updates
    threading.Thread(target=runLoop, args=(env,)).start()
    
    # Graphics thread
    pyglet.app.run()

if __name__ == "__main__":
    main()
    