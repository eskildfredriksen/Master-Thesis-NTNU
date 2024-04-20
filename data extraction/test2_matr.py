import ifcopenshell
import ifcopenshell.geom as geom
import ifcopenshell.util.shape
import ifcopenshell.util.unit as unit 
import ifcopenshell.util.shape
import ifcopenshell.util.element
import numpy
import pandas as pd
#test
#extract file
ifc_file = ifcopenshell.open(r'c:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\IFC\Tennebekk\22018_TennebekkBuss_RIB.ifc')

#scaling
import ifcopenshell.util.element

def extract_number(text):
    # Define the regex pattern to match numbers
    pattern = r'\d+'
    # Search for the pattern in the text
    match = re.search(pattern, text)
    # If a match is found, extract and return the number
    if match:
        return int(match.group())
    else:
        None

def check_steel(material_input):
    similar_words = ["steel", "stål", "stel"]
    for i in material_input.split():
        quality = extract_number(i)
        if i.lower() in similar_words:
            material_name = "Steel"
        else:
            None
    return material_name, quality

def check_concrete(material_input):
    similar_words = ["concrete", "betong", "beton"]
    for i in material_input.split():
        quality = extract_number(i)
        if i.lower() in similar_words:
            material_name = "Concrete"
        else:
            None
    return material_name, quality

def check_timber(material_input):
    similar_words = ["tre", "heltre","wood", "timber"]
    for i in material_input.split():
        quality = extract_number(i)
        if i.lower() in similar_words:
            material_name = "Timber"
        else:
            None
    return material_name, quality


products = ifc_file.by_type('IfcProduct')

elements = []

for product in products:
    id = product.is_a()
    allowed_names = {"IfcBeam", "IfcColumn", "IfcWall", "IfcSlab", "IfcDoor", "IfcWindow"}
    if id in allowed_names:
        elements.append(id)
    else:
        None


import re


elements_sorted = sorted(elements)


beam_input = elements_sorted[0]

beam = ifc_file.by_type(beam_input)[0]
beam_type = ifcopenshell.util.element.get_type(beam)
#materials = ifc_file.by_type("IfcMaterial")


settings = geom.settings()
shape = geom.create_shape(settings, beam)

styles = shape.geometry.materials

st_var = ["steel", "stål"]


for style in styles:
    material = style.original_name()
    print(material_spec(material, st_var, "Steelcheck"))


def check_steel(material_input):
    similar_words = ["steel", "stål", "stel"]
    for i in material_input.split():
        quality = extract_number(i)
        if i.lower() in similar_words:
            material_name = "Steel"
        else:
            None
    return material_name quality

def check_concrete(material_input):
    similar_words = ["concrete", "betong", "beton"]
    for i in material_input.split():
        quality = extract_number(i)
        if i.lower() in similar_words:
            material_name = "Concrete"
        else:
            None
    return material_name, quality

def check_timber(material_input):
    similar_words = ["tre", "heltre","wood", "timber"]
    for i in material_input.split():
        quality = extract_number(i)
        if i.lower() in similar_words:
            material_name = "Timber"
        else:
            None
    return material_name, quality


    





        
         





 