
import matplotlib
matplotlib.use('macosx')
import matplotlib.pyplot as plt
import numpy as np
from zia import Zia

def fract(xpts, ypts, scale, rot):
    if scale <= 0.001:
        return xpts, ypts
    newxpts, newypts = list(), list()
    for xpt, ypt in zip(xpts, ypts):
        xpts1, ypts1 = list((xpts*scale + xpt)), list((ypts*scale + ypt))
        newxpts.append(xpts1)
        newypts.append(ypts1)
    return fract(np.array(newxpts).flatten(), np.array(newypts).flatten(), 0.01*scale, rot)

def main():
    ziaObj = Zia(1.0, 2.0, 1, rayN=5, sunN=4)
    xpts, ypts = ziaObj.genZia()
    xpts, ypts = fract(xpts, ypts, 0.05, 10)
    fig, ax = plt.subplots()
    ax.set_aspect('equal')

    plt.axis('off')
    matplotlib.rcParams['markers.fillstyle'] = 'full'
    matplotlib.rcParams['scatter.marker'] = '.'
    matplotlib.rcParams['lines.markersize'] = 1

    plt.scatter(xpts, ypts, s=1, color='black')
    plt.savefig('ziafract.pdf')
    plt.show()



if __name__ == "__main__":
    main()
