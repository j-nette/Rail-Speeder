import constants as c
from structures import Vehicle

import math
import logging

class Simulation():
    vehicle = Vehicle()

    def __init__(self):
        self.time_points = [0]
        self.position_points = [0]
        self.velocity_points = [0]
        self.acceleration_points = [0]
        self.check_points = [0]
        self.motor_points = [0]

    def start(self, param): 
        global p
        p = param

        isComplete = False

        # track stuff?

        self.straight(0,10,0)

        isComplete = True # add this as a condition to break out of time loop later

        #

        if isComplete is True:
            logging.info('Simulation Complete')

            return {
                'time': self.time_points,
                'position': self.position_points,
                'velocity': self.velocity_points,
                'acceleration': self.acceleration_points,
                'checkpoints': self.check_points,
                'motorpower': self.motor_points
            }
        

    def step(self, x0, v0, deg):
        
        omega_wheel = v0 / ( p['radius'] / 100) 
        omega_motor = omega_wheel * p['ratio']

        torque_motor = c.Motor.torque_s-c.Motor.k*omega_motor
        torque_axel =p['ratio'] * torque_motor * p['t_eff']
        
        # Calculating Forces
        drag_cart = -c.g*(0.005+0.001*v0)*self.vehicle.totalWeight(p['v_mass'], p['c_mass'], p['carts'])
        drag_air = -1/2*c.rho*v0*0.1*1
        gravity = 9.81*self.vehicle.totalWeight(p['v_mass'], p['c_mass'], p['carts'])
        thrust = torque_axel/(p['radius']/100)
        normal_front = p['v_mass']*c.g*math.cos(deg*math.pi/180)*(p['length'] - p['cog'])/(self.vehicle.front_wheel*p['length'])
        normal_back = (p['v_mass']*c.g*math.cos(deg*math.pi/180)-self.vehicle.front_wheel*normal_front)/self.vehicle.back_wheel
        friction_s = normal_back*p['cof']*self.vehicle.back_wheel

        # Slip
        actual_thrust = friction_s if (thrust > friction_s) else thrust

        # take forward & up as positive
        f_net = drag_cart + drag_air + actual_thrust

        a = f_net/self.vehicle.totalWeight(p['v_mass'], p['c_mass'], p['carts'])
        t = self.time_points[-1] + c.dt
        v = v0 + a*c.dt
        x = x0 + v0*c.dt+1/2*a*c.dt**2

        # Calculate motor power
        power = torque_motor/c.Motor.torque_s*100

        # Update lists
        self.time_points.append(t)
        self.position_points.append(x)
        self.velocity_points.append(v)
        self.acceleration_points.append(a)
        self.motor_points.append(power)

        return [x, v]

    
    def straight(self, v0, deg, length):
        x = 0
        x0 = 0

        while x < length:
            [x, v] = self.step(x0,v0,deg)
            x0 = x
            v0 = v

        self.checkpoint()
        return
    
    def hill(self, v0, height, length): #assuming no radius at top or bottom
        x = 0
        x0 = 0

        deg = math.atan(height/(length/2))

        while x < length/2:
            [x, v] = self.step(x0,v0,deg)
            x0 = x
            v0 = v
    
        while x < length:
            [x, v] = self.step(x0,v0,-deg)
            x0 = x
            v0 = v

        self.checkpoint()
        return
    
    def curve(self, v0, radius, deg): #check later
        x = 0
        x0 = 0

        while x < deg*math.pi/180*radius:
            [x, v] = self.step(x0,v0)
            x0 = x
            v0 = v
        
        self.checkpoint()
        return
    
    
    def checkpoint(self):
        t = self.time_points[-1]
        self.check_points.append(t)

        return 

    

    