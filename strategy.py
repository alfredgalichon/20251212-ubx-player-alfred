#!/usr/bin/env python3
"""Your encrypted strategy - edit this file, then encrypt it with setup_encryption.py"""

from typing import Any, Dict

import numpy as np


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
    
    shoot = np.random.randint(0, 3, len(opponents)).tolist()
    keep = np.random.randint(0, 3, len(opponents)).tolist()

    return {
        "shoot": {pid: int(direction) for pid, direction in zip(opponents, shoot)},
        "keep": {pid: int(direction) for pid, direction in zip(opponents, keep)},
    }

