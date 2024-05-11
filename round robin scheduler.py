import tkinter as tk
from tkinter import messagebox


class Process:
    def __init__(self, pid, at, bt):
        self.pid = pid  # process_id
        self.arrival = at  # arrivalTime
        self.burst = bt  # burstTime
        self.start_time = 0
        self.finish_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1


def shiftCL(alist):
    temp = alist[0]
    for i in range(len(alist) - 1):
        alist[i] = alist[i + 1]
    alist[len(alist) - 1] = temp
    return alist


def RR(plist, n, tq):
    global chart, process_matrix
    chart = []  # reset the chart
    process_matrix = {}  # initialize process matrix
    queue = []  # initialize empty queue
    time = 0  # current time
    ap = 0  # arrived process
    rp = 0  # ready process
    done_p = 0  # done process
    q = tq  # time quantum
    start = 0

    while done_p < n:
        for i in range(ap, n):
            if time >= plist[i].arrival:
                queue.append(plist[i])
                ap += 1
                rp += 1

        if rp < 1:
            chart.append(0)
            time += 1
            continue

        # shift
        if start:
            queue = shiftCL(queue)

        if queue[0].burst > 0:
            if queue[0].response_time == -1:
                queue[0].response_time = time - queue[0].arrival

            if queue[0].burst > q:
                for j in range(time, time + q):
                    chart.append(queue[0].pid)
                time += q
                queue[0].burst -= q
            else:
                for g in range(time, time + queue[0].burst):
                    chart.append(queue[0].pid)
                time += queue[0].burst
                queue[0].burst = 0
                queue[0].finish_time = time
                queue[0].turnaround_time = queue[0].finish_time - queue[0].arrival
                queue[0].waiting_time = queue[0].turnaround_time - queue[0].start_time
                process_matrix[queue[0].pid] = [queue[0].waiting_time, queue[0].turnaround_time, queue[0].response_time]
                done_p += 1
                rp -= 1
        start = 1

    return chart


def display_results(processes):
    avg_waiting_time = sum(p.waiting_time for p in processes) / len(processes)
    avg_turnaround_time = sum(p.turnaround_time for p in processes) / len(processes)
    avg_response_time = sum(p.response_time for p in processes) / len(processes)

    result_text = f"Average Waiting Time: {avg_waiting_time:.2f}\n"
    result_text += f"Average Turnaround Time: {avg_turnaround_time:.2f}\n"
    result_text += f"Average Response Time: {avg_response_time:.2f}"

    return result_text


# Function to validate user input
def validate_processes():
    num_processes = num_processes_entry.get()
    time_quantum = time_quantum_entry.get()

    # Check if entries are empty or contain characters other than digits and negative sign (-)
    if not all((num_processes.isdigit() or num_processes == '-',
                time_quantum.isdigit() or time_quantum == '-')):
        messagebox.showerror("Error", "Please enter numeric values for number of processes and time quantum. "
                                      "Negative values are allowed for burst time.")
        return False

    # Check if converted values are within valid ranges (non-negative for processes and time quantum, non-negative for burst time)
    try:
        num_processes = int(num_processes)
        time_quantum = int(time_quantum)
        if num_processes <= 0:
            messagebox.showerror("Error", "Number of processes must be positive.")
            return ValueError
        elif time_quantum < 0:
            messagebox.showerror("Error", "Time quantum must be non-negative.")
            return ValueError
    except ValueError:
        messagebox.showerror("Error", "Invalid input detected. Please enter numeric values.")
        return False

    return True


