from IPython.display import display, Markdown
import pkg_resources
import sympy
from sympy import symbols, Matrix, init_printing, sqrt, simplify, collect


def loadLatexPreamble():
    latexPreambleFilepath = pkg_resources.resource_filename(
        "astrodynamicsbook", "latex_preamble.tex"
    )
    with open(latexPreambleFilepath, "r") as f:
        txt = f.read()
    display(Markdown(txt))


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
        hasattr(v, "__iter__") or isinstance(v, Matrix) or isinstance(v, MatrixBase)
    ) and len(v) == 3, "v must be an iterable of length 3."

    return Matrix([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
