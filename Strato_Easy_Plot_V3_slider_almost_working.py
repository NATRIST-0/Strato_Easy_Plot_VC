#!/bin/usr python3
# author: Tristan Gayrard
#21/05/2024, Laramie WY

"""
Strato_Easy_Plot_V3_slider_almost_working
"""

import tkinter as tk
from tkinter import Text, filedialog
from tkinter import ttk
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.widgets import Slider
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from sys import exit

def update_plot(filtered_data):
    global plot1, plot1_2, plot1_3

    plot1.clear()
    if 'plot1_2' in globals() and plot1_2:
        plot1_2.remove()
        plot1_2 = None
    if 'plot1_3' in globals() and plot1_3:
        plot1_3.remove()
        plot1_3 = None

    y1_variable = selected_Y1.get()
    if y1_variable != 'Select a variable':
        y1_data = filtered_data[y1_variable]
        plot1.plot(filtered_data['Time_from_start'], y1_data, label=y1_variable, color="red")
        plot1.set_xlabel('Time of running (h)')
        plot1.set_ylabel(y1_variable, color="red")

    y2_variable = selected_Y1_2.get()
    if y2_variable != 'Select a variable':
        y2_data = filtered_data[y2_variable]
        plot1_2 = plot1.twinx()
        plot1_2.plot(filtered_data['Time_from_start'], y2_data, label=y2_variable, color="blue")
        plot1_2.set_ylabel(y2_variable, color="blue")
        plot1_2.yaxis.set_label_position("right")
        min_value = np.nanmin(plot1_2.get_ylim())
        max_value = np.nanmax(plot1_2.get_ylim())
        ticks = np.linspace(min_value, max_value, num=5)
        plot1_2.set_yticks(ticks)

    y3_variable = selected_Y1_3.get()
    if y3_variable != 'Select a variable':
        plot1_3 = plot1.twinx()
        plot1_3.spines['right'].set_position(('outward', 60))
        y3_data = filtered_data[y3_variable]
        plot1_3.plot(filtered_data['Time_from_start'], y3_data, label=y3_variable, color="green")
        plot1_3.set_ylabel(y3_variable, color="green")
        plot1_3.yaxis.set_label_position("right")

    if var0.get() == 'On':
        selected_stat_func()
        
    plot1.grid(True)
    plot1.relim()  # Recalculate limits
    plot1.autoscale()  # Apply recalculated limits
    if plot1_2:
        plot1_2.relim()
        plot1_2.autoscale()
    if plot1_3:
        plot1_3.relim()
        plot1_3.autoscale()

    canvas1.draw()

def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())

def selected_stat_func():
    global plot1_2
    # Effacer le plot1_2 précédent
    if 'plot1_2' in globals() and plot1_2:
        plot1_2.remove()
        plot1_2 = None
    
    plot1_2 = plot1.twinx()
    plot1_2.yaxis.set_label_position("right")
    window_size = int(window_text.get("1.0", "end-1c"))
    y1_variable = selected_Y1.get()
    if y1_variable == 'Select a variable':
        return
    
    if selected_stat.get() == 'Rolling Mean':
        rolling_mean = data[y1_variable].rolling(window=window_size).mean()
        plot1_2.plot(data['Time_from_start'], rolling_mean, linestyle='--', color='purple')
        plot1_2.set_ylabel(f"Rolling mean of {y1_variable}", color='purple')
    elif selected_stat.get() == 'Rolling Standard Deviation':
        rolling_std = data[y1_variable].rolling(window=window_size).std()
        plot1_2.plot(data['Time_from_start'], rolling_std, linestyle='--', color='green')
        plot1_2.set_ylabel(f"Rolling Std Dev of {y1_variable}", color='green')
    elif selected_stat.get() == 'Relative Standard Deviation':
        rolling_mean = data[y1_variable].rolling(window=window_size).mean()
        rolling_std = data[y1_variable].rolling(window=window_size).std()
        rolling_cv = (rolling_std / rolling_mean) * 100
        plot1_2.plot(data['Time_from_start'], rolling_cv, linestyle='--', color='orange')
        plot1_2.set_ylabel(f"Relative Std Dev of {y1_variable} (%)", color='orange')
    elif selected_stat.get() == 'RMSE':
        y1_variable_data = data[y1_variable]
        overall_rmse = rmse(y1_variable_data, y1_variable_data.shift())
        plot1_2.axhline(y=overall_rmse, color='deepskyblue', linestyle='--', label=f'RMSE: {overall_rmse * 100: .2f}ppb' )
        plot1_2.set_ylabel(f"RMSE of {y1_variable}", color='deepskyblue')

    # Effacer les anciens ticks de l'axe y2
    plot1_2.yaxis.set_tick_params(length=0)
    
    # Configuration des ticks des axes Y
    min_value = np.nanmin(plot1_2.get_ylim())
    max_value = np.nanmax(plot1_2.get_ylim())
    ticks = np.linspace(min_value, max_value, num=5)
    plot1_2.set_yticks(ticks)
    
    plot1_2.relim()
    plot1_2.autoscale()
    canvas1.draw()

