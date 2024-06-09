import ifcopenshell
import ifcopenshell.geom as geom
import ifcopenshell.util.shape
import ifcopenshell.util.unit as unit 
import ifcopenshell.util.shape
import ifcopenshell.util.element
import numpy 
import pandas as pd
import re
#import OCC.Bnd


#test
#extract file
ifc_file = ifcopenshell.open(r'C:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\Supply 2\SUPPLY 2 IFC4.ifc')


#scaling
import ifcopenshell.util.element



products = ifc_file.by_type('IfcProduct')
#print(products)



#entities = ifc_file.by_type(entity_type)


#entity = ifc_file.by_entity()

#print(products)


#"IfcBeam", "IfcColumn","IfcElementAssembly", "IfcWall", "IfcWallType", "IfcWallStandardCase",

elements = []

#"IfcElementAssembly"


for product in products:
    id = product.is_a()
    allowed_names = {"IfcBeam", "IfcColumn","IfcElementAssembly", "IfcSlab", "IfcWall", "IfcWallType", "IfcWallStandardCase", "IfcDoor", "IfcWindow"}
    if id in allowed_names:
        #print(product)
        #if "Hollow Core Slab" in str(product): #sorts IFC hollow core slab systems as IfcSlab
        #    elements.append("IfcSlab")
        
        #elif "Structural Beam System" in str(product): #sorts IFC beam systems as IfcBeam
        #    elements.append("IfcBeam")
        #else:    
        elements.append(id)
    else:
        None

#print(elements)

#print(i_hc)
#print(i_slab)
#print(i_beam)


elements_sorted = sorted(elements)

#print(elements_sorted)

extracted_elements = []

