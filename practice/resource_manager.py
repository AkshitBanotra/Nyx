#!/usr/bin/env python3

import psutil

def get_top_processes(top_n=3):
    process_list = []
    
    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            # Use a dictionary to store process info safely
            pinfo = proc.info
            # Ensure cpu_percent is initialized
            pinfo['cpu_percent'] = proc.cpu_percent(interval=None) or 0.0
            pinfo['memory_percent'] = pinfo['memory_percent'] or 0.0
            process_list.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Sort by Memory Usage
    top_memory = sorted(process_list, key=lambda p: p['memory_percent'], reverse=True)[:top_n]
    
    # Sort by CPU Usage
    top_cpu = sorted(process_list, key=lambda p: p['cpu_percent'], reverse=True)[:top_n]
    
    return top_memory, top_cpu

top_mem, top_cpu = get_top_processes()

print("Top 3 by Memory:")
for p in top_mem:
    print(f"PID: {p['pid']}, Name: {p['name']}, Mem%: {p['memory_percent']:.2f}%")

print("\nTop 3 by CPU:")
for p in top_cpu:
    print(f"PID: {p['pid']}, Name: {p['name']}, CPU%: {p['cpu_percent']:.2f}%")

