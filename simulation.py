import constants as c
from structures import Vehicle

import math
import numpy as np

class Simulation():
    vehicle = Vehicle()

    def __init__(self):
        self.time_points = [0]
        self.position_points = [0]
        self.velocity_points = [0]
        self.acceleration_points = [0]

    def start(self):      
        t = 0 
        isComplete = False

        # track stuff?

        self.straight(0,10)

        isComplete = True # add this as a condition to break out of time loop later

        #

        if isComplete is True:
            print('Simulation Complete')

            # print(self.time_points)
            # print(self.position_points)
            # print(self.velocity_points)
            # print(self.acceleration_points)

            return {
                'time': self.time_points,
                'position': self.position_points,
                'velocity': self.velocity_points,
                'acceleration': self.acceleration_points
            }
        
        

    def step(self, x0, v0, deg):
        omega_wheel = v0/self.vehicle.wheel_radius/100
        omega_motor = omega_wheel * self.vehicle.gear_ratio

        torque_motor = c.Motor.torque_s-c.Motor.k*omega_motor
        torque_axel = self.vehicle.gear_ratio*torque_motor*Vehicle.efficiency


        # Calculating Forces
        drag_cart = -c.g*(0.005+0.001*v0)*self.vehicle.totalWeight()*(1+c.Cargo.carts)
        drag_air = -1/2*c.rho*v0*0.1*1
        gravity = -9.81*self.vehicle.totalWeight()
        thrust = torque_axel/(self.vehicle.wheel_radius/100)
        normal_front = self.vehicle.mass/1000*c.g*math.cos(deg)*(self.vehicle.length-self.vehicle.cog)/(self.vehicle.front_wheel*self.vehicle.length)
        normal_back = (self.vehicle.mass/1000*c.g*math.cos(deg)-self.vehicle.front_wheel*normal_front)/self.vehicle.back_wheel
        friction_s = normal_back*self.vehicle.cof*self.vehicle.back_wheel

        # Slip
        actual_thrust = friction_s if (thrust > friction_s) else thrust

        # Take forward & up as positive
        f_net = drag_cart + drag_air + actual_thrust

        a = f_net/self.vehicle.totalWeight()
        t = self.time_points[-1] + c.dt
        v = v0 + a*c.dt
        x = x0 + v0*c.dt+1/2*a*c.dt**2


        # Update lists
        self.time_points.append(t)
        self.position_points.append(x)
        self.velocity_points.append(v)
        self.acceleration_points.append(a)

        return [x, v]
    
    def straight(self, v0, length):
        x = 0
        x0 = 0

        while x < length:
            [x, v] = self.step(x0,v0,0)
            x0 = x
            v0 = v
            
        return
    


# Start Simulation 
sim = Simulation()    
print(sim.start())

