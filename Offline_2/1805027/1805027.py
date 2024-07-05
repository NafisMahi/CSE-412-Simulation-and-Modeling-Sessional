import numpy as np
import math
import random
import lcgrand as lcgrand

# Global Variables
amount, bigs, initial_inv_level, inv_level, next_event_type, num_events, num_months, num_values_demand, smalls = 0, 0, 0, 0, 0, 0, 0, 0, 0
area_holding, area_shortage, holding_cost, incremental_cost, maxlag, mean_interdemand, minlag = 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0
global prob_distrib_demand, policies
setup_cost, short_cost, sim_time, time_last_event, total_ordering_cost = 0.0, 0.0, 0.0, 0.0, 0.0
time_next_event = [0.0] * 5 

def generate_exponential(mean):
    val = -mean*math.log(lcgrand.lcgrand(1))
    return val

def uniform(a, b):
    return a + (b - a) * lcgrand.lcgrand(1)

def random_integer(prob_distrib):
    u = uniform(0, 1)
    i = 1
    while u > prob_distrib[i]:
        i += 1
    return i


def initialize():
    global sim_time, inv_level, time_last_event, total_ordering_cost, mean_interdemand, num_events
    global area_holding, area_shortage, time_next_event
    
    sim_time = 0.0
    
    inv_level = initial_inv_level
    time_last_event = 0.0
    
    # Initialize the statistical counters.
    total_ordering_cost = 0.0
    area_holding = 0.0
    area_shortage = 0.0
    num_events = 4
    
    # Initialize the event list with a placeholder for index 0.
    time_next_event = [None]  
    time_next_event.append(1.0e+30) 
    time_next_event.append(sim_time + generate_exponential(mean_interdemand)) 
    time_next_event.append(num_months)
    time_next_event.append(0.0)

    
def read_file():
    global initial_inv_level, num_months, num_policies
    global num_values_demand, mean_interdemand
    global setup_cost, incremental_cost, holding_cost, short_cost
    global minlag, maxlag, prob_distrib_demand, policies

    with open("io1/in.txt", 'r') as file:
       
        initial_inv_level, num_months, num_policies = map(int, file.readline().split())

      
        num_values_demand, mean_interdemand = map(np.double, file.readline().split())

       
        setup_cost, incremental_cost, holding_cost, short_cost = map(np.double, file.readline().split())
        
        
        minlag, maxlag = map(np.double, file.readline().split())

        
        prob_distrib_demand = [0] + list(map(np.double, file.readline().split()))

        policies = [list(map(int, file.readline().split())) for _ in range(int(num_policies))]
    
def timing():
    global next_event_type, sim_time,time_next_event, num_events
    min_time_next_event = 1.0e+30
    next_event_type = 0
    
    for i in range(1, num_events + 1):
        if time_next_event[i] < min_time_next_event:
            min_time_next_event = time_next_event[i]
            next_event_type = i
    
    if next_event_type == 0:
        print("Event list empty at time {}".format(sim_time))
        exit()
    
    sim_time = min_time_next_event
    
def order_arrival():
    global inv_level, time_next_event, amount
    
    inv_level += amount
      
    time_next_event[1] = 1.0e+30

def demand():
    global inv_level, time_next_event, sim_time
    
    demand_size = random_integer(prob_distrib_demand)

    inv_level -= demand_size
    
    # Schedule the time of the next demand.
    time_next_event[2] = sim_time + generate_exponential(mean_interdemand)


def evaluate():
    global inv_level, smalls, bigs, total_ordering_cost, setup_cost, incremental_cost
    global time_next_event, sim_time, minlag, maxlag, amount

    if inv_level < smalls:   
        amount = bigs - inv_level
          
        total_ordering_cost += setup_cost + (incremental_cost * amount)
       
        # Schedule the arrival of the order.
        time_next_event[1] = sim_time + uniform(minlag, maxlag)   
    # Regardless of the place-order decision, schedule the next inventory evaluation.
    time_next_event[4] = sim_time + 1.0
    
def update_time_avg_stats():
    global sim_time, time_last_event, inv_level, area_shortage, area_holding

    time_since_last_event = sim_time - time_last_event
    time_last_event = sim_time

    if inv_level < 0:
        area_shortage -= inv_level * time_since_last_event
    elif inv_level > 0:
        area_holding += inv_level * time_since_last_event
        
    
        
def report_policy_stats(policy):
    # Access the necessary global variables
    global total_ordering_cost, holding_cost, shortage_cost
    global area_holding, area_shortage, num_months
    
    # Calculate the average costs
    avg_ordering_cost = total_ordering_cost / num_months
    avg_holding_cost = holding_cost * area_holding / num_months
    
    avg_shortage_cost = short_cost * area_shortage / num_months
    total_cost = avg_ordering_cost + avg_holding_cost + avg_shortage_cost

    # Return a dictionary containing the calculated statistics
    return {
        'policy': policy,
        'avg_total_cost': total_cost,
        'avg_ordering_cost': avg_ordering_cost,
        'avg_holding_cost': avg_holding_cost,
        'avg_shortage_cost': avg_shortage_cost
    }
    
def write_output_to_file(output_path, policies_results):
    with open(output_path, 'w') as file:
        file.write("-----Single-Product Inventory System-----\n")
        file.write(f"Initial inventory level: {initial_inv_level} items\n\n")
        file.write(f"Number of demand sizes: {num_values_demand}\n\n")
        file.write("Distribution function of demand sizes: " + " ".join(map(str, prob_distrib_demand[1:])) + "\n\n")
        file.write(f"Mean inter-demand time: {mean_interdemand} months\n\n")
        file.write(f"Delivery lag range: {minlag:.2f} to {maxlag:.2f} months\n\n")
        file.write(f"Length of simulation: {num_months} months\n\n")
        file.write("Costs:\n\n")
        file.write(f"K = {setup_cost:.2f}\n")
        file.write(f"i = {incremental_cost:.2f}\n")
        file.write(f"h = {holding_cost:.2f}\n")
        file.write(f"pi = {short_cost:.2f}\n")
        file.write(f"Number of policies: {len(policies)}\n")
        file.write("\nPolicies:\n")
        file.write("-" * 90 + "\n")  # Increase to 80 for wider spacing
        file.write("{:<9} {:<18} {:<20} {:<22} {:<18}\n".format(
            "Policy", "Avg_total_cost", "Avg_ordering_cost", "Avg_holding_cost", "Avg_shortage_cost"
        ))
        file.write("-" * 90 + "\n")
        
        for policy in policies_results:
            file.write("{:<9} {:<18.2f} {:<20.2f} {:<22.2f} {:<18.2f}\n".format(
                str(tuple(policy['policy'])), 
                policy['avg_total_cost'], 
                policy['avg_ordering_cost'], 
                policy['avg_holding_cost'], 
                policy['avg_shortage_cost']
            ))
        
def main():

    policies_results =[]
    read_file() 
    global smalls, bigs
   
    for policy in policies:
        smalls = policy[0]
        bigs = policy[1]
        initialize()
    
        timing()  
        
        update_time_avg_stats()  
        # Run the simulation loop
        while next_event_type != 3: 
            timing()
            update_time_avg_stats()  
            
            if next_event_type == 1:
                order_arrival()
            elif next_event_type == 2:
                demand()
            elif next_event_type == 4:
                evaluate()
        update_time_avg_stats()
        
        # Calculate and collect the statistics for the policy
        policy_statistics = report_policy_stats(policy)
        policies_results.append(policy_statistics)
    
    # Write all the results to the output file
    write_output_to_file("results.txt", policies_results)
  
read_file()
main()