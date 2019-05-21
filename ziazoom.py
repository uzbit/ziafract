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
    fig.set_facecolor((0, 0, 0))
    plt.axis('off')
    colors = ['red', 'yellow', 'teal']
    for i in range(12):
        zia = Zia(1, 2, np.power(10., -i/2.), npts=2000)
        xpts, ypts = zia.genZia()
        plt.scatter(xpts, ypts, s=20, color=colors[i%len(colors)])

    ani = animation.FuncAnimation(fig, animate, fargs=(ax,),
        frames=range(30, 150), interval=30, blit=False)
    plt.show()

    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=30, metadata=dict(artist='Matplotlib'), bitrate=1800)
    ani.save('infzia.mp4', writer=writer, savefig_kwargs={'facecolor':'black'})
    ani.save('infzia.gif', writer='imagemagick', savefig_kwargs={'facecolor':'black'})


if __name__ == '__main__':
    main()
