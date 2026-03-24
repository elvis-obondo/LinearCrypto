from log_returns import get_market_data
import numpy as np
import pprint

# TODO Demean the returns and standardize them so the variance/risk is 1
# TODO Also use log prices...
# TODO Get proper correlation matrix. By multiplying the 
# massive 8000x33 matrix by its transpose to get a 33x33 matrix that we then get the correlation matrix from
# Gives us the correlation of each of the 33 coins to each other
def main():
    combined_matrix=get_market_data()
    correlation_matrix = np.corrcoef(combined_matrix)
    eigendata = np.linalg.eig(correlation_matrix)
    return eigendata
    
eigendata = main()
pprint.pprint(eigendata[0])
pprint.pprint(eigendata[-1])

if __name__ == "__main__":
    main()
    

