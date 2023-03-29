import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# import matplotlib as mpl
# mpl.rcParams['figure.figsize'] = [12, 12]
# mpl.rcParams['figure.dpi'] = 72

# corners are the tuple of tuples: ((a,b), (c,d))
#
# note: it's (y,x) since latitude is x
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

def gps2pixel(gps, corners, imageconf):
    width = corner2width(corners)
    height = corner2height(corners)
    iwidth, iheight = imageconf
    
    (a, b), (c, d) = corners
    y, x = gps
    py = (a - y) * (iheight/height)
    px = (x - b) * (iwidth/width)
    return (int(px), int(py))

def pixel2gps(pixel, corners, imageconf):
    width = corner2width(corners)
    height = corner2height(corners)
    iwidth, iheight = imageconf
    
    (a, b), (c, d) = gps
    px, py = pixel
    x = (px) * (iwidth/width) + a
    y = (-py) * (iheight/height) + b

def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def assert_all_floats(l):
    for ele in l:
        if not isfloat(ele):
            raise RuntimeError(f"found: nonfloat {ele}")

def read_gps(fname):
    """returns (n,2) array of gps data, expects `lattidue_float, longitute_float`"""
    def line2pt(line):
        line = line.strip().split(", ")
        return float(line[0]), float(line[1])

    with open(fname) as fo:
        lines = fo.readlines()
        lines = list(map(line2pt, lines))
        return lines
    
def setarea(px,py):
    for i in range(0, 5):
        for j in range(0, 5):
            if min(i, 4-i) + min(j, 4-j) == 0: # on a corner:
                continue
            y = py + i - 2
            x = px + j - 2
            if x < 0 or x >= imageconf[0] or y < 0 or y >= imageconf[1]:
                continue
            arr[y, x, 0] = 255
            arr[y, x, 1] = 0
            arr[y, x, 2] = 0

corners1 = ((41.837521, -71.413896), (41.817705, -71.371781))
fname1 = "./ss 1.png"

with Image.open(fname1) as im:
    arr = np.asarray(im)[:, :, :3]
    imageconf = arr.shape[1], arr.shape[0]

data = read_gps("./combined.txt")
for pt in data:
    px, py = gps2pixel(pt, corners1, imageconf)
    setarea(px, py)
plt.imshow(arr)
plt.tight_layout()
plt.show()

