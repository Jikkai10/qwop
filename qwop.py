"""
Adaptation from Python QWOP by Prof. Aline Normoyle, originally available at:
https://github.com/alinen/qwop

Game logic and game graphics are now separated, allowing the game engine to run by itself

Game input is in a series of joint forces which allows optimization applications


2024 Daniel Cavalcanti Jeronymo
"""

import pyglet
from pyglet.window import key
from pyglet.math import Mat4
from pyglet import shapes
import pymunk, pymunk.pyglet_util
from pymunk.vec2d import Vec2d
from character import Character, CharacterGraphics

import numpy as np

def hit_ground(arbiter, space, data):
        #print("hit ground!")
        return True

class Game:
    def __init__(self):
        # Window size even though this can run without a window
        self.WINDOW_WIDTH = 960
        self.WINDOW_HEIGHT = 540
        
        # Create world
        space, character = self.setup_world()
        
        self.space = space
        self.character = character

    # Create simulation world with the character
    def setup_world(self):
        # World
        space = pymunk.Space()
        space.gravity = 0, -9820
        space.damping = 0.99

        handler = space.add_collision_handler(100, 1)
        handler.begin = hit_ground

        # Floor
        floorHeight = 10
        floor = pymunk.Segment(space.static_body, Vec2d(-self.WINDOW_WIDTH*100,floorHeight), Vec2d(self.WINDOW_WIDTH*100,10), 1)
        floor.friction = 10.3
        floor.collision_type = 100
        space.add(floor)

        # Character
        w = 100
        h = 200
        bodyx = self.WINDOW_WIDTH // 2
        bodyy = floorHeight + h + h/8 + 10 
        #print("Body start", bodyx, bodyy)
        
        character = Character(space, bodyx, bodyy, w, h)

        return space, character

    # Step simulation
    def step(self):
        for _ in range(10):
            self.space.step(0.001) # 1ms
            
    def get_character_position(self):
        lc = self.character.get_position()[0] - self.WINDOW_WIDTH//2
        return lc
    
