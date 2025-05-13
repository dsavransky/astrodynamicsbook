from IPython.display import display, Markdown
import importlib.resources
import sympy  # noqa: F401
from sympy import (  # noqa: F401
    symbols,
    Matrix,
    init_printing,
    sqrt,
    simplify,
    collect,
    expand,
    cos,
    sin,
    tan,
    asin,
    acos,
    atan,
    atan2,
    eye,
    pi,
    Function,
    diff,
    Derivative,
    cosh,
    sinh,
    tanh,
)
from sympyhelpers.sympyhelpers import (  # noqa: F401
    mat2vec,
    genRefFrame,
    skew,
    fancyMat,
    rotMat,
    rodriguesEq,
    difftotal,
    difftotalmat,
)
import re
import os
import glob
import matplotlib.pyplot as plt  # noqa: F401
import numpy as np  # noqa: F401

# ipynbname won't work on jupyterlite anyway, so won't bother installing it
try:
    import ipynbname
except ModuleNotFoundError:
    pass


def loadLatexPreamble():
    """Load LaTeX definitions for future use"""

    # this is temporary and will be removed once ipython fixes the upstream bug
    init_printing()

    latexPreambleFilepath = os.path.join(
        importlib.resources.files("astrodynamicsbook"), "latex_preamble.tex"
    )
    with open(latexPreambleFilepath, "r") as f:
        txt = f.read()
    display(Markdown(txt))


def genNextLink():
    """Find next chapter (if it exists) and insert markdown link"""
    currpath = ipynbname.path()
    tmp = os.path.split(currpath)
    currnum = int(re.match(r"(\d+)-[\s\S]+", tmp[1]).group(1))
    nextnum = currnum + 1
    nextfile = glob.glob(os.path.join(tmp[0], f"{nextnum:02}" + "*"))
    if nextfile:
        display(Markdown(r"# [Next](<{}>)".format(os.path.split(nextfile[0])[1])))


def genPrevLink():
    """Find previous chapter (if it exists) and insert markdown link"""
    currpath = ipynbname.path()
    tmp = os.path.split(currpath)
    currnum = int(re.match(r"(\d+)-[\s\S]+", tmp[1]).group(1))
    prevnum = currnum - 1
    prevfile = glob.glob(os.path.join(tmp[0], f"{prevnum:02}" + "*"))
    if prevfile:
        display(Markdown(r"# [Previous](<{}>)".format(os.path.split(prevfile[0])[1])))
