import pandas as pd

def check_weight_error(weights):
    """
    Check if the sum of the weights is approximately equal to 1.

    Parameters:
    - weights: dict, dictionary containing asset weights

    Returns:
    - float: sum of the weights
    """
    total_weight = 0
    for key in weights:
        total_weight += weights[key]
    
    total_weight = round(total_weight, 6)
    if total_weight == 1:
        print('Nice allocation')
    else:
        print('Wrong Calculating :(')
        print(f'Sum of given weights is: {total_weight}')
    return total_weight


def check_duplicate_indices(data: pd.DataFrame):
    """
    Check for duplicate indices in the DataFrame.

    Parameters:
    - data: pd.DataFrame, input DataFrame

    Returns:
    - None
    """
    # Check for duplicate indices
    duplicate_indices = data.index.duplicated().any()
    num_of_duplicate = data.index.duplicated().sum()
    if duplicate_indices:
        print(f"{num_of_duplicate} Duplicate indices exist.")
        print("Check out with .index.duplicated() function")
    else:
        print("No duplicate indices.")
