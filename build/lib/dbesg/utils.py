import numpy as np

def annually_to_continously(r):
    """
        Description
        -----------
        연단위금리를 연속단위금리로 변환
    """

    return np.log(1+r)

def continuously_to_annually(r):
    """
        Description
        -----------
        연속단위금리를 연단위금리로 변환
    """
    
    return np.exp(r)-1