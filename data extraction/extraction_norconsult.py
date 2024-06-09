import ifcopenshell
import ifcopenshell.geom as geom
import ifcopenshell.util.shape
import ifcopenshell.util.unit as unit 
import ifcopenshell.util.shape
import ifcopenshell.util.element
import numpy 
import pandas as pd
import re



#extract file
ifc_file = ifcopenshell.open(r'C:\Users\e_ski\Downloads\PHBUP_RIBp.ifc')

products = ifc_file.by_type('IfcProduct')

#element_assemblies = ifc_file.by_type('IfcElementAssembly')
#print(products)


#"IfcElementAssembly",






extracted_elements = []

steel_profiles = {
    "IPE80": {"A": 0.000764, "I_y": 0.8014, "density": 6.00},
    "IPE100": {"A": 0.001032, "I_y": 1.710, "density": 8.10},
    "IPE120": {"A": 0.001321, "I_y": 3.178, "density": 10.4},
    "IPE140": {"A": 0.001643, "I_y": 5.412, "density": 12.9},
    "IPE160": {"A": 0.002009, "I_y": 8.693, "density": 15.8},
    "IPE180": {"A": 0.002395, "I_y": 13.17, "density": 18.8},
    "IPE200": {"A": 0.002848, "I_y": 19.43, "density": 22.4},
    "IPE220": {"A": 0.003337, "I_y": 27.72, "density": 26.2},
    "IPE240": {"A": 0.003912, "I_y": 38.92, "density": 30.7},
    "IPE270": {"A": 0.004595, "I_y": 57.90, "density": 36.1},
    "IPE300": {"A": 0.005381, "I_y": 83.56, "density": 42.2},
    "IPE330": {"A": 0.006261, "I_y": 117.7, "density": 49.1},
    "IPE360": {"A": 0.007273, "I_y": 162.7, "density": 57.1},
    "IPE400": {"A": 0.008446, "I_y": 231.3, "density": 66.3},
    "IPE450": {"A": 0.009882, "I_y": 337.4, "density": 77.6},
    "IPE500": {"A": 0.011552, "I_y": 482.0, "density": 90.7},
    "IPE550": {"A": 0.013442, "I_y": 671.2, "density": 105.5},
    "IPE600": {"A": 0.015598, "I_y": 920.8, "density": 122.4},
    "HE100A ": {"A": 0.002124, "I_y": 3.492, "density": 16.7},
    "HE120A": {"A": 0.002534, "I_y": 6.062, "density": 19.9},
    "HE140A": {"A": 0.003142, "I_y": 10.33, "density": 24.7},
    "HE160A": {"A": 0.003877, "I_y": 16.73, "density": 30.4},
    "HE180A": {"A": 0.004525, "I_y": 25.10, "density": 35.5},
    "HE200A": {"A": 0.005383, "I_y": 36.92, "density": 42.3},
    "HE220A": {"A": 0.006434, "I_y": 54.10, "density": 50.5},
    "HE240A": {"A": 0.007684, "I_y": 77.63, "density": 60.3},
    "HE260A": {"A": 0.008682, "I_y": 104.5, "density": 68.2},
    "HE280A": {"A": 0.009726, "I_y": 136.7, "density": 76.4},
    "HE300A": {"A": 0.011253, "I_y": 182.6, "density": 88.3},
    "HE320A": {"A": 0.012437, "I_y": 229.3, "density": 97.6},
    "HE340A": {"A": 0.013347, "I_y": 276.9, "density": 104.8},
    "HE360A": {"A": 0.014276, "I_y": 330.9, "density": 112.1},
    "HE400A": {"A": 0.015898, "I_y": 450.7, "density": 124.8},
    "HE450A": {"A": 0.017803, "I_y": 637.2, "density": 139.8},
    "HE500A": {"A": 0.019754, "I_y": 869.7, "density": 155.1},
    "HE550A": {"A": 0.021176, "I_y": 1119, "density": 166.2},
    "HE600A": {"A": 0.022646, "I_y": 1412, "density": 177.8},
    "HE650A": {"A": 0.024164, "I_y": 1752, "density": 189.7},
    "HE700A": {"A": 0.026048, "I_y": 2153, "density": 204.5},
    "HE800A": {"A": 0.028583, "I_y": 3034, "density": 224.4},
    "HE900A": {"A": 0.032053, "I_y": 4221, "density": 251.6},
    "HE1000A": {"A": 0.034685, "I_y": 5538, "density": 272.3},
    "HE100B": {"A": 0.002604, "I_y": 4.495, "density": 20.4},
    "HE120B": {"A": 0.003401, "I_y": 8.644, "density": 26.7},
    "HE140B": {"A": 0.004296, "I_y": 15.09, "density": 33.7},
    "HE160B": {"A": 0.005425, "I_y": 24.92, "density": 42.6},
    "HE180B": {"A": 0.006525, "I_y": 38.31, "density": 51.2},
    "HE200B": {"A": 0.007808, "I_y": 56.96, "density": 61.3},
    "HE220B": {"A": 0.009104, "I_y": 80.91, "density": 71.5},
    "HE240B": {"A": 0.010599, "I_y": 112.6, "density": 83.2},
    "HE260B": {"A": 0.011844, "I_y": 149.2, "density": 93.0},
    "HE280B": {"A": 0.013136, "I_y": 192.7, "density": 103.1},
    "HE300B": {"A": 0.014908, "I_y": 251.7, "density": 117.0},
    "HE320B": {"A": 0.016134, "I_y": 308.2, "density": 126.7},
    "HE340B": {"A": 0.01709, "I_y": 366.6, "density": 134.2},
    "HE360B": {"A": 0.0181, "I_y": 431.9, "density": 141.8},
    "HE400B": {"A": 0.0198, "I_y": 576.8, "density": 155.3},
    "HE450B": {"A": 0.0218, "I_y": 798.9, "density": 171.1},
    "HE500B": {"A": 0.0239, "I_y": 1072, "density": 187.3},
    "HE550B": {"A": 0.0254, "I_y": 1367, "density": 199.4},
    "HE600B": {"A": 0.027, "I_y": 1710, "density": 211.9},
    "HE650B": {"A": 0.0286, "I_y": 2106, "density": 224.8},
    "HE700B": {"A": 0.0306, "I_y": 2569, "density": 240.5},
    "HE800B": {"A": 0.0334, "I_y": 3591, "density": 262.3},
    "HE900B": {"A": 0.0371, "I_y": 4941, "density": 291.5},
    "HE1000B": {"A": 0.04, "I_y": 6447, "density": 314.0}
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
    material_split = material_input.split("/")
    for i in material_split:
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

def extract_beam(beam_input):
    beam = beam_input
    

    beam_type = ifcopenshell.util.element.get_type(beam)
    profile = "Beam"
    profile_shape = "Test"


    psets_dict = ifcopenshell.util.element.get_psets(beam_type)
    psets = ifcopenshell.util.element.get_psets(beam)
    psets_props = ifcopenshell.util.element.get_psets(beam, psets_only=True)
    psets_quantities = ifcopenshell.util.element.get_psets(beam, qtos_only=True)
    #print(psets)
    #profile = psets_props['Pset_BeamCommon']['Reference']
    #profile_shape = psets_props['Other']['Family Name']

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
        #print(material)
        material_name, material_letter, quality = check_material(material)
        quality_short = material_letter + str(quality)
    
    #representations = beam.Representation.Representations
    
    

    x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
    y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
    z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)

    dims0 = [x,y,z]
    dims = sorted(dims0)

    
    


    if profile in steel_profiles.keys():    
        area = round(steel_profiles[profile]["A"],3)
        volume = round(dims[-1]*area,3)
        Iy = steel_profiles[profile]["I_y"]
    else:
        area = round(ifcopenshell.util.shape.get_area(shape.geometry),2) / 1000
        volume = dims[-1]*area
        if material_name == "Concrete":
            if x == y or "circular" or "round" in profile_shape.lower():
                Iy = round(numpy.pi/4 * x**4, 2) #divided by e6
            else:
                Iy = round(1/12 * x * y**3, 2)
        else: 
            Iy = None
        

    #print(beam_input, id, x,y,z,profile, material) 
    beam_dict ={" Guid ": element_guid , " Element ": "IfcBeam" , " Material ": material_name , "Quality": quality, "Material label": quality_short, " Length [ m ]": x ," Height [ m ]": z , " Width [ m ]": y , "Volume [m3]" : volume, "Area [m2]": area, "Profile" :profile, "Iy e-6 [mm4]": Iy}
    if material_name == "N/A":
        None
    elif x < 0.5: 
        None
    else:
        extracted_elements.append(beam_dict)
    
