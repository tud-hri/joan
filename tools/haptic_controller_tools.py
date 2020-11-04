import numpy as np

def check_equal(lst):
    return lst[1:] == lst[:-1]


def find_closest_node(node, nodes):
    """
    Find the node in the nodes list (trajectory)
    """
    nodes = np.asarray(nodes)
    deltas = nodes - node
    dist_squared = np.einsum('ij,ij->i', deltas, deltas)
    return np.argmin(dist_squared)