steel_profiles = {
    "IPE80": {"A": 0.764, "I_y": 0.8014, "density": 6.00},
    "IPE100": {"A": 1.032, "I_y": 1.710, "density": 8.10},
    "IPE120": {"A": 1.321, "I_y": 3.178, "density": 10.4},
    "IPE140": {"A": 1.643, "I_y": 5.412, "density": 12.9},
    "IPE160": {"A": 2.009, "I_y": 8.693, "density": 15.8},
    "IPE180": {"A": 2.395, "I_y": 13.17, "density": 18.8},
    "IPE200": {"A": 2.848, "I_y": 19.43, "density": 22.4},
    "IPE220": {"A": 3.337, "I_y": 27.72, "density": 26.2},
    "IPE240": {"A": 3.912, "I_y": 38.92, "density": 30.7},
    "IPE270": {"A": 4.595, "I_y": 57.90, "density": 36.1},
    "IPE300": {"A": 5.381, "I_y": 83.56, "density": 42.2},
    "IPE330": {"A": 6.261, "I_y": 117.7, "density": 49.1},
    "IPE360": {"A": 7.273, "I_y": 162.7, "density": 57.1},
    "IPE400": {"A": 8.446, "I_y": 231.3, "density": 66.3},
    "IPE450": {"A": 9.882, "I_y": 337.4, "density": 77.6},
    "IPE500": {"A": 11.552, "I_y": 482.0, "density": 90.7},
    "IPE550": {"A": 13.442, "I_y": 671.2, "density": 105.5},
    "IPE600": {"A": 15.598, "I_y": 920.8, "density": 122.4},

    "HE100A": {"A": 2.124, "I_y": 3.492, "density": 16.7},
    "HE120A": {"A": 2.534, "I_y": 6.062, "density": 19.9},
    "HE140A": {"A": 3.142, "I_y": 10.33, "density": 24.7},
    "HE160A": {"A": 3.877, "I_y": 16.73, "density": 30.4},
    "HE180A": {"A": 4.525, "I_y": 25.10, "density": 35.5},
    "HE200A": {"A": 5.383, "I_y": 36.92, "density": 42.3},
    "HE220A": {"A": 6.434, "I_y": 54.10, "density": 50.5},
    "HE240A": {"A": 7.684, "I_y": 77.63, "density": 60.3},
    "HE260A": {"A": 8.682, "I_y": 104.5, "density": 68.2},
    "HE280A": {"A": 9.726, "I_y": 136.7, "density": 76.4},
    "HE300A": {"A": 11.253, "I_y": 182.6, "density": 88.3},
    "HE320A": {"A": 12.437, "I_y": 229.3, "density": 97.6},
    "HE340A": {"A": 13.347, "I_y": 276.9, "density": 104.8},
    "HE360A": {"A": 14.276, "I_y": 330.9, "density": 112.1},
    "HE400A": {"A": 15.898, "I_y": 450.7, "density": 124.8},
    "HE450A": {"A": 17.803, "I_y": 637.2, "density": 139.8},
    "HE500A": {"A": 19.754, "I_y": 869.7, "density": 155.1},
    "HE550A": {"A": 21.176, "I_y": 1119, "density": 166.2},
    "HE600A": {"A": 22.646, "I_y": 1412, "density": 177.8},
    "HE650A": {"A": 24.164, "I_y": 1752, "density": 189.7},
    "HE700A": {"A": 26.048, "I_y": 2153, "density": 204.5},
    "HE800A": {"A": 28.583, "I_y": 3034, "density": 224.4},
    "HE900A": {"A": 32.053, "I_y": 4221, "density": 251.6},
    "HE1000A": {"A": 34.685, "I_y": 5538, "density": 272.3},

    "HE100B": {"A": 2.604, "I_y": 4.495, "density": 20.4},
    "HE120B": {"A": 3.401, "I_y": 8.644, "density": 26.7},
    "HE140B": {"A": 4.296, "I_y": 15.09, "density": 33.7},
    "HE160B": {"A": 5.425, "I_y": 24.92, "density": 42.6},
    "HE180B": {"A": 6.525, "I_y": 38.31, "density": 51.2},
    "HE200B": {"A": 7.808, "I_y": 56.96, "density": 61.3},
    "HE220B": {"A": 9.104, "I_y": 80.91, "density": 71.5},
    "HE240B": {"A": 10.599, "I_y": 112.6, "density": 83.2},
    "HE260B": {"A": 11.844, "I_y": 149.2, "density": 93.0},
    "HE280B": {"A": 13.136, "I_y": 192.7, "density": 103.1},
    "HE300B": {"A": 14.908, "I_y": 251.7, "density": 117.0},
    "HE320B": {"A": 16.134, "I_y": 308.2, "density": 126.7},
    "HE340B": {"A": 17.09, "I_y": 366.6, "density": 134.2},
    "HE360B": {"A": 18.1, "I_y": 431.9, "density": 141.8},
    "HE400B": {"A": 19.8, "I_y": 576.8, "density": 155.3},
    "HE450B": {"A": 21.8, "I_y": 798.9, "density": 171.1},
    "HE500B": {"A": 23.9, "I_y": 1072, "density": 187.3},
    "HE550B": {"A": 25.4, "I_y": 1367, "density": 199.4},
    "HE600B": {"A": 27, "I_y": 1710, "density": 211.9},
    "HE650B": {"A": 28.6, "I_y": 2106, "density": 224.8},
    "HE700B": {"A": 30.6, "I_y": 2569, "density": 240.5},
    "HE800B": {"A": 33.4, "I_y": 3591, "density": 262.3},
    "HE900B": {"A": 37.1, "I_y": 4941, "density": 291.5},
    "HE1000B": {"A": 40, "I_y": 6447, "density": 314.0},
    
 "SHSH40x2.6": {"A": 0.386, "I_y": 0.0894, "weight": 3.03},
"SHSH40x3.2": {"A": 0.466, "I_y": 0.104, "weight": 3.66},
"SHSH40x4.0": {"A": 0.568, "I_y": 0.120, "weight": 4.46},

"SHSH50x3.2": {"A": 0.594, "I_y": 0.216, "weight": 4.66},
"SHSH50x4.0": {"A": 0.728, "I_y": 0.256, "weight": 5.72},
"SHSH50x5.0": {"A": 0.888, "I_y": 0.296, "weight": 6.97},

"SHSH60x3.2": {"A": 0.722, "I_y": 0.387, "weight": 5.67},
"SHSH60x4.0": {"A": 0.888, "I_y": 0.461, "weight": 6.97},
"SHSH60x5.0": {"A": 1.09, "I_y": 0.544, "weight": 8.54},

"SHSH80x3.6": {"A": 1.09, "I_y": 1.06, "weight": 8.59},
"SHSH80x4.0": {"A": 1.21, "I_y": 1.16, "weight": 9.48},
"SHSH80x5.0": {"A": 1.49, "I_y": 1.39, "weight": 11.7},
"SHSH80x6.3": {"A": 1.84, "I_y": 1.65, "weight": 14.4},

"SHSH100x4.0": {"A": 1.53, "I_y": 2.34, "weight": 12.0},
"SHSH100x5.0": {"A": 1.89, "I_y": 2.83, "weight": 14.8},
"SHSH100x6.3": {"A": 2.34, "I_y": 3.41, "weight": 18.4},
"SHSH100x8.0": {"A": 2.91, "I_y": 4.08, "weight": 22.9},
"SHSH100x10.0": {"A": 3.55, "I_y": 4.74, "weight": 27.9},

"SHSH120x5.0": {"A": 2.29, "I_y": 5.03, "weight": 18},
"SHSH120x6.3": {"A": 2.85, "I_y": 6.10, "weight": 22.3},
"SHSH120x8.0": {"A": 3.55, "I_y": 7.38, "weight": 27.9},
"SHSH120x10.0": {"A": 4.35, "I_y": 8.70, "weight": 34.2},

"SHSH140x5.0": {"A": 2.66, "I_y": 8.01, "weight": 20.9},
"SHSH140x6.3": {"A": 3.31, "I_y": 9.74, "weight": 26.0},
"SHSH140x8.0": {"A": 4.13, "I_y": 11.8, "weight": 32.4},

"SHSH150x5.0": {"A": 2.86, "I_y": 9.94, "weight": 22.5},
"SHSH150x6.3": {"A": 3.56, "I_y": 12.1, "weight": 28.0},
"SHSH150x8.0": {"A": 4.45, "I_y": 14.7, "weight": 34.9},
"SHSH150x10.0": {"A": 5.49, "I_y": 17.7, "weight": 43.1},

"SHSH160x6.3": {"A": 3.80, "I_y": 14.9, "weight": 29.9},
"SHSH160x8.0": {"A": 4.70, "I_y": 18.1, "weight": 37.4},
"SHSH160x10.0": {"A": 5.85, "I_y": 21.5, "weight": 45.7},

"SHSH180x6.3": {"A": 4.32, "I_y": 21.5, "weight": 33.9},
"SHSH180x8.0": {"A": 5.41, "I_y": 26.3, "weight": 42.5},
"SHSH180x10.0": {"A": 6.65, "I_y": 31.5, "weight": 52.5},

"SHSH200x6.3": {"A": 4.82, "I_y": 29.9, "weight": 37.8},
"SHSH200x8.0": {"A": 6.05, "I_y": 36.8, "weight": 47.5},
"SHSH200x10.0": {"A": 7.45, "I_y": 44.2, "weight": 58.5},

"SHSH250x6.3": {"A": 6.08, "I_y": 59.8, "weight": 47.7},
"SHSH250x8.0": {"A": 7.65, "I_y": 74.0, "weight": 60.0},
"SHSH250x10.0": {"A": 9.45, "I_y": 89.7, "weight": 74.2},

"SHSH300x10.0": {"A": 11.4, "I_y": 159, "weight": 89.9},

"RHSH50x30x2.6": {"A": 0.386, "I_y": 0.124, "density": 3.03},
"RHSH50x30x3.2": {"A": 0.466, "I_y": 0.145, "density": 3.66},
"RHSH50x30x4.0": {"A": 0.568, "I_y": 0.170, "density": 4.46},

"RHSH60x40x3.2": {"A": 0.594, "I_y": 0.283, "density": 4.66},
"RHSH60x40x4.0": {"A": 0.728, "I_y": 0.366, "density": 5.72},

"RHSH80x40x3.2": {"A": 0.722, "I_y": 0.581, "density": 5.67},
"RHSH80x40x4.0": {"A": 0.888, "I_y": 0.696, "density": 6.97},
"RHSH80x40x5.0": {"A": 1.09, "I_y": 0.824, "density": 8.54},

"RHSH100x50x3.2": {"A": 0.914, "I_y": 1.17, "density": 7.18},
"RHSH100x50x4.0": {"A": 1.13, "I_y": 1.42, "density": 8.86},
"RHSH100x50x5.0": {"A": 1.39, "I_y": 1.70, "density": 10.9},

"RHSH120x60x3.6": {"A": 1.24, "I_y": 2.30, "density": 9.27},
"RHSH120x60x5.0": {"A": 1.69, "I_y": 3.04, "density": 13.3},
"RHSH120x60x6.3": {"A": 2.09, "I_y": 3.66, "density": 16.4},

"RHSH120x80x5.0": {"A": 1.89, "I_y": 3.70, "density": 14.8},
"RHSH120x80x6.3": {"A": 2.34, "I_y": 4.47, "density": 18.4},
"RHSH120x80x8.0": {"A": 2.91, "I_y": 5.37, "density": 22.9},

"RHSH140x80x5.0": {"A": 2.09, "I_y": 5.41, "density": 16.4},
"RHSH140x80x6.3": {"A": 2.59, "I_y": 6.56, "density": 20.4},
"RHSH140x80x8.0": {"A": 3.23, "I_y": 7.93, "density": 25.4},

"RHSH150x100x5.0": {"A": 2.39, "I_y": 7.47, "density": 18.7},
"RHSH150x100x6.3": {"A": 2.97, "I_y": 9.10, "density": 23.3},
"RHSH150x100x8.0": {"A": 3.71, "I_y": 11.1, "density": 29.1},

"RHSH160x80x5.0": {"A": 2.29, "I_y": 7.53, "density": 18.0},
"RHSH160x80x6.3": {"A": 2.85, "I_y": 9.17, "density": 22.3},
"RHSH160x80x8.0": {"A": 3.55, "I_y": 11.1, "density": 27.9},
"RHSH160x80x10.0": {"A": 4.35, "I_y": 13.2, "density": 34.2},

"RHSH200x100x5.0": {"A": 2.86, "I_y": 14.8, "density": 22.5},
"RHSH200x100x6.3": {"A": 3.56, "I_y": 18.1, "density": 28.0},
"RHSH200x100x8.0": {"A": 4.45, "I_y": 22.0, "density": 35.9},
"RHSH200x100x10.0": {"A": 5.45, "I_y": 26.1, "density": 42.8},

"RHSH200x120x6.3": {"A": 3.81, "I_y": 20.5, "density": 29.9},
"RHSH200x120x8.0": {"A": 4.77, "I_y": 25.0, "density": 37.4},
"RHSH200x120x10.0": {"A": 5.85, "I_y": 29.7, "density": 42.8},

"RHSH200x150x8.0": {"A": 5.124, "I_y": 28.28, "density": 37.4},
"RHSH200x150x10.0": {"A": 6.257, "I_y": 33.47, "density": 42.8},

"RHSH250x150x6.3": {"A": 4.82, "I_y": 41.1, "density": 37.8},
"RHSH250x150x8.0": {"A": 6.05, "I_y": 50.6, "density": 47.5},
"RHSH250x150x10.0": {"A": 7.45, "I_y": 60.9, "density": 58.5},

"RHSH300x200x6.3": {"A": 6.08, "I_y": 77.9, "density": 47.7},
"RHSH300x200x8.0": {"A": 7.65, "I_y": 96.5, "density": 60.0},
"RHSH300x200x10.0": {"A": 9.45, "I_y": 117.0, "density": 74.2}

}




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

