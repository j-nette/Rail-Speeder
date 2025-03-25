import constants as c
    
class Vehicle():
    cof = 1.2    
    front_wheel = 4 # number of wheels
    back_wheel = 2 # number of wheels

    def __init__(self):
        return
    
    def totalWeight(self, v_mass, c_mass, carts):
         return (v_mass + c.Cargo.cart_mass * carts + c_mass)