def extract_column(col_input):

    col = col_input
    col_type = ifcopenshell.util.element.get_type(col)
    

    psets_dict = ifcopenshell.util.element.get_psets(col_type)
    psets = ifcopenshell.util.element.get_psets(col)
    psets_props = ifcopenshell.util.element.get_psets(col, psets_only=True)
    psets_quantities = ifcopenshell.util.element.get_psets(col, qtos_only=True)
    #profile = psets_props['Pset_ColumnCommon']['Reference']

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

    profile = "Column"
    profile_shape = "Test"


    if profile in steel_profiles.keys():    
        area = round(steel_profiles[profile]["A"],3)
        volume = round(dims[-1]*area,3)
        Iy = steel_profiles[profile]["I_y"]
    else:
        area = round(ifcopenshell.util.shape.get_area(shape.geometry),2) / 1000           #vurdere å fjerne
        volume = dims[-1]*area
        if "rectangular" or "quadratic" in profile_shape.lower():
            Iy = round(1/12 * x * y**3 ,2) #divided by e6 
        elif "circular" or "round" in profile_shape.lower():
            Iy = round(numpy.pi/4 * x**4 ,2) #divided by e6
        else:
            Iy = None

    

    #print(col_input,id, x,y,z,profile, material) 
    col_dict ={" Guid ": element_guid , " Element ": "IfcColumn" , " Material ": material_name ,"Material label": quality_short,  "Quality": quality, " Length [ m ]": x ," Height [ m ]": z , " Width [ m ]": y , "Volume [m3]" : volume, "Area [m2]": area, "Profile" :profile, "Iy e-6 [mm4]": Iy}
    if material_name == "N/A":
        None
    elif x < 0.5: 
        None
    else:
        extracted_elements.append(col_dict)
    

