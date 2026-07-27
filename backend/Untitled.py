import math
from PySide import QtWidgets 


class Circle:
    def calculate(self, radius):
        if radius <0:
            return 0
        else:
            pass
        area=math.pi * radius ** 2
        perimeter=math.pi * radius * 2
        print("Area of Circle:", area)
        print("Perimeter of Circle:", perimeter)
        return area, perimeter


calulator = Circle()
radius = float(input("Enter the radius of the circle: "))
calulator.calculate(radius)

    
