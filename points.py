import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# import matplotlib as mpl
# mpl.rcParams['figure.figsize'] = [12, 12]
# mpl.rcParams['figure.dpi'] = 72

# corners are the tuple of tuples: ((a,b), (c,d))
#
# note: it's (y,x) since latitude is first
# (a,b)
# +--------------+
# |              |
# |              |
# |              |
# |              |
# |              |
# +--------------+ (c,d)

# imageconf is tuple (width, height)

def corner2width(corners):
    (a, b), (c, d) = corners
    return d - b

def corner2height(corners):
    (a, b), (c, d) = corners
    return a - c

"""
Given a gps coord, the corners of an image, and its height and width,
returns the corresponding pixel location
"""
def gps2pixel(coords, corners, imageconf):
    width = corner2width(corners)
    height = corner2height(corners)
    iwidth, iheight = imageconf
    
    (a, b), (c, d) = corners
    y, x = coords
    py = (a - y) * (iheight/height)
    px = (x - b) * (iwidth/width)
    return (int(px), int(py))

def pixel2gps(pixel, corners, imageconf):
    """untested"""
    width = corner2width(corners)
    height = corner2height(corners)
    iwidth, iheight = imageconf
    
    (a, b), (c, d) = corners
    px, py = pixel
    x = (px) * (width/iwidth) + a
    y = (-py) * (height/iheight) + b
    return (x,y)

"""
Removes duplicates from list of points

Params:
    points - a list of 2tuples of floats
Returns: list of 2tuples of floats, each tuple distinct
"""
def remove_duplicate_points(points):
    unique_points = []
    for point in points:
        is_a_duplicate = False
        nx, ny = point
        for unique_point in unique_points:
            ux, uy = unique_point
            if nx == ux and ny == uy:
                is_a_duplicate = True
        if not is_a_duplicate:
            unique_points.append(point)
    return unique_points


def read_gps(fname):
    """returns (n,2) array of gps data, expects `lattidue_float, longitute_float`"""
    def line2pt(line):
        line = line.strip().split(", ")
        return float(line[0]), float(line[1])

    with open(fname) as fo:
        lines = fo.readlines()
        points = list(map(line2pt, lines))
        points = remove_duplicate_points(points)
        return points
    
def plot_point(arr,px,py,imageconf):
    ret = arr.copy()
    for i in range(0, 5):
        for j in range(0, 5):
            if min(i, 4-i) + min(j, 4-j) == 0: # on a corner:
                continue
            y = py + i - 2
            x = px + j - 2
            if x < 0 or x >= imageconf[0] or y < 0 or y >= imageconf[1]:
                continue
            ret[y, x, 0] = 255
            ret[y, x, 1] = 0
            ret[y, x, 2] = 0
    return ret

corners1 = ((41.837521, -71.413896), (41.817705, -71.371781))
fname1 = "./ss 1.png"

corners2 = ((41.848696763227515, -71.41241538461539), (41.8333626547619, -71.37795461538461))
fname2 = "./ss 2.png"

corners = corners2
fname = fname2

with Image.open(fname) as im:
    im = np.asarray(im)[:, :, :3]
    imageconf = im.shape[1], im.shape[0]

data = read_gps("./combined.txt")
new_arr = im
for pt in data:
    px, py = gps2pixel(pt, corners, imageconf)
    new_arr = plot_point(new_arr, px, py, imageconf)
# plt.title(fname)
# plt.imshow(new_arr)
# plt.show()




# SLIDER
# ======

from matplotlib.widgets import Slider, Button

fig, ax = plt.subplots()

# adjust the main plot to make room for the sliders
fig.subplots_adjust(left=0.25, bottom=0.25)

# Make a horizontal slider to control the frequency.
axlat = fig.add_axes([0.25, 0.05, 0.65, 0.03])
long_slider = Slider(
    ax=axlat,
    label='longitude',
    valmin=-0.01,
    valmax=0.01,
    valinit=0,
)
axwidth = fig.add_axes([0.25, 0.15, 0.65, 0.03])
width_slider = Slider(
    ax=axwidth,
    label="width",
    valmin=0.8,
    valmax=1.2,
    valinit=1,
)

# Make a vertically oriented slider to control the amplitude
axlat = fig.add_axes([0.15, 0.25, 0.0225, 0.63])
lat_slider = Slider(
    ax=axlat,
    label="latitude",
    valmin=-0.01,
    valmax=0.01,
    valinit=0,
    orientation="vertical"
)
axheight = fig.add_axes([0.05, 0.25, 0.0225, 0.63])
height_slider = Slider(
    ax=axheight,
    label="height",
    valmin=0.8,
    valmax=1.2,
    valinit=1,
    orientation="vertical"
)



# The function to be called anytime a slider's value changes
def update(val):
    global corners
    global im
    ax.clear()
    new_arr = im
    (a, b), (c, d) = corners
    dx = long_slider.val
    dy = lat_slider.val

    a += dy
    c += dy
    b += dx
    d += dx

    cy, cx = ((a + c) / 2, (b + d) / 2)
    a = (a - cy) * height_slider.val + cy
    c = (c - cy) * height_slider.val + cy
    b = (b - cx) * width_slider.val + cx
    d = (d - cx) * width_slider.val + cx
    new_corners = ((a, b), (c, d))

    print('new corners', new_corners)
    for pt in data:
        px, py = gps2pixel(pt, new_corners, imageconf)
        new_arr = plot_point(new_arr, px, py, imageconf)
    ax.imshow(new_arr)

    fig.canvas.draw_idle()

# register the update function with each slider
lat_slider.on_changed(update)
long_slider.on_changed(update)
width_slider.on_changed(update)
height_slider.on_changed(update)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
button = Button(resetax, 'Reset', hovercolor='0.975')


def reset(event):
    lat_slider.reset()
    long_slider.reset()
button.on_clicked(reset)

new_arr = im
for pt in data:
    px, py = gps2pixel(pt, corners, imageconf)
    new_arr = plot_point(new_arr, px, py, imageconf)
ax.imshow(new_arr)
plt.show()


