"""Stopping criterion based on the relative change of the successive integral estimators."""

import numpy as np

from probnum.quad.solvers.bq_state import BQState
from probnum.quad.solvers.stopping_criteria import BQStoppingCriterion
from probnum.typing import FloatArgType

# pylint: disable=too-few-public-methods


class RelativeMeanChange(BQStoppingCriterion):
    """Stop once the relative change of consecutive integral estimates are smaller than
    a tolerance.

    The stopping criterion is: :math:`|\\hat{F}_{c} - \\hat{F}_{p}|/ |\\hat{F}_{c}| \\leq r`
    where :math:`\\hat{F}_{c}` and :math:`\\hat{F}_{p}` are the integral estimates of the current and previous iteration
    respectively, and :math:`r` is the relative tolerance.

    Parameters
    ----------
    rel_tol:
        Relative error tolerance on consecutive integral mean values.
    """

    def __init__(self, rel_tol: FloatArgType):
        self.rel_tol = rel_tol

    def __call__(self, bq_state: BQState) -> bool:
        integral_belief = bq_state.integral_belief
        return (
            np.abs(
                (integral_belief.mean - bq_state.previous_integral_beliefs[-1].mean)
                / integral_belief.mean
            )
            <= self.rel_tol
        )
