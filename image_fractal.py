#!/usr/bin/env python

# -*- coding: utf-8 -*-
# Created on Tue Apr 08 08:45:59 2014
# License is MIT, see COPYING.txt for more details.
# @author: Danilo de Jesus da Silva Bellini

# Modified for masking fractals with images by Ted McCormack around Dec 18, 2018
# Original repo from author above is: https://github.com/danilobellini/fractal

"""
Julia and Mandelbrot fractals image creation
"""

from __future__ import division, print_function
import sys
import time
from itertools import takewhile
import pylab, argparse, collections, inspect, functools
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import multiprocessing
import cv2

Point = collections.namedtuple("Point", ["x", "y"])


def pair_reader(dtype):
    return lambda data: Point(*map(dtype, data.lower().split("x")))


DEFAULT_SIZE = "512x512"
DEFAULT_DEPTH = "256"
DEFAULT_ZOOM = "1"
DEFAULT_CENTER = "0x0"
DEFAULT_COLORMAP = "gray"

DEFAULT_SMALL_IMG = "imgs/zia_small.png"
DEFAULT_LARGE_IMG = "imgs/zia_big.png"

# best constants so far:
#  -0.75472 -0.11792 j
#

# run with:
#  python3 image_fractal.py julia -0.75472 -0.06592 j --size=1000x1000  --depth=500 --zoom=0.6 --show


def repeater(f):
    """
    Returns a generator function that returns a repeated function composition
    iterator (generator) for the function given, i.e., for a function input
    ``f`` with one parameter ``n``, calling ``repeater(f)(n)`` yields the
    values (one at a time)::

             n, f(n), f(f(n)), f(f(f(n))), ...

    Examples
    --------

    >>> func = repeater(lambda x: x ** 2 - 1)
    >>> func
    <function ...>
    >>> gen = func(3)
    >>> gen
    <generator object ...>
    >>> next(gen)
    3
    >>> next(gen) # 3 ** 2 - 1
    8
    >>> next(gen) # 8 ** 2 - 1
    63
    >>> next(gen) # 63 ** 2 - 1
    3968

    """

    @functools.wraps(f)
    def wrapper(n):
        val = n
        while True:
            yield val
            val = f(val)

    return wrapper


def amount(gen, limit=float("inf")):
    """
    Iterates through ``gen`` returning the amount of elements in it. The
    iteration stops after at least ``limit`` elements had been iterated.

    Examples
    --------

    >>> amount(x for x in "abc")
    3
    >>> amount((x for x in "abc"), 2)
    2
    >>> from itertools import count
    >>> amount(count(), 5) # Endless, always return ceil(limit)
    5
    >>> amount(count(start=3, step=19), 18.2)
    19
    """
    size = 0
    for unused in gen:
        size += 1
        if size >= limit:
            break
    return size


def in_circle(radius):
    """Returns ``abs(z) < radius`` boolean value function for a given ``z``"""
    return lambda z: z.real ** 2 + z.imag ** 2 < radius ** 2


def fractal_eta(z, func, limit, radius=2):
    """
    Fractal Escape Time Algorithm for pixel (x, y) at z = ``x + y * 1j``.
    Returns the fractal value up to a ``limit`` iteration depth.
    """
    return amount(takewhile(in_circle(radius), repeater(func)(z)), limit)


def cqp(c):
    """Complex quadratic polynomial, function used for Mandelbrot fractal"""
    return lambda z: z ** 2 + c


def get_model(model, depth, c):
    """
    Returns the fractal model function for a single pixel.
    """
    if model == "julia":
        func = cqp(c)
        return lambda x, y: fractal_eta(x + y * 1j, func, depth)
    if model == "mandelbrot":
        return lambda x, y: fractal_eta(0, cqp(x + y * 1j), depth)
    raise ValueError("Fractal not found")


def generate_fractal(
    model,
    c=None,
    size=pair_reader(int)(DEFAULT_SIZE),
    depth=int(DEFAULT_DEPTH),
    zoom=float(DEFAULT_ZOOM),
    center=pair_reader(float)(DEFAULT_CENTER),
):
    """
    2D Numpy Array with the fractal value for each pixel coordinate.
    """
    num_procs = multiprocessing.cpu_count()
    print("CPU Count:", num_procs)
    start = time.time()

    # Create a pool of workers, one for each row
    pool = multiprocessing.Pool(num_procs)
    procs = [
        pool.apply_async(generate_row, [model, c, size, depth, zoom, center, row])
        for row in range(size[1])
    ]

    # Generates the intensities for each pixel
    img = pylab.array([row_proc.get() for row_proc in procs])

    print("Fractal time taken:", time.time() - start)
    start = time.time()

    # Place images
    img = place_images(img, size, DEFAULT_SMALL_IMG, DEFAULT_LARGE_IMG)

    print("Image time taken:", time.time() - start)

    fig = plt.figure()
    ax = fig.gca(projection="3d")
    x = range(len(img))
    y = range(len(img[0]))
    x2, y2 = pylab.meshgrid(x, y)
    surf = ax.plot_surface(x2, y2, img, cmap=cm.coolwarm, linewidth=0, antialiased=True)

    plt.show()

    return img


