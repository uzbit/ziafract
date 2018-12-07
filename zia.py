import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

class Zia(object):

    def __init__(self, r, N=500):
        self._r = r
        self._d = 2.0*self._r/6.0
        self._N = N

    def northRayPoints(self):
        rays = list()
        for n in range(1, 5):
            xrn = (n * self._d + 0.5 * self._d) - self._r
            yrn = self._r * np.sin(np.arccos(xrn / self._r))
            l = self._r if n in [2, 3] else (0.75) * self._r
            rays.append(
                [[xrn, yrn],
                [xrn, yrn + l]],
            )

        xpts, ypts = list(), list()
        for ray in rays:
            dx = (ray[1][0] - ray[0][0])/float(self._N)
            dy = (ray[1][1] - ray[0][1])/float(self._N)
            for i in range(self._N):
                xpts.append(ray[0][0] + dx * i)
                ypts.append(ray[0][1] + dy * i)

        return np.array(xpts), np.array(ypts)

    def genRays(self):
        xpts, ypts = self.northRayPoints()
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
        for t in np.linspace(0, 2 * np.pi, self._N):
            xpts.append(self._r * np.cos(t))
            ypts.append(self._r * np.sin(t))
        return np.array(xpts), np.array(ypts)

    def draw(self):
        fig, ax = plt.subplots()

        xpts, ypts = self.genSun()
        plt.scatter(xpts, ypts, color='r')
        xpts, ypts = self.genRays()
        plt.scatter(xpts, ypts, color='r')

        plt.show()




def main():
    zia = Zia(1)
    zia.draw()



if __name__ == '__main__':
    main()
