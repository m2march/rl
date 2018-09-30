import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import animation

fig = plt.figure(figsize=(5, 5))
circ = patches.Circle((-1, 1), radius=1, color='red')

fps = 25

def init():
    ax = plt.gca()
    ax.add_patch(circ)
    plt.xlim(-25, 25)
    plt.ylim(-25, 25)


def update(n):
    rad = n % fps
    circ.set_radius(rad)
    
    return [circ],

anim = animation.FuncAnimation(func=update, fig=fig, init_func=init, 
                               frames=fps * 5)
anim.save('test.mp4', writer='ffmpeg', fps=fps)
