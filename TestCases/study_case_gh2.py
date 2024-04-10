import sys
sys.path.append('./Matching')
from matching import Matching
import pandas as pd
import numpy as np
import sys
import helper_methods_LCA as lca
import helper_methods as hm
import helper_methods_PDF as hmpdf
from matching import run_matching
# read input argument from console
#NOTE TO SVERRE: DONT KNOW IF THIS IS NEEDED?
"""
method_name = sys.argv[1]
demand_path = sys.argv[2]
supply_path = sys.argv[3]
result_path = sys.argv[4]
constraint_string = sys.argv[5]
"""
######################

#==========USER FILLS IN============#
#Constants
#TODO: FIND ALL DEFAULT VALUES FOR CONSTANTS, especially for price
constants = {
    "CONCRETE_GWP": 28.9,      
    "CONCRETE_REUSE_GWP": 2.25,        
    "CONCRETE_DENSITY": 491.0,  
    "CONCRETE_PRICE": 435, 
    "CONCRETE_REUSE_PRICE" : 100,
    
    "CONCRETE - B35_GWP": 28.9,      
    "CONCRETE - B35_REUSE_GWP": 2.25,        
    "CONCRETE - B35_DENSITY": 491.0,  
    "CONCRETE - B35_PRICE": 435, 
    "CONCRETE - B35_REUSE_PRICE" : 100,

    "STEEL - S355_GWP": 28.9,      
    "STEEL - S355_REUSE_GWP": 2.25,        
    "STEEL - S355_DENSITY": 491.0,  
    "STEEL - S355_PRICE": 435, 
    "STEEL - S355_REUSE_PRICE" : 100,

    "STEEL - S235_GWP": 28.9,      
    "STEEL - S235_REUSE_GWP": 2.25,        
    "STEEL - S235_DENSITY": 491.0,  
    "STEEL - S235_PRICE": 435, 
    "STEEL - S235_REUSE_PRICE" : 100,

    "SLAB_GWP": 28.9,      
    "SLAB_REUSE_GWP": 2.25,        
    "SLAB_DENSITY": 491.0,  
    "SLAB_PRICE": 435, 
    "SLAB_REUSE_PRICE" : 100,

    "BEAM_GWP": 28.9,      
    "BEAM_REUSE_GWP": 2.25,        
    "BEAM_DENSITY": 491.0,  
    "BEAM_PRICE": 435, 
    "BEAM_REUSE_PRICE" : 100,

    "WINDOW_GWP": 28.9,      
    "WINDOW_REUSE_GWP": 2.25,        
    "WINDOW_DENSITY": 491.0,  
    "WINDOW_PRICE": 435, 
    "WINDOW_REUSE_PRICE" : 100,

    "DOOR_GWP": 28.9,      
    "DOOR_REUSE_GWP": 2.25,        
    "DOOR_DENSITY": 491.0,  
    "DOOR_PRICE": 435, 
    "DOOR_REUSE_PRICE" : 100,

    "TIMBER_GWP": 28.9,       # based on NEPD-3442-2053-EN
    "TIMBER_REUSE_GWP": 2.25,        # 0.0778*28.9 = 2.25 based on Eberhardt
    "TRANSPORT_GWP": 96.0,    # TODO kg/m3/t based on ????
    "TIMBER_DENSITY": 491.0,  # kg, based on NEPD-3442-2053-EN

    "STEEL_GWP": 800, #Random value
    "STEEL_REUSE_GWP": 4, #Random value
    "VALUATION_GWP": 0.6, #In kr:Per kg CO2, based on OECD
    "TIMBER_PRICE": 435, #Per m^3 https://www.landkredittbank.no/blogg/2021/prisen-pa-sagtommer-okte-20-prosent/
    "TIMBER_REUSE_PRICE" : 100, #Per m^3, Random value
    "STEEL_PRICE": 500, #Per m^2, Random value
    "STEEL_REUSE_PRICE": 200, #Per m^2, Random value
    "PRICE_TRANSPORTATION": 3.78, #Price per km per tonn. Derived from 2011 numbers on scaled t0 2022 using SSB
    "STEEL_DENSITY": 7850,


    ########################
    "Project name": "Sognsveien 17",
    "Metric": "GWP",
    #"Algorithms": ["bipartite", "greedy_plural", "bipartite_plural", "bipartite_plural_multiple"],
    "Algorithms": ["greedy_plural"],
    "Include transportation": False,
    "Site latitude": "59.94161606",
    "Site longitude": "10.72994518",
    "Demand file location": r"./TestCases/Data/CSV/test_demand_IFC.xlsx",
    "Supply file location": r"./TestCases/Data/CSV/test_supply_IFC.xlsx",
    #"Demand file location": r"./TestCases/Data/CSV/test_demand_IFC.csv",
    #"Supply file location": r"./TestCases/Data/CSV/test_supply_IFC.csv",

    "tol_1D_area" : "0.9",
    "tol_1D_moment_of_inertia" : "0.9",
    "tol_1D_length" : "0.9",
    "tol_1D_width" : "0.9",
    "tol_1D_height" : "0.9",  
    "tol_1D_quality" : "0.9",

    "tol_2D_width" : "0.9",
    "tol_2D_height" : "0.9",
    "tol_2D_quality" : "0.9",

    "tol_3D_length" : "0.9",
    "tol_3D_width" : "0.9",
    "tol_3D_height" : "0.9",
    "tol_3D_quality" : "0.9",

    "constraint_dict": {'Area' : '>=', 'Moment of Inertia' : '>=', 'Length' : '>=', 'Width' : '>=', 'Height' : '>=', 'Material': '==', 'Quality' : '>='},
    "constraint2D_dict" :  {'Width' : '==', 'Height' : '==', 'Material' : '==', 'Quality' : '>='},
    "constraint3D_dict" :  {'Length' : '>=','Width' : '==', 'Height' : '==', 'Material' : '==', 'Quality' : '>='}
}
#========================#
#Generating dataset
#===================
supply_coords = pd.DataFrame(columns = ["Location", "Latitude", "Longitude"])

