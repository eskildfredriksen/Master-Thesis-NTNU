# IFC Data Extraction
# Import packages
import pandas as pd
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.unit
import ifcopenshell.util.shape
import ifcopenshell.util.element

# Store IFC file as a variable
ifc_file = ifcopenshell.open ("C:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\IFC\Tennebekk")

# Settings
settings = ifcopenshell . geom . settings ()
settings . set ( settings . DISABLE_OPENING_SUBTRACTIONS , True )

# Units
unit_scale = ifcopenshell . util . unit . calculate_unit_scale ( ifc_file )

global_unit_assignments = ifc_file . by_type (" IfcUnitAssignment ")
global_length_unit = [u for ua in global_unit_assignments for u in ua . Units if u .is_a () in (' IfcSIUnit ', ' IfcConversionBasedUnit ') and u . UnitType ==' LENGTHUNIT'][ -1]
# print ( global_length_unit )

global_volume_unit = [u for ua in global_unit_assignments for u in ua . Units if u .is_a () in (' IfcSIUnit ', ' IfcConversionBasedUnit ') and u . UnitType ==' VOLUMEUNIT'][ -1]
# print ( global_volume_unit )

global_area_unit = [u for ua in global_unit_assignments for u in ua . Units if u. is_a() in (' IfcSIUnit ', ' IfcConversionBasedUnit ') and u . UnitType ==' AREAUNIT '][ -1]
# print ( global_area_unit )

global_mass_unit = [u for ua in global_unit_assignments for u in ua . Units if u. is_a() in (' IfcSIUnit ', ' IfcConversionBasedUnit ') and u . UnitType ==' MASSUNIT '][ -1]
# print ( global_mass_unit )

# Extract IfcBeams and IfcColumns
LB_elements = []
for element_type in [' IfcBeam ',' IfcColumn ']:
    LB_elements . extend ( ifc_file . by_type ( element_type ))

quantites =[]
for element in LB_elements :
    elem = ifcopenshell . geom . create_shape ( settings , element )
    # psets = ifcopenshell . util . element . get_psets ( element , qtos_only = True ) # quantitysets
    # psets = ifcopenshell . util . element . get_psets ( element ) # property sets

# Quantites
volume = ifcopenshell . util . shape . get_volume ( elem . geometry )
x= ifcopenshell . util . shape . get_x ( elem . geometry ) / unit_scale
y= ifcopenshell . util . shape . get_y ( elem . geometry ) / unit_scale
z= ifcopenshell . util . shape . get_z ( elem . geometry ) / unit_scale

guid = element . GlobalId
name = element . Name
owner_history = element . OwnerHistory
moment_of_interia = float (" nan ")
object_type = element . ObjectType

# Material
# material = ifcopenshell . util . element . get_material ( element , should_skip_usage =True )
# material_name = material . Name

material = None
if element . HasAssociations :
    for association in element . HasAssociations :
        # Check if the association is of type IfcRelAssociatesMaterial
        if association . is_a (" IfcRelAssociatesMaterial ") :
            # Get the associated material
            if association . RelatingMaterial :
                if hasattr ( association . RelatingMaterial , " Name ") :
                    material = association . RelatingMaterial . Name
            break


if element . is_a (" IfcBeam ") :
    cross_section_area =( volume / x) *1000 #m ^2
    length = x # mm
    height = z # mm
    width = y # mm

elif element . is_a (" IfcColumn ") :
    cross_section_area =( volume /z ) *1000 #m ^2
    length = z # mm
    height =y # mm
    width = x # mm

# GEOLOCATION
postal_address = ifc_file . by_type (" Ifcpostaladdress ")
site = ifc_file . by_type (" IfcSite ")
                           
for j in postal_address : # Note : The name of the attribute may not neccessarily correspond to the string or value attached
    region = j. Region if hasattr (j , " Region ") else None
    addresslines = j. AddressLines if hasattr (j , " AddressLines ") else None
    country = j. Country if hasattr (j , " Country ") else None
    postal_code = j . PostalCode if hasattr (j , " PostalCode ") else None
    postal_box = j. PostalBox if hasattr (j , " PostalBox ") else None
    town = j. Town if hasattr (j , " Town ") else None

# address_attributes = postal_address [0]. get_info () . keys ()
# site_attributes = site [0]. get_info () . keys ()

location =[ region , postal_code , country ]
location_str =" ,". join ( location )

"""
if all ( item is None for item in location ):
location_str = "" # Assign an empty string if all elements are None . No
location assigned .
else :
location_str = " ,". join ( str ( item ) if item is not None else "" for item in
location )
"""

for s in site :
    long = s. RefLongitude if hasattr (s , " RefLongitude ") else None
    lat = s. RefLatitude if hasattr (s , " RefLatitude ") else None
    elev = s. RefElevation if hasattr (s , " RefElevation ") else None
    ad = s. SiteAddress if hasattr (s , " SiteAddress ") else None

    if long :
        long_float = long [0] + ( long [1] / 60) + ( long [2] / 3600) + long [3] /(3600 * 1000000)

    if lat :
        lat_float = lat [0] + ( lat [1] / 60) + ( lat [2] / 3600) + lat [3] / (3600 * 1000000)

# Add desired quantites and properties to the DataFrame
element_dict ={" Guid ": guid , " Name ": name , " Material ": material , " Length [ mm ]": length ," Height [ mm ]": height , " Width [ mm ]": width ," Cross section area [m^2]": cross_section_area , " Volume [ m ^3]": volume , " Cross section name ":object_type ," Location ": location_str , " Latitude ": lat_float , " Longitude ":long_float }
quantites.append( element_dict )
elements_df = pd.DataFrame ( quantites )
# Export DataFrame to Excel
elements_df.to_excel (" C:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\Excel")                           