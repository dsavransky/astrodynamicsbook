from IPython.display import display, Markdown, HTML
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
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np  # noqa: F401
from angutils import angutils

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


def animRotSet(rotSet, rotangs, rotsteps=12, body=True):
    """Calling method for generating animation of an ordered set of rotations."""

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    fig.tight_layout()
    (a1,) = ax.plot([0, 1], [0, 0], [0, 0], "r", linewidth=5)
    (a2,) = ax.plot([0, 0], [0, 1], [0, 0], "g", linewidth=5)
    (a3,) = ax.plot([0, 0], [0, 0], [0, 1], "b", linewidth=5)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    Rs = []
    currDCM = np.eye(3)
    for rotax, rotang in zip(rotSet, rotangs):
        if body:
            currax = currDCM[:, rotax - 1]
            Rs.append(angutils.calcDCM(currax, rotang / rotsteps))
            currDCM = np.matmul(angutils.calcDCM(currax, rotang), currDCM)
        else:
            Rs.append(angutils.rotMat(rotax, -rotang / rotsteps))

    ani = animation.FuncAnimation(
        fig,
        animateRotations,
        frames=len(rotSet) * rotsteps + 1,
        fargs=(Rs, [a1, a2, a3], rotsteps),
        interval=100,
    )
    plt.close(fig)
    display(HTML(ani.to_jshtml(default_mode="once")))


def animateRotations(i, Rs, axs, rotsteps):
    """Animation function for animating ordered set of rotations"""

    if i == 0:
        return None

    R = Rs[np.digitize(i, np.arange(len(Rs)) * rotsteps + 1) - 1]
    for a in axs:
        a.set_data_3d(np.matmul(R, np.vstack(a.get_data_3d())))


def animEulerAngsAndAxis(rotSet, rotangs, rotsteps=12, body=True):
    """Calling method for generating animation of an Euler Angle set and the equivalent
    rotation about the Euler axis."""

    # set up figure with two subplots and generate axes
    fig = plt.figure()
    ax1 = fig.add_subplot(121, projection="3d")
    ax2 = fig.add_subplot(122, projection="3d")
    fig.tight_layout()

    tmp = []
    for ax in [ax1, ax2]:
        (a1,) = ax.plot([0, 1], [0, 0], [0, 0], "r", linewidth=5)
        (a2,) = ax.plot([0, 0], [0, 1], [0, 0], "g", linewidth=5)
        (a3,) = ax.plot([0, 0], [0, 0], [0, 1], "b", linewidth=5)
        tmp.append([a1, a2, a3])
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_zlim(-1, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

    axs1, axs2 = tmp

    # compute Euler axis and angle and associated rotation matrix
    DCM = angutils.EulerAng2DCM(rotSet, rotangs, body=body)
    n, th = angutils.DCM2axang(DCM)
    Rea = angutils.calcDCM(n, -th / rotsteps / 3)

    # add Euler axis to second plot
    ax2.plot(
        np.array([-1, 1]) * n[0],
        np.array([-1, 1]) * n[1],
        np.array([-1, 1]) * n[2],
        "k--",
    )

    Rs = []
    currDCM = np.eye(3)
    for rotax, rotang in zip(rotSet, rotangs):
        if body:
            currax = currDCM[:, rotax - 1]
            Rs.append(angutils.calcDCM(currax, rotang / rotsteps))
            currDCM = np.matmul(angutils.calcDCM(currax, rotang), currDCM)
        else:
            Rs.append(angutils.rotMat(rotax, -rotang / rotsteps))

    ani = animation.FuncAnimation(
        fig,
        animateEulerRotations,
        frames=len(rotSet) * rotsteps + 1,
        fargs=(Rs, Rea, axs1, axs2, rotsteps),
        interval=100,
    )
    plt.close(fig)
    display(HTML(ani.to_jshtml(default_mode="once")))


def animateEulerRotations(i, Rs, Rea, axs1, axs2, rotsteps):
    """Animation function for comparing an Euler Angle set and the equivalent
    rotation about the Euler axis."""

    if i == 0:
        return None

    R = Rs[np.digitize(i, np.arange(len(Rs)) * rotsteps + 1) - 1]
    for a in axs1:
        a.set_data_3d(np.matmul(R, np.vstack(a.get_data_3d())))

    for a in axs2:
        a.set_data_3d(np.matmul(Rea, np.vstack(a.get_data_3d())))
