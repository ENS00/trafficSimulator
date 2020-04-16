import const

# Main object that interacts with graphic library
class Graphic():
    def __init__(self, title, width, height, background_color=const.BLACK, icon_path=None):
        const.pygame.init()                                             # Initialize library for current OS

        self.graphic = const.pygame
        self.graphic.display.set_caption(title)                         # Sets a title for this window

        if icon_path:                                                   # Tries to load an icon
            try:
                self.graphic.display.set_icon(self.graphic.image.load(icon_path))
            except Exception as error:
                print('Couldn\'t load icon with path: "' + icon_path + '".',error)

        self.screen = self.graphic.display.set_mode((width, height))    # Creates the window with a resolution
        self.width = width
        self.height = height
        self.background_color = background_color
        self.fonts = {}
        self.screen.fill(background_color)                              # Draws all the background
        self.graphic.display.flip()                                     # Updates every pixel of the window

        self.updateFrequency = round(1000/const.FPS)

    # Utility to draw a text on the window
    def drawText(self, pos, text, size, font=None, color=const.BLACK):
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

    def update(self):
        self.graphic.display.flip()                                     # update the screen