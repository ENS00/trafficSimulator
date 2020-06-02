from const import BLACK, pygame, W_POS_X, W_POS_Y
from os import environ

# Main object that interacts with graphic library
class Graphic():
    def __init__(self, title, width, height, background_color = BLACK, icon_path = None):
        # set the window position
        environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (W_POS_X,W_POS_Y)

        pygame.init()                                                   # Initialize library for current OS

        self.graphic = pygame
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
        self.screen.fill(background_color)                              # Draws the background
        self.graphic.display.flip()                                     # Updates every pixel of the window

        self.updateAreas = []

    # Utility to draw a text on the window
    def drawText(self, pos, text, size, color = BLACK):
        myfont = self.fonts[size]
        text = str(text).splitlines()
        for line in text:
            myline = myfont.render(line, 1, color)
            self.screen.blit(myline, pos)
            w,h = myfont.size(line)
            pos[1] += h

    # update all areas on screen
    def update(self):
        self.graphic.display.update(self.updateAreas)
