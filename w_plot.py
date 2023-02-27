import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

def f(x: float, coef: list):
    return coef[0] * x ** 2 + coef[1] * x + coef[2]

def returnSliders(fig, labels, coords, bounds, values):
    sliders = []
    for i in range(len(labels)):
        slider = Slider(
            ax=fig.add_axes(coords[i]),
            label=labels[i],
            valmin=bounds[0],
            valmax=bounds[1],
            valinit=values[i],
            orientation='vertical'
        )
        sliders.append(slider)
    return sliders

x = np.linspace(-20, 20, 1000)
params = [[1, 0, 0], [1, 0, 1]]

fig, ax = plt.subplots()
line1, = ax.plot(x, f(x, params[0]), lw=2, color='red')
line2, = ax.plot(x, f(x, params[1]), lw=2, color='blue')
ax.set_xlabel('x')

fig.subplots_adjust(left=0.25, bottom=0.25)

coordinates = [
    [0.1, 0.25, 0.0225, 0.63], 
    [0.15, 0.25, 0.0225, 0.63], 
    [0.2, 0.25, 0.0225, 0.63], 
    [0.25, 0.25, 0.0225, 0.63],
    [0.3, 0.25, 0.0225, 0.63],
    [0.35, 0.25, 0.0225, 0.63]
]

coefSliders = returnSliders(fig, ['a', 'b', 'c', 'p', 'q', 'r'], coordinates, (-10, 10), np.array(params).flatten())

def update(val):
    newParams = [slider.val for slider in coefSliders]
    newParams = [newParams[0:3], newParams[3:6]]
    line1.set_ydata(f(x, newParams[0]))
    line2.set_ydata(f(x, newParams[1]))
    fig.canvas.draw_idle()

for slider in coefSliders:
    slider.on_changed(update)

resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])

button = Button(resetax, 'Reset', hovercolor='0.975')


def reset(event):
    for slider in coefSliders:
        slider.reset()
button.on_clicked(reset)

plt.show()