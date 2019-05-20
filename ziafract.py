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
MAX_PLT_PTS = None #100000
FRAMES = 200

# depth0 center at 0.0, 0.0
# depth1 centerx at 0.7
# depth2 centerx at 0.7 + 0.7*SCALE_STEPDOWN
# depth3 centerx at 0.7 + 0.7*SCALE_STEPDOWN + 0.7*SCALE_STEPDOWN*SCALE_STEPDOWN
#
# depthN = posx*(1*min(1, depth)+SCALE_STEPDOWN*min(1, depth)+SCALE_STEPDOWN^2+...SCALE_STEPDOWN^N)
# at depth1 i should be at 1*FRAMES/NUM_DEPTH and shiftx,y should be 0.7, 0.7
# at depth2 i should be at 2*FRAMES/NUM_DEPTH and shiftx,y should be 0.7, 0.7
#
# i = depth*FRAMES/NUM_DEPTH
# depth = i*NUM_DEPTH/FRAMES

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
    print(f"Frame {i} of {FRAMES}")
    POSX, POSY = np.cos(np.pi/4), np.sin(np.pi/4)
    dpf = 1.0/FRAMES
    st = -3.*dpf*(FRAMES-i)
    en =  3.*dpf*(FRAMES-i)
    depth = (float(i)*NUM_DEPTH/FRAMES)

    def getShift(scale, shift):
        if scale <= SCALE_DEPTH:
            return shift
        return getShift(SCALE_STEPDOWN*scale, shift+scale*shift)

    shift = getShift(INIT_SCALE, i*dpf*POSX)

    st += shift
    en += shift
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
    if MAX_PLT_PTS and len(xpts) > MAX_PLT_PTS:
        subinds = np.random.choice(len(xpts), size=MAX_PLT_PTS, replace=False)
    else:
        subinds = list(range(len(xpts)))

    plt.scatter(xpts[subinds], ypts[subinds], s=1, color='black')

    ani = animation.FuncAnimation(fig, animate, fargs=(ax,),
        frames=range(0, FRAMES), interval=30, blit=False)
    #plt.show()

    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=30, metadata=dict(artist='Matplotlib'), bitrate=1800)
    ani.save('infzia2.mp4', writer=writer, savefig_kwargs={'facecolor':'white'})
    ani.save('infzia2.gif', writer='imagemagick', savefig_kwargs={'facecolor':'white'})



if __name__ == "__main__":
    main()