tiller = ["Tiller", "63.3604", "10.4008"]
gjovik = ["Gjovik", "60.8941", "10.5001"]
orkanger = ["Orkanger", "63.3000", "9.8468"]
storlien = ["Storlien", "63.3160", "12.1018"]

supply_coords.loc[len(supply_coords)] = tiller
supply_coords.loc[len(supply_coords)] = gjovik
supply_coords.loc[len(supply_coords)] = orkanger
supply_coords.loc[len(supply_coords)] = storlien



materials = ["Timber", "Steel", "Window", "Door", "Slab", "Concrete - B35", "Steel - S355", "Steel - S235"]
name = ["IfcBeam", "IfcColumn", "IfcSlab"]

#GENERATE FILE
#============
"""supply = hmpdf.create_random_data_supply_pdf_reports(supply_count = 10, length_min = 1.0, length_max = 10.0, width_min = 1.0, width_max = 10.0, height_min = 1.0, height_max = 10.0, area_min = 0.15, area_max = 0.30, materials = materials, supply_coords = supply_coords)
demand = hmpdf.create_random_data_demand_pdf_reports(demand_count = 10, length_min = 1.0, length_max = 10.0, width_min = 1.0, width_max = 10.0, height_min = 1.0, height_max = 10.0, area_min = 0.15, area_max = 0.30, materials = materials)
hm.export_dataframe_to_csv(supply, r"" + "./TestCases/Data/CSV/test_supply.csv")
hm.export_dataframe_to_csv(demand, r"" + "./TestCases/Data/CSV/test_demand.csv")
"""
#========================================
score_function_string = hm.generate_score_function_string(constants)
supply = hm.import_dataframe_from_file(r"" + constants["Supply file location"], index_replacer = "S")
demand = hm.import_dataframe_from_file(r"" + constants["Demand file location"], index_replacer = "D")


#hm.create_graph(supply, demand, "Length", number_of_intervals= 2, save_filename = r"C:\Users\sigur\Downloads\test.png")

constraint_dict = constants["constraint_dict"]
constraint2D_dict = constants["constraint2D_dict"]
constraint3D_dict = constants["constraint3D_dict"]
#Add necessary columns to run the algorithm
supply = hmpdf.add_necessary_columns_pdf(supply, constants)
demand = hmpdf.add_necessary_columns_pdf(demand, constants)

m= Matching(demand, supply, score_function_string, constraints = constraint_dict, constraints2D = constraint2D_dict, constraints3D = constraint3D_dict, solution_limit=60)

m.match_greedy(plural_assign=True)
print(m.weights)
simple_pairs = m.pairs
m.calculate_result()
simple_results = m.result


print("Simple pairs:")
print(simple_pairs)

print()
print("Simple results")
print(simple_results)