def check_material(material_input):
    steel_words = ["steel", "stål", "stel"]
    concrete_words = ["concrete", "betong", "beton"]
    timber_words = ["tre", "heltre","wood", "timber"]
    material_name = "N/A"
    material_letter = "N/A"
    quality = None
    for i in material_input.split():
        if i.lower() in steel_words:
            material_name = "Steel"
            material_letter = "s"
        elif i.lower() in concrete_words:
            material_name = "Concrete"
            material_letter = "c"
        elif i.lower() in timber_words:
            material_name = "Timber" 
            material_letter = "t"
        quality = extract_number(material_input)

    return material_name, material_letter, quality

def heAB_formatting(profile_input):
    if profile_input.startswith('HEA'):
        return 'HE' + profile_input[3:] + 'A'
    elif profile_input.startswith('HEB'):
        return 'HE' + profile_input[3:] + 'A'
    return profile_input

def replace_hup_with_shs_rhs(input_profile):

    if input_profile.startswith('HUP'):
        input_profile_formatted = input_profile.replace(" ", "")
        parts = re.split('[PxX]', input_profile_formatted) 
        #update_profile = input_profile.replace('HUP', 'SHS')
        
        #print(parts)
        #parts = re.split('[PxX]', update_profile) 
        
        if parts[1] == parts[2]:
              #changes format from 80x80x5 to 80x5 f.ex
            if '.' in parts[3]:
                formatted_profile = f"SHSH{parts[2]}x{parts[3]}"
            else:
                formatted_profile = f"SHSH{parts[2]}x{parts[3]}.0"
        else:
            if '.' in parts[3]:
                formatted_profile = f"RHSH{parts[1]}x{parts[2]}x{parts[3]}" 
            else:
                formatted_profile = f"RHSH{parts[1]}x{parts[2]}x{parts[3]}.0" 

    elif input_profile.startswith('SHS'):
        formatted_profile = "SHSH" + input_profile[3:]
        if '.' not in formatted_profile:
            formatted_profile += '.0'
    
    elif input_profile.startswith('RHS'):
        formatted_profile = "RHSH" + input_profile[3:]
        if '.' not in formatted_profile:
            formatted_profile += '.0'  
        
    else: 
        formatted_profile = input_profile

    return formatted_profile


