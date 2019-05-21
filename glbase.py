
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys


class GLBase(object):
    # Some api in the chain is translating the keystrokes to this octal string
    # so instead of saying: ESCAPE = 27, we use the following.
    ESCAPE = b'\x1b'

    def __init__(self, title, width, height):    
        # Number of the glut window.
        self.title = title
        self.width = width
        self.height = height
        self.window = 0
        self.init = False
        
    # A general OpenGL initialization function.  Sets all of the initial parameters. 
    def initGL(self):				# We call this right after our OpenGL window is created.
        glClearColor(0.0, 0.0, 0.0, 0.0)	# This Will Clear The Background Color To Black
        glClearDepth(1.0)					# Enables Clearing Of The Depth Buffer
        glDepthFunc(GL_LESS)				# The Type Of Depth Test To Do
        glEnable(GL_DEPTH_TEST)				# Enables Depth Testing
        glShadeModel(GL_SMOOTH)				# Enables Smooth Color Shading
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()					# Reset The Projection Matrix
                                            # Calculate The Aspect Ratio Of The Window
        gluPerspective(45.0, float(self.width)/float(self.height), 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)

    # The function called when our window is resized (which shouldn't happen if you enable fullscreen, below)
    def reSizeGLScene(self, width, height):
        self.width = width
        self.height = height
        if self.height == 0:						# Prevent A Divide By Zero If The Window Is Too Small 
            self.height = 1

        glViewport(0, 0, self.width, self.height)		# Reset The Current Viewport And Perspective Transformation
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(self.width)/float(self.height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    # The main drawing function. 
    # -----------OVERWRITE-----------
    def drawGLScene(self):
        if not self.init:
            self.rtri = 0
            self.rquad = 0
            self.init = True

        # Clear The Screen And The Depth Buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()					# Reset The View 

        # Move Left 1.5 units and into the screen 6.0 units.
        glTranslatef(-1.5, 0.0, -6.0)

        # We have smooth color mode on, this will blend across the vertices.
        # Draw a triangle rotated on the Y axis. 
        glRotatef(self.rtri, 0.0, 1.0, 0.0)      # Rotate
        glBegin(GL_POLYGON)                 # Start drawing a polygon
        glColor3f(1.0, 0.0, 0.0)            # Red
        glVertex3f(0.0, 1.0, 0.0)           # Top
        glColor3f(0.0, 1.0, 0.0)            # Green
        glVertex3f(1.0, -1.0, 0.0)          # Bottom Right
        glColor3f(0.0, 0.0, 1.0)            # Blue
        glVertex3f(-1.0, -1.0, 0.0)         # Bottom Left
        glEnd()                             # We are done with the polygon

        # We are "undoing" the rotation so that we may rotate the quad on its own axis.
        # We also "undo" the prior translate.  This could also have been done using the
        # matrix stack.
        glLoadIdentity()
        
        # Move Right 1.5 units and into the screen 6.0 units.
        glTranslatef(1.5, 0.0, -6.0)

        # Draw a square (quadrilateral) rotated on the X axis.
        glRotatef(self.rquad, 1.0, 0.0, 0.0)		# Rotate 
        glColor3f(0.3, 0.5, 1.0)            # Bluish shade
        glBegin(GL_QUADS)                   # Start drawing a 4 sided polygon
        glVertex3f(-1.0, 1.0, 0.0)          # Top Left
        glVertex3f(1.0, 1.0, 0.0)           # Top Right
        glVertex3f(1.0, -1.0, 0.0)          # Bottom Right
        glVertex3f(-1.0, -1.0, 0.0)         # Bottom Left
        glEnd()                             # We are done with the polygon

        # What values to use?  Well, if you have a FAST machine and a FAST 3D Card, then
        # large values make an unpleasant display with flickering and tearing.  I found that
        # smaller values work better, but this was based on my experience.
        self.rtri += 1.0                  # Increase The Rotation Variable For The Triangle
        self.rquad -= 1.0                 # Decrease The Rotation Variable For The Quad


        #  since this is double buffered, swap the buffers to display what just got drawn. 
        glutSwapBuffers()

    # The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)  
    def keyPressed(*args):
        #print(args[1])
        # If escape is pressed, kill everything.
        if args[1] == GLBase.ESCAPE:
            sys.exit()

    def run(self):
        glutInit(sys.argv)

        # Select type of Display mode:   
        #  Double buffer 
        #  RGBA color
        # Alpha components supported 
        # Depth buffer
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        
        # get a width x height window 
        glutInitWindowSize(self.width, self.height)
        
        # the window starts at the upper left corner of the screen 
        glutInitWindowPosition(0, 0)
        
        # Okay, like the C version we retain the window id to use when closing, but for those of you new
        # to Python (like myself), remember this assignment would make the variable local and not global
        # if it weren't for the global declaration at the start of main.
        self.window = glutCreateWindow(self.title)

        # Register the drawing function with glut, BUT in Python land, at least using PyOpenGL, we need to
        # set the function pointer and invoke a function to actually register the callback, otherwise it
        # would be very much like the C version of the code.	
        glutDisplayFunc(self.drawGLScene)
        
        # Uncomment this line to get full screen.
        # glutFullScreen()

        # When we are doing nothing, redraw the scene.
        glutIdleFunc(self.drawGLScene)
        
        # Register the function called when our window is resized.
        glutReshapeFunc(self.reSizeGLScene)
        
        # Register the function called when the keyboard is pressed.  
        glutKeyboardFunc(self.keyPressed)

        # Initialize our window. 
        self.initGL()

        # Start Event Processing Engine	
        glutMainLoop()


def main():
    glBaseObj = GLBase("test", 640, 480)
    glBaseObj.run()

if __name__ == "__main__":
    main()