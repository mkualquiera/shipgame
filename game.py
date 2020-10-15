import pyglet
import huesync

huesync.create_entry("ship/desired_heading", 90, huesync.DatabaseEntry)
huesync.run_server("127.0.0.1",5678)

pyglet.resource.path = ['res']
window = pyglet.window.Window()

ship_img = pyglet.resource.image("ship.png")
ship_img.anchor_x = ship_img.width // 2
ship_img.anchor_y = ship_img.height // 2

ship = pyglet.sprite.Sprite(ship_img, x=window.width//2, y=window.height//2)

@window.event
def on_draw():
    window.clear()
    ship.draw()
    

def on_update(dt):
    desheading = int(huesync.traverse_database("ship/desired_heading")
        .value) - 90
    print(desheading)
    ship.rotation += (desheading - ship.rotation)/10

pyglet.clock.schedule(on_update)

pyglet.app.run()