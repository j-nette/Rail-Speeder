import constants as c
from structures import Vehicle

import math
import logging

class Simulation():
    isComplete = False
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

        self.isComplete = False

        # testing purposes
        stage = [{'func': self.straight, "params": { "length": 10, "incline": 0 }}]

        for element in stage:
            if self.isComplete == True: break
            else:
                element['func'](element['params'])
            
        logging.info('Simulation Complete')

        return {
            'time': self.time_points,
            'position': self.position_points,
            'velocity': self.velocity_points,
            'acceleration': self.acceleration_points,
            'checkpoints': self.check_points,
            'motorpower': self.motor_points
        }
        

    def step(self, x0, deg):
        v0 = self.velocity_points[-1]

        omega_wheel = v0 / ( p['radius'] / 100) 
        omega_motor = omega_wheel * p['ratio']

        torque_motor = c.Motor.torque_s-c.Motor.k*omega_motor
        torque_axel =p['ratio'] * torque_motor * p['t_eff']
        
        # Calculating Forces
        drag_cart = -c.g*(0.005+0.001*v0)*self.vehicle.totalWeight(p['v_mass'], p['c_mass'], p['carts'])
        drag_air = -1/2*c.rho*v0*0.1*1

        gravity_n = -9.81*self.vehicle.totalWeight(p['v_mass'], p['c_mass'], p['carts'])*math.cos(deg*math.pi/180)
        gravity_t = -9.81*self.vehicle.totalWeight(p['v_mass'], p['c_mass'], p['carts'])*math.sin(deg*math.pi/180)

        thrust = torque_axel/(p['radius']/100)

        normal_front = p['v_mass']*c.g*math.cos(deg*math.pi/180)*(p['length'] - p['cog'])/(self.vehicle.front_wheel*p['length'])
        normal_back = (p['v_mass']*c.g*math.cos(deg*math.pi/180)-self.vehicle.front_wheel*normal_front)/self.vehicle.back_wheel
        friction_s = normal_back*p['cof']*self.vehicle.back_wheel

        # Check for slip
        actual_thrust = friction_s if (thrust > friction_s) else thrust

        # take forward & up as positive
        f_t = drag_cart + drag_air + actual_thrust
        f_n = gravity_n + normal_back + normal_front

        a_t= f_t/self.vehicle.totalWeight(p['v_mass'], p['c_mass'], p['carts'])
        a_n = f_n/self.vehicle.totalWeight(p['v_mass'], p['c_mass'], p['carts'])

        a = math.sqrt(a_t**2+a_n**2)

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

        return x

    
    def straight(self, params):
        deg = params['incline']
        length = params['length']

        x = 0
        x0 = 0

        while x < length:
            x = self.step(x0,deg)
            print(x)
            x0 = x

        self.checkpoint()
        return
    
    def hill(self, params): #assuming no radius at top or bottom
        height = params['height']
        length = params['length']

        x = 0
        x0 = 0

        deg = math.atan(height/(length/2))

        while x < length/2:
            x = self.step(x0,deg)
            x0 = x
        
        while x < length:
            x= self.step(x0,-deg)
            x0 = x
        

        self.checkpoint()
        return
    
    def curve(self, params): #check later, need centripetal accel
        radius = params['radius']
        deg = params['deg']

        x = 0
        x0 = 0

        while x < deg*math.pi/180*radius:
            x = self.step(x0)
            x0 = x
        
        self.checkpoint()
        return
    
    
    def checkpoint(self, params = None): #note times of section ends & gates
        t = self.time_points[-1]
        self.check_points.append(t)
        return 


    

    