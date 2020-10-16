
class Scene:
    def __init__(self, window):
        self.objects = {}
        self.window = window
    
    def update(self, dt):
        for gameobject in self.objects.values():
            gameobject.update(dt)
    
    def draw(self):
        for gameobject in self.objects.values():
            gameobject.draw()