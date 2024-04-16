from matplotlib.ticker import FuncFormatter
import pandas as pd
import matplotlib.pyplot as plt

def visualize(port_return, bench_return):
    
    # Find the min and max points
    min_point = port_return['Cum_return'].idxmin()
    max_point = port_return['Cum_return'].idxmax()
    end_point = port_return['Cum_return'].index[-1]
    min_val = port_return['Cum_return'].min()
    max_val = port_return['Cum_return'].max()
    end_val = port_return['Cum_return'][-1]
    
    min_point_bench = bench_return['Cum_return'].idxmin()
    max_point_bench = bench_return['Cum_return'].idxmax()
    end_point_bench = bench_return['Cum_return'].index[-1]
    min_val_bench = bench_return['Cum_return'].min()
    max_val_bench = bench_return['Cum_return'].max()
    end_val_bench = bench_return['Cum_return'][-1]

    # Set the y-axis to comparable sight
    max_y = max(max_val,max_val_bench)+0.2
    min_y = min(min_val,min_val_bench)-0.2

    # Plot the cumulative returns
    plt.figure(figsize=(20, 5))
    plt.plot(port_return.index, port_return['Cum_return'],color='r',label="Your Port.")
    plt.plot(bench_return.index, bench_return['Cum_return'],color='b',alpha=0.6, label="bench")

    # Add shaded regions for min and max points
    plt.axvspan(min_point, min_point, color='r', alpha=0.4, linewidth=3)
    plt.axvspan(max_point, max_point, color='r', alpha=0.4, linewidth=3)
    plt.axvspan(min_point_bench, min_point_bench, color='b', alpha=0.4, linewidth=3)
    plt.axvspan(max_point_bench, max_point_bench, color='b', alpha=0.4, linewidth=3)

    # Mark the min and max points
    plt.scatter([min_point, max_point,end_point], 
                [min_val, max_val,end_val], color='red', zorder=2)
    plt.scatter([min_point_bench, max_point_bench,end_point_bench], 
                [min_val_bench, max_val_bench,end_val_bench], color='blue', zorder=2)
    
    # Annotate the portfolio [min, max, end] points
    plt.annotate(f'{min_val:.1%}', (min_point, min_val),
                    textcoords="offset points", xytext=(0,-5), ha='center', fontsize=8)
    plt.annotate(f'{max_val:.1%}', (max_point, max_val),
                    textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)
    
    # Annotate the benchmark [min, max, end] points
    plt.annotate(f'{min_val_bench:.1%}', (min_point_bench, min_val_bench),
                    textcoords="offset points", xytext=(0,-10), ha='center', fontsize=8)
    plt.annotate(f'{max_val_bench:.1%}', (max_point_bench, max_val_bench),
                    textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)

    # Set y-axis to percentage format
    formatter = FuncFormatter(lambda y, _: f'{y:.0%}')
    plt.gca().yaxis.set_major_formatter(formatter)
    
    plt.ylim(min_y, max_y)

    # Add grid lines
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Set the title and labels
    plt.title('Portfolio Cumulative Returns')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')

    # Show the plot
    plt.legend()
    plt.show()