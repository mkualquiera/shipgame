import pyglet

def set_cam(window, x, y, s_x, s_y, rotation):
    pyglet.gl.glPushMatrix()
    pyglet.gl.glLoadIdentity()
    pyglet.gl.glTranslatef(window.width//2,window.height//2,0)
    pyglet.gl.glScalef(s_x,s_y,1)
    pyglet.gl.glRotatef(rotation, 0, 0, 1)
    pyglet.gl.glTranslatef(-x,-y,0)

def unset_cam():
    pyglet.gl.glPopMatrix()