def extract_beam(beam_input,index):
    beam = ifc_file.by_type(beam_input)[index]
    beam_type = ifcopenshell.util.element.get_type(beam)
    
    psets_dict = ifcopenshell.util.element.get_psets(beam_type)
    psets = ifcopenshell.util.element.get_psets(beam)
    psets_props = ifcopenshell.util.element.get_psets(beam, psets_only=True)
    psets_quantities = ifcopenshell.util.element.get_psets(beam, qtos_only=True)
    #print(psets)
   
    profile = psets_props['Pset_BeamCommon']['Reference']
    

    #profile_heAB = heAB_formatting(profile1)
    #profile_shs_rhs = replace_hup_with_shs_rhs(profile_heAB)
    #profile = profile_shs_rhs.replace(" ", "")
    #profile_shape = psets_props['Other']['Family Name']
    

    #print(profile)
    #print(profile_shape)

    settings = geom.settings()
    shape = geom.create_shape(settings, beam)

    element_guid = shape.guid         #relevant?
    element_id = shape.id              #relevant?
    guid = ifc_file.by_guid(shape.guid)

    id = shape.geometry.id

    matrix = shape.transformation.matrix.data
    matrix = ifcopenshell.util.shape.get_shape_matrix(shape)


    location = matrix[:,3][0:3]             # may be relevant for checking robustness of code and if an element actually is a beam or not
    orientation = matrix[:,0][0:3]          # may be relevant for checking robustness of code and if an element actually is a beam or not


    styles = shape.geometry.materials

    for style in styles:
        material = style.original_name()
        material_name, material_letter, quality = check_material(material)
        quality_short = material_letter + str(quality)



    x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
    y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
    z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)

    dims0 = [x,y,z]
    dims = sorted(dims0)

    
    profile_shape = "test"

    #print(profile)

    

    if str(profile) in steel_profiles.keys():    
        area = round(steel_profiles[profile]["A"],3)
        volume = round(dims[-1]*area,3)
        Iy = steel_profiles[profile]["I_y"]
    else:
        area = round(ifcopenshell.util.shape.get_area(shape.geometry),2) / 1000
        volume = dims[-1]*area
        if "rectangular" in profile_shape.lower() or "quadratic" in profile_shape.lower():
            Iy1 = 1/12 * x * y**3 * 10**6 #divided by e6 
            Iy = round(Iy1, 2)
        elif "circular" in profile_shape.lower() or "round" in profile_shape.lower():
            Iy1 = numpy.Pi/4 * x**4 * 10**6 #divided by e6
            Iy = round(Iy1,2)
        else:
            Iy = None

        
        

    #print(beam_input, id, x,y,z,profile, material) 
    beam_dict ={" Guid ": element_guid , " Element ": beam_input , " Material ": material_name , "Quality": quality, "Material label": quality_short, " Length [ m ]": x ," Height [ m ]": z , " Width [ m ]": y , "Volume [m3]" : volume, "Area [m2]": area, "Profile" :profile, "Iy e-6 [mm4]": Iy}
    #if material_name == "N/A":
    #    None
    #else:
    extracted_elements.append(beam_dict)
    
