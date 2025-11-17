import numpy as np
from envqwop import QWOPEnv
from bot import Bot

def runLoop(env):
    bot = Bot(env)
    
    # Simulate for 10 seconds
    for _ in range(1000):
        action = bot.act()
        
        obs, reward, done, truncated, info = env.step(action)
        
        bot.observe(obs)
        
        print('REWARD: ', reward)

def main():
    env = QWOPEnv(screen=False)
    runLoop(env)

if __name__ == "__main__":
    main()
    