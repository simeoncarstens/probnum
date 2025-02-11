"""Tests for a policy returning random unit vectors."""
import pathlib

import numpy as np
from pytest_cases import parametrize_with_cases

from probnum import randvars
from probnum.linalg.solvers import LinearSolverState, policies

case_modules = (pathlib.Path(__file__).parent / "cases").stem
cases_policies = case_modules + ".policies"
cases_states = case_modules + ".states"


@parametrize_with_cases("policy", cases=cases_policies, glob="*conjugate_gradient")
@parametrize_with_cases("state", cases=cases_states)
def test_initial_action_is_negative_gradient(
    policy: policies.ConjugateGradientPolicy, state: LinearSolverState
):
    assert state.step == 0
    action = policy(state)
    np.testing.assert_allclose(action, -state.residual)


@parametrize_with_cases("policy", cases=cases_policies, glob="*conjugate_*")
@parametrize_with_cases("state", cases=cases_states, has_tag=["initial"])
def test_conjugate_actions(
    policy: policies.ConjugateGradientPolicy, state: LinearSolverState
):
    """Tests whether actions generated by the policy are A-conjugate via a naive CG
    implementation."""
    A = state.problem.A

    for _ in range(A.shape[1]):

        # Action
        s = policy(state)
        state.action = s

        # Observation
        y = A @ s
        state.observation = y

        # Residual
        r = state.residual

        # Step size
        alpha = np.linalg.norm(r) ** 2 / np.inner(s, y)

        # Solution update
        x = state.belief.x.mean
        state.belief.x = randvars.Constant(x + alpha * s)

        state.next_step()

    actions = np.array(state.actions[:-1]).T
    innerprods = actions.T @ A @ actions

    np.testing.assert_allclose(
        innerprods, np.diag(np.diag(innerprods)), atol=1e-7, rtol=1e7
    )