class GameWindow(pyglet.window.Window):
    def __init__(self, game):
        w = game.WINDOW_WIDTH
        h = game.WINDOW_HEIGHT
        
        super(GameWindow, self).__init__(w, h, fullscreen = False, vsync = True)
        
        self.game = game
        
        #self.window = pyglet.window.Window(width=game.WINDOW_WIDTH, height=game.WINDOW_HEIGHT)
        self.batch = pyglet.graphics.Batch() # for background
        self.batch2 = pyglet.graphics.Batch() # for character
        self.fps_display = pyglet.window.FPSDisplay(window=self)
        self.label = pyglet.text.Label('0 meters', font_name='Times New Roman', font_size=24, x=w//2, y=h*0.9, anchor_x='center', anchor_y='center')
        
        self.charactergraphics = CharacterGraphics(self.game.character, self.batch2)
        
        self.qDown = False
        self.wDown = False
        self.oDown = False
        self.pDown = False
        self.paused = False
        self.debug_draw = False
        
        self.xi = 0
        


    #@window.event
    def on_key_release(self, symbol, modifiers):
        if symbol == key.Q:
            self.qDown = False
        elif symbol == key.W:
            self.wDown = False
        elif symbol == key.O:
            self.oDown = False
        elif symbol == key.P:
            self.pDown = False

    #@window.event
    def on_key_press(self, symbol, modifiers):
        self.qDown = self.wDown = self.oDown = self.pDown = False
        if symbol == key.ESCAPE:
            self.close()
        elif symbol == key.R:
            self.game.character.reset()
        elif symbol == key.Q:
            self.qDown = True
        elif symbol == key.W:
            self.wDown = True
        elif symbol == key.O:
            self.oDown = True
        elif symbol == key.P:
            self.pDown = True
        elif symbol == key.S:
            self.game.step()
        elif symbol == key.SPACE:
            self.paused = not self.paused
        elif symbol == key.D:
            self.debug_draw = not self.debug_draw

    def print_commands(self):
        print("SPACE: Pause simulation")
        print("S: Step simulation")
        print("R: Reset character")
        print("D: Toggle debug draw of physics objects")
        print("Q: Apply force to left thigh")
        print("W: Apply force to right thigh")
        print("O: Apply force to left calf")
        print("P: Apply force to right calf")

    def draw_rect(self, h1, h2, c1, c2):
        w = self.width
        h = self.height

        lc = self.game.get_character_position()
        background = ((lc, h*h1), 
                    (w+lc, h*h1),
                    (w+lc, h*h2),
                    (lc, h*h2))
        colors = (c1[0],c1[1],c1[2],c1[3], 
                c1[0],c1[1],c1[2],c1[3], 
                c2[0],c2[1],c2[2],c2[3], 
                c2[0],c2[1],c2[2],c2[3])
        obj = shapes.Polygon(*background, color=colors, batch=self.batch)
        return [obj]
        

    def draw_white_line(self, h):
        objs = []
        objs += self.draw_rect(h, h+0.01, (255,255,255,255), (255,255,255,100))
        objs += self.draw_rect(h-0.01, h, (255,255,255,100), (255,255,255,255))
        return objs

    def draw_start(self):
        x = self.width/2
        h = self.height
        
        w1 = 25
        w2 = 10
        line1 = ((x-w1, 10/h),
                (x, 10/h),
                (x, h*0.28),
                (x-w2, h*0.28))
        line2 = ((x, 10/h),
                (x+w1, 10/h),
                (x+w2, h*0.28),
                (x, h*0.28))
        color1 = (255,255,255,50, 
                255,255,255,255, 
                255,255,255,255, 
                255,255,255,50)
        color2 = (255,255,255,255, 
                255,255,255,50, 
                255,255,255,50, 
                255,255,255,255)
        objs = []
        objs += [shapes.Polygon(*line1, color=color1, batch=self.batch)]
        objs += [shapes.Polygon(*line2, color=color2, batch=self.batch)]
        return objs

    #@window.event
    def on_draw(self):
        self.clear()

        w = self.width
        h = self.height
        
        lc = self.game.get_character_position()

        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        self.projection = Mat4.orthogonal_projection(lc, lc+w, 0, h, -1, 1)
        

        # NOTE: pyglet needs objects alive because of garbage collection, so everything is placed in this list before drawing
        objs = []
        objs += self.draw_rect(0.5, 1.0, (0,0,255,255), (0,0,50,255))
        objs += self.draw_rect(0.45, 0.5, (0,200,0,255), (0,0,255,255))
        objs += self.draw_rect(0.45, 0.35, (0,200,0,255), (0,200,0,255))
        objs += self.draw_rect(0.35, 0.25, (0,200,0,255), (200,0,0,255))
        objs += self.draw_rect(10/h, 0.25, (200,0,0,255), (200,0,0,255))
        objs += self.draw_white_line(0.1)
        objs += self.draw_white_line(0.2)
        objs += self.draw_white_line(0.25)
        objs += self.draw_white_line(0.28)
        objs += self.draw_start()        
        self.batch.draw()

        if self.debug_draw:
            self.fps_display.draw()
            options = pymunk.pyglet_util.DrawOptions()
            self.game.space.debug_draw(options)
        else:
            self.charactergraphics.draw()

        self.projection = Mat4.orthogonal_projection(0, w, 0, h, -1, 1)
        
        factor = 1.25/200
        self.label.text = "%.1f meters"%(lc * factor)
        self.label.draw()

    # normal update method - considers user inputs
    def update(self, dt, game : Game):
        if self.qDown:
            self.game.character.move_thighL(9000)
            self.game.character.move_thighR(-9000)
        elif self.wDown:
            self.game.character.move_thighL(-9000)
            self.game.character.move_thighR(9000)
        elif self.oDown:
            self.game.character.move_calfL(9000)
            self.game.character.move_calfR(-9000)
        elif self.pDown:
            self.game.character.move_calfL(-9000)
            self.game.character.move_calfR(9000)

        if not self.paused:
            self.game.step()
        
    # update method for external inputs
    # pyglet doesn't allow main loop control so we handle x indexing by a variable xi
    def updateBot(self, dt, game : Game, x : np.ndarray):
        if not self.paused:
            if self.xi + 1 < x.shape[0]:
                self.game.character.move_thighL(x[self.xi, 0])
                self.game.character.move_thighR(x[self.xi, 1])
                self.game.character.move_calfL(x[self.xi, 2])
                self.game.character.move_calfR(x[self.xi, 3])
                
                self.xi += 1
                
            self.game.step()


def mainGraphics():
    game = Game()
    gameWindow = GameWindow(game)
    
    updateGame = lambda dt: gameWindow.update(dt, game)
    
    gameWindow.print_commands()
    
    pyglet.clock.schedule_interval(updateGame, 0.01)
    pyglet.app.run()
    

if __name__ == "__main__":
    mainGraphics()