def dist2(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def fuse(points, scales, multiplier):
    ret = []
    indexes = list(range(len(scales)))
    indexes.sort(key=scales.__getitem__, reverse=True)
    points = list(map(points.__getitem__, indexes))
    scales = list(map(scales.__getitem__, indexes))

    n = len(points)
    taken = [False] * n
    for i in range(n):
        if not taken[i]:
            count = 1
            point = [points[i][0], points[i][1]]
            taken[i] = True
            d2 = multiplier * scales[i]
            d2 *= d2
            for j in range(i + 1, n):
                if dist2(points[i], points[j]) < d2:
                    point[0] += points[j][0]
                    point[1] += points[j][1]
                    count += 1
                    taken[j] = True
            point[0] /= count
            point[1] /= count
            ret.append([int(point[0]), int(point[1])])
    return np.array(ret)


MIN_FOR_PEAK = 0.4
RADIAL_MULTIPLIER = 50
MIN_ZIA_SIZE = 35
ZIA_SCALE = 150


def place_images(img, size, imagesmall, imagebig):
    blurx, blury = int(size[0] / 200.0), int(size[0] / 200.0)
    img = cv2.blur(img, (blurx, blury))
    img = np.sqrt(img)

    def read_image(path):
        imageimg = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        imageimg = cv2.bitwise_not(imageimg)
        return imageimg

    imagesmall = read_image(imagesmall)
    imagebig = read_image(imagebig)

    scaledimg = img / np.max(img)
    orig = np.array(scaledimg)
    peaks = np.argwhere((scaledimg >= MIN_FOR_PEAK))

    peakscales = list()
    for peak in peaks:
        scale = scaledimg[peak[0]][peak[1]]
        peakscales.append(scale)
    peaks = fuse(peaks, peakscales, RADIAL_MULTIPLIER)
    if len(peaks) % 2 == 1:
        peaks = peaks[:-1]

    fig = plt.figure()
    plt.imshow(img, cmap="gray")
    plt.scatter([x[1] for x in peaks], [x[0] for x in peaks])
    plt.show()

    def get_xy(cx, cy, mag, s):
        x1 = int(cx - s / 2 * mag)
        x2 = int(cx + s / 2 * mag)
        diff = x2 - x1
        if diff % 2 == 1:
            x1 += 1
            diff -= 1
        y1 = int(cy - diff / 2)
        y2 = int(cy + diff / 2)
        return max(x1, 0), min(x2, size[0]), max(y1, 0), min(y2, size[1])

    def select_box(img, cx, cy, mag, s):
        x1, x2, y1, y2 = get_xy(cx, cy, mag, s)
        return img[x1:x2, :][:, y1:y2]

    def replace_box(img, repl, cx, cy, mag, s):
        x1, x2, y1, y2 = get_xy(cx, cy, mag, s)
        for i, x in enumerate(range(x1, x2)):
            for j, y in enumerate(range(y1, y2)):
                img[x][y] += repl[i][j]
        return img

    mask = np.zeros(orig.shape)
    imageimg = imagesmall
    for peak in peaks:
        scale = scaledimg[peak[0]][peak[1]]
        subbox = select_box(mask, peak[0], peak[1], scale, ZIA_SCALE)
        # print(subbox.shape)
        if subbox.shape[0] <= MIN_ZIA_SIZE:
            continue
        subbox = np.transpose(cv2.resize(imageimg, subbox.shape, cv2.INTER_CUBIC))
        mask = replace_box(mask, subbox, peak[0], peak[1], scale, ZIA_SCALE)

    img = mask * img
    # print(np.max(img))
    # print(np.std(img[img>0]))
    # print(np.min(img[img>0]))

    img = np.power(img, 0.3)
    fig, ax = plt.subplots()
    plt.axis("off")
    plt.tight_layout()
    ax.set_aspect("equal")
    # print(np.max(img))
    # print(np.std(img[img>0]))
    # print(np.min(img[img>0]))
    # # for row in img:
    # 	print(row)
    plt.imshow(img, cmap="gray")
    plt.savefig("imgs/juliaziafract.png", dpi=size[0])
    plt.show()
    return img


def threshold_img(img, cutoff):
    for i in range(len(img)):
        for j in range(len(img[0])):
            if img[i][j] <= cutoff:
                img[i][j] = 0
    return img


def generate_row(model, c, size, depth, zoom, center, row):
    """
    Generate a single row of fractal values, enabling shared workload.
    """
    func = get_model(model, depth, c)
    width, height = size
    cx, cy = center
    side = max(width, height)
    sidem1 = side - 1
    deltax = (side - width) / 2  # Centralize
    deltay = (side - height) / 2
    y = (2 * (height - row + deltay) / sidem1 - 1) / zoom + cy
    return [
        func((2 * (col + deltax) / sidem1 - 1) / zoom + cx, y) for col in range(width)
    ]


def img2output(img, cmap=DEFAULT_COLORMAP, output=None, show=False):
    """Plots and saves the desired fractal raster image"""
    if output:
        pylab.imsave(output, img, cmap=cmap)
    if show:
        pylab.imshow(img, cmap=cmap)
        pylab.show()


def call_kw(func, kwargs):
    """Call func(**kwargs) but remove the possible unused extra keys before"""
    keys = inspect.getargspec(func).args
    kwfiltered = dict((k, v) for k, v in kwargs.items() if k in keys)
    return func(**kwfiltered)


def exec_command(kwargs):
    """Fractal command from a dictionary of keyword arguments (from CLI)"""
    kwargs["img"] = call_kw(generate_fractal, kwargs)
    call_kw(img2output, kwargs)


def cli_parse_args(args=None, namespace=None):
    """
    CLI (Command Line Interface) parsing based on ``ArgumentParser.parse_args``
    from the ``argparse`` module.
    """
    # CLI interface description
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="by Danilo J. S. Bellini",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "model", choices=["julia", "mandelbrot"], help="Fractal type/model"
    )
    parser.add_argument(
        "c",
        nargs="*",
        default=argparse.SUPPRESS,
        help="Single Julia fractal complex-valued constant "
        "parameter (needed for julia, shouldn't appear "
        "for mandelbrot), e.g. -.7102 + .2698j (with the "
        "spaces), or perhaps with zeros and 'i' like "
        "-0.6 + 0.4i. If the argument parser gives "
        "any trouble, just add spaces between the numbers "
        "and their signals, like '- 0.6 + 0.4 j'",
    )
    parser.add_argument(
        "-s",
        "--size",
        default=DEFAULT_SIZE,
        type=pair_reader(int),
        help="Size in pixels for the output file",
    )
    parser.add_argument(
        "-d",
        "--depth",
        default=DEFAULT_DEPTH,
        type=int,
        help="Iteration depth, the step count limit",
    )
    parser.add_argument(
        "-z",
        "--zoom",
        default=DEFAULT_ZOOM,
        type=float,
        help="Zoom factor, assuming data is shown in the "
        "[-1/zoom; 1/zoom] range for both dimensions, "
        "besides the central point displacement",
    )
    parser.add_argument(
        "-c",
        "--center",
        default=DEFAULT_CENTER,
        type=pair_reader(float),
        help="Central point in the image",
    )
    parser.add_argument(
        "-m",
        "--cmap",
        default=DEFAULT_COLORMAP,
        help="Matplotlib colormap name to be used",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=argparse.SUPPRESS,
        help="Output to a file, with the chosen extension, " "e.g. fractal.png",
    )
    parser.add_argument(
        "--show",
        default=argparse.SUPPRESS,
        action="store_true",
        help="Shows the plot in the default Matplotlib backend",
    )

    # Process arguments
    ns_parsed = parser.parse_args(args=args, namespace=namespace)
    if ns_parsed.model == "julia" and "c" not in ns_parsed:
        parser.error("Missing Julia constant")
    if ns_parsed.model == "mandelbrot" and "c" in ns_parsed:
        parser.error("Mandelbrot has no constant")
    if "output" not in ns_parsed and "show" not in ns_parsed:
        parser.error("Nothing to be done (no output file name nor --show)")
    if "c" in ns_parsed:
        try:
            ns_parsed.c = complex("".join(ns_parsed.c).replace("i", "j"))
        except ValueError as exc:
            parser.error(exc)

    return vars(ns_parsed)


if __name__ == "__main__":
    exec_command(cli_parse_args())
