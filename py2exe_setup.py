# py2exe setup program
from distutils.core import setup
import py2exe
import sys
import os
import glob, shutil
import pygame
sys.argv.append("py2exe")
os.chdir(sys.argv[0][0:sys.argv[0].rfind("\\")]) #Ensure right folder

VERSION = '0.03'
AUTHOR_NAME = 'James Stevenson'
AUTHOR_EMAIL = 'theboss@comicjk.com'
AUTHOR_URL = "http://comicjk.com/"
PRODUCT_NAME = "Peace"
SCRIPT_MAIN = 'main.pyw'
VERSIONSTRING = PRODUCT_NAME + " ALPHA " + VERSION
ICONFILE = 'data/icon.ico'
 
# Remove the build tree on exit automatically
REMOVE_BUILD_ON_EXIT = True
PYGAMEDIR = os.path.split(pygame.base.__file__)[0]
 
SDL_DLLS = glob.glob(os.path.join(PYGAMEDIR,'*.dll'))
 
if os.path.exists('dist/'): shutil.rmtree('dist/')
 
extra_files = []
"""("",[ICONFILE,'icon.png','readme.txt']),
                   ("data",glob.glob(os.path.join('data','*.dat'))),
                   ("gfx",glob.glob(os.path.join('gfx','*.jpg'))),
                   ("gfx",glob.glob(os.path.join('gfx','*.png'))),
                   ("fonts",glob.glob(os.path.join('fonts','*.ttf'))),
                   ("music",glob.glob(os.path.join('music','*.ogg'))),
                   ("snd",glob.glob(os.path.join('snd','*.wav')))]"""
                   
# List of all modules to automatically exclude from distribution build
# This gets rid of extra modules that aren't necessary for proper functioning of app
# You should only put things in this list if you know exactly what you DON'T need
# This has the benefit of drastically reducing the size of your dist
 
MODULE_EXCLUDES =[
'email',
'AppKit',
'Foundation',
'bdb',
'difflib',
'tcl',
'Tkinter',
'Tkconstants',
'curses',
'distutils',
'setuptools',
'urllib',
'urllib2',
'urlparse',
'BaseHTTPServer',
'_LWPCookieJar',
'_MozillaCookieJar',
'ftplib',
'gopherlib',
'_ssl',
'htmllib',
'httplib',
'mimetools',
'mimetypes',
'rfc822',
'tty',
'webbrowser',
'hashlib',
'base64',
'compiler',
'pydoc']
 
INCLUDE_STUFF = ['encodings',"encodings.latin_1",]
 
setup(windows=[
             {'script': SCRIPT_MAIN,
               'other_resources': [(u"VERSIONTAG",1,VERSIONSTRING)],
               'icon_resources': [(1,ICONFILE)]}],
         options = {"py2exe": {
                             "optimize": 2,
                             "includes": INCLUDE_STUFF,
                             "compressed": 1,
                             "ascii": 1,
                             "bundle_files": 2,
                             "ignores": ['tcl','AppKit','Numeric','Foundation'],
                             "excludes": MODULE_EXCLUDES} },
          name = PRODUCT_NAME,
          version = VERSION,
          data_files = extra_files,
          zipfile = None,
          author = AUTHOR_NAME,
          author_email = AUTHOR_EMAIL,
          url = AUTHOR_URL)
 
# Create the /save folder for inclusion with the installer
#shutil.copytree('save','dist/save')

if os.path.exists('dist/tcl'): shutil.rmtree('dist/tcl') 
 
shutil.rmtree('build/')
shutil.copytree('data', 'dist/data')
 
if os.path.exists('dist/tcl84.dll'): os.unlink('dist/tcl84.dll')
if os.path.exists('dist/tk84.dll'): os.unlink('dist/tk84.dll')
 
for f in SDL_DLLS:
    fname = os.path.basename(f)
    try:
        shutil.copyfile(f,os.path.join('dist',fname))
    except: pass
