import numpy as np

probabilities = [0.2126 * (0.5893)**(i-1) for i in range(1, 4)]
p_0 = 1 - sum(probabilities)
probabilities.insert(0, p_0)

def simulate_generation(neutrons, probabilities):
    new_neutrons = 0
    for _ in range(neutrons):
        new_neutrons += np.random.choice([0, 1, 2, 3], p=probabilities)
    return new_neutrons

# Run the simulation for 10 generations, 10,000 times
num_simulations = 10000
num_generations = 10
generation_counts = np.zeros((num_simulations, num_generations), dtype=int)


for sim in range(num_simulations):
    neutrons = 1  # Start with one neutron
    for gen in range(num_generations):
        neutrons = simulate_generation(neutrons, probabilities)
        generation_counts[sim, gen] = neutrons

# Correct initialization for storing probabilities for 0, 1, 2, 3, and 4 neutrons
generation_probabilities = np.zeros((num_generations, 5))

for gen in range(num_generations):
    neutron_distribution = np.bincount(generation_counts[:, gen], minlength=5)
    # If there are more categories than expected, you might need to handle them appropriately
    # For this case, it's assumed the distribution already aligns with the requirement
    
    # Normalize counts to probabilities, ensure the distribution is for 0 to 4
    normalized_distribution = neutron_distribution[:5] / num_simulations
    
    # Manually ensure p[4] = 0.0
    # normalized_distribution[4] = 0.0
    
    generation_probabilities[gen] = normalized_distribution

# Print the probabilities for each generation in the specified format
for gen in range(num_generations):
    print(f"Generation-{gen + 1}:")
    for i in range(5):
        print(f"p[{i}] = {generation_probabilities[gen, i]:.4f}")
    print()  # Add an empty line for spacing between generations