def extract_column(col_input,index):
    col = ifc_file.by_type(col_input)[index]
    col_type = ifcopenshell.util.element.get_type(col)
    
    psets_dict = ifcopenshell.util.element.get_psets(col_type)
    psets = ifcopenshell.util.element.get_psets(col)
    psets_props = ifcopenshell.util.element.get_psets(col, psets_only=True)
    psets_quantities = ifcopenshell.util.element.get_psets(col, qtos_only=True)
    
    profile = psets_props['Pset_ColumnCommon']['Reference']
    #profile_heAB = heAB_formatting(profile1)
    #profile_shs_rhs = replace_hup_with_shs_rhs(profile_heAB)
    #profile = profile_shs_rhs.replace(" ", "")


    #profile_shape = psets_props['Other']['Family Name']

    #print(psets_props)

    settings = geom.settings()
    shape = geom.create_shape(settings, col)

    element_guid = shape.guid
    element_id = shape.id
    guid = ifc_file.by_guid(shape.guid)

    id = shape.geometry.id

    matrix = shape.transformation.matrix.data
    matrix = ifcopenshell.util.shape.get_shape_matrix(shape)
    location = matrix[:,3][0:3]
    orientation = matrix[:,0][0:3]


    styles = shape.geometry.materials

    for style in styles:
        material = style.original_name()
        material_name, material_letter, quality = check_material(material)
        quality_short = material_letter + str(quality)
        
    x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
    y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
    z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)

    dims0 = [x,y,z]
    dims = sorted(dims0)

    profile_shape = "test"


    if profile in steel_profiles.keys():    
        area = round(steel_profiles[profile]["A"],3)
        volume = round(dims[-1]*area,3)
        Iy = steel_profiles[profile]["I_y"]
    else:
        area = round(ifcopenshell.util.shape.get_area(shape.geometry),2) / 1000           #vurdere å fjerne
        volume = dims[-1]*area
        if "rectangular" in profile_shape.lower() or "quadratic" in profile_shape.lower():
            Iy1 = 1/12 * x * y**3 * 10**6 #divided by e6 
            Iy = round(Iy1, 2)
        elif "circular" in profile_shape.lower() or "round" in profile_shape.lower():
            Iy1 = numpy.Pi/4 * x**4 * 10**6 #divided by e6
            Iy = round(Iy1,2)
        else:
            Iy = None
    

    #print(col_input,id, x,y,z,profile, material) 
    col_dict ={" Guid ": element_guid , " Element ": col_input , " Material ": material_name ,"Material label": quality_short,  "Quality": quality, " Length [ m ]": x ," Height [ m ]": z , " Width [ m ]": y , "Volume [m3]" : volume, "Area [m2]": area, "Profile" :profile, "Iy e-6 [mm4]": Iy}
    #if material_name == "N/A":
    #    None
    #else:
    extracted_elements.append(col_dict)

