# Created on Dec 7 2018
# License is MIT, see COPYING.txt for more details.
# @author: Theodore John McCormack

import numpy as np

class Zia(object):

    def __init__(self, radius, rayLen, scale, npts=None, thickness=100, rayN=500, sunN=500):
        self._r = radius
        self._l = rayLen
        self._s = scale
        self._t = thickness
        self._d = 2.0*self._r/6.0
        self._rN = rayN
        self._sN = sunN
        if npts:
            self._rN = int(npts*0.2*0.25)
            self._sN = int(npts*0.2)

    def genZia(self):
        xpts, ypts = np.array([]), np.array([])
        ptsx, ptsy = self.genSun()
        xpts = np.append(xpts, ptsx)
        ypts = np.append(ypts, ptsy)
        ptsx, ptsy = self.genRays()
        xpts = np.append(xpts, ptsx)
        ypts = np.append(ypts, ptsy)

        return self._s * np.array(xpts), self._s * np.array(ypts)

    def genNorthRays(self):
        rays = list()
        for n in range(1, 5):
            xrn = (n * self._d + 0.5 * self._d) - self._r
            yrn = self._r * np.sin(np.arccos(xrn / self._r))
            l = self._l if n in [2, 3] else (0.75) * self._l
            rays.append(
                [[xrn, yrn],
                [xrn, yrn + l]],
            )

        xpts, ypts = list(), list()
        for k, ray in enumerate(rays):
            N = self._rN
            dx = (ray[1][0] - ray[0][0])/float(N)
            dy = (ray[1][1] - ray[0][1])/float(N)
            for i in range(N):
                xpts.append(ray[0][0] + dx * i)
                ypts.append(ray[0][1] + dy * i)

        return np.array(xpts), np.array(ypts)

    def genRays(self):
        xpts, ypts = self.genNorthRays()
        raysx, raysy = list(xpts), list(ypts)
        t = np.pi/2
        rotM = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
        for i in range(3):
            rays = np.vstack((xpts, ypts))
            rotRays = np.dot(rotM, rays)
            xpts = rotRays[0][:]
            ypts = rotRays[1][:]
            raysx += list(xpts)
            raysy += list(ypts)

        return np.array(raysx), np.array(raysy)

    def genSun(self):
        xpts, ypts = list(), list()
        if self._sN != 4:
            for t in np.linspace(0, 2 * np.pi, self._sN):
                xpts.append(self._r * np.cos(t))
                ypts.append(self._r * np.sin(t))
        else:
            for t in [np.pi/4.0, 3*np.pi/4.0, 5*np.pi/4.0, 7*np.pi/4.0]:
                xpts.append(self._r * np.cos(t))
                ypts.append(self._r * np.sin(t))

        return np.array(xpts), np.array(ypts)

    @staticmethod
    def getImage(N, M, show=True):
        import matplotlib.pyplot as plt
        zia = Zia(0.25, 0.5, 1, npts=500)
        xpts, ypts = zia.genZia()
        img = np.empty((N, M))
        xpts, ypts = ((N/2.)*xpts+(N/2.)), ((M/2.)*ypts+(M/2.))
        for x, y in zip(xpts, ypts):
            img[int(x)][int(y)] = 1

        if show:
            print(np.sum(img))
            print(img)
            plt.imshow(img, cmap='gray')
            plt.show()

        return img

    def draw(self):
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        fig.set_size_inches(1, 1)
        xpts, ypts = self.genZia()
        ax.set_aspect('equal')

        plt.axis('off')
        plt.scatter(xpts, ypts, s=self._t, color='red')
        plt.savefig('zia_small.png', dpi=250)
        plt.show()
