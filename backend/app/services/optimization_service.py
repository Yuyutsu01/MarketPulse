from typing import Dict, Any, List
import numpy as np
from scipy.optimize import minimize

class BudgetOptimizationEngine:
    """
    Deterministic Constrained Budget Allocation Optimization Engine.
    Uses SLSQP (Sequential Least Squares Programming) to maximize expected ROI / Revenue
    subject to total budget constraints and channel min/max caps.
    """

    @classmethod
    def optimize_budget(
        cls,
        total_budget: float,
        channel_historical_roi: Dict[str, float],
        min_channel_spend_pct: float = 0.05,
        max_channel_spend_pct: float = 0.50
    ) -> Dict[str, Any]:
        """
        Calculates optimal channel budget allocation.
        """
        channels = list(channel_historical_roi.keys())
        num_channels = len(channels)

        if num_channels == 0 or total_budget <= 0:
            return {"allocations": {}, "expected_roi": 0.0, "total_expected_revenue": 0.0}

        rois = np.array([channel_historical_roi[ch] for ch in channels])
        
        # Initial equal guess
        x0 = np.full(num_channels, total_budget / num_channels)

        # Objective Function: Negative Expected Return (to minimize)
        def objective(x):
            # Diminishing returns scaling: revenue = spend * (1 + roi/100) * (1 - 0.1 * spend/total_budget)
            expected_returns = x * (1 + rois / 100) * (1 - 0.1 * (x / total_budget))
            return -np.sum(expected_returns)

        # Constraint: Sum of channel allocations must equal total_budget
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - total_budget})

        # Bounds: Min/Max spend per channel
        min_spend = total_budget * min_channel_spend_pct
        max_spend = total_budget * max_channel_spend_pct
        bounds = [(min_spend, max_spend) for _ in range(num_channels)]

        res = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)

        optimal_allocations = {}
        if res.success:
            alloc_values = res.x
        else:
            # Fallback to proportional ROI allocation
            weights = np.maximum(rois, 0.1)
            alloc_values = total_budget * (weights / np.sum(weights))

        for ch, val in zip(channels, alloc_values):
            optimal_allocations[ch] = round(float(val), 2)

        total_exp_rev = sum(optimal_allocations[ch] * (1 + channel_historical_roi[ch] / 100) for ch in channels)
        overall_roi = ((total_exp_rev - total_budget) / total_budget * 100) if total_budget > 0 else 0.0

        return {
            "total_budget": total_budget,
            "allocations": optimal_allocations,
            "expected_overall_roi": round(overall_roi, 2),
            "expected_total_revenue": round(total_exp_rev, 2),
            "optimization_status": "SUCCESS" if res.success else "PROPORTIONAL_FALLBACK"
        }