def extract_slab(slab_input,index):
    slab = ifc_file.by_type(slab_input)[index]
    
    slab_type = ifcopenshell.util.element.get_type(slab)
    #print(slab_type)
    psets = ifcopenshell.util.element.get_psets(slab)
    #print(psets)

   
    # Get all properties and quantities of the wall, including inherited type properties
    #psets = ifcopenshell.util.element.get_psets(slab)

    # Get only quantities and not properties
    psets_quantities = ifcopenshell.util.element.get_psets(slab, qtos_only=True)
    #print(psets_quantities)
    #psets_props = ifcopenshell.util.element.get_psets(slab, psets_only=True)
    #print(psets_props)
    #type = psets_props['Pset_ReinforcementBarPitchOfSlab']['Description']

    #print(psets_quantities)

    #length = 

    #area = round(psets['Dimensions']['Area'],2)
    #volume = round(psets['Dimensions']['Volume'],2)
    #thickness = round(psets['Dimensions']['Thickness'],2)

    #length = volume / area
    
    #length = round(volume / thickness,2)
    #width = area / thickness 
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
    
    #settings = geom.settings()
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
        
        if material_name == "N/A":
           material_name = "Concrete"
        else:
           None
        quality_short = material_letter + str(quality)

    
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

    #area = round(volume / length,2)

   

    

    #print(slab_input,id, x,y,z, material) 
    slab_dict = {" Guid ": element_guid , " Element ": "IfcSlab" , " Material ": material_name , "Quality": quality,"Material label": quality_short, " Length [ m ]": length ," Height [ m ]": thickness , " Width [ m ]": width , "Volume [m3]" : volume, "Area [m2]": area}
    #if material_name == "N/A" or length < 0.5 or width < 0.5:
    #    None
    #else:
    #print(slab_dict)
    extracted_elements.append(slab_dict)

def extract_hollow_core_slab(slab_input,index):
    slab = ifc_file.by_type(slab_input)[index]
    #print(slab)
    slab_type = ifcopenshell.util.element.get_type(slab)
    #print(slab_type)
    psets = ifcopenshell.util.element.get_psets(slab)
    #print(psets)
    
    # Get all properties and quantities of the wall, including inherited type properties
    #psets = ifcopenshell.util.element.get_psets(slab)

    # Get only quantities and not properties
    psets_quantities = ifcopenshell.util.element.get_psets(slab, qtos_only=True)
    #print(psets_quantities)
    psets_props = ifcopenshell.util.element.get_psets(slab, psets_only=True)
    #print(psets_props)
    #type = psets_props['Pset_ReinforcementBarPitchOfSlab']['Description']

    #print(psets_quantities)
    
    #area = round(psets['Dimensions']['Area'],2)
    #volume = round(psets['Dimensions']['Volume'],2)
    length = round(psets['Data(Type)']['Element Length'],2)
    #thickness = round(psets['Dimensions']['Thickness'],2)
    #length = volume / thickness
    width = round(psets['Data(Type)']['Element Width'],2) 
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
    """
    #settings = geom.settings()
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
    """

    #print(slab_input,id, x,y,z, material) 
    #slab_dict = {" Guid ": element_guid , " Element ": "IfcSlab" , " Material": material_info[0] , "Quality": material_info[2],"Material label": material_info[1], " Length [ m ]": length ," Height [ m ]": thickness , " Width [ m ]": width , "Volume [m3]" : volume, "Area [m2]": area}
    #if material_name == "N/A" or length < 0.5 or width < 0.5:
    #    None
    #else:
    #print(slab_dict)
    #extracted_elements.append(slab_dict)

def extract_wall(wall_input,index):
    wall = ifc_file.by_type("IfcWall")[index]
    wall_type = ifcopenshell.util.element.get_type(wall)

    psets_dict = ifcopenshell.util.element.get_psets(wall_type)


    # Get all properties and quantities of the wall, including inherited type properties
    psets = ifcopenshell.util.element.get_psets(wall)

    # Get only quantities and not properties
    psets_quantities = ifcopenshell.util.element.get_psets(wall, qtos_only=True)
    psets_props = ifcopenshell.util.element.get_psets(wall, psets_only=True)
    #type = psets_props['Pset_ReinforcementBarPitchOfSlab']['Description']

    settings = geom.settings()
    shape = geom.create_shape(settings, wall)


    element_guid = shape.guid
    element_id = shape.id
    guid = ifc_file.by_guid(shape.guid)

    id = shape.geometry.id

    matrix = shape.transformation.matrix.data

    matrix = ifcopenshell.util.shape.get_shape_matrix(shape)

    location = numpy.round(matrix[:,3][0:3],2)
    orientation = numpy.round(matrix[:,0][0:3],2)


    styles = shape.geometry.materials

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
    height = dims[-2]
    area = length * height
    volume = round(area*thickness,2)
    

    
    wall_dict = {" Guid ": guid , " Element ": "IfcWall" , " Material ": material_name , "Quality": quality,"Material label": quality_short, " Length [ m ]": length," Height [ m ]": height , " Width [ m ]": thickness , "Volume [m3]" : volume, "Area [m2]": area}
    #print(wall_input,id, x,y,z, material)
    #if material_name == "N/A" or height < 0.5 or thickness < 0.5:
    #    None
    #else:
    extracted_elements.append(wall_dict)

