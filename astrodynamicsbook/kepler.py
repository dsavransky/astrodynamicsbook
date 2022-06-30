import numpy as np
import warnings
from typing import Union, Any
import numpy.typing as npt

floatORarray = Union[float, np.ndarray]

def forcendarray(x: floatORarray) -> npt.NDArray[Any]:
    """Convert any numerical value into 1-D ndarray

    Args:
        x (float or numpy.ndarray):
            Input
    Returns:
        numpy.ndarray:
            Same size as input but in ndarray form
    """

    return np.array(x, ndmin=1).astype(float).flatten()


def validateOrbitalStateInputs(r: np.ndarray, v: np.ndarray, mu: floatORarray) -> tuple:
    """Validate and standardize dimensionality of orbital state vector inputs

    Args:
        r (numpy.ndarray):
            Components of orbital radius. 3n elements in 1D as
            [r1(1);r1(2);r1(3);r2(1);r2(2)r2(3);...;rn(1);rn(2);rn(3)]
            or in 2D as nx3 or 3xn
        v (numpy.ndarray):
            Components of orbital velocity. Same stacking as r
        mu (float or numpy.ndarray):
            Gravitational parameters.  If float, assuming all state vectors belong to
            the same system.

    Returns:
        tuple:
        r (numpy.ndarray):
            Components of orbital radius. (n x 3)
        v (numpy.ndarray):
            Components of orbital velocity. (n x 3)
        mu (numpy.ndarray):
            Gravitational parameters.  (size 1 or n)
    """
    # figure out dimensionality of inputs
    assert len(r.shape) <= 3, "r input must have max dimension 2"
    if (len(r.shape) == 1) or (1 in r.shape):
        r = r.flatten().reshape(r.size // 3, 3)
    else:
        assert 3 in r.shape, "If r is 2D, one dimension must be length 3"
        if r.shape[0] == 3:
            r = r.transpose()

    assert len(v.shape) <= 3, "v input must have max dimension 2"
    if (len(v.shape) == 1) or (1 in v.shape):
        v = v.flatten().reshape(v.size // 3, 3)
    else:
        assert 3 in v.shape, "If v is 2D, one dimension must be length 3"
        if v.shape[0] == 3:
            v = v.transpose()

    mu = forcendarray(mu)

    assert len(r) == len(v), "r and v must have same sizes."
    assert mu.size == 1 or mu.size == len(
        r
    ), "mu must be scalar or same length as r and v"

    return r, v, mu


def unitvector(vec, mag):
    """Return the unit vectors of an array of vectors

    Args:
        vec(numpy.ndarray):
            Vectors as nx3
        mag (numpy.ndarray):
            Vector magnitudes as nx1

    Returns:
        numpy.ndarray:
            Unit vectors in the same layout as input
    """

    return vec / np.tile(mag, (3, 1)).transpose()


def invKepler(
    M, e, tol=None, E0=None, maxIter=100, return_nu=False, convergence_error=True
):
    """Finds eccentric/hyperbolic/parabolic anomaly from mean anomaly and eccentricity

    This method uses Newton-Raphson iteration to find the eccentric
    anomaly from mean anomaly and eccentricity, assuming a closed (0<e<1)
    orbit.

    Args:
        M (float or ndarray):
            mean anomaly (rad)
        e (float or ndarray):
            eccentricity (eccentricity may be a scalar if M is given as
            an array, but otherwise must match the size of M.)
        tolerance (float):
            Convergence of tolerance. Defaults to eps(2*pi)
        E0 (float or ndarray):
            Initial guess for iteration.  Defaults to Taylor-expansion based value for
            closed orbits and Vallado-derived heuristic for open orbits. If set, must
            match size of M.
        maxiter (int):
            Maximum numbr of iterations.  Optional, defaults to 100.
        return_nu (bool):
            Return true anomaly (defaults false)
        convergence_error (bool):
            Raise error on convergence failure. Defaults True.  If false, throws a
            warning.

    Returns:
        tuple:
            E (ndarray):
                eccentric/parabolic/hyperbolic anomaly (rad)
            numIter (ndarray):
                Number of iterations
            nu (ndarray):
                True anomaly (returned only if return_nu=True)

    Notes:
        If either M or e are scalar, and the other input is an array, the scalar input
        will be expanded to the same size array as the other input.  So, a scalar M
        and array e will result in the calculation of the eccentric anomaly for one
        mean anomaly at a variety of eccentricities, and a scalar e and array M input
        will result in the calculation of eccentric anomalies for one eccentricity at
        a variety of mean anomalies.  If both inputs are arrays then they are matched
        element by element.

    """

    # make sure M and e are of the correct format.
    # if either is scalar, expand to match sizes
    M = forcendarray(M)
    e = forcendarray(e)
    if e.size != M.size:
        if e.size == 1:
            e = np.array([e[0]] * len(M))
        if M.size == 1:
            M = np.array([M[0]] * len(e))

    assert e.shape == M.shape, "Incompatible inputs."
    assert np.all((e >= 0)), "e values below zero"

    # define output
    Eout = np.zeros(M.size)
    numIter = np.zeros(M.size)

    # circles
    cinds = e == 0
    Eout[cinds] = M[cinds]

    # ellipses
    einds = (e > 0) & (e < 1)
    if any(einds):

        Me = np.mod(M[einds], 2 * np.pi)
        ee = e[einds]

        # initial values for E
        if E0 is None:
            E = Me / (1 - ee)
            mask = ee * E**2 > 6 * (1 - ee)
            E[mask] = np.cbrt(6 * Me[mask] / ee[mask])
        else:
            E = E0[einds]

        # Newton-Raphson setup
        counter = np.ones(E.shape)
        err = np.ones(E.shape)

        # set tolerance is none provided
        if tol is None:
            etol = np.spacing(2 * np.pi)
        else:
            etol = tol

        while (np.max(err) > etol) and (np.max(counter) < maxIter):
            inds = err > etol
            E[inds] = E[inds] - (Me[inds] - E[inds] + ee[inds] * np.sin(E[inds])) / (
                ee[inds] * np.cos(E[inds]) - 1
            )
            err[inds] = np.abs(Me[inds] - (E[inds] - ee[inds] * np.sin(E[inds])))
            counter[inds] += 1

        if np.max(counter) == maxIter:
            if convergence_error:
                raise Exception("Maximum number of iterations exceeded")
            else:
                warnings.warn("Maximum number of iterations exceeded")

        Eout[einds] = E
        numIter[einds] = counter

    # parabolae
    pinds = e == 1
    if np.any(pinds):
        q = 9 * M[pinds] / 6
        B = (q + np.sqrt(q**2 + 1)) ** (1.0 / 3.0) - (np.sqrt(q**2 + 1) - q) ** (
            1.0 / 3.0
        )
        Eout[pinds] = B

    # hyperbolae
    hinds = e > 1
    if np.any(hinds):
        Mh = M[hinds]
        eh = e[hinds]

        # initialize H
        if E0 is None:
            H = Mh / (eh - 1)
            mask = eh * H**2 > 6 * (eh - 1)
            H[mask] = np.cbrt(6 * Mh[mask] / eh[mask])
        else:
            H = E0[hinds]

        # Newton-Raphson setup
        counter = np.ones(H.shape)
        err = np.ones(H.shape)

        # set tolerance is none provided
        if tol is None:
            htol = np.spacing(np.max([2 * np.pi, np.max(np.abs(Mh))])) * 4.0
        else:
            htol = tol

        while (np.max(err) > htol) and (np.max(counter) < maxIter):
            inds = err > htol
            H[inds] = H[inds] + (Mh[inds] - eh[inds] * np.sinh(H[inds]) + H[inds]) / (
                eh[inds] * np.cosh(H[inds]) - 1
            )
            err[inds] = np.abs(Mh[inds] - (eh[inds] * np.sinh(H[inds]) - H[inds]))
            counter[inds] += 1

        if np.max(counter) == maxIter:
            if convergence_error:
                raise Exception("Maximum number of iterations exceeded")
            else:
                warnings.warn("Maximum number of iterations exceeded")

        Eout[hinds] = H
        numIter[hinds] = counter

    out = (Eout, numIter)
    if return_nu:
        nuout = np.zeros(M.size)

        # circles
        nuout[cinds] = M[cinds]

        # ellipses
        if np.any(einds):
            nuout[einds] = np.mod(
                2 * np.arctan(np.sqrt((1 + e[einds]) / (1 - e[einds])) * np.tan(E / 2)),
                2 * np.pi,
            )

        # parabolae
        if np.any(pinds):
            nuout[pinds] = 2 * np.arctan(B)

        # hyperbolae
        if np.any(hinds):
            nuout[hinds] = 2 * np.arctan(
                np.sqrt((e[hinds] + 1) / (e[hinds] - 1)) * np.tanh(H / 2)
            )

        out += (nuout,)

    return out


def kepler2orbstate(a, e, O, I, w, mu, nu):
    """Calculate orbital state vectors from Keplerian elements

    Args:
        a (float or numpy.ndarray):
            Semi-major axis (or semi-parameter is e = 1)
        e (float or numpy.ndarray):
            eccentricity
        O (float or numpy.ndarray):
            longitude of ascending node (rad)
        I (float or numpy.ndarray):
            inclination (rad)
        w (float or numpy.ndarray):
            arguments of periapsis (rad)
        mu (float or numpy.ndarray):
            Gravitational parameters.  If float, assuming all state vectors belong to
            the same system.
        nu (float or numpy.ndarray):
            True anomaly (rad)

    Returns:
        tuple:
            r (numpy.ndarray):
                Components of orbital radius (n x 3)
            v (numpy.ndarray):
                Components of orbital velocity (n x 3)

    Notes:
        r.flatten() and v.flatten() will automatically stack elements in the proper
        order in a 1D array

    """

    # force all inputs to ndarrays
    a = forcendarray(a)
    e = forcendarray(e)
    O = forcendarray(O)
    I = forcendarray(I)
    w = forcendarray(w)
    mu = forcendarray(mu)
    nu = forcendarray(nu)

    # semi-parameter
    ell = a * (1 - e**2)
    ell[e == 1] = a[e == 1]

    # specific angular momentum
    h = np.sqrt(mu * ell)

    # orbital radius
    r = ell / (1 + e * np.cos(nu))

    r = np.vstack(
        [
            r * (-np.sin(O) * np.sin(nu + w) * np.cos(I) + np.cos(O) * np.cos(nu + w)),
            r * (np.sin(O) * np.cos(nu + w) + np.sin(nu + w) * np.cos(I) * np.cos(O)),
            r * np.sin(I) * np.sin(nu + w),
        ]
    ).transpose()

    v = np.vstack(
        [
            -mu
            * (
                e * np.sin(O) * np.cos(I) * np.cos(w)
                + e * np.sin(w) * np.cos(O)
                + np.sin(O) * np.cos(I) * np.cos(nu + w)
                + np.sin(nu + w) * np.cos(O)
            )
            / h,
            mu
            * (
                -e * np.sin(O) * np.sin(w)
                + e * np.cos(I) * np.cos(O) * np.cos(w)
                - np.sin(O) * np.sin(nu + w)
                + np.cos(I) * np.cos(O) * np.cos(nu + w)
            )
            / h,
            mu * (e * np.cos(w) + np.cos(nu + w)) * np.sin(I) / h,
        ]
    ).transpose()

    return r, v


def orbstate2kepler(r, v, mu):
    """Calculate  Keplerian elements given orbital state vectors

    Args:
        r (numpy.ndarray):
            Components of orbital radius. 3n elements in 1D as
            [r1(1);r1(2);r1(3);r2(1);r2(2)r2(3);...;rn(1);rn(2);rn(3)]
            or in 2D as nx3 or 3xn
        v (numpy.ndarray):
            Components of orbital velocity. Same stacking as r
        mu (float or numpy.ndarray):
            Gravitational parameters.  If float, assuming all state vectors belong to
            the same system.

    Returns:
        tuple:
            a (float):
                Semi-major axis (or semi-parameter where e = 1)
            e (float):
                eccentricity
            O (float):
                longitude of ascending node (rad)
            I (float):
                inclination (rad)
            w (float):
                arguments of periapsis (rad)
            tp (float):
                time of periapsis passage
    """
    r, v, mu = validateOrbitalStateInputs(r, v, mu)

    v2 = np.sum(v * v, axis=1)  # velocity magnitude squared
    rmag = np.sqrt(np.sum(r * r, axis=1))  # orbital radius magnitude

    hvec = np.cross(r, v)  # specific angular momentum vector
    h2 = np.sum(hvec * hvec, axis=1)  # magnitude squared
    hmag = np.sqrt(h2)  # momentum magnitude
    hhat = unitvector(hvec, hmag)  # unit vector

    # line of nodes:
    nvec = np.vstack([-hvec[:, 1], hvec[:, 0], np.zeros(len(hvec))]).transpose()
    nmag = np.sqrt(np.sum(nvec * nvec, axis=1))  # magnitude
    nhat = unitvector(nvec, nmag)  # unit vector

    # eccentricity vector:
    evec = (
        np.tile(v2 / mu - 1 / rmag, (3, 1)).transpose() * r
        - np.tile(np.sum(r * v, axis=1), (3, 1)).transpose() * v
    )
    e = np.sqrt(np.sum(evec * evec, axis=1))  # eccentricity magnitude
    ehat = unitvector(evec, e)

    En = v2 / 2 - mu / rmag  # specific energy
    a = -mu / 2 / En  # semi-major axis

    # handle parabolas (a var is redefined as ell for these cases)
    e[np.abs(e - 1) < 100 * np.spacing(1)] = 1  # grab all cases where e~1
    pinds = e == 1
    if np.any(pinds):
        if mu.size == 1:
            a[pinds] = h2[pinds] / mu
        else:
            a[pinds] = h2[pinds] / mu[pinds]

    # inclination
    sinI = np.sqrt(np.sum(hhat[:, [0, 1]] ** 2, axis=1))
    cosI = hhat[:, 2]
    I = np.arctan2(sinI, cosI)

    # longitude of the ascending node
    O = np.mod(np.arctan2(hvec[:, 0], -hvec[:, 1]), 2 * np.pi)

    # argument of periapsis
    sinw = np.sum(np.cross(nhat, ehat) * hhat, axis=1)
    cosw = np.sum(ehat * nhat, axis=1)
    w = np.mod(np.arctan2(sinw, cosw), 2 * np.pi)

    # handle zero inclination case
    tmp = np.isnan(w)
    if np.any(tmp):
        w[tmp] = np.arctan2(evec[tmp, 1], evec[tmp, 0])
        w[I[tmp] == np.pi] = 2 * np.pi - w[I[tmp] == np.pi]

    # true anomaly
    cosnu = np.sum(ehat * r, axis=1) / rmag
    sinnu = np.sum(np.cross(ehat, r) * hhat, axis=1) / rmag
    nu = np.arctan2(sinnu, cosnu)

    # finally, periapsis time is orbit-type specific
    E = np.zeros(len(r))  # eccentric/parabolic/hyperbolic anomaly

    # elliptic case:
    einds = e < 1
    E[einds] = np.mod(
        2 * np.arctan(np.sqrt((1 - e[einds]) / (1 + e[einds])) * np.tan(nu[einds] / 2)),
        2 * np.pi,
    )

    # parabolic case:
    E[pinds] = np.tan(nu[pinds] / 2)

    # hyperbolic case:
    hinds = e > 1
    E[hinds] = 2 * np.arctanh(
        np.sqrt((e[hinds] - 1) / (e[hinds] + 1)) * np.tan(nu[hinds] / 2)
    )

    # mean motion
    n = np.sqrt(mu / np.abs(a) ** 3)
    # handle parabolas
    if np.any(pinds):
        n[pinds] *= 2

    # periapse passage time
    tp = np.zeros(len(r))

    # elliptic
    tp[einds] = -(E[einds] - e[einds] * np.sin(E[einds])) / n[einds]

    # hyperbolic
    tp[hinds] = -(e[hinds] * np.sinh(E[hinds]) - E[hinds]) / n[hinds]

    # parabolic
    tp[pinds] = -(E[pinds] + E[pinds] ** 3 / 3) / n[pinds]

    return a, e, O, I, w, tp


def c2c3(psi):
    """Calculate the c2, c3 coefficients for the universal variable

    Args:
        psi (iterable or float):
            psi = chi^2/a for universal variable chi and semi-major axis a

    Returns:
        tuple:
            c2 (numpy.ndarray):
                c2 coefficients (same size as input)
            c3 (numpy.ndarray):
                c3 coefficients (same size as input)
    """

    # force input into 1D ndarray
    psi = np.array(psi, ndmin=1).astype(float).flatten()
    c2 = np.zeros(psi.size)
    c3 = np.zeros(psi.size)

    zeropsi = psi == 0
    pospsi = psi > 0
    negpsi = psi < 0

    c2[zeropsi] = 1 / 2
    c3[zeropsi] = 1 / 6

    c2[pospsi] = (1 - np.cos(np.sqrt(psi[pospsi]))) / psi[pospsi]
    c3[pospsi] = (np.sqrt(psi[pospsi]) - np.sin(np.sqrt(psi[pospsi]))) / np.sqrt(
        psi[pospsi] ** 3
    )

    c2[negpsi] = (1 - np.cosh(np.sqrt(-psi[negpsi]))) / psi[negpsi]
    c3[negpsi] = (np.sinh(np.sqrt(-psi[negpsi])) - np.sqrt(-psi[negpsi])) / np.sqrt(
        -psi[negpsi] ** 3
    )

    return c2, c3


def universalfg(r0, v0, mu, dt):
    """Propagate orbital state vectors by delta t via universal variable-based f and g

    Args:
        r0 (numpy.ndarray):
            Components of orbital radius. 3n elements in 1D as
            [r1(1);r1(2);r1(3);r2(1);r2(2)r2(3);...;rn(1);rn(2);rn(3)]
            or in 2D as nx3 or 3xn
        v0 (numpy.ndarray):
            Components of orbital velocity. Same stacking as r
        mu (float or numpy.ndarray):
            Gravitational parameters.  If float, assuming all state vectors belong to
            the same system.
        dt (float or numpy.ndarray):
            Propagation time.  If float, assuming all states are propagated for the same
            time

    Returns:
        tuple:
            r (numpy.ndarray):
                Components of orbital radius (n x 3)
            v (numpy.ndarray):
                Components of orbital velocity (n x 3)

    Notes:
        r.flatten() and v.flatten() will automatically stack elements in the proper
        order in a 1D array

    """

    r0, v0, mu = validateOrbitalStateInputs(r0, v0, mu)
    dt = forcendarray(dt)
    assert dt.size == 1 or dt.size == len(
        r0
    ), "dt must be scalar or same size as r0 and v0"
