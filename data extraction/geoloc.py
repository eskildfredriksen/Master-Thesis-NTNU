import ifcopenshell
import ifcopenshell
import ifcopenshell.geom as geom
import ifcopenshell.util.shape
import ifcopenshell.util.unit as unit 
import ifcopenshell.util.shape
import ifcopenshell.util.element
import numpy
import pandas as pd
import ifcopenshell.util.element

ifc_file = ifcopenshell.open(r'c:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\IFC\Tennebekk\22018_TennebekkBuss_RIB.ifc')




# GEOLOCATION
postal_address = ifc_file.by_type ("Ifcpostaladdress")
site = ifc_file.by_type ("IfcSite")

print(site)
                           
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

filtered_location = [loc for loc in location if loc is not None]

location_str =" , ".join(filtered_location)

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
