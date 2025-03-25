import math

g = 9.81
max_time = 2 # [min]
dt = 0.01 # [s]
rho = 1.2

max_torque = 8.647/1000

min_height = 7 #cm

timeout = 10
slip_threshold = 0.1 #m


class Cargo:
    cart_mass = 0.5 # [kg]


class Motor:
    speed_nl = 10679
    torque_s = 0.01729
    k = torque_s/(speed_nl/60*2*math.pi)

# Unused   
class sim_status:
    COMPLETE = 0
    TIMEOUT = 1
    SLIP = 2
    RUNTIME = 3