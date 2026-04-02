import logging

logger = logging.getLogger("PoisonGuard.RLWarden")

class RLWarden:
    def __init__(self, initial_eps=0.5):
        self.cumulative_reward = 100.0
        self.current_eps = initial_eps

    def evaluate_action(self, detected_as_poison, true_label):
        is_actual_poison = (true_label == 1)
        step_reward = 0.0
        eps_adjustment = 0.0

        if detected_as_poison and is_actual_poison:
            step_reward = 5.0 
            action_log = "Threat Neutralized (True Positive)."
        elif not detected_as_poison and not is_actual_poison:
            step_reward = 0.5 
            action_log = "Clean Pass (True Negative)."
        elif not detected_as_poison and is_actual_poison:
            step_reward = -10.0 # DOUBLE penalty for missing fraud
            eps_adjustment = -0.15 # Tighten aggressively
            action_log = "Threat Missed! (False Negative)."
        elif detected_as_poison and not is_actual_poison:
            # FIX: Increased penalty from -1.0 to -4.0
            # This forces the AI to value customer experience
            step_reward = -4.0 
            eps_adjustment = 0.25 # Open gates wider on false alarms
            action_log = "False Alarm! (False Positive)."

        self.cumulative_reward += step_reward
        self.current_eps += eps_adjustment
        self.current_eps = max(0.05, min(5.0, self.current_eps)) # Raised max to 5.0

        return {
            "reward": round(self.cumulative_reward, 2),
            "new_eps": round(self.current_eps, 3),
            "action_log": action_log
        }
