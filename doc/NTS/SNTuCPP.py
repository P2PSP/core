from functools import reduce
from math import ceil

MAX_PREDICTED_PORTS = 20
peer_number = 3
max_port_step = 10
splitter_port = 0

def get_divisors(n):
    return sorted(set(reduce(list.__add__, ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0))))

def count_product_combinations(factors):
    return reduce(lambda a, b: a + b, factors)

def get_guessed_ports(peer_number, max_port_step, splitter_port):
    divisors = get_divisors(max_port_step)
    num_combinations = count_product_combinations(divisors)
    count_factor = MAX_PREDICTED_PORTS/float(num_combinations)
    return sorted(set(reduce(list.__add__, (list(
        splitter_port + (peer_number + skips) * port_step
        for skips in range(int(ceil(max_port_step/port_step*count_factor))+1))
        for port_step in divisors))))

print(get_guessed_ports(peer_number, max_port_step, splitter_port))
