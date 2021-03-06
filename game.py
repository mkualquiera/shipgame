import pyglet
import huesync
import camera
import random
import scene
import engine
import webserver
import physics


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



class Ship(physics.ControllableSprite):
    def __init__(self,x,y):
        ship_img = pyglet.resource.image("ship.png")
        ship_img.anchor_x = ship_img.width // 2
        ship_img.anchor_y = ship_img.height // 2
        super().__init__(ship_img, x, y, 1000, 64,
            forward_thrust=10000,
            right_thrust=10000,
            angular_thrust=10000)
        pyglet.clock.schedule_interval(self.send_kinematics,0.1)
    
    def send_kinematics(self,dt):
        kinematics = {
            "mass":self.mass,
            "longitude":self.longitude,
            "moment_of_inertia":(self.mass*self.longitude)/12,
            "pos_x":self.x,
            "pos_y":self.y,
            "vel_x":self.vx,
            "vel_y":self.vy,
            "acc_x":self.last_ax,
            "acc_y":self.last_ay,
            "pos_angle":self.rotation,
            "vel_angle":self.va,
            "acc_angle":self.last_aa,
        }
        sync_env.run_coro(sync_env.get_entry("ship/kinematics")
            .set_value(kinematics))
    
    def update(self,dt):
        self.forward_throttle = float(sync_env.get_entry(
            "ship/forward_throttle")
            .get_value()) / 5
        self.right_throttle = float(sync_env.get_entry(
            "ship/right_throttle")
            .get_value()) / 5
        self.angular_throttle = float(sync_env.get_entry(
            "ship/angular_throttle")
            .get_value()) / 5
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
        camera.set_cam(self.window,ship.x,ship.y,1,1,0)#ship.rotation - 90
        super().draw()
        camera.unset_cam()

sync_env = huesync.HueSync("0.0.0.0", 60606)
sync_env.create_entry("ship/forward_throttle", 0, huesync.DatabaseEntry)
sync_env.create_entry("ship/right_throttle", 0, huesync.DatabaseEntry)
sync_env.create_entry("ship/angular_throttle", 0, huesync.DatabaseEntry)
sync_env.create_entry("ship/kinematics", {}, huesync.DatabaseEntry)
sync_env.run_server()

webserver.run_in_thread(port=62626)

engine.current_scene = GameScene(engine.window)
engine.run()