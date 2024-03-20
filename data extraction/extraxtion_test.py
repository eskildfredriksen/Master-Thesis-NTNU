import ifcopenshell
import ifcopenshell.util.unit as unit
from ifcopenshell.util.selector import Selector

ifc_file = ifcopenshell.open(r'c:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\IFC\Tennebekk\22018_TennebekkBuss_RIB.ifc')

walls = ifc_file.by_type('IfcWall')




products = ifc_file.by_type('IfcProduct')

elements = []

for product in products:
    id = product.is_a()
    if id in elements:
        None
    else:
        elements.append(id)

print(elements)


#----------------------
import ifcopenshell
import ifcopenshell.util.unit as unit
from ifcopenshell.util.selector import Selector

ifc_file = ifcopenshell.open(r'c:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\IFC\Tennebekk\22018_TennebekkBuss_RIB.ifc')

walls = ifc_file.by_type('IfcWall')




products = ifc_file.by_type('IfcProduct')

elements = []

for product in products:
    id = product.is_a()
    if id in elements:
        None
    else:
        elements.append(id)

print(elements)


#-----------------
import ifcopenshell
import ifcopenshell.util.unit as unit
from ifcopenshell.util.selector import Selector

ifc_file = ifcopenshell.open(r'c:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\IFC\Tennebekk\22018_TennebekkBuss_RIB.ifc')

walls = ifc_file.by_type('IfcWall')




products = ifc_file.by_type('IfcProduct')

elements = []

for product in products:
    id = product.is_a()
    if id in elements:
        None
    else:
        elements.append(id)

print(elements)


#-------
import ifcopenshell 
ifc = ifcopenshell.open(r'c:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\IFC\Tennebekk\22018_TennebekkBuss_RIB.ifc')

walls = ifc.by_type('IfcWall')

wall = ifc.by_type('IfcWall')[0]
print(wall.is_a()) # Returns 'IfcWall'

print(wall.is_a('IfcWall')) # Returns True
print(wall.is_a('IfcElement')) # Returns True
print(wall.is_a('IfcWindow')) # Returns False

print(wall.id())

print(wall[0]) # The first attribute is the GlobalId
print(wall[2]) # The third attribute is the Name

#Knowing the order of attributes is boring and technical. We can access them by name too:

print(wall.GlobalId)
print(wall.Name)

print(wall.get_info()) # Gives us a dictionary of attributes, such as {'id': 8, 'type': 'IfcWall', 'GlobalId': '2_qMTAIHrEYu0vYcqK8cBX', ... }

import ifcopenshell.util
import ifcopenshell.util.element
print(ifcopenshell.util.element.get_psets(wall))

print(wall.IsDefinedBy)

#print(ifc.get_inverse(wall))

print(ifc.traverse(wall, max_levels=1)) # Or, let's just go down one level deep

wall.Name = 'My new wall name'

wall.GlobalId = ifcopenshell.guid.new()