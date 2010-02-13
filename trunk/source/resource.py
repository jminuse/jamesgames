import sys, random, math, pygame, socket, heapq, os
from pygame.locals import *

loaded_images = dict()

def image(name, size=None):
    """ Load image and return image object"""
    id = (name,size)
    if id in loaded_images:
        return loaded_images[id]
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        if size is not None: image = pygame.transform.scale(image, size)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    loaded_images[id] = image, image.get_rect()
    return loaded_images[id]

def sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound

def error_log(s): open('error_log.txt',"a").write(s+'\n')
def print_now(*args):
    for a in args: print a,
    print
    sys.stdout.flush()

os.chdir(sys.argv[0][0:sys.argv[0].rfind("\\")]) #Ensure right folder
os.chdir('..')
pygame.init()
screen = pygame.display.set_mode((700, 500))
screenSize = screen.get_size()
pygame.display.set_caption('Peace')
pygame.mouse.set_cursor(*pygame.cursors.broken_x)

font = pygame.font.Font("data/font.ttf", 100)
