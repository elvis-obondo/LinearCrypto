from log_returns import get_market_data
import numpy as np

correlation_list = []

def main():
    sol_data,kmno_data=get_market_data()
    max_lag = 4
    for i in range(max_lag+1):
        combined_matrix = np.vstack([sol_data[i:],kmno_data[:None if i==0 else -i]])
        correlation_matrix = np.corrcoef(combined_matrix)
        correlation_list.append(correlation_matrix)
    
    print(f"Successfully done correlation matrix")
    return correlation_list
    


if __name__ == "__main__":
    main()
    

