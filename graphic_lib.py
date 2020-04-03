import copy
import const

class Graphic():
    def __init__(self, title, width, height, background_color = const.BLACK, icon_path = None):
        const.pygame.init()
        self.graphic = const.pygame
        self.graphic.display.set_caption(title)
        
        if icon_path:
            try:
                self.graphic.display.set_icon(self.graphic.image.load(icon_path))
            except Exception as error:
                print('Couldn\'t load icon with path: "' + icon_path + '".',error)
        self.screen = self.graphic.display.set_mode((width, height))
        self.width = width
        self.height = height
        self.background_color = background_color
        self.fonts = {}
        self.updateAreas = []
        self.screen.fill(background_color)
        self.graphic.display.flip()

    def setFps(self, fps):
        self.fps_speed = round(1000/fps)

    def drawText(self, pos, text, size, font = None, color = const.BLACK):
        if font != None:
            font = const.FONT_PATH+font+const.FONT_EXT
            if font in self.fonts:
                myfont = self.fonts[font]
            else:
                myfont = self.graphic.font.Font(font, size)
                self.fonts[font] = myfont
        else:
            myfont = self.graphic.font.Font(font, size)
        text = myfont.render(text, 1, color)
        return self.screen.blit(text, pos)

    def move(self, obj, x, y):
        if hasattr(obj, 'graphicitems'):
            [i.move(x, y) for i in obj.graphicitems]
        if hasattr(obj, 'graphic'):
            obj.graphic.move(x, y)

    def moveTo(self, obj, x, y):
        if hasattr(obj, 'graphicitems'):
            [i.move_ip(x, y) for i in obj.graphicitems]
        if hasattr(obj, 'graphic'):
            obj.graphic.move_ip(x, y)

    def setCoords(self, obj, newCoords):
        if hasattr(obj, 'graphic'):
            obj.graphic = self.graphic.draw.polygon(self.screen,(0,0,0),((newCoords[0], newCoords[1]),
                                                                (newCoords[2], newCoords[3]),
                                                                (newCoords[4], newCoords[5]),
                                                                (newCoords[6], newCoords[7])))

    def update(self):
        self.graphic.time.wait(self.fps_speed)
        self.graphic.display.update(self.updateAreas)