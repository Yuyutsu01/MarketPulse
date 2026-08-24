from typing import List, Dict, Any

class MultiTouchAttributionEngine:
    """
    Enterprise Multi-Touch Marketing Attribution Engine.
    Supports First Touch, Last Touch, Linear, Time Decay, and Position-Based (40-20-40) models.
    """

    @classmethod
    def calculate_attribution(cls, channels: List[str], total_conversion_value: float, model: str = "linear") -> Dict[str, float]:
        """
        Distributes conversion value credit across touchpoint channels according to the chosen attribution model.
        """
        if not channels:
            return {}

        num_touchpoints = len(channels)
        credit_distribution: Dict[str, float] = {ch: 0.0 for ch in channels}

        model_lower = model.lower()

        if model_lower == "first_touch":
            credit_distribution[channels[0]] = total_conversion_value

        elif model_lower == "last_touch":
            credit_distribution[channels[-1]] = total_conversion_value

        elif model_lower == "linear":
            equal_share = total_conversion_value / num_touchpoints
            for ch in channels:
                credit_distribution[ch] += equal_share

        elif model_lower == "position_based":
            if num_touchpoints == 1:
                credit_distribution[channels[0]] = total_conversion_value
            elif num_touchpoints == 2:
                credit_distribution[channels[0]] = total_conversion_value * 0.5
                credit_distribution[channels[1]] = total_conversion_value * 0.5
            else:
                first_credit = total_conversion_value * 0.40
                last_credit = total_conversion_value * 0.40
                middle_credit = (total_conversion_value * 0.20) / (num_touchpoints - 2)

                credit_distribution[channels[0]] += first_credit
                credit_distribution[channels[-1]] += last_credit
                for ch in channels[1:-1]:
                    credit_distribution[ch] += middle_credit

        elif model_lower == "time_decay":
            # Half-life weight decaying for earlier touchpoints
            weights = [2 ** (i - num_touchpoints + 1) for i in range(num_touchpoints)]
            total_weight = sum(weights)
            for ch, w in zip(channels, weights):
                credit_distribution[ch] += (w / total_weight) * total_conversion_value
        else:
            raise ValueError(f"Unknown attribution model: {model}")

        # Round outputs to 2 decimal places
        return {ch: round(val, 2) for ch, val in credit_distribution.items()}
