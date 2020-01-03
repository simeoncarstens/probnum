"""Finite dimensional linear operators.

This module defines classes and methods that implement finite dimensional linear operators. It can be used to do linear
algebra with (structured) matrices without explicitly representing them in memory. This often allows for the definition
of a more efficient matrix-vector product. Linear operators can be applied, added, multiplied, transposed, and more as
one would expect from matrix algebra.

Several algorithms in the :mod:`probnum.linalg` library are able to operate on :class:`LinearOperator` instances.
"""

import numpy as np
import scipy.sparse.linalg
import probnum.probability as probability


class LinearOperator(scipy.sparse.linalg.LinearOperator):
    """
    Finite dimensional linear operators.

    This class provides a way to define finite dimensional linear operators without explicitly constructing a matrix
    representation. Instead it suffices to define a matrix-vector product and a shape attribute. This avoids unnecessary
    memory usage and can often be more convenient to derive.

    LinearOperator instances can be multiplied, added and exponentiated. This happens lazily: the result of these
    operations is a new, composite LinearOperator, that defers linear operations to the original operators and combines
    the results.

    To construct a concrete LinearOperator, either pass appropriate callables to the constructor of this class, or
    subclass it.

    A subclass must implement either one of the methods ``_matvec`` and ``_matmat``, and the
    attributes/properties ``shape`` (pair of integers) and ``dtype`` (may be ``None``). It may call the ``__init__`` on
    this class to have these attributes validated. Implementing ``_matvec`` automatically implements ``_matmat`` (using
    a naive algorithm) and vice-versa.

    Optionally, a subclass may implement ``_rmatvec`` or ``_adjoint`` to implement the Hermitian adjoint (conjugate
    transpose). As with ``_matvec`` and ``_matmat``, implementing either ``_rmatvec`` or ``_adjoint`` implements the
    other automatically. Implementing ``_adjoint`` is preferable; ``_rmatvec`` is mostly there for backwards
    compatibility.

    This class wraps :class:`scipy.sparse.linalg.LinearOperator` to provide support for
    :class:`~probnum.RandomVariable`.

    Parameters
    ----------
    shape : tuple
        Matrix dimensions (M, N).
    matvec : callable f(v)
        Returns :math:`A v`.
    rmatvec : callable f(v)
        Returns :math:`A^H v`, where :math:`A^H` is the conjugate transpose of :math:`A`.
    matmat : callable f(V)
        Returns :math:`AV`, where :math:`V` is a dense matrix with dimensions (N, K).
    dtype : dtype
        Data type of the matrix.
    rmatmat : callable f(V)
        Returns :math:`A^H V`, where :math:`V` is a dense matrix with dimensions (M, K).

    See Also
    --------
    aslinearoperator : Construct LinearOperators.

    Examples
    --------
    >>> import numpy as np
    >>> from probnum.linalg import LinearOperator
    >>> def mv(v):
    ...     return np.array([2*v[0], 3*v[1]])
    ...
    >>> A = LinearOperator((2,2), matvec=mv)
    >>> A
    <2x2 _CustomLinearOperator with dtype=float64>
    >>> A.matvec(np.ones(2))
    array([ 2.,  3.])
    >>> A * np.ones(2)
    array([ 2.,  3.])

    """

    def __init__(self, Op=None, explicit=False):
        # todo: how should this constructor work and is it necessary to have our own?
        # todo: should we just allow subclassing of LinearOperator?
        self.explicit = explicit
        if Op is not None:
            self.Op = Op
            self.shape = self.Op.shape
            self.dtype = self.Op.dtype

    def _matvec(self, x):
        if callable(self.Op._matvec):
            return self.Op._matvec(x)

    def _rmatvec(self, x):
        if callable(self.Op._rmatvec):
            return self.Op._rmatvec(x)

    def _matmat(self, X):
        """Matrix-matrix multiplication handler.
        Modified version of scipy _matmat to avoid having trailing dimension
        in col when provided to matvec.
        """
        # TODO: do we need this?
        return np.vstack([self.matvec(col.reshape(-1)) for col in X.T]).T

    def __mul__(self, x):
        y = super().__mul__(x)
        if isinstance(y, scipy.sparse.linalg.LinearOperator):
            y = LinearOperator(y)
        return y

    def __rmul__(self, x):
        return LinearOperator(super().__rmul__(x))

    def __pow__(self, p):
        return LinearOperator(super().__pow__(p))

    def __add__(self, x):
        return LinearOperator(super().__add__(x))

    def __neg__(self):
        return LinearOperator(super().__neg__())

    def __sub__(self, x):
        return LinearOperator(super().__sub__(x))

    def _adjoint(self):
        return LinearOperator(super()._adjoint())

    def _transpose(self):
        return LinearOperator(super()._transpose())

    def todense(self):
        """
        Dense matrix representation of the linear operator.

        This operation can be computationally costly depending on the size of the operator.

        Returns
        -------
        matrix : ndarray
            Dense matrix representation.

        """
        # needed if self is a _SumLinearOperator or _ProductLinearOperator
        linop = LinearOperator(self)
        identity = np.eye(self.shape[1], dtype=self.dtype)
        return linop.matmat(identity)

    # TODO: implement operations (eigs, cond, ...)


class IdentityOperator(LinearOperator):
    """
    The identity operator returning its input.
    """

    def __init__(self, shape, dtype=None):
        super(IdentityOperator, self).__init__(dtype, shape)

    def _matvec(self, x):
        return x

    def _rmatvec(self, x):
        return x

    def _rmatmat(self, x):
        return x

    def _matmat(self, x):
        return x

    def _adjoint(self):
        return self


def aslinearoperator(A):
    """
    Return A as a LinearOperator.

    Parameters
    ----------
    A : array-like or spmatrix or LinearOperator or RandomVariable or object
        Argument to be represented as a linear operator. When `A` is an object it needs to have the attributes `.shape`
        and `.matvec`.

    Notes
    -----
    If `A` has no `.dtype` attribute, the data type is determined by calling
    :func:`LinearOperator.matvec()` - set the `.dtype` attribute to prevent this
    call upon the linear operator creation.

    See Also
    --------
    LinearOperator : Class representing linear operators.

    Examples
    --------
    >>> from probnum.linalg import aslinearoperator
    >>> M = np.array([[1,2,3],[4,5,6]], dtype=np.int32)
    >>> aslinearoperator(M)
    <2x3 MatrixLinearOperator with dtype=int32>
    """
    if isinstance(A, probability.RandomVariable):
        # TODO: aslinearoperator also for random variables; change docstring example
        raise NotImplementedError
    else:
        return scipy.sparse.linalg.aslinearoperator(A)
