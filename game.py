import pyglet
import huesync
import camera
import random
import scene
import engine
import webserver

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

class Ship(pyglet.sprite.Sprite):
    def __init__(self,x,y):
        ship_img = pyglet.resource.image("ship.png")
        ship_img.anchor_x = ship_img.width // 2
        ship_img.anchor_y = ship_img.height // 2
        super().__init__(ship_img, x=x, y=y)
    
    def update(self,dt):
        desheading = int(sync_env.get_entry("ship/desired_heading")
            .get_value()) - 90
        self.rotation += (desheading - self.rotation)/10


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
        camera.set_cam(self.window,ship.x,ship.y,1,1,ship.rotation)
        super().draw()
        camera.unset_cam()

sync_env = huesync.HueSync("192.168.1.58", 60606)
sync_env.create_entry("ship/desired_heading", 90, huesync.DatabaseEntry)
sync_env.run_server()

webserver.run_in_thread(port=62626)

engine.current_scene = GameScene(engine.window)
engine.run()