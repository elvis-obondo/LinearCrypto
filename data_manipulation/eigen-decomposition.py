import numpy as np
from covariance_matrix import main
import pprint

correlation_list= main()

def get_eigendata(correlation_list):
    eigenvalues,eigenvectors = np.linalg.eig(correlation_list)
    return eigenvalues,eigenvectors

if __name__ == "__main__":
    get_eigendata(correlation_list)


