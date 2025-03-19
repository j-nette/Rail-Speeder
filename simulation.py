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
        self.status = c.sim_status.COMPLETE

        # Start sim

        for element in stage:
            if self.isComplete == True: 
                print(self.time_points[-1])
                self.status = c.sim_status.TIMEOUT
                logging.error('Maximum Round Time Exceeded.')
                break
            elif start_time > c.timeout+start_time:
                self.status = c.sim_status.RUNTIME
                logging.error("Timeout - Simulation took too long to run")
                break
            else:
                failed = element['func'](element['params'])
                
                # Check for cart going backwards
                if failed:
                    self.status = c.sim_status.SLIP
                    logging.error("Cart rolled backwards past threshold. Stopping simulation")
                    break
                
          
        logging.info('Simulation Complete')

        return {
            'status': self.status,
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
        
        # TODO: Determine vehicle coefficients
        mu_vehicle = 0.05
        mu_vehicle_roll = 0.5
        
        # From tests, mu_cart was between 0.0359 and 0.06157
        mu_cart = 0.05 # TODO: From cart tests
        mu_cart_roll = 0.01
        
        phi = p['hitch_ang'] # deg
        phi_rad = phi*math.pi/180
        area_f = (p['width'] * c.min_height) * 100**-2 # m^2
        mass_total = self.vehicle.totalWeight(p['v_mass'], p['c_mass'], p['carts'])
        b = p['cog_y'] # cm
        d = p['hitch'] # cm
            
        v0 = self.velocity_points[-1]
   
        omega_wheel = v0 / ( p['radius'] / 100) 
        omega_motor = omega_wheel * p['ratio']

        # Calculate motor efficiency
        torque_motor = max(c.Motor.torque_s-c.Motor.k*max(omega_motor,0), 0) # Motor provides no torque when spinning above its rated RPM
        
        torque_axel = p['ratio'] * torque_motor * p['t_eff']
        thrust = torque_axel/(p['radius']/100)

        # Calculate cart forces
        f_cart_air = 1*0.5*c.rho*v0**2*area_f #*p['carts']
        f_cart_int = 9.81*self.vehicle.totalWeight(0, p['c_mass'], p['carts'])*mu_cart*p['carts']*(mu_cart+mu_cart_roll*v0**2)
        # TODO: Double check if v or v^2
        
        tension = 1/math.cos(phi_rad)*(f_cart_air+f_cart_int)

        # Calculate vehicle forces
        f_v_air = 1*1/2*c.rho*v0**2*area_f
        f_v_int = c.g*(mu_vehicle+mu_vehicle_roll*v0**2)*mass_total

        # Calculate vehicle normals
        norm_front = ( mass_total*9.81*(p['length'] - p['cog'])*math.cos(deg*math.pi/180) - (f_v_air+f_v_int)*b + tension*math.cos(phi_rad)/(b+d) ) / p['length']
        norm_back = mass_total*9.81 + tension*math.sin(phi_rad) - norm_front

        friction_b = norm_back*p['cof']
        friction_f = norm_front*p['cof_f']
        gravity = mass_total*9.81*math.sin(deg*math.pi/180)
        
        # Check for slip
        if (p['awd']):
          f_total = friction_b + friction_f
          actual_thrust = f_total if (p['motors']*thrust > f_total) else p['motors']*thrust
        else:
          actual_thrust = friction_b if (p['motors']*thrust > friction_b) else p['motors']*thrust

        f_t = actual_thrust - f_v_air - f_v_int - gravity - tension*math.cos(phi_rad)

        # Calculate step variables
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
        x0 = self.position_points[-1]
        isFailed = False

        while x - x0 < length and not self.isComplete:
            x = self.step(x,deg)

            if max(self.position_points) - x > c.slip_threshold:
                isFailed = True
                break

        self.checkpoint()
        return isFailed
    
    def hill(self, params): #assuming no radius at top or bottom
        height = params['height']
        length = params['length']
        deg = math.atan(height/(length/2))

        length_slope = length/math.cos(deg*math.pi/180)

        x = self.position_points[-1]
        x0 = self.position_points[-1]
        isFailed = False

        while x - x0 < length_slope/2:
            x = self.step(x,deg)
        
        while x < length_slope:
            x = self.step(x,-deg)
        

        self.checkpoint()
        return isFailed
    
    def curve(self, params): #check later, need centripetal accel
        radius = params['curve_radius']
        deg = params['angle']

        x = self.position_points[-1]
        x0 = self.position_points[-1]
        isFailed = False

        while x - x0 < deg*math.pi/180*radius:
            x = self.step(x, 0, True)
        
        self.checkpoint()
        return isFailed
    
    
    def checkpoint(self, params = None): #note times of section ends & gates
        t = self.time_points[-1]
        self.check_points.append(t)

        return False