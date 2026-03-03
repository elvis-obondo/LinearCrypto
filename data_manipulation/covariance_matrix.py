from log_returns import get_market_data
import numpy as np

correlation_list = []

def main():
    sol_data,kmno_data=get_market_data()
    
    
    combined_matrix = np.vstack([sol_data,kmno_data])
    correlation_matrix = np.corrcoef(combined_matrix)
    correlation_list.append(correlation_matrix)
    
   
    return correlation_list
    


if __name__ == "__main__":
    main()
    