def extract_window_door(wall_input,index):
    wall = ifc_file.by_type("IfcWindow")[index]
    wall_type = ifcopenshell.util.element.get_type(wall)

    psets_dict = ifcopenshell.util.element.get_psets(wall_type)


    # Get all properties and quantities of the wall, including inherited type properties
    psets = ifcopenshell.util.element.get_psets(wall)

    # Get only quantities and not properties
    psets_quantities = ifcopenshell.util.element.get_psets(wall, qtos_only=True)
    psets_props = ifcopenshell.util.element.get_psets(wall, psets_only=True)
    #type = psets_props['Pset_ReinforcementBarPitchOfSlab']['Description']

    settings = geom.settings()
    shape = geom.create_shape(settings, wall)


    element_guid = shape.guid
    element_id = shape.id
    guid = ifc_file.by_guid(shape.guid)

    id = shape.geometry.id

    matrix = shape.transformation.matrix.data

    matrix = ifcopenshell.util.shape.get_shape_matrix(shape)

    location = numpy.round(matrix[:,3][0:3],2)
    orientation = numpy.round(matrix[:,0][0:3],2)


    styles = shape.geometry.materials

    for style in styles:
        material = style.original_name()
        material_name, material_letter, quality = check_material(material)
        quality_short = material_letter + str(quality)
        if material_name == "N/A":
            material_name = "Timber"
        else:
            None
        

        

    x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
    y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
    z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)


    dims0 = [x,y,z]
    dims = sorted(dims0)
    thickness = dims[0]
    length =  dims[-1]
    height = dims[-2]
    area = length * height
    volume = round(area*thickness,2)
    

    
    wall_dict = {" Guid ": element_guid , " Element ": wall_input , " Material ": material_name , "Quality": quality, "Material label": quality_short, " Length [ m ]": thickness," Height [ m ]": height , " Width [ m ]": length , "Volume [m3]" : volume, "Area [m2]": area}
    #print(wall_input,id, x,y,z, material)
    #if material_name == "N/A" or height < 0.5 or thickness < 0.5:
    #    None
    #else:
    extracted_elements.append(wall_dict)



i_beam = 0
i_col = 0
i_slab = 0
i_hollow_core_slab = 0
i_wall = 0
i_window = 0
i_door = 0 

#print(products)
#print(elements_sorted)
#print(len(elements_sorted))

for i in range(len(elements_sorted)):
    element = elements_sorted[i]
    if element == "IfcBeam":
        extract_beam(element,i_beam)
        i_beam +=1
    elif element == "IfcColumn":
        extract_column(element,i_col)
        i_col += 1

    elif element == "IfcSlab":
        extract_slab(element,i_slab)
        i_slab +=1

    #elif element == "IfcElementAssembly":
    #    if "Hollow Core Slab" in str(products[i]):
    #        extract_hollow_core_slab(element, i_hollow_core_slab)        
    #    i_hollow_core_slab +=1

    elif element == "IfcWall" or element == "IfcWallType" or element == "IfcWallStandardCase":
        extract_wall(element,i_wall)
        i_wall +=1

    elif element == "IfcWindow":
        extract_window_door(element,i_window)
        i_window +=1

    elif element == "IfcDoor":
        extract_window_door(element,i_door) #same function
        i_door +=1
   
    else:
        None

ext_elements_df = pd.DataFrame(extracted_elements)
ext_elements_df.to_excel(r'C:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\Supply 2\supply 2 ifc4.xlsx')


# Add desired quantites and properties to the DataFrame
#element_dict ={" Guid ": guid , " Name ": name , " Material ": material , " Length [ mm ]": length ," Height [ mm ]": height , " Width [ mm ]": width ," Cross section area [m^2]": cross_section_area , " Volume [ m ^3]": volume , " Cross section name ":object_type ," Location ": location_str , " Latitude ": lat_float , " Longitude ":long_float }
#quantites.append( element_dict )
#elements_df = pd.DataFrame ( quantites )
# Export DataFrame to Excel
#elements_df.to_excel (" C:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\Excel")                           


