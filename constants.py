import math

g = 9.81
max_time = 1 # [min]
dt = 0.01/10 # [s]
rho = 1.2

curve_eff = 0.7
straight_eff = 0.5

curve_accel = 0.1

max_torque = 8.647/1000



class Cargo:
    cart_mass = 0.5 # [kg]


class Motor:
    speed_nl = 10679
    torque_s = 0.01729
    k = torque_s/(speed_nl/60*2*math.pi)

    




