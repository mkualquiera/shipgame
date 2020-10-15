import pyglet
import huesync
import camera
import random

huesync.create_entry("ship/desired_heading", 90, huesync.DatabaseEntry)
huesync.run_server("127.0.0.1",5678)

pyglet.resource.path = ['res']
window = pyglet.window.Window()

pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST
pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

ship_img = pyglet.resource.image("ship.png")
ship_img.anchor_x = ship_img.width // 2
ship_img.anchor_y = ship_img.height // 2

ship = pyglet.sprite.Sprite(ship_img, x=200, y=0)

star_img = pyglet.resource.image("star.png")
star_img.anchor_x = star_img.width // 2
star_img.anchor_y = star_img.height // 2

stars = pyglet.graphics.Batch()

print(window.width)

stars_s = set()

for i in range(30):
    stars_s.add(pyglet.sprite.Sprite(star_img, batch=stars, 
        x=random.randint(-500, +500),
        y=random.randint(-500, +500)))


@window.event
def on_draw():
    window.clear()
    camera.set_cam(window,ship.x,ship.y,1,1,ship.rotation)
    stars.draw()
    ship.draw()
    camera.unset_cam()
    

def on_update(dt):

    desheading = int(huesync.traverse_database("ship/desired_heading")
        .get_value()) - 90
    #print(desheading)
    ship.rotation += (desheading - ship.rotation)/10

pyglet.clock.schedule(on_update)

pyglet.app.run()