def on_time_change(event):
    try:
        time1_val = float(time1.get("1.0", "end-1c"))
        time2_val = float(time2.get("1.0", "end-1c"))
        filtered_data = data[(data['Time_from_start'] >= time1_val) & (data['Time_from_start'] <= time2_val)]
        update_plot(filtered_data)
    except ValueError:
        pass

def load_file():
    global data, columns
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        data = pd.read_csv(file_path, delimiter=',')
        data['Time'] = pd.to_datetime(data['Time Stamp'])
        start_time = data['Time'].min()
        data['Time_from_start'] = data['Time'].apply(lambda x: convert_time_from_start(start_time, x))

        columns = data.columns.tolist()
        columns.insert(0, 'Select a variable')

        update_dropdowns()
        update_plot(data)

def convert_time_from_start(start_time, current_time):
    time_diff = current_time - start_time
    time_in_hours = time_diff.total_seconds() / 3600
    return time_in_hours

def _clear1():
    global plot1, plot1_2, plot1_3
    plot1.clear()
    if plot1_2:
        plot1_2.clear()
    if plot1_3:
        plot1_3.clear()
    time1.delete("1.0", tk.END)
    time2.delete("1.0", tk.END)
    canvas1.draw()
    selected_Y1.set(columns[0])
    selected_Y1_2.set(columns[0])
    selected_Y1_3.set(columns[0])
    window_text.delete("1.0", tk.END)

def on_close():
    root.destroy()
    exit()

def update_dropdowns():
    Y1_menu['menu'].delete(0, 'end')
    Y1_2_menu['menu'].delete(0, 'end')
    Y1_3_menu['menu'].delete(0, 'end')

    for column in columns:
        Y1_menu['menu'].add_command(label=column, command=tk._setit(selected_Y1, column, lambda _: update_plot(data)))
        Y1_2_menu['menu'].add_command(label=column, command=tk._setit(selected_Y1_2, column, lambda _: update_plot(data)))
        Y1_3_menu['menu'].add_command(label=column, command=tk._setit(selected_Y1_3, column, lambda _: update_plot(data)))

    selected_Y1.set(columns[0])
    selected_Y1_2.set(columns[0])
    selected_Y1_3.set(columns[0])