def extract_slab(slab_input):
    slab = slab_input
    slab = ifc_file.by_type(slab_input)[index]
    #print(slab)
    slab_type = ifcopenshell.util.element.get_type(slab)
    #print(slab_type)
    psets = ifcopenshell.util.element.get_psets(slab)
    #print(psets)

    """
    if "Hollow Core Slab" in str(products[i]):
        hc_slab = ifc_file.by_type("IfcElementAssembly")[index]

        pset_hollowcore= ifcopenshell.util.element.get_psets(hc_slab)    
        #print(pset_hollowcore)
        length = round(pset_hollowcore['Data(Type)']['Element Length'],2)
        #thickness = round(psets['Dimensions']['Thickness'],2)
        #length = volume / thickness
        width = round(pset_hollowcore['Data(Type)']['Element Width'],2)
    else: 
        None
        
        #settings = geom.settings()
        settings = geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)
        settings.set(settings.USE_BREP_DATA, True)  # Use BREP for better geometric processing
        settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, True)
        shape = geom.create_shape(settings, slab)
        

        element_guid = shape.guid
        element_id = shape.id
        guid = ifc_file.by_guid(shape.guid)

        x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
        y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
        z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)

        dims0 = [x,y,z]
        dims = sorted(dims0)

        #thickness = dims[0]
        length =  dims[-1]
        width = dims[-2]
        #area = length * width
        #volume = area*thickness
        #area = round(volume / length,2)
    
    """
    # Get all properties and quantities of the wall, including inherited type properties
    #psets = ifcopenshell.util.element.get_psets(slab)

    # Get only quantities and not properties
    psets_quantities = ifcopenshell.util.element.get_psets(slab, qtos_only=True)
    #print(psets_quantities)
    psets_props = ifcopenshell.util.element.get_psets(slab, psets_only=True)
    #print(psets_props)
    #type = psets_props['Pset_ReinforcementBarPitchOfSlab']['Description']

    #print(psets_quantities)

    #length = 

    area = round(psets['Dimensions']['Area'],2)
    volume = round(psets['Dimensions']['Volume'],2)
    thickness = round(psets['Dimensions']['Thickness'],2)

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
    material_description = psets['Identity Data']['Material']
    #print(material_description)

# Process material:
    material_info = check_material(material_description)
    material_name = material_info[0]

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
    

    
    #for style in styles:
    #    material = style.original_name()
    #    material_name, material_letter, quality = check_material(material)
    #    quality_short = material_letter + str(quality)
    #    if material_name == "N/A":
     #       material_name = "Concrete"
     #   else:
     #       None

    
    x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
    y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
    z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)

    dims0 = [x,y,z]
    dims = sorted(dims0)

    #thickness = dims[0]
    length =  dims[-1]
    width = dims[-2]
    #area = length * width
    #volume = area*thickness

    #area = round(volume / length,2)

   

    

    #print(slab_input,id, x,y,z, material) 
    slab_dict = {" Guid ": element_guid , " Element ": "IfcSlab" , " Material ": material_info[0] , "Quality": material_info[2],"Material label": material_info[1], " Length [ m ]": length ," Height [ m ]": thickness , " Width [ m ]": width , "Volume [m3]" : volume, "Area [m2]": area}
    #if material_name == "N/A" or length < 0.5 or width < 0.5:
    #    None
    #else:
    #print(slab_dict)
    extracted_elements.append(slab_dict)



