#!python

import glob
import nbformat as nbf


def main():
    nbs = glob.glob("Notebooks/*.ipynb")

    newtxt = (
        "# This preamble must be executed when running in jupyterlite \n"
        "import IPython.display\nimport importlib.resources\nimport sympy\n"
        "import re\nimport os\nimport glob\nimport matplotlib.pyplot \nimport numpy"
        " \n%pip install -q sympyhelpers angutils"
    )

    newcell = nbf.v4.new_code_cell(source=newtxt)

    for nb in nbs:
        # grab notebook
        if nb.startswith("Notebooks/00"):
            continue
        ntbk = nbf.read(nb, nbf.NO_CONVERT)

        # insert new cell at very top
        ntbk.cells.insert(0, newcell)

        # find cell with genPrevLink
        prevcell = None
        for jj, c in enumerate(ntbk.cells):
            if "genPrevLink()" in c.source:
                prevcell = c
                break
        if prevcell is not None:
            ntbk.cells[jj] = nbf.v4.new_markdown_cell(
                prevcell["outputs"][0]["data"]["text/markdown"]
            )

        # find cell with genNextLink
        nextcell = None
        for kk, c in enumerate(ntbk.cells):
            if "genNextLink()" in c.source:
                nextcell = c
                break
        if nextcell is not None:
            ntbk.cells[kk] = nbf.v4.new_markdown_cell(
                nextcell["outputs"][0]["data"]["text/markdown"]
            )

        # write output
        nbf.write(ntbk, nb)


if __name__ == "__main__":
    main()
