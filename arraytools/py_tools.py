# -*- coding: UTF-8 -*-
"""
py_tools
========

Script :   py_tools.py

Author :   Dan_Patterson@carleton.ca

Modified: 2018-05-25

-------

Purpose : tools for working with python, numpy and other python packages

- iterables :
    _flatten, flatten_shape, pack, unpack
- folders :
    get_dir, folders, sub-folders, dirr2, dir_py, *dirr*
Useage:

References:

------------------------------------------------------------------------------
"""
# ---- imports, formats, constants ---------------------------------------
import sys
import os
from textwrap import dedent, wrap
import numpy as np


ft = {'bool': lambda x: repr(x.astype(np.int32)),
      'float_kind': '{: 0.3f}'.format}
np.set_printoptions(edgeitems=10, linewidth=80, precision=2, suppress=True,
                    threshold=100, formatter=ft)
np.ma.masked_print_option.set_display('-')  # change to a single -

script = sys.argv[0]  # print this should you need to locate the script


__all__ = ['comp_info',
           'get_dir', 'folders', 'sub_folders',  # basic folder functions
           'dirr2', 'dir_py', 'dirr',    # object and directory functions
           '_flatten', 'flatten_shape',  # iterables
           'pack', 'unpack']


# ---- (1) computer, python stuff ... code section ---------------------------
#
def comp_info():
    """Return information for the computer and python version
    """
    import platform
    winv =platform.platform()
    py_ver = platform.python_version()
    plat = platform.architecture()
    proc = platform.processor()
    p_node = platform._node()
    u_name = platform.uname()
    ud = u_name._asdict()
    udl = list(zip(ud.keys(), ud.values()))
    frmt = """
    ---------------------------
    Computer/python information

    Platform:        {}
    python version:  {}
    windows version: {}
    processor:       {}
    node:            {}
    user/machine:    {}\n
    Alternate form...."""
    args = [winv, py_ver,plat, proc, p_node, u_name]
    print(dedent(frmt).format(*args))
    print("\n".join(["{:<10}: {}".format(*i) for i in udl]))


# ---- (2) general file functions ... code section ---------------------------
#
def get_dir(path):
    """Get the directory list from a path, excluding geodatabase folders.
    Used by.. folders

    >>> get_dir('C:/Git_Dan/arraytools')
    ['C:\\Git_Dan\\arraytools\\.spyproject',
     'C:\\Git_Dan\\arraytools\\analysis',
     ... snip ...
     'C:\\Git_Dan\\arraytools\\__pycache__']
    >>> # ---- common path prefix
    >>> os.path.commonprefix(get_dir('C:/Git_Dan/arraytools'))
    'C:\\Git_Dan\\arraytools\\'
    """
    if os.path.isfile(path):
        path = os.path.dirname(path)
    p = os.path.normpath(path)
    full = [os.path.join(p, v) for v in os.listdir(p)]
    dirlist = [val for val in full if os.path.isdir(val)]
    return dirlist


def folders(path, first=True, prefix=""):
    """ Print recursive listing of folders in a path.  Make sure you `raw`
    format the path...
    ::
        r'c:\Temp'  or 'c:/Temp' or 'c:\\Temp'

    - Requires : _get_dir .... also, an example of path common prefix
    """
    if first:  # Detect outermost call, print a heading
        print("-"*30 + "\n|.... Folder listing for ....|\n|--{}".format(path))
        prefix = "|-"
        first = False
        cprev = path
    dirlist = get_dir(path)
    for d in dirlist:
        fullname = os.path.join(path, d)  # Turn name into full pathname
        if os.path.isdir(fullname):       # If a directory, recurse.
            cprev = path
            pad = ' ' * len(cprev)
            n = d.replace(cprev, pad)
            print(prefix + "-" + n)  # fullname) # os.path.relpath(fullname))
            p = "  "
            folders(fullname, first=False, prefix=p)
    # ----


def sub_folders(path):
    """Print the folders in a path
    """
    import pathlib
    print("Path...\n{}".format(path))
    r = " "*len(path)
    f = "\n".join([(p._str).replace(path, r)
                   for p in pathlib.Path(path).iterdir() if p.is_dir()])
    print("{}".format(f))


# ---- (3) dirr ... code section ... -----------------------------------------
#
def dirr2(obj, sub=None, colwise=False, cols=3, prn=True):
    """call either numpy or python dirr function
    """
    obj = dir(obj)
    if sub is not None:
        obj = [i for i in obj if sub in i]
    if 'np' in globals().keys():
        dirr(obj, colwise=colwise, cols=cols, prn=prn)
    else:
        dir_py(obj, colwise=colwise, cols=cols, prn=prn)


def dir_py(obj, colwise=False, cols=4, prn=True):
    """The non-numpy version of dirr
    """
    from itertools import zip_longest as zl
    a = dir(obj)
    w = max([len(i) for i in a])
    frmt = (("{{!s:<{}}} ".format(w)))*cols
    csze = len(a) / cols  # split it
    csze = int(csze) + (csze % 1 > 0)
    if colwise:
        a_0 = [a[i: i+csze] for i in range(0, len(a), csze)]
        a_0 = list(zl(*a_0, fillvalue=""))
    else:
        a_0 = [a[i: i+cols] for i in range(0, len(a), cols)]
    if hasattr(obj, '__name__'):
        args = ["-"*70, obj.__name__, obj]
    else:
        args = ["-"*70, type(obj), "py version"]
    txt_out = "\n{}\n| dir({}) ...\n|    {}\n-------".format(*args)
    cnt = 0
    for i in a_0:
        cnt += 1
        txt = "\n  ({:>03.0f})  ".format(cnt)
        frmt = (("{{!s:<{}}} ".format(w)))*len(i)
        txt += frmt.format(*i)
        txt_out += txt
    if prn:
        print(txt_out)
    else:
        return txt_out


