from rl.analysis import stadium
import matplotlib.pyplot as plt

def test_plot_stadium():
    plt.figure()
    for a, b in zip(stadium.SURFACE_POINTS, 
                    stadium.SURFACE_POINTS[1:] + [stadium.SURFACE_POINTS[0]]):
        print(list(zip(a, b)))
        plt.plot(*list(zip(a, b)), color='grey')
    plt.xlim(stadium.Y_RANGE)
    plt.ylim(stadium.Y_RANGE)
    plt.savefig('stadium.png')
