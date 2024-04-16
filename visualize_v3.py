from matplotlib.ticker import FuncFormatter
import pandas as pd
import matplotlib.pyplot as plt

def visualize(*additional_returns):
    plt.figure(figsize=(20, 5))
    
    # Define colors and labels for additional datasets
    colors = ['red', 'blue', 'green', 'c', 'm', 'black', 'k']  # 'r' is reserved for port_return
    labels = ['Data1', 'Data2', 'Data3', 'Data4', 'Data5', 'Data6','Data7']

    # Container for all returns to find global min and max for y-axis scaling later
    all_returns = list(additional_returns)

    for i, dataset in enumerate(all_returns):
        color = colors[i]
        label = labels[i]
        
        # Plot the cumulative returns
        plt.plot(dataset.index, dataset['Cum_return'], color=color, alpha=0.8, label=label)
        
        # Find and mark the min and max points
        min_point = dataset['Cum_return'].idxmin()
        max_point = dataset['Cum_return'].idxmax()
        min_val = dataset['Cum_return'].min()
        max_val = dataset['Cum_return'].max()

        # Add shaded regions for min and max points
        plt.axvline(x=min_point, color=color, alpha=0.3, linewidth=3)
        plt.axvline(x=max_point, color=color, alpha=0.3, linewidth=3)

        # Mark the min, max, and end points
        plt.scatter([min_point, max_point], 
                    [min_val, max_val], color=color, zorder=2)

        # Annotate the [min, max, end] points
        plt.annotate(f'{min_val:.1%}', (min_point, min_val),
                        textcoords="offset points", xytext=(0,-10), ha='center', fontsize=8)
        plt.annotate(f'{max_val:.1%}', (max_point, max_val),
                        textcoords="offset points", xytext=(10,15), ha='center', fontsize=14)
        
         # Rolling window to check for the drop of more than 20%
        # rolling_min = dataset['Cum_return'].rolling(window=121, min_periods=1).min()
        # # 기록사항 : rolling min으로 진행하면, 정확하게 언제부터 언제까지 drop 하게 된건지 로직을 강화해줘야하ㅑㅁ
        # # Identify the periods with a drop greater than 20%
        # significant_drops = rolling_min[rolling_min <= -0.20]

        # for drop_date in significant_drops.index:
        #     # Highlight the period of the significant drop
        #     start_from = dataset.loc[drop_date-pd.Timedelta(days=121):drop_date,'Cum_return'].idxmax()
        #     plt.axvspan(start_from, drop_date, color=color, alpha=0.1, linewidth=0)

    # Set y-axis to percentage format
    formatter = FuncFormatter(lambda y, _: f'{y:.0%}')
    plt.gca().yaxis.set_major_formatter(formatter)

    # Determine the global min and max for y-axis scaling
    max_val = max([data['Cum_return'].max() for data in all_returns]) + 0.2
    min_val = min([data['Cum_return'].min() for data in all_returns]) - 0.2
    
    plt.ylim(min_val, max_val)

    # Add grid, labels, and title
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.title('Portfolio Cumulative Returns')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    
    plt.show()
