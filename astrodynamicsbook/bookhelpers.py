from IPython.display import display, Markdown
import pkg_resources
import sympy
from sympy import symbols, Matrix, init_printing, sqrt, simplify, collect, expand, cos,\
    sin, eye, pi, Function, diff, Derivative
import ipynbname
import re
import os
import glob
import matplotlib.pyplot as plt
import numpy as np

# to be removed:
import warnings
from matplotlib import MatplotlibDeprecationWarning


def loadLatexPreamble():
    """Load LaTeX definitions for future use"""

    # this is temporary and will be removed once ipython fixes the upstream bug
    warnings.filterwarnings("ignore", category=MatplotlibDeprecationWarning)
    init_printing()

    latexPreambleFilepath = pkg_resources.resource_filename(
        "astrodynamicsbook", "latex_preamble.tex"
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


def mat2vec(mat, basis="e"):
    """Transform matrix representation of a vector to the vector equation
    for a given basis.

    Args:
        mat (sympy.Matrix)
            3-element column matrix representing the components of a geometric vector
        basis (str or iterable of strings of length 3)
            If basis is a string, it is used to generate a standard basis-like notation.
            For example, the default (basis = 'e') results in a basis set of:
            '\mathbf{\hat{e}}_1, \mathbf{\hat{e}}_2, \mathbf{\hat{e}}_3'
            If basis is an iterable, then the contents are used exactly to represent the
            basis vectors.

    Returns:
        sympy.Add:
            The full vector in the specified basis (reference frame).

    """

    assert isinstance(basis, str) or (
        hasattr(basis, "__iter__") and len(basis) == 3
    ), "basis input must be a string or iterable of length 3."

    if isinstance(basis, str):
        basis = [r"\mathbf{\hat{" + basis + "}}_" + str(j) for j in range(1, 4)]

    basissyms = symbols(basis)
    basisvec = Matrix(basissyms)

    vec = (mat.T * basisvec)[0]

    return collect(vec, basissyms)

def genRefFrame(basis):
    """ Generate symbols corresponding to unit vectors of a reference frame

    Args:
        basis (str)
            Common character of unit vectors.
            For example, basis = 'e' results in a basis set of:
            '\mathbf{\hat{e}}_1, \mathbf{\hat{e}}_2, \mathbf{\hat{e}}_3'

    Returns:
        sympy.Symbol

    """

    basis = [r"\mathbf{\hat{" + basis + "}}_" + str(j) for j in range(1, 4)]
    return symbols(basis)

def skew(v):
    """Skew-symmetric (cross-produce equivalent) matrix of a geometric vector

    Args:
        v (iterable of length 3):
            Component (column matrix) representation of a geoemtric vector.

    Returns:
        sympy.Matrix:
            The skew-symmetric (3x3) matrix.

    """

    assert (
        hasattr(v, "__iter__")
        or isinstance(v, Matrix)
        or isinstance(v, sympy.MatrixBase)
    ) and len(v) == 3, "v must be an iterable of length 3."

    return Matrix([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def fancyMat(prefix, shape):
    """Create an indexed matrix using the given prefix
    Simillar to symarray, but indexing is 1-based and the matrix must be 2D

    Args:
        prefix (str):
            Name of each matrix element
        shape (iterable of length 2):
            Number of matrix rows and columns.

    Returns:
        sympy.Matrix:
            The resulting (3x3) matrix.


    Notes:
        Indexing is 1-based.


    Example:
        fancyMat('{}^\mathcal{B}C^{\mathcal{A}}',(3,3))
    """

    M = []
    for r in range(1, shape[0] + 1):
        row = []
        for c in range(1, shape[1] + 1):
            row.append(prefix + "_{" + str(r) + str(c) + "}")
        M.append(row)
    M = Matrix(symbols(M))

    return M

def rotMat(axis,angle):
    """ Returns the DCM ({}^B C^A) for a frame rotation of angle about
    the specified axis

    Args:
        axis (int):
            Axis to rotate about (1, 2, or 3)
        angle (float or sympy.Symbol):
            Angle of rotation

    Returns:
        sympy.Matrix:
            The resulting (3x3) matrix.


    """
    if axis == 1:
        return Matrix(([1,0,0],[0,cos(angle),sin(angle)],[0,-sin(angle),cos(angle)]))
    elif axis == 2:
        return Matrix(([cos(angle),0,-sin(angle)],[0,1,0],[sin(angle), 0, cos(angle)]))
    elif axis == 3:
        return Matrix(([cos(angle),sin(angle),0],[-sin(angle),cos(angle),0],[0,0,1]))
    else:
        return -1


def difftotal(expr, diffby, diffmap):
    """Take the total derivative with respect to a variable.

    Args:
        expr (sympy.core.*):
            The expression to differentiate
        diffby (symbol):
            The variable to differentiate with respect to
        diffmap (dict):
            Dictionary of variable derivatives of the form {var:deriv,...}

    Returns:
        sympy.core.*:
            The resulting derivative expression

    Example:

        theta, t, theta_dot = symbols("theta t theta_dot")
        difftotal(cos(theta), t, {theta: theta_dot})
        >> -theta_dot*sin(theta)

    Notes:
        Based almost entirely on the original code by  by Chris Wagner at:
        http://robotfantastic.org/total-derivatives-in-sympy.html

    """
    # Replace all symbols in the diffmap by a functional form
    fnexpr = expr.subs({s:Function(str(s))(diffby) for s in diffmap})
    # Do the differentiation
    diffexpr = diff(fnexpr, diffby)
    # Replace the Derivatives with the variables in diffmap
    derivmap = {Derivative(Function(str(v))(diffby), diffby):dv
                for v,dv in diffmap.items()}
    finaldiff = diffexpr.subs(derivmap)
    # Replace the functional forms with their original form
    return finaldiff.subs({Function(str(s))(diffby):s for s in diffmap})


def difftotalmat(mat,diffby,diffmap):
    """Take the total derivative with respect to a variable of a matrix.

    Args:
        mat (sympy.Matrix):
            The matrix to differentiate
        diffby (symbol):
            The variable to differentiate with respect to
        diffmap (dict):
            Dictionary of variable derivatives of the form {var:deriv,...}

    Returns:
        sympy.Matrix:
            The resulting derivative expression

    Notes:
        Applies method diftotal element by element to the input matrix.

    """

    return Matrix([difftotal(x,diffby,diffmap) for x in mat]).reshape(*mat.shape)


