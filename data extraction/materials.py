import ifcopenshell
ifc_file = ifcopenshell.open(r'c:\Users\e_ski\OneDrive\Documents\NTNU\10. semester\Masteroppgave\IFC\Tennebekk\22018_TennebekkBuss_RIB.ifc')
products = ifc_file.by_type('IfcProduct')

material_list = []

for product in products:
    if product.HasAssociations:
        for i in product.HasAssociations:
            if i.is_a('IfcRelAssociatesMaterial'):

                if i.RelatingMaterial.is_a('IfcMaterial'):
                    material_list.append(i.RelatingMaterial.Name)

                if i.RelatingMaterial.is_a('IfcMaterialList'):
                    for materials in i.RelatingMaterial.Materials:
                        material_list.append(materials.Name)

                if i.RelatingMaterial.is_a('IfcMaterialLayerSetUsage'):
                    for materials in i.RelatingMaterial.ForLayerSet.MaterialLayers:
                        material_list.append(materials.Material.Name)

print (material_list)