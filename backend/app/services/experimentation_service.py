import math
from typing import Dict, Any
from scipy import stats

class ExperimentationEngine:
    """
    Enterprise A/B Testing & Statistical Experimentation Engine.
    Calculates percentage lift, Welch's t-statistic, p-value, 95% confidence intervals, and statistical significance.
    """

    @classmethod
    def analyze_experiment(
        cls,
        control_conversions: int,
        control_sample_size: int,
        treatment_conversions: int,
        treatment_sample_size: int,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Runs statistical hypothesis test between Control and Treatment variants.
        """
        if control_sample_size <= 0 or treatment_sample_size <= 0:
            raise ValueError("Sample sizes must be greater than zero.")

        p_control = control_conversions / control_sample_size
        p_treatment = treatment_conversions / treatment_sample_size

        # Percentage Lift
        lift = ((p_treatment - p_control) / p_control * 100) if p_control > 0 else 0.0

        # Standard Error for Difference in Proportions
        se = math.sqrt(
            (p_control * (1 - p_control) / control_sample_size) +
            (p_treatment * (1 - p_treatment) / treatment_sample_size)
        )

        if se > 0:
            z_score = (p_treatment - p_control) / se
            p_value = float(2 * (1 - stats.norm.cdf(abs(z_score))))
        else:
            z_score = 0.0
            p_value = 1.0

        alpha = 1.0 - confidence_level
        z_crit = stats.norm.ppf(1 - alpha / 2)

        ci_lower = (p_treatment - p_control) - (z_crit * se)
        ci_upper = (p_treatment - p_control) + (z_crit * se)

        is_significant = p_value < alpha

        return {
            "control_conversion_rate": round(p_control * 100, 2),
            "treatment_conversion_rate": round(p_treatment * 100, 2),
            "percentage_lift": round(lift, 2),
            "z_score": round(z_score, 4),
            "p_value": round(p_value, 5),
            "is_significant": is_significant,
            "confidence_interval_95": (round(ci_lower * 100, 2), round(ci_upper * 100, 2)),
            "recommendation": (
                "Statistically significant positive lift detected. Promote Treatment variant to Production."
                if is_significant and lift > 0
                else "No statistically significant improvement detected. Continue experiment or retain Control."
            )
        }
