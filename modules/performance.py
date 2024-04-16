import pandas as pd
import numpy as np
import warnings

def calculate_cagr(Total_value: pd.Series) -> float:
    """
    Calculate the Compound Annual Growth Rate (CAGR).

    :param Total_value: Series of total value over a period of time.
    :return: The CAGR.
    """
    # Check if the input is a pandas Series
    if not isinstance(Total_value, pd.Series):
        warnings.warn("Input data is not a pandas Series. Please provide a valid pandas Series.", Warning)
        return None

    # Calculate the total return over the investment period
    total_return = (Total_value.iloc[-1] - Total_value.iloc[0]) / Total_value.iloc[0]
    
    # Calculate the number of trading days
    days = len(Total_value)
    years = days / 252

    # Calculate the CAGR
    cagr = (1 + total_return) ** (1 / years) - 1
    
    return cagr


def calculate_mdd(total_value: pd.Series) -> tuple: 
    """
    Calculate the Maximum Drawdown (MDD) from a Series of total value.

    :param total_value: Series of value over a period of time.
    :return: Tuple containing MDD value, MDD period informations
    """
 
    mdd = 0  # Initialize MDD to 0
    peak_idx = 0  # Initialize peak and trough values
    peak = 1
    
    for idx, values in enumerate(total_value):
        if values > total_value[peak_idx]:
            peak_idx = idx
            peak = values
        
        drawdown = (values - peak) / peak  # Calculate drawdown
        
        if drawdown < mdd:
            mdd = drawdown
            past_peak_idx = peak_idx
            past_peak = peak
            past_peak_time = total_value.index[past_peak_idx]

            trough_idx = idx
            trough = values
            trough_time = total_value.index[trough_idx]
    return mdd, past_peak, past_peak_time, trough, trough_time

def calculate_sharpe_ratio(returns: pd.Series, df_rf: pd.DataFrame) -> list:
    """
    Calculate the Sharpe Ratio for each annual period.

    :param returns: Series of portfolio returns.
    :param df_rf: DataFrame containing risk-free rate of return data.
    :return: List of tuples containing start date, end date, and Sharpe Ratio for each annual period.
    """
    # Calculate the number of complete annual periods
    count = (len(returns) // 252)
    sharpe_lst = []  # Initialize list to store Sharpe Ratios for each period
    
    # Iterate over each annual period
    for i in range(1, count + 2):
        
        # Extract returns data for the current annual period
        annual = returns.iloc[252 * (i - 1):252 * i]
        
        # Calculate annualized return and standard deviation
        annual_ret = annual.mean() * 252
        annual_std = annual.std() * np.sqrt(252)
        
        # Determine the start and end dates of the current annual period
        start, end = annual.index[0], annual.index[-1]
        
        # Extract risk-free rate of return data for the current annual period
        annual_rf = df_rf['Close'].loc[start:end]
        
        # Calculate the average risk-free rate of return for the current annual period
        annual_rf = annual_rf.mean()
        
        # Calculate the Sharpe Ratio for the current annual period
        sharpe_ratio = (annual_ret - annual_rf) / annual_std
        
        # Store the start date, end date, and Sharpe Ratio for the current annual period in a tuple
        sharpe_lst.append((start, end, sharpe_ratio))
        
    return sharpe_lst
