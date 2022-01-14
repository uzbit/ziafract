# Created on May 21 2019
# License is MIT, see COPYING.txt for more details.
# @author: Theodore John McCormack

from zia import Zia
from glbase import GLBase, CUBE, drawCube, getCubeArray
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import random
import time

random.seed()

class Zia3D(GLBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zia = Zia(1, 2, 1, npts=2000)
        xpts, ypts = self.zia.genZia()
        zpts = np.zeros(xpts.shape)
        self.xpts = xpts
        self.ypts = ypts
        self.zpts = zpts
        self.center = np.array([0.0, 0.0, -15.0])
        self.rotate = np.array([0.0, 0.0, 0.0, 1.0])
        self.dRotate = np.array([1.0, 0, 0, 0])
        self.size = 0.05
        self.rotateV = 0.1
        self.time = 0
        
        # Make the zia matrix
        self.arr = np.array([])
        for xpt, ypt, zpt in zip(self.xpts, self.ypts, self.zpts):
            if self.arr.size:
                self.arr = np.concatenate(
                    (self.arr, getCubeArray(xpt, ypt, zpt, self.size))
                )
            else:
                self.arr = getCubeArray(xpt, ypt, zpt, self.size)

        self.col = np.abs(self.arr.copy())

        print(self.arr.shape)
        print(self.arr.ravel())

    def drawGLScene(self):
        self.time += 0.1

        # Clear The Screen And The Depth Buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()  # Reset The View

        # Draw center of origin cube
        glTranslatef(*self.center)
        glColor3f(1, 1, 1)
        drawCube(0, 0, 0, self.size)

        # Draw the zia using draw arrays (executes on Graphics card this way since only one cpu call sends the whole zia)
        glEnableClientState(GL_COLOR_ARRAY)
        glEnableClientState(GL_VERTEX_ARRAY)
        glTranslatef(0, 0, -10 * np.sin(self.time))
        glRotatef(*self.rotate)
        glColorPointer(3, GL_FLOAT, 0, self.col)
        glVertexPointer(3, GL_FLOAT, 0, self.arr)
        glDrawArrays(GL_TRIANGLES, 0, int(self.arr.shape[0] / 3))
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

        #  since this is double buffered, swap the buffers to display what just got drawn.
        glutSwapBuffers()

        self.rotate += self.dRotate

        self.framerate()


def main():
    zia3d = Zia3D("Zia3D", 640, 480)
    zia3d.run()


if __name__ == "__main__":
    main()
