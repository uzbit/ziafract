# Created on Dec 7 2018
# License is MIT, see COPYING.txt for more details.
# @author: Theodore John McCormack

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from zia import Zia

NUM_DEPTH = 2
SCALE_STEPDOWN = 0.01
INIT_SCALE = 0.05
SCALE_DEPTH = INIT_SCALE * np.power(SCALE_STEPDOWN, NUM_DEPTH)
MAX_PLT_PTS = 1000000

def fract(xpts, ypts, scale):
    print("Calculating for scale = %f, depth = %f, npts = %d..." % (scale, SCALE_DEPTH, len(xpts)))
    if scale <= SCALE_DEPTH:
        print("Reached max depth.")
        return xpts, ypts
    newxpts, newypts = list(), list()
    for xpt, ypt in zip(xpts, ypts):
        xpts1, ypts1 = (xpts*scale + xpt), (ypts*scale + ypt)
        newxpts.append(xpts1)
        newypts.append(ypts1)
    return fract(np.array(newxpts).flatten(), np.array(newypts).flatten(), SCALE_STEPDOWN*scale)

def animate(i, ax):
    st,en = -3.*np.power(2., -i/40.) + 1-np.power(2., -i*SCALE_STEPDOWN), 3.*np.power(2., -i/40.) + 1-np.power(2., -i*SCALE_STEPDOWN)
    ax.set_xlim(st,en)
    ax.set_ylim(st,en)
    return ax,

def main():
    ziaObj = Zia(1.0, 2.0, 1, rayN=5, sunN=4)
    xpts, ypts = ziaObj.genZia()
    xpts, ypts = fract(xpts, ypts, INIT_SCALE)
    print("Finished calculating %d fractal points." % (len(xpts)))

    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    plt.axis('off')
    matplotlib.rcParams['markers.fillstyle'] = 'full'
    matplotlib.rcParams['scatter.marker'] = '.'
    matplotlib.rcParams['lines.markersize'] = 1
    if len(xpts) > MAX_PLT_PTS:
        subinds = np.random.choice(len(xpts), size=MAX_PLT_PTS, replace=False)
    else:
        subinds = list(range(len(xpts)))

    plt.scatter(xpts[subinds], ypts[subinds], s=1, color='black')

    ani = animation.FuncAnimation(fig, animate, fargs=(ax,),
        frames=range(0, 500), interval=30, blit=False)
    plt.show()



if __name__ == "__main__":
    main()
