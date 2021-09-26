from IPython.display import display, Markdown
import pkg_resources
import sympy
from sympy import symbols, Matrix, init_printing, sqrt, simplify, collect, expand
import ipynbname
import re
import os
import glob

#to be removed:
import warnings
from matplotlib import MatplotlibDeprecationWarning

def loadLatexPreamble():
    """ Load LaTeX definitions for future use"""

    #this is temporary and will be removed once ipython fixes the upstream bug
    warnings.filterwarnings('ignore', category=MatplotlibDeprecationWarning)
    init_printing()

    latexPreambleFilepath = pkg_resources.resource_filename(
        "astrodynamicsbook", "latex_preamble.tex"
    )
    with open(latexPreambleFilepath, "r") as f:
        txt = f.read()
    display(Markdown(txt))

def genNextLink():
    """ Find next chapter (if it exists) and insert markdown link """
    currpath = ipynbname.path()
    tmp = os.path.split(currpath)
    currnum = int(re.match('(\d+)-[\s\S]+',tmp[1]).group(1))
    nextnum = currnum + 1
    nextfile = glob.glob(os.path.join(tmp[0],f'{nextnum:02}'+'*'))
    if nextfile:
        display(Markdown(r"[Next](<{}>)".format(os.path.split(nextfile[0])[1]) ))


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
        hasattr(v, "__iter__") or isinstance(v, Matrix) or isinstance(v, sympy.MatrixBase)
    ) and len(v) == 3, "v must be an iterable of length 3."

    return Matrix([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])

def fancyMat(prefix,shape):
    """ Create an indexed matrix using the given prefix
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
    for r in range(1, shape[0]+1):
        row = []
        for c in range(1, shape[1]+1):
            row.append(prefix+'_{'+str(r)+str(c)+'}')
        M.append(row)
    M = Matrix(symbols(M))

    return M
