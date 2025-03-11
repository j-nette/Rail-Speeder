import constants as c
    
class Vehicle():
    mass = 100 # [g]
    cof = 1.2    
    wheel_radius = 5 # [cm]
    cog = 19 # [cm] from front
    width = 3 # [cm]
    length = 20 # [cm]
    front_wheel = 4 # number of wheels
    back_wheel = 2 # number of wheels
    gear_ratio = 200
    efficiency = 1 # [%] transmission efficiency

    def __init__(self):
        return
    
    def totalWeight(self):
        return (self.mass + c.Cargo.mass)/1000