def make_slider():
    global slider, highlight1
    if 'slider' in globals() and slider:
        slider.ax.remove()
        slider = None
        highlight1.remove()
        canvas1.draw()
        return

    filtered_data = data[(data['Time_from_start'] >= float(time1.get("1.0", "end-1c"))) & (data['Time_from_start'] <= float(time2.get("1.0", "end-1c")))]
    y1_variable = selected_Y1.get()
    if y1_variable == 'Select a variable':
        return

    y1_data = filtered_data[y1_variable]
    slider_ax = plot1.figure.add_axes([0.25, 0.01, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(slider_ax, 'Position', 0, len(y1_data) - 50, valinit=0, valstep=1)

    def update(val):
        pos = int(slider.val)
        highlight1.set_data(filtered_data['Time_from_start'].iloc[pos:pos + 50], y1_data.iloc[pos:pos + 50])
        canvas1.draw()

    slider.on_changed(update)
    highlight1, = plot1.plot(filtered_data['Time_from_start'].iloc[:50], y1_data.iloc[:50], 'ro')
    canvas1.draw()




root = tk.Tk()
root.title("Strato Easy Plot")
root.geometry("1000x700")

style = ttk.Style()
style.theme_use('clam')

frame_main = ttk.Frame(root)
frame_main.pack(fill=tk.BOTH, expand=True)

frame_top = ttk.Frame(frame_main)
frame_top.pack(side=tk.TOP, fill=tk.X)

frame_bottom = ttk.Frame(frame_main)
frame_bottom.pack(side=tk.BOTTOM, fill=tk.X)

frame_plot = ttk.Frame(frame_main)
frame_plot.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

fig1 = Figure(figsize=(8, 4.5), dpi=100)
plot1 = fig1.add_subplot()
fig1.subplots_adjust(right=0.75)
plot1_2 = None
plot1_3 = None

canvas1 = FigureCanvasTkAgg(fig1, frame_plot)
canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

frame_controls = ttk.Frame(frame_bottom)
frame_controls.pack(side=tk.TOP, fill=tk.X)

frame_Ys_1 = ttk.Frame(frame_controls)
frame_Ys_1.grid(row=0, column=2, padx=10, pady=10)

label_Y1 = ttk.Label(frame_Ys_1, text="1st Y axis:")
label_Y1.grid(row=0, column=0, sticky="e")
selected_Y1 = tk.StringVar(frame_Ys_1)
selected_Y1.set('Select a variable')
Y1_menu = ttk.OptionMenu(frame_Ys_1, selected_Y1, 'Select a variable')
Y1_menu.grid(row=0, column=1)

frame_Ys_1_2 = ttk.Frame(frame_controls)
frame_Ys_1_2.grid(row=1, column=2, padx=10, pady=10)

label_Y1_2 = ttk.Label(frame_Ys_1_2, text="2nd Y axis:")
label_Y1_2.grid(row=0, column=0, sticky="e")
selected_Y1_2 = tk.StringVar(frame_Ys_1_2)
selected_Y1_2.set('Select a variable')
Y1_2_menu = ttk.OptionMenu(frame_Ys_1_2, selected_Y1_2, 'Select a variable')
Y1_2_menu.grid(row=0, column=1)

frame_Ys_1_3 = ttk.Frame(frame_controls)
frame_Ys_1_3.grid(row=2, column=2, padx=10, pady=10)

label_Y1_3 = ttk.Label(frame_Ys_1_3, text="3rd Y axis:")
label_Y1_3.grid(row=0, column=0, sticky="e")
selected_Y1_3 = tk.StringVar(frame_Ys_1_3)
selected_Y1_3.set('Select a variable')
Y1_3_menu = ttk.OptionMenu(frame_Ys_1_3, selected_Y1_3, 'Select a variable')
Y1_3_menu.grid(row=0, column=1)

label_time1 = ttk.Label(frame_controls, text="Time lower limit (h):", font=('Sans-serif', 12))
label_time1.grid(row=0, column=0, padx=10, pady=5)
time1 = Text(frame_controls, height=1, width=8, font=('Sans-serif', 12))
time1.grid(row=0, column=1, padx=10, pady=5)
time1.bind("<KeyRelease>", on_time_change)

label_time2 = ttk.Label(frame_controls, text="Time upper limit (h):", font=('Sans-serif', 12))
label_time2.grid(row=1, column=0, padx=10, pady=5)
time2 = Text(frame_controls, height=1, width=8, font=('Sans-serif', 12))
time2.grid(row=1, column=1, padx=10, pady=5)
time2.bind("<KeyRelease>", on_time_change)

stat_label = ttk.Label(frame_controls, text="Choose Statistics:", font=('Sans-serif', 12))
stat_label.grid(row=0, column=3, padx=10, pady=5)
selected_stat = tk.StringVar(frame_controls)
selected_stat.set('Select a Statistic')
stat_menu = ttk.OptionMenu(frame_controls, selected_stat, 'Select a Statistic', 'RMSE', 'Rolling Mean', 'Rolling Standard Deviation', 'Relative Standard Deviation')
stat_menu.grid(row=0, column=4)

window_label = ttk.Label(frame_controls, text="Window (s):", font=('Sans-serif', 12))
window_label.grid(row=0, column=5, padx=10, pady=5)
window_text = Text(frame_controls, height=1, width=5, font=('Sans-serif', 12))
window_text.grid(row=0, column=6, padx=10, pady=5)

var0 = tk.StringVar()
plot_stat_button = ttk.Checkbutton(frame_controls, text='Plot Stat', variable=var0, onvalue='On', offvalue='Off', command=selected_stat_func)
plot_stat_button.grid(row=0, column=7, padx=10, pady=5)

var1 = tk.StringVar()
slider_button = ttk.Checkbutton(frame_controls, text='Slider', variable=var1, onvalue='On', offvalue='Off', command=make_slider)
slider_button.grid(row=0, column=8, padx=10, pady=5)

clear_button = ttk.Button(frame_controls, text="Clear", command=_clear1)
clear_button.grid(row=6, column=1, padx=10, pady=5)

load_button = ttk.Button(frame_controls, text="Load File", command=load_file)
load_button.grid(row=6, column=2, padx=10, pady=5)

guide_label = ttk.Label(frame_controls, text="", font=('Sans-serif', 12))
guide_label.grid(row=7, column=0, columnspan=4, padx=10, pady=5)

def guide():
    if guide_label.cget("text"):
        guide_label.config(text="")
    else:
        guide_text = (
            "- Load RAW Aeris Data file\n"
            "- To use statistics button, enter time and window for rolling stats\n"
            "- When statistics is shown, dotted line is rolling mean,\n"
            "  Half Transparent line is uncertainty of plotted values, \n"
            "  made with rolling_mean and rolling_std.dev"
        )
        guide_label.config(text=guide_text)

guide_button = ttk.Button(frame_controls, text="?", command=guide)
guide_button.grid(row=6, column=0, padx=10, pady=5)

signature_label = ttk.Label(frame_controls, text="By : Tristan Gayrard 👍😎", font=('Sans-serif', 12))
signature_label.grid(row=7, column=0, sticky="e")

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()