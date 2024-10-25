import glob
import nbformat as nbf

nbs = glob.glob("Notebooks/*.ipynb")

for nb in nbs:
    ntbk = nbf.read(nb, nbf.NO_CONVERT)

    # find cell with genPrevLink
    headcell = None
    headcellind = None
    for j, c in enumerate(ntbk.cells):
        if "genPrevLink()" in c.source:
            headcell, headcellind = c, j
            break

    # if found, split cell into two
    if headcell is not None:
        origsrc = headcell.source.split("\n")
        origout1 = headcell.outputs[0]
        origout2 = headcell.outputs[1]
        headcell.source = "\n".join(origsrc[:-3])
        headcell.outputs = [origout1]

        newcell = nbf.v4.new_code_cell(
            source="\n".join(origsrc[-2:]), outputs=[origout2]
        )
        ntbk.cells.insert(j + 1, newcell)

        nbf.write(ntbk, nb)
