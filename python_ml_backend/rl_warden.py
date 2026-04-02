class RLWarden:
    def __init__(self, initial_eps=0.15):
        self.cumulative_reward = 100.0
        self.current_eps = initial_eps
        print(f"[ML] RL Warden: Active Policy Brain Initialized. Starting EPS: {self.current_eps}")

    def evaluate_action(self, detected_as_poison, true_label):
        """
        The Warden compares the DBSCAN cluster result against the Ground Truth.
        It actively tunes the system's sensitivity (eps) based on performance.
        """
        is_actual_poison = (true_label == 1)
        
        step_reward = 0.0
        eps_adjustment = 0.0
        action_log = "Optimal Shielding."

        # 1. True Positive: Caught the fraud
        if detected_as_poison and is_actual_poison:
            step_reward = 1.5
            action_log = "Threat Neutralized (True Positive)."
        
        # 2. True Negative: Let clean data pass
        elif not detected_as_poison and not is_actual_poison:
            step_reward = 0.2
            action_log = "Clean Pass (True Negative)."
            
        # 3. False Negative: MISSED the fraud! (Shields too loose)
        elif not detected_as_poison and is_actual_poison:
            step_reward = -5.0
            eps_adjustment = -0.02 # Make it MORE sensitive
            action_log = "Threat Missed! Tightening Shields (False Negative)."
            
        # 4. False Positive: Flagged a normal user! (Shields too tight)
        elif detected_as_poison and not is_actual_poison:
            step_reward = -2.0
            eps_adjustment = 0.02 # Make it LESS sensitive
            action_log = "False Alarm! Relaxing Shields (False Positive)."

        # Apply reward and epsilon tuning
        self.cumulative_reward += step_reward
        self.current_eps += eps_adjustment
        
        # Hard limits: Keep eps within mathematical bounds so DBSCAN doesn't break
        self.current_eps = max(0.05, min(0.5, self.current_eps))

        return {
            "reward": round(self.cumulative_reward, 2),
            "new_eps": round(self.current_eps, 3),
            "action_log": action_log
        }