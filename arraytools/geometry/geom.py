# -*- coding: UTF-8 -*-
"""
:Script:   geom.py
:Author:   Dan.Patterson@carleton.ca
:Modified: 2017-10-20
:Purpose:  tools for working with numpy arrays
:Functions: a and b are arrays
: - e_area(a, b=None)
: - e_dist(a, b, metric='euclidean')
: - e_leng(a)
:References:  See ein_geom.py for full details and examples
:  https://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon
:  https://iliauk.com/2016/03/02/centroids-and-centres-numpy-r/
:---------------------------------------------------------------------:
"""
# ---- imports, formats, constants ----
import sys
import numpy as np

ft = {'bool': lambda x: repr(x.astype('int32')),
      'float': '{: 0.3f}'.format}

np.set_printoptions(edgeitems=10, linewidth=80, precision=2, suppress=True,
                    threshold=100, formatter=ft)
np.ma.masked_print_option.set_display('-')  # change to a single -

_script = sys.argv[0]  # print this should you need to locate the script

__all__ = ['e_area', 'e_dist', 'e_leng']


def center(a, remove_dup=True):
    """Return the center of an array. If the array represents a polygon, then
    :  a check is made for the duplicate first and last point to remove one.
    """
    if remove_dup:
        if np.all(a[0] == a[-1]):
            a = a[:-1]
    return a.mean(axis=0)


def centroid(a):
    """Return the centroid of a closed polygon
    : e_area required
    """
    x, y = a.T
    t = ((x[:-1] * y[1:]) - (y[:-1] * x[1:]))
    a_6 = e_area(a) * 6.0  # area * 6.0
    x_c = np.sum((x[:-1] + x[1:]) * t) / a_6
    y_c = np.sum((y[:-1] + y[1:]) * t) / a_6
    return np.asarray([-x_c, -y_c])


def e_area(a, b=None):
    """Area calculation, using einsum.
    :  Some may consider this overkill, but consider a huge list of polygons,
    :  many multipart, many with holes and even multiple version therein.
    :Requires:
    :--------
    :  a - either a 2D+ array of coordinates or arrays of x, y values
    :  b - if a < 2D, then the y values need to be supplied
    :  Outer rings are ordered clockwise, inner holes are counter-clockwise
    :Notes: see ein_geom.py for examples
    :-----------------------------------------------------------------------
    """
    a = np.asarray(a)
    if isinstance(a, (list, tuple)):
        a = np.asarray(a)
    if b is None:
        xs = a[..., 0]
        ys = a[..., 1]
    else:
        xs, ys = a, b
    x0 = np.atleast_2d(xs[..., 1:])
    y0 = np.atleast_2d(ys[..., :-1])
    x1 = np.atleast_2d(xs[..., :-1])
    y1 = np.atleast_2d(ys[..., 1:])
    e0 = np.einsum('...ij,...ij->...i', x0, y0)
    e1 = np.einsum('...ij,...ij->...i', x1, y1)
    area = abs(np.sum((e0 - e1)*0.5))
    return area


def e_dist(a, b, metric='euclidean'):
    """Distance calculation for 1D, 2D and 3D points using einsum
    : a, b   - list, tuple, array in 1,2 or 3D form
    : metric - euclidean ('e','eu'...), sqeuclidean ('s','sq'...),
    :-----------------------------------------------------------------------
    """
    a = np.asarray(a)
    b = np.atleast_2d(b)
    a_dim = a.ndim
    b_dim = b.ndim
    if a_dim == 1:
        a = a.reshape(1, 1, a.shape[0])
    if a_dim >= 2:
        a = a.reshape(np.prod(a.shape[:-1]), 1, a.shape[-1])
    if b_dim > 2:
        b = b.reshape(np.prod(b.shape[:-1]), b.shape[-1])
    diff = a - b
    dist_arr = np.einsum('ijk,ijk->ij', diff, diff)
    if metric[:1] == 'e':
        dist_arr = np.sqrt(dist_arr)
    dist_arr = np.squeeze(dist_arr)
    return dist_arr


def e_leng(a):
    """Length/distance between points in an array using einsum
    : Inputs
    :   a list/array coordinate pairs, with ndim = 3 and the
    :   Minimum shape = (1,2,2), eg. (1,4,2) for a single line of 4 pairs
    :   The minimum input needed is a pair, a sequence of pairs can be used.
    : Returns
    :   d_leng - the distances between points forming the array
    :   length - the total length/distance formed by the points
    :-----------------------------------------------------------------------
    """
    #
    d_leng = 0.0
    # ----
    def _cal(diff):
        """ perform the calculation
        :diff = g[:, :, 0:-1] - g[:, :, 1:]
        : for 4D
        " d = np.einsum('ijk..., ijk...->ijk...', diff, diff).flatten() or
        :   = np.einsum('ijkl, ijkl->ijk', diff, diff).flatten()
        :: d = np.sum(np.sqrt(d)
        """
        d_leng = np.sqrt(np.einsum('ijk,ijk->ij', diff, diff))
        length = np.sum(d_leng.flatten())
        return length, d_leng
    # ----
    diffs = []
    a = np.atleast_2d(a)
    if a.shape[0] == 1:
        return 0.0
    if a.ndim == 2:
        a = np.reshape(a, (1,) + a.shape)
    if a.ndim == 3:
        diff = a[:, 0:-1] - a[:, 1:]
        length, d_leng = _cal(diff)
        diffs.append(d_leng)
    if a.ndim == 4:
        length = 0.0
        for i in range(a.shape[0]):
            diff = a[i][:, 0:-1] - a[i][:, 1:]
            leng, d_leng = _cal(diff)
            diffs.append(d_leng)
            length += leng
    return length, diffs


# ----------------------------------------------------------------------
# __main__ .... code section
if __name__ == "__main__":
    """Optionally...
    : - print the script source name.
    : - run the _demo
    """
#    print("Script... {}".format(_script))
    args = [e_area.__doc__, e_dist.__doc__, e_leng.__doc__]
    print("\n{}\n{}\n{}".format(*args))
    del args
a = np.array([[342000., 5022000.], [342000., 5023000.], [343000., 5023000.],
              [343000., 5022000.], [342000., 5022000.]])
