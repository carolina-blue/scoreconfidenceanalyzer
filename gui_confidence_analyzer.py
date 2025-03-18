import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
import os
import sys
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from analyze_confidence import categorize_confidence

# Prevent matplotlib from using the main thread warning
plt.switch_backend('Agg')

class ConfidenceAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Confidence vs. Score Analyzer")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TFrame", background="#f0f0f0")
        
        # Variables
        self.file_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.calibration_threshold = tk.IntVar(value=5)
        self.results_df = None
        self.summary_df = None
        
        # Main container
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        self.create_input_section(main_frame)
        
        # Results section
        self.create_results_section(main_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_input_section(self, parent):
        input_frame = ttk.LabelFrame(parent, text="Input Parameters", padding=10)
        input_frame.pack(fill=tk.X, pady=5)
        
        # File selection
        file_frame = ttk.Frame(input_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(file_frame, text="CSV File:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(file_frame, textvariable=self.file_path, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT, padx=5)
        
        # Output directory
        output_frame = ttk.Frame(input_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Output Directory:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_dir).pack(side=tk.LEFT, padx=5)
        
        # Calibration threshold
        threshold_frame = ttk.Frame(input_frame)
        threshold_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(threshold_frame, text="Calibration Threshold (%):").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(threshold_frame, from_=1, to=20, textvariable=self.calibration_threshold, width=5).pack(side=tk.LEFT, padx=5)
        
        # Run button
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Run Analysis", command=self.run_analysis).pack(side=tk.RIGHT, padx=5)
    
    def create_results_section(self, parent):
        results_frame = ttk.LabelFrame(parent, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Notebook for different results views
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="Summary")
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, font=("Courier", 12))
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Data tab
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="Data")
        
        self.data_text = scrolledtext.ScrolledText(data_frame, wrap=tk.WORD, font=("Courier", 12))
        self.data_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scatter Plot tab
        self.scatter_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scatter_frame, text="Scatter Plot")
        
        # Create scatter plot canvas in advance
        self.scatter_figure = Figure(figsize=(8, 6))
        self.scatter_canvas = FigureCanvasTkAgg(self.scatter_figure, self.scatter_frame)
        self.scatter_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Distribution Plot tab
        self.bar_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bar_frame, text="Distribution")
        
        # Create distribution plot canvas in advance
        self.bar_figure = Figure(figsize=(8, 6))
        self.bar_canvas = FigureCanvasTkAgg(self.bar_figure, self.bar_frame)
        self.bar_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add tab change event handler
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
    
    def on_tab_change(self, event):
        # Get the current tab
        current_tab = self.notebook.index(self.notebook.select())
        tab_name = self.notebook.tab(current_tab, "text")
        
        if self.results_df is not None:
            if tab_name == "Scatter Plot":
                self.create_scatter_plot()
            elif tab_name == "Distribution":
                self.create_distribution_plot()
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filename:
            self.file_path.set(filename)
            # Set default output directory to same as input file
            default_output = os.path.dirname(filename)
            if not self.output_dir.get():
                self.output_dir.set(default_output)
    
    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
    
    def run_analysis(self):
        # Validate inputs
        file_path = self.file_path.get()
        output_dir = self.output_dir.get()
        threshold = self.calibration_threshold.get()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a CSV file")
            return
        
        if not output_dir:
            # Use same directory as input file
            output_dir = os.path.dirname(file_path)
            self.output_dir.set(output_dir)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Clear previous results
        self.summary_text.delete(1.0, tk.END)
        self.data_text.delete(1.0, tk.END)
        
        # Run in a separate thread to keep UI responsive
        self.status_var.set("Running analysis...")
        
        # Disable run button during analysis
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button) and widget["text"] == "Run Analysis":
                widget.state(["disabled"])
        
        threading.Thread(target=self.perform_analysis, args=(file_path, output_dir, threshold), daemon=True).start()
    
    def perform_analysis(self, file_path, output_dir, threshold):
        try:
            # Read the data directly
            df = pd.read_csv(file_path)
            required_columns = ['User Name', 'Quiz Score', 'Confidence Score']
            
            # Verify required columns
            for col in required_columns:
                if col not in df.columns:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Missing required column '{col}' in the CSV file."))
                    self.root.after(0, lambda: self.status_var.set("Analysis failed: Missing columns."))
                    self.root.after(0, self.enable_run_button)
                    return
            
            # Add confidence category column
            df['Confidence Category'] = df.apply(lambda row: categorize_confidence(row, threshold), axis=1)
            
            # Calculate summary statistics
            summary = df['Confidence Category'].value_counts().reset_index()
            summary.columns = ['Category', 'Count']
            summary['Percentage'] = (summary['Count'] / len(df) * 100).round(1)
            
            # Save files
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"confidence_analysis_results_{timestamp}.csv")
            summary_file = os.path.join(output_dir, f"confidence_analysis_summary_{timestamp}.csv")
            
            # Save CSV files
            df.to_csv(output_file, index=False)
            summary.to_csv(summary_file, index=False)
            
            # Save scatter plot
            plt.figure(figsize=(10, 8))
            categories = df['Confidence Category'].unique()
            colors = plt.cm.tab10(np.linspace(0, 1, len(categories)))
            
            for i, category in enumerate(categories):
                subset = df[df['Confidence Category'] == category]
                plt.scatter(subset['Quiz Score'], subset['Confidence Score'], 
                           label=category, color=colors[i], alpha=0.7)
            
            plt.plot([0, 100], [0, 100], 'k--', label='Perfect Calibration')
            plt.plot([0, 100], [threshold, 100 + threshold], 'r:', label=f'+{threshold}% Threshold')
            plt.plot([0, 100], [-threshold, 100 - threshold], 'r:', label=f'-{threshold}% Threshold')
            
            plt.xlabel('Quiz Score (%)')
            plt.ylabel('Confidence Score (%)')
            plt.title('Quiz Score vs Confidence Analysis')
            plt.grid(True, alpha=0.3)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            scatter_file = os.path.join(output_dir, f"confidence_scatter_plot_{timestamp}.png")
            plt.savefig(scatter_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Save distribution plot
            plt.figure(figsize=(10, 6))
            sorted_summary = summary.sort_values('Count', ascending=False)
            colors = plt.cm.tab10(np.linspace(0, 1, len(sorted_summary)))
            bars = plt.bar(sorted_summary['Category'], sorted_summary['Count'], color=colors)
            
            # Add count labels on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.annotate(f'{height}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom')
            
            plt.xlabel('Confidence Category')
            plt.ylabel('Number of Users')
            plt.title('Distribution of Confidence Categories')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            dist_file = os.path.join(output_dir, f"confidence_distribution_{timestamp}.png")
            plt.savefig(dist_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Save results to instance variables
            self.results_df = df
            self.summary_df = summary
            
            # Update UI on the main thread
            self.root.after(0, self.update_results)
            self.root.after(0, lambda: self.status_var.set(f"Analysis complete. Results saved to {output_dir}"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Analysis failed."))
        
        # Re-enable run button
        self.root.after(0, self.enable_run_button)
    
    def enable_run_button(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button) and widget["text"] == "Run Analysis":
                widget.state(["!disabled"])
    
    def update_results(self):
        # Update summary tab
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, "Summary of Confidence Categories:\n\n")
        
        max_cat_len = max(len(cat) for cat in self.summary_df['Category']) + 2
        self.summary_text.insert(tk.END, f"{'Category':{max_cat_len}}  {'Count':8}  {'Percentage':10}\n")
        self.summary_text.insert(tk.END, f"{'-'*max_cat_len}  {'-'*8}  {'-'*10}\n")
        
        for _, row in self.summary_df.iterrows():
            self.summary_text.insert(tk.END, f"{row['Category']:{max_cat_len}}  {row['Count']:8}  {row['Percentage']:10.1f}%\n")
        
        # Update data tab
        self.data_text.delete(1.0, tk.END)
        
        # Show first 100 rows with formatting
        display_df = self.results_df.head(100)
        headers = display_df.columns.tolist()
        
        # Calculate column widths
        col_widths = {}
        for col in headers:
            col_widths[col] = max(len(col), display_df[col].astype(str).str.len().max()) + 2
        
        # Create header
        header_line = ""
        for col in headers:
            header_line += f"{col:{col_widths[col]}}"
        self.data_text.insert(tk.END, header_line + "\n")
        
        # Add separator
        separator = ""
        for col in headers:
            separator += f"{'-' * col_widths[col]}"
        self.data_text.insert(tk.END, separator + "\n")
        
        # Add data rows
        for _, row in display_df.iterrows():
            line = ""
            for col in headers:
                line += f"{str(row[col]):{col_widths[col]}}"
            self.data_text.insert(tk.END, line + "\n")
        
        if len(self.results_df) > 100:
            self.data_text.insert(tk.END, f"\nShowing 100 of {len(self.results_df)} rows.")
        
        # Create initial plots
        self.create_scatter_plot()
        self.create_distribution_plot()
    
    def create_scatter_plot(self):
        if self.results_df is None:
            return
            
        # Clear the figure
        self.scatter_figure.clear()
        ax = self.scatter_figure.add_subplot(111)
        
        # Get unique categories and assign colors
        categories = self.results_df['Confidence Category'].unique()
        colors = plt.cm.tab10(range(len(categories)))
        
        # Plot each category
        for i, category in enumerate(categories):
            subset = self.results_df[self.results_df['Confidence Category'] == category]
            ax.scatter(subset['Quiz Score'], subset['Confidence Score'], 
                      label=category, color=colors[i], alpha=0.7)
        
        # Add reference lines
        ax.plot([0, 100], [0, 100], 'k--', label='Perfect Calibration')
        threshold = self.calibration_threshold.get()
        ax.plot([0, 100], [threshold, 100 + threshold], 'r:', label=f'+{threshold}% Threshold')
        ax.plot([0, 100], [-threshold, 100 - threshold], 'r:', label=f'-{threshold}% Threshold')
        
        ax.set_xlabel('Quiz Score (%)')
        ax.set_ylabel('Confidence Score (%)')
        ax.set_title('Quiz Score vs Confidence Analysis')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
        
        self.scatter_figure.tight_layout()
        self.scatter_canvas.draw()
    
    def create_distribution_plot(self):
        if self.summary_df is None:
            return
            
        # Clear the figure
        self.bar_figure.clear()
        ax = self.bar_figure.add_subplot(111)
        
        # Sort by count
        sorted_summary = self.summary_df.sort_values('Count', ascending=False)
        
        # Create bar chart with different colors
        colors = plt.cm.tab10(np.linspace(0, 1, len(sorted_summary)))
        bars = ax.bar(sorted_summary['Category'], sorted_summary['Count'], color=colors)
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        ax.set_xlabel('Confidence Category')
        ax.set_ylabel('Number of Users')
        ax.set_title('Distribution of Confidence Categories')
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        self.bar_figure.tight_layout()
        self.bar_canvas.draw()

def main():
    root = tk.Tk()
    app = ConfidenceAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 