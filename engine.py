import pyglet
import scene

pyglet.resource.path = ['res']
window = pyglet.window.Window()

pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST
pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

current_scene = scene.Scene(window)

@window.event
def on_draw():
    current_scene.draw()
    
def on_update(dt):
    current_scene.update(dt)

pyglet.clock.schedule(on_update)

def run():
    pyglet.app.run()