"""
#----------------------------------------------------------------------------    
slab = ifc_file.by_type("IfcSlab")[0]
slab_type = ifcopenshell.util.element.get_type(slab)



# Get all properties and quantities as a dictionary
# returns {"Pset_WallCommon": {"id": 123, "FireRating": "2HR", ...}}
psets_dict = ifcopenshell.util.element.get_psets(slab_type)


# Get all properties and quantities of the wall, including inherited type properties
psets = ifcopenshell.util.element.get_psets(slab)


# Get only properties and not quantities
psets_props = ifcopenshell.util.element.get_psets(slab, psets_only=True)

# Get only quantities and not properties
psets_quantities = ifcopenshell.util.element.get_psets(slab, qtos_only=True)

type = psets_props['Pset_ReinforcementBarPitchOfSlab']['Description']

#print(psets)
#print(psets_dict)

#profile = psets_props['Pset_BeamCommon']['Reference']




settings = geom.settings()
shape = geom.create_shape(settings, slab)

# The GUID of the element we processed
element_guid = shape.guid

# The ID of the element we processed
element_id = shape.id

# The element we are processing
guid = ifc_file.by_guid(shape.guid)

# A unique geometry ID, useful to check whether or not two geometries are
# identical for caching and reuse. The naming scheme is:
# IfcShapeRepresentation.id{-layerset-LayerSet.id}{-material-Material.id}{-openings-[Opening n.id ...]}{-world-coords}
id = shape.geometry.id


# A 4x4 matrix representing the location and rotation of the element, in the form:
# [ [ x_x, y_x, z_x, x   ]
#   [ x_y, y_y, z_y, y   ]
#   [ x_z, y_z, z_z, z   ]
#   [ 0.0, 0.0, 0.0, 1.0 ] ]
# The position is given by the last column: (x, y, z)
# The rotation is described by the first three columns, by explicitly specifying the local X, Y, Z axes.
# The first column is a normalised vector of the local X axis: (x_x, x_y, x_z)
# The second column is a normalised vector of the local Y axis: (y_x, y_y, y_z)
# The third column is a normalised vector of the local Z axis: (z_x, z_y, z_z)
# The axes follow a right-handed coordinate system.
# Objects are never scaled, so the scale factor of the matrix is always 1.
matrix = shape.transformation.matrix.data

# For convenience, you might want the matrix as a nested numpy array, so you can do matrix math.
matrix = ifcopenshell.util.shape.get_shape_matrix(shape)

# You can also extract the XYZ location of the matrix.
location = numpy.round(matrix[:,3][0:3],2)
orientation = numpy.round(matrix[:,0][0:3],2)

# X Y Z of vertices in flattened list e.g. [v1x, v1y, v1z, v2x, v2y, v2z, ...]
# These vertices are local relative to the shape's transformation matrix.
#verts = shape.geometry.verts

# Indices of vertices per edge e.g. [e1v1, e1v2, e2v1, e2v2, ...]
# If the geometry is mesh-like, edges contain the original edges.
# These may be quads or ngons and not necessarily triangles.
#edges = shape.geometry.edges

# Indices of vertices per triangle face e.g. [f1v1, f1v2, f1v3, f2v1, f2v2, f2v3, ...]
# Note that faces are always triangles.
#faces = shape.geometry.faces

# Since the lists are flattened, you may prefer to group them like so depending on your geometry kernel
# A nested numpy array e.g. [[v1x, v1y, v1z], [v2x, v2y, v2z], ...]
#grouped_verts = ifcopenshell.util.shape.get_vertices(shape.geometry)
# A nested numpy array e.g. [[e1v1, e1v2], [e2v1, e2v2], ...]
#grouped_edges = ifcopenshell.util.shape.get_edges(shape.geometry)
# A nested numpy array e.g. [[f1v1, f1v2, f1v3], [f2v1, f2v2, f2v3], ...]
#grouped_faces = ifcopenshell.util.shape.get_faces(shape.geometry)

# A list of styles that are relevant to this shape
styles = shape.geometry.materials

for style in styles:
    # Each style is named after the entity class if a default
    # material is applied. Otherwise, it is named "surface-style-{SurfaceStyle.name}"
    # All non-alphanumeric characters are replaced with a "-".
    material = style.original_name()

    # A more human readable name
    #print(style.name)

    # Each style may have diffuse colour RGB codes
    #if style.has_diffuse:
    #   print(style.diffuse)

    # Each style may have transparency data
    #if style.has_transparency:
    #    print(style.transparency)

# Indices of material applied per triangle face e.g. [f1m, f2m, ...]
#material_ids = shape.geometry.material_ids

# IDs representation item per triangle face e.g. [f1i, f2i, ...]
#item_ids = shape.geometry.item_ids

#material = shape.geometry.materials[0] 
#material_name = material.original_name()

x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)

print(id, x,y,z,material, type,location,orientation)
"""