import ifcopenshell
import ifcopenshell.geom as geom
import ifcopenshell.util.shape
import ifcopenshell.util.unit as unit 
import ifcopenshell.util.shape
import ifcopenshell.util.element
import numpy 
import pandas as pd
import re


ifc_file = ifcopenshell.open(r'C:\Users\e_ski\Downloads\PHBUP_RIBp.ifc')

products = ifc_file.by_type('IfcElementAssembly')

#print(products)

slab = products[20]
print(slab)


slab_type = ifcopenshell.util.element.get_type(slab)
#print(slab_type)
psets = ifcopenshell.util.element.get_psets(slab)
print(psets)

# Get all properties and quantities of the wall, including inherited type properties
#psets = ifcopenshell.util.element.get_psets(slab)

# Get only quantities and not properties
psets_quantities = ifcopenshell.util.element.get_psets(slab, qtos_only=True)
print(psets_quantities)
psets_props = ifcopenshell.util.element.get_psets(slab, psets_only=True)
print(psets_props)
#type = psets_props['Pset_ReinforcementBarPitchOfSlab']['Description']

#print(psets_quantities)
"""
area = round(psets['Dimensions']['Area'],2)
volume = round(psets['Dimensions']['Volume'],2)
length = round(psets['Data(Type)']['Element Length'],2)
#thickness = round(psets['Dimensions']['Thickness'],2)
#length = volume / thickness
width = round(psets['Data(Type)']['Element Width'],2) 
#area = round(volume / length,2)
"""
#print(area)
#print(volume)
#print(length)
#print(width)
#print(thickness)


 #print(psets_quantities)
    
#area = round(psets['Dimensions']['Area'],2)
#volume = round(psets['Dimensions']['Volume'],2)
#length = round(psets['Data(Type)']['Element Length'],2)
#thickness = round(psets['Dimensions']['Thickness'],2)
#length = volume / thickness
#width = round(psets['Data(Type)']['Element Width'],2) 
#area = round(volume / length,2)

#print(area)
#print(volume)
#print(length)
#print(width)
#print(thickness)


# Extract material:
#material_description = psets['Identity Data']['Material']
#print(material_description)

# Process material:
#material_info = check_material(material_description)
#material_name = material_info[0]

#print(material_info)

settings = geom.settings()
settings = geom.settings()

shape = geom.create_shape(settings, slab)
settings.set(settings.USE_WORLD_COORDS, True)
settings.set(settings.USE_BREP_DATA, True)  # Use BREP for better geometric processing
settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)

element_guid = shape.guid
element_id = shape.id
guid = ifc_file.by_guid(shape.guid)

#print(element_guid)
id = shape.geometry.id

matrix = shape.transformation.matrix.data

matrix = ifcopenshell.util.shape.get_shape_matrix(shape)

#location = numpy.round(matrix[:,3][0:3],2)
#orientation = numpy.round(matrix[:,0][0:3],2)


styles = shape.geometry.materials

# Correct material fetching method



for style in styles:
    material = style.original_name()
    material_name, material_letter, quality = check_material(material)
    quality_short = material_letter + str(quality)
    if material_name == "N/A":
        material_name = "Concrete"
    else:
        None


x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)

dims0 = [x,y,z]
dims = sorted(dims0)

thickness = dims[0]
length =  dims[-1]
width = dims[-2]

area = length * width
volume = area*thickness
area = round(volume / length,2)

#print(x)
#print(y)
#print(z)
#element_guid = None