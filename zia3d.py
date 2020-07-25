# Created on May 21 2019
# License is MIT, see COPYING.txt for more details.
# @author: Theodore John McCormack

from zia import Zia
from glbase import GLBase
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import random
import time


random.seed(time.time())

def drawCube(xpt, ypt, zpt, size):
    glPushMatrix()
    glTranslatef(xpt, ypt, zpt)
    glBegin(GL_QUADS)                   # Start drawing a 4 sided polygon
    glVertex3f( size, size,-size);		# Top Right Of The Quad (Top)
    glVertex3f(-size, size,-size);		# Top Left Of The Quad (Top)
    glVertex3f(-size, size, size);		# Bottom Left Of The Quad (Top)
    glVertex3f( size, size, size);		# Bottom Right Of The Quad (Top)

    glVertex3f( size,-size, size);		# Top Right Of The Quad (Bottom)
    glVertex3f(-size,-size, size);		# Top Left Of The Quad (Bottom)
    glVertex3f(-size,-size,-size);		# Bottom Left Of The Quad (Bottom)
    glVertex3f( size,-size,-size);		# Bottom Right Of The Quad (Bottom)

    glVertex3f( size, size, size);		# Top Right Of The Quad (Front)
    glVertex3f(-size, size, size);		# Top Left Of The Quad (Front)
    glVertex3f(-size,-size, size);		# Bottom Left Of The Quad (Front)
    glVertex3f( size,-size, size);		# Bottom Right Of The Quad (Front)

    glVertex3f( size,-size,-size);		# Bottom Left Of The Quad (Back)
    glVertex3f(-size,-size,-size);		# Bottom Right Of The Quad (Back)
    glVertex3f(-size, size,-size);		# Top Right Of The Quad (Back)
    glVertex3f( size, size,-size);		# Top Left Of The Quad (Back)

    glVertex3f(-size, size, size);		# Top Right Of The Quad (Left)
    glVertex3f(-size, size,-size);		# Top Left Of The Quad (Left)
    glVertex3f(-size,-size,-size);		# Bottom Left Of The Quad (Left)
    glVertex3f(-size,-size, size);		# Bottom Right Of The Quad (Left)

    glVertex3f( size, size,-size);		# Top Right Of The Quad (Right)
    glVertex3f( size, size, size);		# Top Left Of The Quad (Right)
    glVertex3f( size,-size, size);		# Bottom Left Of The Quad (Right)
    glVertex3f( size,-size,-size);		# Bottom Right Of The Quad (Right)
    glEnd()           
    glPopMatrix()

class Zia3D(GLBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zia = Zia(1, 2, 1, npts=1000)
        xpts, ypts = self.zia.genZia()
        zpts = np.zeros(xpts.shape)
        self.xpts = xpts
        self.ypts = ypts
        self.zpts = zpts  
        self.center = np.array([0.0, 0.0, -8.0])
        self.rotate = np.array([0.1, 0.0, 1.0, 0.0])
        self.dRotate = np.array([1-random.random(), 1-random.random(), 1-random.random(), 1-random.random()])
        self.size = 0.05  
        self.rotateV = 0.1
        self.time = 0
        
    def drawGLScene(self):
        self.time += 0.1
        # Clear The Screen And The Depth Buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()					# Reset The View 

        glTranslatef(*self.center)
        
        size = self.size
        cols = [random.random(), random.random(), random.random()]

        for xpt, ypt, zpt in zip(self.xpts, self.ypts, self.zpts):
            norm = np.linalg.norm([xpt, ypt, zpt])
            
            glColor3f(*cols)
            glRotatef(*self.rotate)      
            drawCube(xpt, ypt, zpt, size)
            
        if random.random() < 0.1: 
            self.dRotate = 0.2*np.array([(1-2*random.random())/norm, (1-2*random.random())/norm, (1-2*random.random())/norm, 1-2*random.random()])
            cols = self.time*np.array([random.random(), random.random(), random.random()])
        
        if self.time > 100:
            self.time = 0

        #  since this is double buffered, swap the buffers to display what just got drawn. 
        glutSwapBuffers()
        
        self.rotate = self.time*self.dRotate
        self.framerate()
        

def main():
    zia3d = Zia3D("Zia3D", 640, 480)
    zia3d.run()

if __name__ == "__main__":
    main()
