import sys, random, math, pygame, socket, heapq, os, copy
from pygame.locals import *

loaded_images = {}
def image(name, size=None, rotation=None):
    """ Load image and return image object"""
    id = (name,size,rotation)
    if id in loaded_images:
        return loaded_images[id]
    fullname = os.path.join('data', name)
    try:
        if (name, size, None) in loaded_images: image,rect = loaded_images[(name, size, None)]
        else: image = pygame.image.load(fullname)
        
        if size is not None: image = pygame.transform.scale(image, size)
        if rotation is not None: image = pygame.transform.rotate(image, rotation)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        error_log(message)
        raise SystemExit, message
    loaded_images[id] = image, image.get_rect()
    return loaded_images[id]

loaded_sounds = {}
def sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    if name in loaded_sounds: return loaded_sounds[name]
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        error_log(message)
        raise SystemExit, message
    loaded_sounds[name] = sound
    return sound

def error_log(s): open('error_log.txt',"a").write(s+'\n')
def print_now(*args):
    for a in args: print a,
    print
    sys.stdout.flush()

os.chdir(sys.argv[0][0:sys.argv[0].rfind("\\")]) #Ensure right folder
os.chdir('..')
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.display.init() #Initialize display first
screen = pygame.display.set_mode((700, 500))
screenSize = screen.get_size()
pygame.display.set_caption('A Few More Heroes')
pygame.font.init()
font = pygame.font.Font("data/font.ttf", 70)
text = font.render('A Few More Heroes', True, (30,50,150) )
screen.blit(text, text.get_rect(center=screen.get_rect().center))
pygame.display.flip()
pygame.init() #Then initialize everything else
pygame.mouse.set_cursor(*pygame.cursors.broken_x)
