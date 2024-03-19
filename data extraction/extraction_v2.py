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
    elements.append(id)

extracted_elements = []


def extract_beam(beam_input,index):
    beam = ifc_file.by_type(beam_input)[index]
    beam_type = ifcopenshell.util.element.get_type(beam)
    
    psets_dict = ifcopenshell.util.element.get_psets(beam_type)
    psets = ifcopenshell.util.element.get_psets(beam)
    psets_props = ifcopenshell.util.element.get_psets(beam, psets_only=True)
    psets_quantities = ifcopenshell.util.element.get_psets(beam, qtos_only=True)
    profile = psets_props['Pset_BeamCommon']['Reference']

    settings = geom.settings()
    shape = geom.create_shape(settings, beam)

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

    x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
    y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
    z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)

    #print(beam_input, id, x,y,z,profile, material) 
    beam_dict ={" Guid ": guid , " Name ": beam_input , " Material ": material , " Length [ m ]": x ," Height [ m ]": z , " Width [ m ]": y , "Profile" :profile}
    extracted_elements.append(beam_dict)
    
def extract_column(col_input,index):
    col = ifc_file.by_type(col_input)[index]
    col_type = ifcopenshell.util.element.get_type(col)
    
    psets_dict = ifcopenshell.util.element.get_psets(col_type)
    psets = ifcopenshell.util.element.get_psets(col)
    psets_props = ifcopenshell.util.element.get_psets(col, psets_only=True)
    psets_quantities = ifcopenshell.util.element.get_psets(col, qtos_only=True)
    profile = psets_props['Pset_ColumnCommon']['Reference']

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
        
    x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
    y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
    z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)

    #print(col_input,id, x,y,z,profile, material) 
    col_dict ={" Guid ": guid , " Name ": col_input , " Material ": material , " Length [ m ]": x ," Height [ m ]": z , " Width [ m ]": y , "Profile" :profile}
    extracted_elements.append(col_dict)

def extract_slab(slab_input,index):
    slab = ifc_file.by_type("IfcSlab")[index]
    slab_type = ifcopenshell.util.element.get_type(slab)

    psets_dict = ifcopenshell.util.element.get_psets(slab_type)


    # Get all properties and quantities of the wall, including inherited type properties
    psets = ifcopenshell.util.element.get_psets(slab)

    # Get only quantities and not properties
    psets_quantities = ifcopenshell.util.element.get_psets(slab, qtos_only=True)
    psets_props = ifcopenshell.util.element.get_psets(slab, psets_only=True)
    #type = psets_props['Pset_ReinforcementBarPitchOfSlab']['Description']

    settings = geom.settings()
    shape = geom.create_shape(settings, slab)


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



    x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
    y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
    z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)

    #print(slab_input,id, x,y,z, material) 
    slab_dict ={" Guid ": guid , " Name ": slab_input , " Material ": material , " Length [ m ]": x ," Height [ m ]": z , " Width [ m ]": y }
    extracted_elements.append(slab_dict)

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



    x = round(ifcopenshell.util.shape.get_x(shape.geometry),2)
    y = round(ifcopenshell.util.shape.get_y(shape.geometry),2)
    z = round(ifcopenshell.util.shape.get_z(shape.geometry),2)

    #print(wall_input,id, x,y,z, material)
    wall_dict ={" Guid ": guid , " Name ": wall_input , " Material ": material , " Length [ m ]": x ," Height [ m ]": z , " Width [ m ]": y }
    extracted_elements.append(wall_dict)


i_beam = 0
i_col = 0
i_slab = 0
i_wall = 0

for i in range(len(elements)-1):
    element = elements[i]
    if element == "IfcBeam":
        extract_beam(element,i_beam)
        i_beam +=1
    elif element == "IfcColumn":
        extract_column(element,i_col)
        i_col += 1

    elif element == "IfcSlab":
        extract_slab(element,i_slab)
        i_slab +=1

    elif element == "IfcWall":
        extract_wall(element,i_wall)
        i_wall +=1
    else:
        None

ext_elements_df = pd.DataFrame(extracted_elements)
ext_elements_df.to_excel(r'c:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\Excel\Test extraction.xlsx')


# Add desired quantites and properties to the DataFrame
#element_dict ={" Guid ": guid , " Name ": name , " Material ": material , " Length [ mm ]": length ," Height [ mm ]": height , " Width [ mm ]": width ," Cross section area [m^2]": cross_section_area , " Volume [ m ^3]": volume , " Cross section name ":object_type ," Location ": location_str , " Latitude ": lat_float , " Longitude ":long_float }
#quantites.append( element_dict )
#elements_df = pd.DataFrame ( quantites )
# Export DataFrame to Excel
#elements_df.to_excel (" C:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\Excel")                           


"""""
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