import tkinter as tk
 from tkinter import ttk, messagebox, filedialog
 import matplotlib
 matplotlib.use('TkAgg')
 import matplotlib.pyplot as plt
 from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
 import random
 import json
 import csv
 from typing import List, Tuple, Dict
 
 class DiskScheduler:
     """Class to simulate disk scheduling algorithms."""
     def __init__(self, requests: List[int], head: int, disk_size: int):
         """Initialize the scheduler with requests, head position, and disk size."""
         self.requests = requests
         self.head = head
         self.disk_size = disk_size
         self.seek_sequence: List[int] = []
         self.total_seek: int = 0
 
     def calculate_metrics(self) -> Tuple[int, float, float]:
         """Calculate total seek time, average seek time, and throughput."""
         self.total_seek = sum(abs(self.seek_sequence[i] - self.seek_sequence[i-1]) 
                             for i in range(1, len(self.seek_sequence)))
         avg_seek = self.total_seek / len(self.requests) if self.requests else 0
         throughput = len(self.requests) / (self.total_seek + 1) if self.total_seek > 0 else 0
         return self.total_seek, avg_seek, throughput
 
     def fcfs(self) -> Tuple[int, float, float]:
         """First Come First Serve algorithm."""
         self.seek_sequence = [self.head] + self.requests
         return self.calculate_metrics()
 
     def sstf(self) -> Tuple[int, float, float]:
         """Shortest Seek Time First algorithm."""
         self.seek_sequence = [self.head]
         remaining = self.requests.copy()
         while remaining:
             closest = min(remaining, key=lambda x: abs(x - self.seek_sequence[-1]))
             self.seek_sequence.append(closest)
             remaining.remove(closest)
         return self.calculate_metrics()
 
     def scan(self, direction: str = "right") -> Tuple[int, float, float]:
         """SCAN (Elevator) algorithm with specified direction."""
         self.seek_sequence = [self.head]
         sorted_requests = sorted(self.requests)
         if direction == "right":
             left = [x for x in sorted_requests if x < self.head]
             right = [x for x in sorted_requests if x >= self.head]
             self.seek_sequence += right + ([self.disk_size - 1] if right and right[-1] != self.disk_size - 1 else []) + left[::-1]
         else:
             left = [x for x in sorted_requests if x <= self.head]
             right = [x for x in sorted_requests if x > self.head]
             self.seek_sequence += left[::-1] + ([0] if left and left[0] != 0 else []) + right
         return self.calculate_metrics()
 
     def cscan(self) -> Tuple[int, float, float]:
         """Circular SCAN algorithm."""
         self.seek_sequence = [self.head]
         sorted_requests = sorted(self.requests)
         right = [x for x in sorted_requests if x >= self.head]
         left = [x for x in sorted_requests if x < self.head]
         self.seek_sequence += right + ([self.disk_size - 1] if right and right[-1] != self.disk_size - 1 else []) + [0] + left
         return self.calculate_metrics()
 
 class DiskSchedulerGUI:
     """Graphical User Interface for the Disk Scheduling Simulator."""
     def __init__(self, root: tk.Tk):
         """Initialize the GUI with a Tkinter root window."""
         self.root = root
         self.root.title("Disk Scheduling Simulator")
         self.root.geometry("1200x900")
         self.root.configure(bg="#1e1e2f")
 
         # Style Configuration
         style = ttk.Style()
         style.theme_use('clam')
         style.configure("TLabel", font=("Segoe UI", 12), background="#1e1e2f", foreground="#e0e0e0")
         style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=8, background="#2d2d44", foreground="#ffffff")
         style.configure("Accent.TButton", background="#6b48ff", foreground="#ffffff")
         style.configure("TFrame", background="#1e1e2f")
         style.configure("TLabelframe", background="#252537", foreground="#ffffff")
         style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"), background="#252537", foreground="#6b48ff")
         style.configure("TNotebook", background="#1e1e2f")
         style.configure("TNotebook.Tab", background="#252537", foreground="#ffffff", padding=[10, 5])
         style.map("TNotebook.Tab", background=[("selected", "#6b48ff")])
 
         # Main Frame
         main_frame = tk.Frame(self.root, bg="#1e1e2f")
         main_frame.pack(fill="both", expand=True, padx=20, pady=20)
 
         # Title
         ttk.Label(main_frame, text="Disk Scheduling Simulator", 
                  font=("Segoe UI", 20, "bold"), foreground="#6b48ff").pack(pady=(0, 20))
 
         # Input Frame
         input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding=15)
         input_frame.pack(fill="x", pady=10)
 
         self.disk_size_entry = ttk.Entry(input_frame, width=15, font=("Segoe UI", 11))
         self.head_entry = ttk.Entry(input_frame, width=15, font=("Segoe UI", 11))
         self.requests_entry = ttk.Entry(input_frame, width=50, font=("Segoe UI", 11))
 
         for i, (label, entry) in enumerate([
             ("Disk Size:", self.disk_size_entry),
             ("Head Position:", self.head_entry),
             ("Request Queue:", self.requests_entry)
         ]):
             ttk.Label(input_frame, text=label).grid(row=i, column=0, padx=10, pady=8, sticky="e")
             entry.grid(row=i, column=1, padx=10, pady=8)
 
         btn_style = {"style": "TButton"}
         ttk.Button(input_frame, text="Load Preset", command=self.load_preset, **btn_style).grid(row=2, column=2, padx=5)
         ttk.Button(input_frame, text="Load File", command=self.load_file, **btn_style).grid(row=2, column=3, padx=5)
         ttk.Button(input_frame, text="Generate Random", command=self.generate_random, **btn_style).grid(row=2, column=4, padx=5)
 
         # Algorithm Selection Frame
         algo_frame = ttk.LabelFrame(main_frame, text="Simulation Options", padding=15)
         algo_frame.pack(fill="x", pady=10)
 
         ttk.Label(algo_frame, text="Algorithm:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
         self.algo_var = tk.StringVar(value="FCFS")
         self.algo_combo = ttk.Combobox(algo_frame, textvariable=self.algo_var, 
                                       values=["FCFS", "SSTF", "SCAN", "C-SCAN", "Compare All"], 
                                       width=15, font=("Segoe UI", 11))
         self.algo_combo.grid(row=0, column=1, padx=10, pady=8, sticky="w")
         self.algo_combo.bind("<<ComboboxSelected>>", self.on_algo_select)
 
         self.direction_frame = ttk.Frame(algo_frame)
         self.direction_frame.grid(row=1, column=0, columnspan=2, pady=5)
         ttk.Label(self.direction_frame, text="SCAN Direction:").pack(side="left", padx=10)
         self.direction_var = tk.StringVar(value="right")
         self.direction_combo = ttk.Combobox(self.direction_frame, textvariable=self.direction_var, 
                                            values=["right", "left"], state="disabled", width=10, font=("Segoe UI", 11))
         self.direction_combo.pack(side="left")
 
         ttk.Button(algo_frame, text="Help", command=self.show_help, **btn_style).grid(row=0, column=2, padx=10)
 
         # Action Buttons Frame
         button_frame = ttk.Frame(main_frame)
         button_frame.pack(pady=15)
         self.run_button = ttk.Button(button_frame, text="Run Simulation", command=self.run_simulation, 
                                     style="Accent.TButton")
         self.run_button.pack(side="left", padx=10)
         ttk.Button(button_frame, text="Clear", command=self.clear_output, **btn_style).pack(side="left", padx=10)
         ttk.Button(button_frame, text="Save Results", command=self.save_results, **btn_style).pack(side="left", padx=10)
         ttk.Button(button_frame, text="Export CSV", command=self.export_csv, **btn_style).pack(side="left", padx=10)
 
         # Notebook
         self.notebook = ttk.Notebook(main_frame)
         self.notebook.pack(fill="both", expand=True, pady=10)
 
         # Results Tab
         self.results_tab = ttk.Frame(self.notebook)
         self.notebook.add(self.results_tab, text="Results")
         self.result_text = tk.Text(self.results_tab, height=10, width=100, font=("Consolas", 11), 
                                   bg="#252537", fg="#e0e0e0", relief="flat", borderwidth=2, insertbackground="white")
         self.result_text.pack(fill="x", padx=5, pady=5)
 
         # Metrics Table
         self.tree = ttk.Treeview(self.results_tab, columns=("Algorithm", "Total Seek", "Avg Seek", "Throughput"), show="headings")
         self.tree.heading("Algorithm", text="Algorithm")
         self.tree.heading("Total Seek", text="Total Seek Time")
         self.tree.heading("Avg Seek", text="Avg Seek Time")
         self.tree.heading("Throughput", text="Throughput")
         self.tree.pack(fill="both", expand=True, padx=5, pady=5)
 
         # Graphs Tab
         self.graphs_tab = ttk.Frame(self.notebook)
         self.notebook.add(self.graphs_tab, text="Graphs")
 
         plt.style.use('dark_background')
         self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8), height_ratios=[2, 1])
         self.fig.patch.set_facecolor('#1e1e2f')
         self.ax1.set_facecolor('#252537')
         self.ax2.set_facecolor('#252537')
         
         self.canvas = FigureCanvasTkAgg(self.fig, master=self.graphs_tab)
         self.canvas.get_tk_widget().configure(bg="#1e1e2f")
         self.canvas.get_tk_widget().pack(fill="both", expand=True)
 
         # Tooltip
         self.tooltip = tk.Label(self.root, text="", bg="#6b48ff", fg="white", font=("Segoe UI", 10),
                                relief="flat", borderwidth=0, padx=5, pady=2)
         self.tooltip.place_forget()
         self.canvas.mpl_connect('motion_notify_event', self.on_hover)
 
         # Key bindings
         self.root.bind("<Control-r>", lambda event: self.run_simulation())
         self.root.bind("<Control-c>", lambda event: self.clear_output())
         self.root.bind("<Control-s>", lambda event: self.save_results())
         self.requests_entry.bind("<Return>", lambda event: self.run_simulation())
 
         self.toggle_direction()
 
     def toggle_direction(self) -> None:
         """Enable or disable SCAN direction combo box based on selected algorithm."""
         if hasattr(self, 'direction_combo'):
             self.direction_combo.config(state="normal" if self.algo_var.get() == "SCAN" else "disabled")
 
     def on_algo_select(self, event: tk.Event) -> None:
         """Show explanation of the selected algorithm."""
         self.toggle_direction()
         algo = self.algo_var.get()
         explanations = {
             "FCFS": "First Come First Serve: Processes requests in the order they arrive.",
             "SSTF": "Shortest Seek Time First: Selects the request closest to the current head position.",
             "SCAN": "SCAN (Elevator): Moves in one direction, servicing requests, then reverses.",
             "C-SCAN": "Circular SCAN: Moves in one direction, jumps back to start, then continues.",
             "Compare All": "Runs all algorithms for comparison."
         }
         messagebox.showinfo(f"{algo} Explanation", explanations[algo])
 
     def _clear_and_insert_entries(self, disk_size: str, head: str, requests: str) -> None:
         """Helper method to clear and insert values into input entries."""
         self.disk_size_entry.delete(0, tk.END)
         self.head_entry.delete(0, tk.END)
         self.requests_entry.delete(0, tk.END)
         self.disk_size_entry.insert(0, disk_size)
         self.head_entry.insert(0, head)
         self.requests_entry.insert(0, requests)
 
     def load_preset(self) -> None:
         """Load predefined sample input values."""
         self._clear_and_insert_entries("200", "50", "98 183 37 122 14 124 65 67")
         messagebox.showinfo("Preset Loaded", "Sample input loaded")
 
     def load_file(self) -> None:
         """Load input parameters from a file (TXT, CSV, or JSON)."""
         file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("JSON files", "*.json")])
         if not file_path:
             return
         try:
             if file_path.endswith('.txt'):
                 with open(file_path, 'r') as f:
                     lines = f.readlines()
                     if len(lines) < 3:
                         raise ValueError("Text file must contain at least 3 lines: disk size, head, requests.")
                     self._clear_and_insert_entries(lines[0].strip(), lines[1].strip(), lines[2].strip())
             elif file_path.endswith('.csv'):
                 with open(file_path, 'r') as f:
                     reader = csv.reader(f)
                     data = next(reader)
                     if len(data) < 3:
                         raise ValueError("CSV file must contain at least 3 columns: disk size, head, requests.")
                     self._clear_and_insert_entries(data[0], data[1], ' '.join(data[2:]))
             elif file_path.endswith('.json'):
                 with open(file_path, 'r') as f:
                     data = json.load(f)
                     if not all(key in data for key in ['disk_size', 'head', 'requests']):
                         raise ValueError("JSON file must contain 'disk_size', 'head', and 'requests' keys.")
                     self._clear_and_insert_entries(str(data['disk_size']), str(data['head']), ' '.join(map(str, data['requests'])))
             messagebox.showinfo("Success", "File loaded successfully")
         except FileNotFoundError:
             messagebox.showerror("Error", f"File not found: {file_path}")
         except ValueError as e:
             messagebox.showerror("Error", str(e))
         except Exception as e:
             messagebox.showerror("Error", f"Failed to load file: {str(e)}")
 
     def generate_random(self) -> None:
         """Generate random disk scheduling parameters."""
         try:
             disk_size_input = self.disk_size_entry.get().strip()
             disk_size = int(disk_size_input) if disk_size_input else 200
             if disk_size <= 0:
                 raise ValueError("Disk size must be positive.")
             head = random.randint(0, disk_size - 1)
             requests = sorted([random.randint(0, disk_size - 1) for _ in range(random.randint(5, 15))])
             self._clear_and_insert_entries(str(disk_size), str(head), ' '.join(map(str, requests)))
             messagebox.showinfo("Random Generated", "Random requests generated")
         except ValueError as e:
             messagebox.showerror("Error", f"Invalid disk size: {str(e)}")
 
     def show_help(self) -> None:
         """Display help information about the simulator."""
         help_text = """
         Disk Scheduling Algorithms:
         FCFS: First Come First Serve - Processes requests in order
         SSTF: Shortest Seek Time First - Selects closest request
         SCAN: Elevator algorithm - Moves in one direction then reverses
         C-SCAN: Circular SCAN - Moves in one direction then jumps back
         Compare All: Runs all algorithms and compares results
         """
         messagebox.showinfo("Help", help_text)
 
     def _validate_inputs(self) -> Tuple[int, int, List[int]]:
         """Validate and return disk size, head position, and requests."""
         disk_size = self.disk_size_entry.get().strip()
         head = self.head_entry.get().strip()
         requests = self.requests_entry.get().strip()
         
         if not all([disk_size, head, requests]):
             raise ValueError("All input fields must be filled.")
         
         try:
             disk_size = int(disk_size)
             head = int(head)
             requests = [int(x) for x in requests.split() if x.strip()]
         except ValueError:
             raise ValueError("Inputs must be integers.")
         
         if not requests:
             raise ValueError("Request queue cannot be empty.")
         if disk_size <= 0:
             raise ValueError("Disk size must be positive.")
         if not (0 <= head < disk_size) or any(r < 0 or r >= disk_size for r in requests):
             raise ValueError("Head and requests must be within disk size (0 to disk_size-1).")
         
         return disk_size, head, requests
 
     def _run_algorithm(self, algo: str, requests: List[int], head: int, disk_size: int) -> Dict[str, Tuple[List[int], Tuple[int, float, float]]]:
         """Execute the selected algorithm(s) and return results."""
         results = {}
         scheduler = DiskScheduler(requests, head, disk_size)
         if algo == "Compare All":
             for a in ["FCFS", "SSTF", "SCAN", "C-SCAN"]:
                 scheduler = DiskScheduler(requests, head, disk_size)
                 metrics = (scheduler.fcfs() if a == "FCFS" else
                           scheduler.sstf() if a == "SSTF" else
                           scheduler.scan(self.direction_var.get()) if a == "SCAN" else
                           scheduler.cscan())
                 results[a] = (scheduler.seek_sequence, metrics)
         else:
             metrics = (scheduler.fcfs() if algo == "FCFS" else
                       scheduler.sstf() if algo == "SSTF" else
                       scheduler.scan(self.direction_var.get()) if algo == "SCAN" else
                       scheduler.cscan())
             results[algo] = (scheduler.seek_sequence, metrics)
         return results
 
     def _update_results(self, results: Dict[str, Tuple[List[int], Tuple[int, float, float]]]) -> None:
         """Update text output and metrics table with simulation results."""
         self.result_text.delete(1.0, tk.END)
         output = ""
         for algo, (seq, (total, avg, throughput)) in results.items():
             output += (f"{algo} - Seek Sequence: {seq}\n"
                       f"Total Seek Time: {total}\n"
                       f"Average Seek Time: {avg:.2f}\n"
                       f"Throughput: {throughput:.4f}\n\n")
         self.result_text.insert(tk.END, output)
 
         for i in self.tree.get_children():
             self.tree.delete(i)
         for algo, (_, (total, avg, throughput)) in results.items():
             self.tree.insert("", "end", values=(algo, total, f"{avg:.2f}", f"{throughput:.4f}"))
 
     def _plot_graphs(self, results: Dict[str, Tuple[List[int], Tuple[int, float, float]]], disk_size: int) -> None:
         """Plot seek sequences and seek time comparison."""
         self.ax1.cla()
         self.ax2.cla()
         colors = {'FCFS': '#ff6b6b', 'SSTF': '#4ecdc4', 'SCAN': '#45b7d1', 'C-SCAN': '#96ceb4'}
 
         # Seek Sequence Plot
         self.ax1.set_title("Seek Sequences", fontsize=14, color="#6b48ff")
         self.ax1.set_xlabel("Request Number", fontsize=12, color="#e0e0e0")
         self.ax1.set_ylabel("Cylinder Position", fontsize=12, color="#e0e0e0")
         self.ax1.grid(True, linestyle='--', alpha=0.3, color="#e0e0e0")
         self.ax1.set_ylim(0, disk_size)
         self.ax1.tick_params(colors="#e0e0e0")
 
         # Bar Chart
         self.ax2.set_title("Total Seek Time Comparison", fontsize=14, color="#6b48ff")
         self.ax2.set_ylabel("Seek Time", fontsize=12, color="#e0e0e0")
         self.ax2.tick_params(colors="#e0e0e0")
 
         algo_names = list(results.keys())
         seek_times = [metrics[0] for _, metrics in results.values()]
         
         for algo, (seq, _) in results.items():
             self.ax1.plot(range(len(seq)), seq, marker='o', color=colors[algo], 
                          lw=2, markersize=8, label=algo, picker=5, alpha=0.9)
         self.ax1.legend(facecolor="#252537", edgecolor="#6b48ff", labelcolor="#e0e0e0")
         self.ax1.set_xlim(0, max(len(seq) for seq, _ in results.values()) - 1)
         
         bars = self.ax2.bar(algo_names, seek_times, color=[colors[a] for a in algo_names], alpha=0.8)
         for bar in bars:
             bar.set_edgecolor("#6b48ff")
             bar.set_linewidth(1)
         self.ax2.tick_params(axis='x', rotation=45, colors="#e0e0e0")
 
         self.fig.tight_layout()
         self.canvas.draw()
 
     def run_simulation(self) -> None:
         """Run the disk scheduling simulation."""
         if not self.run_button.winfo_exists():
             return
 
         self.run_button.config(state="disabled")
         self.clear_output(clear_text=False)
 
         try:
             disk_size, head, requests = self._validate_inputs()
             results = self._run_algorithm(self.algo_var.get(), requests, head, disk_size)
             self._update_results(results)
             self._plot_graphs(results, disk_size)
             self.run_button.config(state="normal")
         except ValueError as e:
             messagebox.showerror("Error", str(e))
             self.run_button.config(state="normal")
         except Exception as e:
             messagebox.showerror("Error", f"Unexpected error: {str(e)}")
             self.run_button.config(state="normal")
 
     def on_hover(self, event: matplotlib.backend_bases.MouseEvent) -> None:
         """Display tooltip with cylinder position on graph hover."""
         if event.inaxes == self.ax1:
             for line in self.ax1.get_lines():
                 if line.contains(event)[0]:
                     x, y = int(event.xdata), int(event.ydata)
                     self.tooltip.config(text=f"Cylinder: {y}")
                     canvas_x, canvas_y = self.canvas.get_tk_widget().winfo_rootx(), self.canvas.get_tk_widget().winfo_rooty()
                     self.tooltip.place(x=canvas_x + event.x + 15, y=canvas_y + event.y + 15)
                     return
         self.tooltip.place_forget()
 
     def clear_output(self, clear_text: bool = True) -> None:
         """Clear the output displays."""
         if clear_text:
             self.result_text.delete(1.0, tk.END)
             for i in self.tree.get_children():
                 self.tree.delete(i)
         self.ax1.cla()
         self.ax2.cla()
         self.ax1.set_facecolor('#252537')
         self.ax2.set_facecolor('#252537')
         self.canvas.draw()
         self.run_button.config(state="normal")
 
     def save_results(self) -> None:
         """Save simulation results and graph to files."""
         text_content = self.result_text.get(1.0, tk.END).strip()
         if not text_content:
             messagebox.showwarning("Warning", "No results to save!")
             return
         if not self.ax1.lines:
             messagebox.showwarning("Warning", "No graph to save!")
             return
 
         file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
         if file_path:
             try:
                 with open(file_path, "w") as f:
                     f.write(text_content)
                 self.fig.savefig(file_path.replace(".txt", ".png"), dpi=100, facecolor='#1e1e2f')
                 messagebox.showinfo("Success", "Results and graph saved successfully!")
             except PermissionError:
                 messagebox.showerror("Error", f"Permission denied to write to {file_path}")
             except Exception as e:
                 messagebox.showerror("Error", f"Failed to save: {str(e)}")
 
     def export_csv(self) -> None:
         """Export metrics table to a CSV file."""
         if not self.tree.get_children():
             messagebox.showwarning("Warning", "No results to export!")
             return
 
         file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                                 filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
         if file_path:
             try:
                 with open(file_path, "w", newline='') as f:
                     writer = csv.writer(f)
                     writer.writerow(["Algorithm", "Total Seek Time", "Avg Seek Time", "Throughput"])
                     for item in self.tree.get_children():
                         writer.writerow(self.tree.item(item)["values"])
                 messagebox.showinfo("Success", "Results exported to CSV successfully!")
             except PermissionError:
                 messagebox.showerror("Error", f"Permission denied to write to {file_path}")
             except Exception as e:
                 messagebox.showerror("Error", f"Failed to export: {str(e)}")
 
 def main() -> None:
     """Main entry point for the application."""
     root = tk.Tk()
     app = DiskSchedulerGUI(root)
     root.mainloop()
 
 if __name__ == "__main__":
     main()
