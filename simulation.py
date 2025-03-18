import constants as c
from structures import Vehicle

import math
import logging

import time

class Simulation():
    isComplete = False
    vehicle = Vehicle()

    time_points = [0]
    position_points = [0]
    velocity_points = [0]
    acceleration_points = [0]
    check_points = [0]
    motor_points = [0]

    def __init__(self):
        return

    def start(self, param, stage): 
    

        # Setup stuff
        global p
        p = param

        start_time = time.time()

        self.time_points = [0]
        self.position_points = [0]
        self.velocity_points = [0]
        self.acceleration_points = [0]
        self.check_points = [0]
        self.motor_points = [0]

        self.isComplete = False

        # Start sim

        for element in stage:
            if self.isComplete == True: 
                print(self.time_points[-1])
                logging.error('Maximum Round Time Exceeded.')
                break
            elif start_time > c.timeout+start_time:
                logging.error("Timeout - Simulation took too long to run")
            else:
                element['func'](element['params'])
                
                # Check for cart going backwards
                
                if not len(self.position_points) == 1:
                    if self.position_points[-1] < self.position_points[-2]:
                        logging.error("Cart rolled backwards. Stopping simulation")
                        break



            
        logging.info('Simulation Complete')

        return {
            'time': self.time_points,
            'position': self.position_points,
            'velocity': self.velocity_points,
            'acceleration': self.acceleration_points,
            'checkpoints': self.check_points,
            'motorpower': self.motor_points
        }
        
    def step(self, x0, deg, isCurve = False):
        if self.time_points[-1] > c.max_time*60:
            self.isComplete = True
            return -1
        
        phi = 5 # deg
        phi_rad = phi*math.pi/180
        area_f = 0.1 # m^2
        mass_total = self.vehicle.totalWeight(p['v_mass'], p['c_mass'], p['carts'])
        mu_cart = 0.5 # TODO: From cart tests
        b = 5 # cm
        d = 2 # cm
            
        v0 = self.velocity_points[-1]
   
        omega_wheel = v0 / ( p['radius'] / 100) 
        omega_motor = omega_wheel * p['ratio']

        # Calculate motor efficiency
        torque_motor = (c.Motor.torque_s-c.Motor.k*omega_motor)
        
        torque_axel =p['ratio'] * torque_motor * p['t_eff']
        thrust = torque_axel/(p['radius']/100)

        # Calculate cart forces
        f_cart_air = 1*0.5*c.rho*v0**2*area_f #*p['carts']
        f_cart_int = 9.81*self.vehicle.totalWeight(0, p['c_mass'], p['carts'])*mu_cart*p['carts']
        
        tension = 1/math.cos(phi_rad)*(f_cart_air+f_cart_int)

        # Calculate vehicle forces
        f_v_air = 1*1/2*c.rho*v0**2*area_f
        f_v_int = c.g*(0.001+0.5*v0**2)*mass_total # TODO: determine vehicle coefficients?

        # Calculate vehicle normals
        norm_front = ( mass_total*9.81*(p['length'] - p['cog']) - (f_v_air+f_v_int)*b + tension*math.cos(phi_rad)/(b+d) ) / p['length']
        norm_back = mass_total*9.81 + tension*math.sin(phi_rad) - norm_front

        friction_s = norm_back*p['cof']
        gravity = mass_total*9.81*math.sin(deg*math.pi/180)
        
        # Check for slip
        actual_thrust = friction_s if (thrust > friction_s) else thrust

        f_t = actual_thrust - f_v_air - f_v_int - gravity - tension*math.cos(phi_rad)


        a = f_t/mass_total

        t = self.time_points[-1] + c.dt
        v = v0 + a*c.dt 
        x = x0 + v0*c.dt+1/2*a*c.dt**2

        # Calculate motor power
        power = max((torque_motor/c.Motor.torque_s)*100,0)

        # Update lists
        self.time_points.append(t)
        self.position_points.append(x)
        self.velocity_points.append(v)
        self.acceleration_points.append(a)
        self.motor_points.append(power)

        return x

    
    def straight(self, params):
        deg = params['incline']
        length = params['length']/math.cos(deg*math.pi/180)

        x = self.position_points[-1]
        x0 = 0

        while x < length+self.position_points[-1] and not self.isComplete:
            x = self.step(x0,deg)
            x0 = x

            if x < 0:
                logging.error('Simulation failed: x<0')
                break

        self.checkpoint()
        return
    
    def hill(self, params): #assuming no radius at top or bottom
        height = params['height']
        length = params['length']
        deg = math.atan(height/(length/2))

        length_slope = length/math.cos(deg*math.pi/180)

        x = 0
        x0 = 0

        while x < length_slope/2:
            x = self.step(x0,deg)
            x0 = x
        
        while x < length_slope:
            x= self.step(x0,-deg)
            x0 = x
        

        self.checkpoint()
        return
    
    def curve(self, params): #check later, need centripetal accel
        radius = params['curve_radius']
        deg = params['angle']

        x = 0
        x0 = 0

        while x < deg*math.pi/180*radius:
            x = self.step(x0, 0, True)
            x0 = x
        
        self.checkpoint()
        return
    
    
    def checkpoint(self, params = None): #note times of section ends & gates
        t = self.time_points[-1]
        self.check_points.append(t)

        print(t)
        return 


    

    