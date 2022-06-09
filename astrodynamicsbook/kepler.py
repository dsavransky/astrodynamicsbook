import numpy as np


def invKepler(M, e, tol=None, E0=None, maxIter=100, return_iter=False, return_nu=False):
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
        return_iter (bool):
            Return number of iterations (defaults false)
        return_nu (bool):
            Return true anomaly (defaults false)

    Returns:
        tuple:
            E (ndarray):
                eccentric/parabolic/hyperbolic anomaly (rad)
            numIter (ndarray):
                Number of iterations (returned only if return_iter=True)
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
    M = np.array(M, ndmin=1).astype(float).flatten()
    e = np.array(e, ndmin=1).astype(float).flatten()
    if e.size != M.size:
        if e.size == 1:
            e = np.array([e[0]] * len(M))
        if M.size == 1:
            M = np.array([M[0]] * len(e))

    assert e.shape == M.shape, "Incompatible inputs."
    assert np.all((e >= 0)), "e values below zero"

    # set tolerance is none provided
    if tol is None:
        tol = np.spacing(2*np.pi)

    # define output
    Eout = np.zeros(M.size)
    numIter = np.zeros(M.size)

    # circles
    cinds = e == 0
    Eout[cinds] = M[cinds]

    # ellipses
    einds = (e > 0) & (e < 1)
    if any(einds):

        Me = M(einds)
        ee = e(einds)

        # initial values for E
        if E0 is None:
            E = Me / (1 - ee)
            mask = ee * E ** 2 > 6 * (1 - ee)
            E[mask] = (6 * Me[mask] / ee[mask]) ** (1.0 / 3.0)
        else:
            E = E0(einds)

        # Newton-Raphson setup
        counter = np.ones(E.shape)
        err = np.ones(E.shape)
        while (np.max(err) > tol) and (max(counter) < maxIter):
            inds = err > tol
            E[inds] = E[inds] - (Me[inds] - E[inds] + ee[inds] * np.sin(E[inds])) / (ee[inds] * np.cos(E[inds]) - 1)
            err[inds] = np.abs(Me[inds] - (E[inds] - ee[inds] * np.sin(E[inds])))
            counter[inds] += 1

        if np.max(counter) == maxIter:
            raise Exception("Maximum number of iterations exceeded")

        Eout[einds] = E
        numIter[einds] = counter

    # parabolae
    pinds = e == 1
    if np.any(pinds):
        q = 9*M[pinds]/6;
        B = (q + np.sqrt(q**2 + 1))**(1.0/3.0) - (np.sqrt(q**2 + 1)-q)**(1.0/3.0)
        Eout[pinds] = B;

    # hyperbolae



    out = (E,)
    if return_iter:
        out += (numIter,)
    if return_nu:
        out += (nu, )

    return out

