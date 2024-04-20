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


products = ifc_file.by_type('IfcProduct')

elements = []

for product in products:
    id = product.is_a()
    allowed_names = {"IfcBeam", "IfcColumn", "IfcWall", "IfcSlab", "IfcDoor", "IfcWindow"}
    if id in allowed_names:
        elements.append(id)
    else:
        None


elements_sorted = sorted(elements)

material_list = []

"""""
for product in elements_sorted:
    if product.HasAssociations:
        for i in product.HasAssociations:
            if i.is_a('IfcRelAssociatesMaterial'):

                if i.RelatingMaterial.is_a('IfcMaterial') and i.RelatingMaterial.Name not in material_list:
                    material_list.append(i.RelatingMaterial.Name)

                if i.RelatingMaterial.is_a('IfcMaterialList'):
                    for materials in i.RelatingMaterial.Materials:
                        if materials.Name not in material_list:
                            material_list.append(materials.Name)

                if i.RelatingMaterial.is_a('IfcMaterialLayerSetUsage'):
                    for materials in i.RelatingMaterial.ForLayerSet.MaterialLayers:
                        if materials.Material.Name not in material_list:
                            material_list.append(materials.Material.Name)

#print (material_list)
"""""


import re

def extract_number(text):
    # Define the regex pattern to match numbers
    pattern = r'\d+'
    
    # Search for the pattern in the text
    match = re.search(pattern, text)
    
    # If a match is found, extract and return the number
    if match:
        return int(match.group())
    else:
        return None

beam_input = elements_sorted[0]

beam = ifc_file.by_type(beam_input)[0]
beam_type = ifcopenshell.util.element.get_type(beam)
#materials = ifc_file.by_type("IfcMaterial")


settings = geom.settings()
shape = geom.create_shape(settings, beam)

styles = shape.geometry.materials

for style in styles:
    material = style.original_name()

print(material)

steel_variations = ["stål", "steel"]
steel_replaced = "Steel"

#print(material.lower())

#if material.lower() in enumerate(steel_variations):
#    value = extract_number(material)
#    material = "Steel"

#print(value)
#print(material)
    
def replace_words(text, words_to_replace, new_word):
    # Split the text into individual words
    words = text.split()

    # Iterate through each word
    for i, word in enumerate(words):
        # Check if the word needs to be replaced
        if word.lower() in words_to_replace:
            # Replace the word with the new word
            words[i] = new_word

    # Join the words back into a single string
    new_text = ' '.join(words)

    return new_text


print(replace_words(material, steel_variations, steel_replaced))
