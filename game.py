import pyglet
import huesync
import camera
import random
import scene
import engine
import webserver
import math

class PhysicsSprite(pyglet.sprite.Sprite):
    def __init__(self,image,x,y,mass):
        super().__init__(image,x=x,y=y)
        self.mass = mass
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
        self.va = 0
        self.aa = 0
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

    def forward(self):
        return (math.cos(math.pi * (180-self.rotation) / 180), 
                math.sin(math.pi * (180-self.rotation) / 180))


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

class Ship(PhysicsSprite):
    def __init__(self,x,y):
        ship_img = pyglet.resource.image("ship.png")
        ship_img.anchor_x = ship_img.width // 2
        ship_img.anchor_y = ship_img.height // 2
        super().__init__(ship_img, x, y, 1000)
        self.rotation = 90
    
    def update(self,dt):
        fx, fy = self.forward()
        self.apply_force(fx*10000, fy*10000)
        desheading = int(sync_env.get_entry("ship/desired_heading")
            .get_value())
        self.rotation += (desheading - self.rotation)/10
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

sync_env = huesync.HueSync("192.168.1.58", 60606)
sync_env.create_entry("ship/desired_heading", 90, huesync.DatabaseEntry)
sync_env.run_server()

webserver.run_in_thread(port=62626)

engine.current_scene = GameScene(engine.window)
engine.run()