class RLWarden:
    def __init__(self):
        self.cumulative_reward = 100.0
        print("[ML] RL Warden: Policy Gradient Brain Initialized.")

    def evaluate_action(self, is_poisoned, risk_score):
        """
        The Warden gets a reward if it correctly identifies a 'fracture'.
        risk_score comes from the PyTorch Hidden Layer intensity.
        """
        # Logic: High reward for catching real poison, penalty for false alarms
        if is_poisoned and risk_score > 0.8:
            step_reward = 1.5  # Correct Isolation
        elif not is_poisoned and risk_score < 0.3:
            step_reward = 0.2  # Correct Pass-through
        else:
            step_reward = -2.0 # False Positive or Missed Threat!
            
        self.cumulative_reward += step_reward
        return round(self.cumulative_reward, 2)