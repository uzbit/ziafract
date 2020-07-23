# Created on Dec 7 2018
# License is MIT, see COPYING.txt for more details.
# @author: Theodore John McCormack

from zia import Zia
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

def animate(i, ax):
    st,en = -3.*np.power(10., -i/40.), 3.*np.power(10., -i/40.)
    ax.set_xlim(st,en)
    ax.set_ylim(st,en)
    return ax,

def main():
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    fig.set_size_inches(20, 20)
    fig.set_facecolor((0, 0, 0, 0))
    plt.axis('off')
    colors = ['red', 'yellow', 'turquoise']
    sizes = [400, 100, 10, 1, 1, 1, 1]
    radius = 1.1 # the 0.1 if for the size of the dots to be inset
    ray = 2
    for i in range(6, -1, -1):
        zia = Zia(radius, ray, np.power(radius+ray, float(-i)), npts=2000)
        xpts, ypts = zia.genZia()
        size = sizes[i]
        plt.scatter(xpts, ypts, s=size, color=colors[i%len(colors)])

    # ani = animation.FuncAnimation(fig, animate, fargs=(ax,),
    #      frames=range(30, 150), interval=30, blit=False)
    plt.savefig("zia.png", facecolor=None, edgecolor=None, transparent=True, dpi=100)
    plt.show()
    

    # Writer = animation.writers['ffmpeg']
    # writer = Writer(fps=30, metadata=dict(artist='Matplotlib'), bitrate=1800)
    # ani.save('infzia.mp4', writer=writer, savefig_kwargs={'facecolor':'black'})
    # ani.save('infzia.gif', writer='imagemagick', savefig_kwargs={'facecolor':'black'})


if __name__ == '__main__':
    main()
