"""
Adaptation from Python QWOP by Prof. Aline Normoyle, originally available at:
https://github.com/alinen/qwop

armless ragdoll character

Physics and graphics representation of the character are now separated
This allows the character to be simulated by itself


2024 Daniel Cavalcanti Jeronymo
"""

import math
import pyglet
import pymunk, pymunk.pyglet_util
from pymunk.vec2d import Vec2d

class Character:
    def __init__(self, space, bodyx, bodyy, w, h):
        self.space = space

        mass = 20

        torso = setup_body(space, bodyx+0, bodyy+h*3/8, mass*2, w, h*3/4, 1, 2)
        head = setup_body(space, bodyx+0, bodyy+h*7/8, mass/2.0, w/2, h/4, 1, 2)

        thighL = setup_body(space, bodyx-w/4.0, bodyy-h/4.0, mass, w/2.0, h/2.0, 2)
        thighR = setup_body(space, bodyx+w/4.0, bodyy-h/4.0, mass, w/2.0, h/2.0, 2)

        calfL = setup_body(space, bodyx-w/4.0, bodyy-h*3/4.0, mass, w/2.0, h/2.0, 2)
        calfR = setup_body(space, bodyx+w/4.0, bodyy-h*3/4.0, mass, w/2.0, h/2.0, 2)

        footL = setup_body(space, bodyx-w/4+w/8, bodyy-h*17/16, mass/2.0, w*3/4, h/8, 2)
        footR = setup_body(space, bodyx+w/4+w/8, bodyy-h*17/16, mass/2.0, w*3/4, h/8, 2)


        create_joint(space, torso,  head,   bodyx,       bodyy+h*3/4, -math.pi/10,  math.pi/10)
        create_joint(space, torso,  thighL, bodyx-w/4,   bodyy      , -math.pi/10, math.pi/2)
        create_joint(space, torso,  thighR, bodyx+w/4,   bodyy      , -math.pi/10, math.pi/2)
        create_joint(space, thighL, calfL,  bodyx-w/4.0, bodyy-h/2.0, -math.pi/2,  -math.pi/3)
        create_joint(space, thighR, calfR,  bodyx+w/4.0, bodyy-h/2.0, -math.pi/2,  -math.pi/3)
        create_joint(space, calfL,  footL,  bodyx-w/4.0, bodyy-h    , -math.pi/10,  math.pi/10)
        create_joint(space, calfR,  footR,  bodyx+w/4.0, bodyy-h    , -math.pi/10,  math.pi/10)

        # for debugging
        #torso_pin = pymunk.PinJoint(torso, space.static_body, (0,0), (bodyx, bodyy+h))
        #space.add(torso_pin)

        # save variables as members
        self.thighL = thighL
        self.thighR = thighR
        self.calfL = calfL
        self.calfR = calfR
        self.footL = footL
        self.footR = footR
        self.torso = torso
        self.head = head
        
        self.bodies = [thighL, thighR, calfL, calfR, footL, footR, torso, head]

        self.set_pose([-math.pi/6, -math.pi/10, 0, math.pi/6, -math.pi/10, 0], bodyx, bodyy, w, h)

    def get_position(self):
        return self.torso.position

    def move_thighL(self, force=9000):
        if force > 9000:
            force = 9000
        elif force < -9000:
            force = -9000
        self.thighL.apply_impulse_at_local_point((force, 0), (0, 0))

    def move_thighR(self, force=9000):
        if force > 9000:
            force = 9000
        elif force < -9000:
            force = -9000
        self.thighR.apply_impulse_at_local_point((force, 0), (0, 0))

    def move_calfL(self, force=9000):
        if force > 9000:
            force = 9000
        elif force < -9000:
            force = -9000
        self.calfL.apply_impulse_at_local_point((-force, 0), (0, 0))

    def move_calfR(self, force=9000):
        if force > 9000:
            force = 9000
        elif force < -9000:
            force = -9000
        self.calfR.apply_impulse_at_local_point((-force, 0), (0, 0))

    def set_pose(self, pose, bodyx, bodyy, w, h):
        d11 = (bodyx-w/4, bodyy)
        d21 = (bodyx+w/4, bodyy)

        d2 = (0, -h/2)
        d3 = (0, -h/2)
        d4 = (w/4-w/8, -h*1/16)

        p11 = d11
        p12 = add(p11, rotate(pose[0], d2))
        p13 = add(p12, rotate(pose[0]+pose[1], d3))
        p14 = add(p13, rotate(pose[0]+pose[1]+pose[2], d4)) 

        p21 = d21
        p22 = add(p21, rotate(pose[3], d2))
        p23 = add(p22, rotate(pose[3]+pose[4], d3))
        p24 = add(p23, rotate(pose[3]+pose[4]+pose[5], d4)) 

        self.thighL.start_position = mul(0.5, add(p12, p11))
        self.thighL.start_angle = pose[0]

        self.calfL.start_position = mul(0.5, add(p13, p12))
        self.calfL.start_angle = pose[0]+pose[1]

        self.footL.start_position = p14
        self.footL.start_angle = pose[0]+pose[1]+pose[2]

        self.thighR.start_position = mul(0.5, add(p22, p21))
        self.thighR.start_angle = pose[3]

        self.calfR.start_position = mul(0.5, add(p23, p22))
        self.calfR.start_angle = pose[3]+pose[4]

        self.footR.start_position = p24
        self.footR.start_angle = pose[3]+pose[4]+pose[5]

        # set positions and angles to initial (start) states
        self.reset()
        
    def reset(self):
        for body in self.bodies:
            body.position = body.start_position
            body.angle = body.start_angle

