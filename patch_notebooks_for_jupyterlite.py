#!python

import glob
import nbformat as nbf


def main():
    nbs = glob.glob("Notebooks/*.ipynb")

    newtxt = (
        "# This preamble must be executed when running in jupyterlite \n"
        "from IPython.display import display, Markdown\n"
        "import importlib.resources\nimport sympy\n"
        "from sympy import (\n    symbols,\n    Matrix,\n    init_printing,\n"
        "sqrt,\n    simplify,\n    collect,\n    expand,\n    cos,\n    sin,\n"
        "tan,\n    eye,\n    pi,\n    Function,\n    diff,\n    Derivative,\n"
        "cosh,\n    sinh,\n    tanh,\n)\nimport re\nimport os\n"
        "import glob\nimport matplotlib.pyplot as plt\n"
        "import numpy as np\nimport piplite\n"
        'await piplite.install(["ipynbname", "jupyter_core"])\nimport ipynbname'
    )

    newcell = nbf.v4.new_code_cell(source=newtxt)

    for nb in nbs:
        ntbk = nbf.read(nb, nbf.NO_CONVERT)
        ntbk.cells.insert(0, newcell)
        nbf.write(ntbk, nb)


if __name__ == "__main__":
    main()
