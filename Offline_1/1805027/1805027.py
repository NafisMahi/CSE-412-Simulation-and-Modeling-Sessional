import numpy as np
import math
import random
import lcgrand as lcgrand

Q_LIMIT = 100  
BUSY = 1      
IDLE = 0      

# Global state variables
next_event_type = None
num_custs_delayed = 0
num_delays_required = 0
num_events = 0
num_in_q = 0
server_status = IDLE
sim_time = 0.0
event_count = 0

outfile = None

def open_global_file(path):
    global outfile  # Use the global file variable
    outfile = open(path, "w")  # Open a file for writing

def write_to_global_file(data):
    global outfile  # Use the global file variable
    if outfile is not None:  # Check if the file is opened
        outfile.write(data + "\n")

def close_global_file():
    global outfile  # Use the global file variable
    if outfile is not None:  # Check if the file is opened
        outfile.close()

# Statistical counters
area_num_in_q = 0.0
area_server_status = 0.0
mean_interarrival = 0.0
mean_service = 0.0
time_last_event = 0.0

# Time event data
time_next_event = [0.0, 0.0, 0.0]
time_arrival = [0.0 for _ in range(Q_LIMIT + 1)] 
total_of_delays = 0.0

def generate_exponential(mean):
    val = -mean*math.log(lcgrand.lcgrand(1))
    return val

def initialize():
    
    global sim_time , num_in_q, num_events, time_last_event, num_custs_delayed, total_of_delays, area_num_in_q, area_server_status, server_status
    sim_time = 0.0
    num_in_q = 0
    num_events = 2
    time_last_event = 0.0
    num_custs_delayed = 0
    total_of_delays = 0.0
    area_num_in_q = 0.0
    area_server_status
    server_status = IDLE
    
    time_next_event[1] = sim_time + generate_exponential(mean_interarrival)
    time_next_event[2] = 1.0e+30

def timing():
    global next_event_type, sim_time,time_next_event, num_events
    min_time_next_event = 1.0e+29
    next_event_type = 0
    
    for i in range(1, num_events + 1):
        if time_next_event[i] < min_time_next_event:
            min_time_next_event = time_next_event[i]
            next_event_type = i
    
    if next_event_type == 0:
        print("Event list empty at time {}".format(sim_time))
        exit()
    
    sim_time = min_time_next_event

def arrive():
    global server_status, num_in_q, sim_time, num_custs_delayed, time_arrival, time_next_event, total_of_delays, mean_service, mean_interarrival

    #schedule next arrival
    time_next_event[1] = sim_time + generate_exponential(mean_interarrival)

    if server_status == BUSY:
        num_in_q += 1

        if num_in_q > Q_LIMIT:
            print("Overflow of the array time_arrival at", sim_time)
            exit(2)
        
        time_arrival[num_in_q] = sim_time

    else:
        delay = 0.0
        total_of_delays += delay

        num_custs_delayed += 1
        write_to_global_file("\n-----------No. of customers delayed: {}-----------\n".format(num_custs_delayed))
        server_status = BUSY

        time_next_event[2] = sim_time + generate_exponential(mean_service)

def depart():
    global server_status, num_in_q, time_next_event, total_of_delays, num_custs_delayed, time_arrival, sim_time, mean_service

    if num_in_q == 0:
        server_status = IDLE
        time_next_event[2] = 1.0e+30

    else:
        num_in_q -= 1
        delay = sim_time - time_arrival[1]
        total_of_delays += delay

        num_custs_delayed += 1
        write_to_global_file("\n-----------No. of customers delayed: {}-----------\n".format(num_custs_delayed))
        time_next_event[2] = sim_time + generate_exponential(mean_service)

        for i in range(1, num_in_q + 1):
            time_arrival[i] = time_arrival[i + 1]

def update_time_avg_stats():
    global area_num_in_q, area_server_status, time_last_event, sim_time, num_in_q, server_status

    time_since_last_event = sim_time - time_last_event
    time_last_event = sim_time

    area_num_in_q += num_in_q * time_since_last_event

    area_server_status += server_status * time_since_last_event

def report():
    global area_num_in_q, area_server_status, mean_interarrival, mean_service, num_custs_delayed, num_delays_required, sim_time, total_of_delays

    with open("results.txt", "w") as file:
        file.write("-----Single Server Queue Simulation-----\n\n")

        file.write(f"Mean inter-arrival time: {mean_interarrival:.6f} minutes\n")
        file.write(f"Mean service time: {mean_service:.6f} minutes\n")
        file.write(f"Number of customers: {num_delays_required}\n\n")

        avg_delay_in_queue = total_of_delays / num_custs_delayed
        avg_number_in_queue = area_num_in_q / sim_time
        server_utilization = area_server_status / sim_time
        sim_end_time = sim_time

        file.write(f"Avg delay in queue: {avg_delay_in_queue:.6f} minutes\n")
        file.write(f"Avg number in queue: {avg_number_in_queue:.6f}\n")
        file.write(f"Server utilization: {server_utilization:.6f}\n")
        file.write(f"Time simulation ended: {sim_end_time:.6f} minutes\n")

def readFile():
    global num_delays_required, mean_interarrival, mean_service
    with open("IOs/io2/in.txt", "r") as f:
        line = f.readline().strip()
        parts = line.split()
        mean_interarrival = float(parts[0])
        mean_service = float(parts[1])
        num_delays_required = int(parts[2])

def main():
    readFile()
    initialize()
    open_global_file("events_order.txt")
    global event_count
    

    while num_custs_delayed < num_delays_required:
        timing()
        update_time_avg_stats()

        if next_event_type == 1:
            write_to_global_file(f"{event_count+1}. Next event: Customer {num_custs_delayed+1} Arrival")
            event_count += 1
            arrive()
        elif next_event_type == 2:
            write_to_global_file(f"{event_count+1}. Next event: Customer {num_custs_delayed} Departure")
            event_count += 1
            depart()
    
    report()


main()
