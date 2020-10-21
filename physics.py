import math
import pyglet

class PhysicsSprite(pyglet.sprite.Sprite):
    def __init__(self,image,x,y,mass,longitude):
        super().__init__(image,x=x,y=y)
        self.mass = mass
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
        self.va = 0
        self.aa = 0
        self.longitude = longitude
        self.debug_batch = pyglet.graphics.Batch()
        self.vel_line = pyglet.shapes.Line(self.x,self.y,
            self.x + self.vx, self.y + self.vy, color = (0, 0, 255),
            batch = self.debug_batch)
        self.acc_line = pyglet.shapes.Line(self.x,self.y,
            self.x + self.ax, self.y + self.ay, color = (0, 255, 0),
            batch = self.debug_batch)

    def update(self,dt):
        self.vel_line.x = self.x
        self.vel_line.y = self.y
        self.vel_line.x2 = self.x + self.vx
        self.vel_line.y2 = self.y + self.vy
        self.acc_line.x = self.x
        self.acc_line.y = self.y
        self.acc_line.x2 = self.x + self.ax
        self.acc_line.y2 = self.y + self.ay
        self.vx += self.ax * dt
        self.ax = 0
        self.x += self.vx * dt
        self.vy += self.ay * dt
        self.ay = 0
        self.y += self.vy * dt
        self.va += self.aa * dt
        self.aa = 0
        self.rotation += self.va * dt

    def debug(self):
        self.debug_batch.draw()

    def apply_force(self, x, y):
        self.ax += x/self.mass
        self.ay += y/self.mass

    def apply_torque(self, value):
        self.aa += value / ((self.mass*self.longitude)/12)

    def forward(self):
        return (math.cos(math.pi * (180-self.rotation) / 180), 
                math.sin(math.pi * (180-self.rotation) / 180))
    
    def right(self):
        return (math.cos(math.pi * (90-self.rotation) / 180), 
                math.sin(math.pi * (90-self.rotation) / 180))

class ControllableSprite(PhysicsSprite):
    def __init__(self,image,x,y,mass,longitude,forward_thrust=0,
        right_thrust=0,angular_thrust=0):
        super().__init__(image,x,y,mass,longitude)
        self.forward_thrust = forward_thrust
        self.right_thrust = right_thrust
        self.angular_thrust = angular_thrust
        self.forward_throttle = 0
        self.right_throttle = 0
        self.angular_throttle = 0
    
    def update(self, dt):
        fx, fy = self.forward()
        self.apply_force(fx*self.forward_thrust*self.forward_throttle,
                        fy*self.forward_thrust*self.forward_throttle)
        rx, ry = self.right()
        self.apply_force(rx*self.right_thrust*self.right_throttle,
                        ry*self.right_thrust*self.right_throttle)
        self.apply_torque(self.angular_thrust*self.angular_throttle)
        super().update(dt)        