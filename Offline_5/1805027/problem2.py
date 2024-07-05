import numpy as np
import matplotlib.pyplot as plt

def simulate_secretary_problem(n, s, num_simulations=10000):
    success_rates = np.zeros(n)
    for m in range(n):
        success_count = 0
        for _ in range(num_simulations):
            candidates = np.random.permutation(n) + 1  # Rank candidates from 1 to n
            benchmark = max(candidates[:m]) if m > 0 else 0
            for candidate in candidates[m:]:
                if candidate > benchmark:
                    # Check if the chosen candidate is within the top 's' ranks
                    if n - candidate < s:
                        success_count += 1
                    break
        success_rates[m] = success_count / num_simulations
    return success_rates

n = 100  # Population size
success_criteria = [1, 3, 5, 10]

plt.figure(figsize=(14, 8))
for s in success_criteria:
    success_rates = simulate_secretary_problem(n, s)
    plt.plot(range(n), success_rates, label=f'Top {s}')

plt.xlabel('Sample Size (m)')
plt.ylabel('Success Rate')
plt.title('Success Rate vs. Sample Size (m) for Various Success Criteria')
plt.legend()
plt.grid(True)
plt.show()