# TODO DCJ note:        
# Character.py should be a physics abstraction only
# self.bodies is a set of sprites for drawing it with pyglet, along with draw method
# all of these were moved to a CharacterGraphics class
class CharacterGraphics:
    def __init__(self, character, batch):
        self.character = character
        self.batch = batch
        
        # Order determines draw order for sprites
        self.bodies = [load_sprite("assets/hthigh.png", character.thighR), 
                       load_sprite("assets/hcalf.png", character.calfR), 
                       load_sprite("assets/hfoot.png", character.footR, (5, 0)), 
                       load_sprite("assets/htorso.png", character.torso, (30, 10)), 
                       load_sprite("assets/hthigh.png", character.thighL), 
                       load_sprite("assets/hcalf.png", character.calfL), 
                       load_sprite("assets/hfoot.png", character.footL, (5, 0)), 
                       load_sprite("assets/hhead.png", character.head, (0,40))]
        
        # associate sprites for batch drawing
        for sprite in self.bodies:
            sprite.batch = batch
        
        # set sprites to initial physical body state
        #self.reset()
        
    def draw(self):
        for sprite in self.bodies:
            offset = rotate(sprite.body.angle, sprite.offset)
            
            pos = sprite.body.position + offset # TODO DCJ: pyglet 2.x treats this as 2D instead of 3D
            
            sprite.position = (pos.x, pos.y, 0) # TODO DCJ: can't use pos directly
            sprite.rotation = -sprite.body.angle * 180 / math.pi
            
        # batch drawing of sprites
        self.batch.draw()


def rotate(angle, p):
    px = math.cos(angle) * p[0] - math.sin(angle) * p[1]
    py = math.sin(angle) * p[0] + math.cos(angle) * p[1] 
    return (px, py)

def sub(a, b):
    return (a[0]-b[0], a[1]-b[1])

def add(a, b):
    return (a[0]+b[0], a[1]+b[1])

def mul(a, p):
    return (a*p[0], a*p[1])

def create_joint(space, b1, b2, px, py, lim1, lim2):
    """
    b1, b2: Body objects
    px, py: (float) Pivot point in world coordinates
    lim1, lim2: (float)  joint rotation limits (radians)
    """
    b1_b2 = pymunk.PivotJoint(b1, b2, (px, py))
    b1_b2.collide_bodies = False
    space.add(b1_b2)

    b1_b2_limit = pymunk.RotaryLimitJoint(b1, b2, lim1, lim2)
    space.add(b1_b2_limit)
    return b1_b2

def setup_body(space, centerx, centery, mass, width, height, collisionType, groupId = 1):
    moment = pymunk.moment_for_box(mass, (width, height))
    body = pymunk.Body(mass, moment)
    body.position = centerx, centery
    body.start_position = Vec2d(*body.position)
    body.start_angle = 0
    body.width = width
    body.height = height
    
    shape = pymunk.Poly.create_box(body, (width, height))
    shape.friction = 0.3
    shape.collision_type = collisionType
    shape.filter = pymunk.ShapeFilter(group=1)
    shape.group = groupId
    space.add(body, shape)
    return body

# https://pyglet.readthedocs.io/en/latest/modules/sprite.html
def load_sprite(name, body, offset=(0,0)):
    image = pyglet.resource.image(name)                        
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
    sprite = pyglet.sprite.Sprite(image)
    #sprite.scale = body.height / (image.height)
    sprite.body = body
    sprite.offset = offset
    return sprite