def add_process_fields(time_quantum):
    if not validate_processes():
        return

    num_processes = int(num_processes_entry.get())

    # Check if all process entry fields are filled
    for arrival_entry, burst_entry in zip(arrival_entries, burst_entries):
        if not arrival_entry.get() or not burst_entry.get():
            messagebox.showerror("Error", "Please fill all arrival and burst time fields for processes.")
            return

    # Validate arrival and burst time entries for numeric values with specific range checks
    for arrival_entry, burst_entry in zip(arrival_entries, burst_entries):
        try:
            arrival_time = int(arrival_entry.get())
            burst_time = int(burst_entry.get())
            if arrival_time < 0:
                messagebox.showerror("Error", "Arrival time cannot be negative.")
                return
            if burst_time <= 0:
                messagebox.showerror("Error", "Burst time must be positive.")
                return
        except ValueError:
            messagebox.showerror("Error", "Arrival and burst times must be numeric values.")
            return

    num_processes = int(num_processes)

    add_process_fields_button.grid_forget()
    for i in range(num_processes):
        arrival_label = tk.Label(window, text=f"Arrival Time for Process {i + 1}:")
        arrival_label.grid(row=i + 2, column=0, padx=5, pady=5)
        arrival_entry = tk.Entry(window)
        arrival_entry.grid(row=i + 2, column=1, padx=5, pady=5)
        arrival_entries.append(arrival_entry)

        burst_label = tk.Label(window, text=f"Burst Time for Process {i + 1}:")
        burst_label.grid(row=i + 2, column=2, padx=5, pady=5)
        burst_entry = tk.Entry(window)
        burst_entry.grid(row=i + 2, column=3, padx=5, pady=5)
        burst_entries.append(burst_entry)

    run_scheduler_button.grid(row=num_processes + 3, column=1, padx=5, pady=5)


def run_scheduler():
    if not validate_processes():
        return

    num_processes = int(num_processes_entry.get())
    time_quantum = int(time_quantum_entry.get())

    processes = []
    for i in range(num_processes):
        pid = i + 1
        try:
            arrival_time = int(arrival_entries[i].get())
            burst_time = int(burst_entries[i].get())
        except ValueError:
            messagebox.showerror("Error",
                                 f"Invalid input for process {i + 1}. Please enter numeric values for arrival and burst time.")
            return

        processes.append(Process(pid, arrival_time, burst_time))
    chart = RR(processes, num_processes, time_quantum)
    # Display results
    result_text = display_results(processes)
    result_label = tk.Label(window, text=result_text)
    result_label.grid(row=num_processes + 5, column=1, padx=5, pady=5)

    # Display process matrix
    matrix_text = "Process Matrix:\n"
    matrix_text += "Process | Waiting Time | Turnaround Time | Response Time\n"
    for pid, values in process_matrix.items():
        matrix_text += f"{pid}\t| {values[0]}\t| {values[1]}\t| {values[2]}\n"
    matrix_label = tk.Label(window, text=matrix_text)
    matrix_label.grid(row=num_processes + 6, column=1, padx=5, pady=5)

    # Display the Gantt chart
    chart_text = "Gantt Chart:\n"
    chart_text += str(chart)
    chart_label = tk.Label(window, text=chart_text)
    chart_label.grid(row=num_processes + 7, column=1, padx=5, pady=5)


# Create Tkinter window
window = tk.Tk()
window.title("Round Robin Scheduler")

# Number of processes label and entry
num_processes_label = tk.Label(window, text="Number of Processes:")
num_processes_label.grid(row=0, column=0, padx=5, pady=5)
num_processes_entry = tk.Entry(window)
num_processes_entry.grid(row=0, column=1, padx=5, pady=5)

# Time quantum label and entry
time_quantum_label = tk.Label(window, text="Time Quantum:")
time_quantum_label.grid(row=1, column=0, padx=5, pady=5)
time_quantum_entry = tk.Entry(window)
time_quantum_entry.grid(row=1, column=1, padx=5, pady=5)

arrival_entries = []
burst_entries = []


# Add Process button
add_process_fields_button = tk.Button(window, text="Add Process",
                                      command=lambda: add_process_fields(time_quantum_entry.get()))
add_process_fields_button.grid(row=2, column=1, padx=5, pady=5)

# Run Scheduler button
run_scheduler_button = tk.Button(window, text="Run Scheduler", command=run_scheduler)

# Run the Tkinter event loop
window.mainloop()
