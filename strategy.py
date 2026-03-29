#!/usr/bin/env python3
"""Your encrypted strategy - edit this file, then encrypt it with setup_encryption.py"""

from typing import Any, Dict

import numpy as np
from scipy.optimize import linprog

def sample_data():
    data =  [{
        "_turnId": 1,
        "player-id-A": {
            "player-id-B": {"shoot": 2, "keep": 0, "outcome": True},
            "player-id-C": {"shoot": 0, "keep": 1, "outcome": False}
        },
        "player-id-B": {
            "player-id-A": {"shoot": 1, "keep": 2, "outcome": False},
            "player-id-C": {"shoot": 2, "keep": 0, "outcome": True}
        },
        "player-id-C": {
            "player-id-A": {"shoot": 0, "keep": 1, "outcome": True},
            "player-id-B": {"shoot": 1, "keep": 2, "outcome": False}
        }
    },
    {
        "_turnId": 2,
        "player-id-A": {
            "player-id-B": {"shoot": 1, "keep": 1, "outcome": False},
            "player-id-C": {"shoot": 3, "keep": 0, "outcome": True}
        },
        "player-id-B": {
            "player-id-A": {"shoot": 0, "keep": 2, "outcome": True},
            "player-id-C": {"shoot": 1, "keep": 1, "outcome": False}
        },
        "player-id-C": {
            "player-id-A": {"shoot": 2, "keep": 1, "outcome": False},
            "player-id-B": {"shoot": 0, "keep": 3, "outcome": True}
        }
    },
    {
        "_turnId": 3,
        "player-id-A": {
            "player-id-B": {"shoot": 0, "keep": 2, "outcome": False},
            "player-id-C": {"shoot": 2, "keep": 1, "outcome": True}
        },
        "player-id-B": {
            "player-id-A": {"shoot": 3, "keep": 0, "outcome": True},
            "player-id-C": {"shoot": 0, "keep": 2, "outcome": False}
        },
        "player-id-C": {
            "player-id-A": {"shoot": 1, "keep": 1, "outcome": False},
            "player-id-B": {"shoot": 2, "keep": 0, "outcome": True}
        }
    }]
    
    return data

def build_goal_matrix(observations):
    """
    Build a 3x3 empirical goal matrix from past observations.

    Each observation is a tuple (i, j, goal), where:
        i    in {0,1,2} is the shooter's action
        j    in {0,1,2} is the keeper's action
        goal in {0,1} is the realized outcome
             (1 = goal, 0 = no goal)

    The function returns two 3x3 matrices:

    1. phi_i_j
       Entry (i,j) is the estimated probability of scoring when
       the shooter plays action i and the keeper plays action j.

       This is computed as the empirical average of 'goal' in that cell,
       but only when that cell has been observed at least 5 times.

       If a cell has been observed fewer than 5 times, its value is set
       to 0.5 instead, as a default fallback value.

    2. count_i_j
       Entry (i,j) is the number of observations in which the shooter
       played i and the keeper played j.

    So:
        - count_i_j tells you how much data you have in each cell
        - phi_i_j tells you the estimated scoring rate in each cell,
          except that sparse cells (count < 5) are replaced by 0.5
    """
    sums = np.zeros((3, 3), dtype=float)
    count_i_j = np.zeros((3, 3), dtype=int)

    for i, j, goal in observations:
        sums[i, j] += goal
        count_i_j[i, j] += 1

    phi_i_j = 0.5 * np.ones((3, 3), dtype=float)
    mask = count_i_j >= 5
    phi_i_j[mask] = sums[mask] / count_i_j[mask]

    return phi_i_j, count_i_j
    
    
def compute_strat(phi_i_j,shooter=True):
    I, J = phi_i_j.shape
    # Variables: x = [u, p_1, ..., p_I]  (length 1 + I)
    # Maximize u  <=>  minimize -u
    c = np.zeros(1 + I)
    c[0] = -1.0
    # Inequality constraints: u - sum_i phi_i_j p_i <= 0, for each j
    A_ub = np.hstack([np.ones((J, 1)), -phi_i_j.T])   # shape (J, 1+I)
    b_ub = np.zeros(J)
    # Equality constraint: sum_i p_i = 1
    A_eq = np.zeros((1, 1 + I))
    A_eq[0, 1:] = 1.0
    b_eq = np.array([1.0])
    # Bounds: u unconstrained, p_i >= 0
    bounds = [(None, None)] + [(0, None)] * I
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
              bounds=bounds, method='highs')
    
    pstar_i = res.x[1:]
    qstar_j = lambda_j = -res.ineqlin.marginals 
    if shooter:
        return pstar_i
    else:
        return qstar_j


def strategy(state: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    """
    Your strategy function.
    
    Args:
        state: Game state dictionary containing:
            - playerIds: list of all player IDs
            - myPlayerId: your player ID
            - opponentsIds: list of opponent IDs
            - state: list of completed turns (history)
            - turnId: current turn number
    
    Returns:
        Dictionary with 'shoot' and 'keep' maps:
        {
            "shoot": {opponent_id: direction (0-2), ...},
            "keep": {opponent_id: direction (0-2), ...}
        }
        
    Directions:
        - 0 = left
        - 1 = center
        - 2 = right
    """
    my_id = state.get("myPlayerId")
    opponents = state.get("opponentsIds") or []



    if not my_id or not opponents:
        return {"shoot": {}, "keep": {}}

    # Example: random strategy
    # Replace this with your actual strategy logic
    # You can analyze state.get("state", []) to see previous turns
    # and make decisions based on opponent behavior
    

    shoot = []
    keep = []
    for opp_id in opponents:
        # data where I am the shooter
        obs_shooter = [ (turn[my_id][opp_id]['shoot'], turn[my_id][opp_id]['keep'],1*turn[my_id][opp_id]['outcome']) for turn in thedata]
        phi_i_j, _ = build_goal_matrix(obs_shooter)
        pstar_i = compute_strat(phi_i_j,shooter=True)
        i = np.random.choice(3, p=pstar_i)
        shoot.append(i)

        # data where I am the keeper
        obs_keeper = [ (turn[opp_id][my_id]['shoot'], turn[opp_id][my_id]['keep'],1*turn[opp_id][my_id]['outcome']) for turn in thedata]
        phi_i_j, _ = build_goal_matrix(obs_keeper)
        qstar_j = compute_strat(phi_i_j,shooter=False)
        j = np.random.choice(3, p=qstar_j)
        keep.append(j)



    return {
        "shoot": {pid: int(direction) for pid, direction in zip(opponents, shoot)},
        "keep": {pid: int(direction) for pid, direction in zip(opponents, keep)},
    }

