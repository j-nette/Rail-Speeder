import math

g = 9.81
max_time = 5 # [min]
dt = 1 # [s]
rho = 1.2


class Cargo:
    carts = 4 # number of carts
    mass = 100 # [g]

class Motor:
    speed_nl = 10679
    torque_s = 0.01729
    k = torque_s/(speed_nl/60*2*math.pi)
    