def dirr(obj, colwise=False, cols=4, sub=None, prn=True):
    """A formatted `dir` listing of an object, module, function... anything you
    can get a listing for.

    Source : arraytools module in py_tools.py

    Return a directory listing of a module's namespace or a part of it if the
    `sub` option is specified.

    Use `prn=True`, to print. `prn=False`, returns a string.

    Parameters
    ----------
    colwise : boolean
        `True` or `1`, otherwise, `False` or `0`
    cols : number
      pick a size to suit
    sub : text
      sub array with wildcards
      ::
        `arr*`  begin with `arr`
        `*arr`  endswith `arr` or
        `*arr*` contains `arr`
    prn : boolean
      `True` for print or `False` to return output as string

    Notes
    -----
    See the `inspect` module for possible additions like `isfunction`,
    'ismethod`, `ismodule`

    **Examples**::

        dirr(art, colwise=True, cols=3, sub=None, prn=True)  # all columnwise
        dirr(art, colwise=True, cols=3, sub='arr', prn=True) # just the `arr`'s

          (001)    _arr_common     arr2xyz         arr_json
          (002)    arr_pnts        arr_polygon_fc  arr_polyline_fc
          (003)    array2raster    array_fc
          (004)    array_struct    arrays_cols
    """
    err = """
    ...No matches found using substring .  `{0}`
    ...check with wildcards, *, ... `*abc*`, `*abc`, `abc*`
    """
    d_arr = dir(obj)
    a = np.array(d_arr)
    dt = a.dtype.descr[0][1]
    if sub not in (None, '', ' '):
        start = [0, 1][sub[0] == "*"]
        end = [0, -1][sub[-1] == "*"]
        if not start and end:
            a = [i for i in d_arr
                 if i.startswith(sub[start:end], start, len(i))]
        elif start and end:
            a = [i for i in d_arr
                 if sub[1:4] in i[start:len(i)]]
        elif not end:
            sub = sub.replace("*", "")
            a = [i for i in d_arr
                 if i.endswith(sub, start, len(i))]
        else:
            a = []
        if len(a) == 0:
            print(dedent(err).format(sub))
            return None
        num = max([len(i) for i in a])
    else:
        num = int("".join([i for i in dt if i.isdigit()]))
    frmt = ("{{!s:<{}}} ".format(num)) * cols
    if colwise:
        z = np.array_split(a, cols)
        zl = [len(i) for i in z]
        N = max(zl)
        e = np.empty((N, cols), dtype=z[0].dtype)
        for i in range(cols):
            n = min(N, zl[i])
            e[:n, i] = z[i]
    else:
        csze = len(a) / cols
        rows = int(csze) + (csze % 1 > 0)
        z = np.array_split(a, rows)
        e = np.empty((len(z), cols), dtype=z[0].dtype)
        N = len(z)
        for i in range(N):
            n = min(cols, len(z[i]))
            e[i, :n] = z[i][:n]
    if hasattr(obj, '__name__'):
        args = ["-"*70, obj.__name__, obj]
    else:
        args = ["-"*70, type(obj), "np version"]
    txt_out = "\n{}\n| dir({}) ...\n|    {}\n-------".format(*args)
    cnt = 1
    for i in e:
        txt_out += "\n  ({:>03.0f})    {}".format(cnt, frmt.format(*i))
        cnt += cols
    if prn:
        print(txt_out)
    else:
        return txt_out


# ---- (4) iterables ---------------------------------------------------------
#
def _flatten(a_list, flat_list=None):
    """Change the isinstance as appropriate.

    Flatten an object using recursion

    see: itertools.chain() for an alternate method of flattening.
    """
    if flat_list is None:
        flat_list = []
    for item in a_list:
        if isinstance(item, (list, tuple, np.ndarray, np.void)):
            _flatten(item, flat_list)
        else:
            flat_list.append(item)
    return flat_list


def flatten_shape(shp, completely=False):
    """Flatten a shape using itertools.

    Parameters:
    -----------

    shp :
       either a polygon, polyline, point shape
    completely :
       True returns points for all objects
       False, returns Array for polygon or polyline objects
    Notes:
    ------
        __iter__ - Polygon, Polyline, Array all have this property...
        Points do not.
    """
    import itertools
    if completely:
        vals = [i for i in itertools.chain(shp)]
    else:
        vals = [i for i in itertools.chain.from_iterable(shp)]
    return vals


def pack(a, param='__iter__'):
    """Pack an iterable into an ndarray or object array
    """
    if not hasattr(a, param):
        return a
    return np.asarray([np.asarray(i) for i in a])


def unpack(iterable, param='__iter__'):
    """Unpack an iterable based on the param(eter) condition using recursion.

    Notes:
    ------
    - Use `flatten` for recarrays or structured arrays.
    - See main docs for more information and options.
    - To produce uniform array from this, use the following after this is done.
    >>> out = np.array(xy).reshape(len(xy)//2, 2)

    - To check whether unpack can be used.
    >>> isinstance(x, (list, tuple, np.ndarray, np.void)) like in flatten above
    """
    xy = []
    for x in iterable:
        if hasattr(x, param):
            xy.extend(unpack(x))
        else:
            xy.append(x)
    return xy


# ---- (5) demos  -------------------------------------------------------------
#
def _demo():
    """
    : -
    """
    pass

# ----------------------------------------------------------------------------
# ---- __main__ .... code section --------------------------------------------
if __name__ == "__main__":
    """Optionally...
    : - print the script source name.
    : - run the _demo
    """
#    print("Script... {}".format(script))
    _demo()

