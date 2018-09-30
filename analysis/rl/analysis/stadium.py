import itertools

import matplotlib.pyplot as plt
from matplotlib import transforms
from mpl_toolkits import mplot3d

WIDTH = 8240
LENGTH = 10280
HEIGHT = 2000 # TODO: Revisar con más datos

X_RANGE = (-WIDTH / 2, WIDTH / 2)
Y_RANGE = (-LENGTH / 2, LENGTH / 2)
Z_RANGE = (0, HEIGHT)

ELBOW_WIDTH = 1330

GOAL_DEPTH = (100 /  1210) * LENGTH
GOAL_WIDTH = (200 /  1050) * WIDTH

SURFACE_POINTS = [
    (- GOAL_WIDTH / 2, Y_RANGE[0]),
    (X_RANGE[0] + ELBOW_WIDTH, Y_RANGE[0]),
    (X_RANGE[0], Y_RANGE[0] + ELBOW_WIDTH),
    (X_RANGE[0], 0),

    (X_RANGE[0], Y_RANGE[1] - ELBOW_WIDTH),
    (X_RANGE[0] + ELBOW_WIDTH, Y_RANGE[1]),
    (- GOAL_WIDTH / 2, Y_RANGE[1]),
    (- GOAL_WIDTH / 2, Y_RANGE[1] + GOAL_DEPTH),

    (GOAL_WIDTH / 2, Y_RANGE[1] + GOAL_DEPTH),
    (GOAL_WIDTH / 2, Y_RANGE[1]),
    (X_RANGE[1] - ELBOW_WIDTH, Y_RANGE[1]),
    (X_RANGE[1], Y_RANGE[1] - ELBOW_WIDTH),

    (X_RANGE[1], 0),
    (X_RANGE[1], Y_RANGE[0] + ELBOW_WIDTH),
    (X_RANGE[1] - ELBOW_WIDTH, Y_RANGE[0]),
    (GOAL_WIDTH / 2, Y_RANGE[0]),

    (GOAL_WIDTH / 2, Y_RANGE[0] - GOAL_DEPTH),
    (- GOAL_WIDTH / 2, Y_RANGE[0] - GOAL_DEPTH)
]

SURFACE_LINES = list(zip(SURFACE_POINTS, 
                         SURFACE_POINTS[1:] + [SURFACE_POINTS[0]]))


def prep_2d_court(width=10, rotate=False):
    fig = plt.figure(figsize=(width, width))
    ax = plt.gca()

    base = ax.transData
    rot = transforms.Affine2D().rotate_deg(90 if rotate else 0)
    trans = rot + base

    return fig, ax, trans


def draw_2d_court(ax, trans, court_color='grey'):
    '''
    Plots the rocket league standard court.

    Returns:
        ax: current axis
        trans: the transformation to set to the transform parameter in further
               plots
    '''

    for a, b in SURFACE_LINES:
        ax.plot(*zip(a, b), color=court_color, transform=trans)

    ax.set_xlim(Y_RANGE[0] * 1.2, Y_RANGE[1] * 1.2)
    ax.set_ylim(Y_RANGE[0] * 1.2, Y_RANGE[1] * 1.2)

    return ax, trans


def prep_3d_court(width=10):
    fig = plt.figure(figsize=(width * 1.7, width))
    ax = plt.axes(projection='3d')

    return fig, ax


def draw_3d_court(ax, court_color='grey'):
    for x, y in SURFACE_LINES:
        xs, ys = zip(x, y)
        ax.plot(xs, ys, [0, 0], color=court_color)

    ax.set_xlim(Y_RANGE[0] * 1.2, Y_RANGE[1] * 1.2)
    ax.set_ylim(Y_RANGE[0] * 1.2, Y_RANGE[1] * 1.2)
    ax.set_zlim(0, HEIGHT * 1.3)
