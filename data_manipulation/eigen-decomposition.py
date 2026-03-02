import numpy as np
from covariance_matrix import main
import pprint
correlation_list= main()
i=0
for cmatrix in correlation_list:

    eigenvalues,eigenvectors = np.linalg.eig(cmatrix)
    print(f"correlation matrix {i}:")
    pprint.pprint(cmatrix)
    print("Eigenvalues")
    pprint.pprint(eigenvalues)
    print("Eigenvectors")
    pprint.pprint(eigenvectors)
    i+=1