def extract_hollow_core_slab(hollow_core_slab):
    
    txt = str(hollow_core_slab)
    split = txt.split("'")
    guid = split[1]
    
    
    slab_type = ifcopenshell.util.element.get_type(hollow_core_slab)
    #print(slab_type)
    psets = ifcopenshell.util.element.get_psets(hollow_core_slab)
   
    #print(psets)
    
    # Get all properties and quantities of the wall, including inherited type properties
    #psets = ifcopenshell.util.element.get_psets(slab)

    # Get only quantities and not properties
    psets_quantities = ifcopenshell.util.element.get_psets(hollow_core_slab, qtos_only=True)
    #print(psets_quantities)
    psets_props = ifcopenshell.util.element.get_psets(hollow_core_slab, psets_only=True)
    #print(psets_props)
    #type = psets_props['Pset_ReinforcementBarPitchOfSlab']['Description']

    #print(psets_quantities)
    
    #area = round(psets['Dimensions']['Area'],2)
    #volume = round(psets['Dimensions']['Volume'],2)
    #length = round(psets['Data(Type)']['Element Length'],2)
    #thickness = round(psets['Dimensions']['Thickness'],2)
    #length = volume / thickness
    width = round(psets['BaseQuantities']['Width'],2) / 1000
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
    """
    
    thickness_norconsult = 0.265
    #print(slab_input,id, x,y,z, material) 
    #slab_dict = {" Guid ": element_guid , " Element ": "IfcSlab" , " Material": material_info[0] , "Quality": material_info[2],"Material label": material_info[1], " Length [ m ]": length ," Height [ m ]": thickness , " Width [ m ]": width , "Volume [m3]" : volume, "Area [m2]": area}
    slab_dict = {" Guid ": guid , " Element ": "IfcSlab" , " Material ": "Hollow Core Concrete" , "Quality": None,"Material label": None, " Length [ m ]": None ," Height [ m ]": thickness_norconsult , " Width [ m ]": width , "Volume [m3]" : None, "Area [m2]": None}
    
    #if material_name == "N/A" or length < 0.5 or width < 0.5:
    #    None
    #else:
    #print(slab_dict)
    extracted_elements.append(slab_dict)

def extract_wall(wall_input):
    wall = wall_input
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
    

    
    wall_dict = {" Guid ": element_guid , " Element ": "IfcWall" , " Material ": material_name , "Quality": quality,"Material label": quality_short, " Length [ m ]": length," Height [ m ]": height , " Width [ m ]": thickness , "Volume [m3]" : volume, "Area [m2]": area}
    #print(wall_input,id, x,y,z, material)
    #if material_name == "N/A" or height < 0.5 or thickness < 0.5:
    #    None
    #else:
    extracted_elements.append(wall_dict)

def extract_window_door(wall_input):
    wall = wall_input
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
    

    
    wall_dict = {" Guid ": guid , " Element ": wall_input , " Material ": material_name , "Quality": quality, "Material label": quality_short, " Length [ m ]": thickness," Height [ m ]": height , " Width [ m ]": length , "Volume [m3]" : volume, "Area [m2]": area}
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

#extract_hollow_core_slab(test,0)

#print(products)
#print(elements_sorted)
#print(len(elements_sorted))

print(products)

for product in products:
    id = product.is_a()
    allowed_names = {"IfcBeam", "IfcColumn", "IfcWall", "IfcElementAssembly", "IfcWallType", "IfcWallStandardCase", "IfcSlab","IfcDoor", "IfcWindow"}
    if id in allowed_names:
        element = id
        if element == "IfcBeam":
            extract_beam(product)
            i_beam +=1

        elif element == "IfcColumn":
            extract_column(product)
            i_col += 1

        elif element == "IfcSlab":
            extract_slab(product)
            #i_slab +=1

        elif element == "IfcElementAssembly":
            
            if "slab" in product.Name.lower():
                extract_hollow_core_slab(product)        
                i_hollow_core_slab +=1
            
            else:
                None

        elif element == "IfcWall" or element == "IfcWallType" or element == "IfcWallStandardCase":
            extract_wall(product)
            i_wall +=1

        elif element == "IfcWindow":
            extract_window_door(product)
            i_window +=1

        elif element == "IfcDoor":
            extract_window_door(product) #same function
            i_door +=1
   
    
#extracted_elements_sorted = extracted_elements.sort_values(" Element ")



ext_elements_df = pd.DataFrame(extracted_elements)
ext_elements_df_sort = ext_elements_df.sort_values(" Element ")
ext_elements_df_sort.to_excel(r'C:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\Excel\Test Norconsult fil.xlsx')


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