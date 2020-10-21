import pyglet
import huesync
import camera
import random
import scene
import engine
import webserver
import math

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


class Starfield(pyglet.graphics.Batch):
    def __init__(self,n,xa,xb,ya,yb):
        super().__init__()
        self.stars_s = set()
        star_img = pyglet.resource.image("star.png")
        star_img.anchor_x = star_img.width // 2
        star_img.anchor_y = star_img.height // 2
        for _ in range(n):
            self.stars_s.add(pyglet.sprite.Sprite(star_img, batch=self, 
                x=random.randint(xa, xb),
                y=random.randint(ya, yb)))

    def update(self,dt):
        pass


def angle_diff(a,b):
    diff = (a-b+180) % 360 - 180
    return diff + 360 if diff < -180 else diff

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


class Ship(ControllableSprite):
    def __init__(self,x,y):
        ship_img = pyglet.resource.image("ship.png")
        ship_img.anchor_x = ship_img.width // 2
        ship_img.anchor_y = ship_img.height // 2
        super().__init__(ship_img, x, y, 1000, 64,
            forward_thrust=10000,
            right_thrust=1000,
            angular_thrust=1000)
    
    def update(self,dt):
        self.forward_throttle = float(sync_env.get_entry(
            "ship/forward_throttle")
            .get_value()) / 100
        self.right_throttle = float(sync_env.get_entry(
            "ship/right_throttle")
            .get_value()) / 100
        self.angular_throttle = float(sync_env.get_entry(
            "ship/angular_throttle")
            .get_value()) / 100
        super().update(dt)

    def draw(self):
        super().draw()
        super().debug()


class GameScene(scene.Scene):
    def __init__(self,window):
        super().__init__(window)

        self.objects["starfield"] = Starfield(40, -500, 500, -500, 500)
        self.objects["ship"] = Ship(100, 100)

    def update(self,dt):
        super().update(dt)

    def draw(self):
        self.window.clear()
        ship = self.objects['ship']
        camera.set_cam(self.window,ship.x,ship.y,1,1,ship.rotation - 90)
        super().draw()
        camera.unset_cam()

sync_env = huesync.HueSync("0.0.0.0", 60606)
sync_env.create_entry("ship/forward_throttle", 0, huesync.DatabaseEntry)
sync_env.create_entry("ship/right_throttle", 0, huesync.DatabaseEntry)
sync_env.create_entry("ship/angular_throttle", 0, huesync.DatabaseEntry)
sync_env.run_server()

webserver.run_in_thread(port=62626)

engine.current_scene = GameScene(engine.window)
engine.run()