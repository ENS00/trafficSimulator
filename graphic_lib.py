import const
from os import environ

# Main object that interacts with graphic library
class Graphic():
    def __init__(self, title, width, height, background_color = const.BLACK, icon_path = None):
        # set the window position
        environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (const.W_POS_X,const.W_POS_Y)
        
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
        for size in range(8, 90):                                       # Loads all default fonts
            self.fonts[size] = self.graphic.font.Font(None, size)
        self.screen.fill(background_color)                              # Draws all the background
        self.graphic.display.flip()                                     # Updates every pixel of the window

    # Utility to draw a text on the window
    def drawText(self, pos, text, size, color = const.BLACK):
        myfont = self.fonts[size]
        text = myfont.render(str(text), 1, color)
        return self.screen.blit(text, pos)

    def update(self):
        self.graphic.display.flip()                                     # update the screen