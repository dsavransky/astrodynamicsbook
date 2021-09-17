import os
from IPython.display import display, Markdown
import pkg_resources
import sympy
from sympy import symbols, Matrix

def loadLatexPreamble():
    latexPreambleFilepath = pkg_resources.resource_filename(
        "astrodynamicsbook", "latex_preamble.tex"
    )
    with open(latexPreambleFilepath, "r") as f:
        txt = f.read()
    display(Markdown(txt))

def mat2vec(mat,basis='e'):
    """ Transform matrix representation of a vector to the vector equation
    for a given basis.

    basis can be either a string (i.e. 'e' becomes basis e_1,e_2,e_3) or an
    iterable of length 3.

    mat is assumed to be a sympy matrix representing a column vector
    """

    assert isinstance(basis,str) or (hasattr(basis,'__iter__') and len(basis)==3),\
            "basis input must be a string or iterable of length 3."

    if isinstance(basis,str):
        basis = ['\mathbf{\hat{'+basis+'}}_'+str(j) for j in range(1,4)]

    basissyms = symbols(basis,commutative=False)
    basisvec = Matrix(basissyms)

    return (mat.T*basisvec)[0]


