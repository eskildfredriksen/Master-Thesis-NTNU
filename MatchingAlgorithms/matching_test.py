from matching import Matching, run_matching #, TIMBER_GWP, REUSE_GWP_RATIO
import pandas as pd
import random
import time
import helper_methods as hm
    

### Test with just few elements

demand = pd.DataFrame(columns = ['Length', 'Area', 'Inertia_moment', 'Height'])
supply = pd.DataFrame(columns = ['Length', 'Area', 'Inertia_moment', 'Height', 'Is_new'])
# Add a perfect matching pair
demand.loc['D1'] = {'Material': 1, 'Length': 7.00, 'Area': 0.04, 'Inertia_moment':0.00013, 'Height': 0.20}
supply.loc['R1'] = {'Material': 1, 'Length': 7.00, 'Area': 0.04, 'Inertia_moment':0.00013, 'Height': 0.20, 'Is_new':False}
# Add non-matchable demand
# demand.loc['D2'] = {'Material': 1, 'Length': 13.00, 'Area': 0.001, 'Inertia_moment':0.00001, 'Height': 0.05}
# TODO new inertia moment
demand.loc['D2'] = {'Material': 1, 'Length': 13.00, 'Area': 0.02, 'Inertia_moment':0.00001, 'Height': 0.05}
# Add non-matchable supply
# supply.loc['R2'] = {'Material': 1, 'Length': 0.1, 'Area': 0.04, 'Inertia_moment':0.00013, 'Height': 0.20, 'Is_new':False}
supply.loc['R2'] = {'Material': 1, 'Length': 1.2, 'Area': 0.04, 'Inertia_moment':0.00013, 'Height': 0.20, 'Is_new':False}
# Add element with two good matches, where second slighlty better
demand.loc['D3'] = {'Material': 1, 'Length': 5.00, 'Area': 0.04, 'Inertia_moment':0.00013, 'Height': 0.20}
supply.loc['R3'] = {'Material': 1, 'Length': 5.20, 'Area': 0.042, 'Inertia_moment':0.00015, 'Height': 0.22, 'Is_new':False}
supply.loc['R4'] = {'Material': 1, 'Length': 5.10, 'Area': 0.041, 'Inertia_moment':0.00014, 'Height': 0.21, 'Is_new':False}
# Add element with much bigger match
demand.loc['D4'] = {'Material': 1, 'Length': 8.00, 'Area': 0.1, 'Inertia_moment':0.0005, 'Height': 0.50}
supply.loc['R5'] = {'Material': 1, 'Length': 12.00, 'Area': 0.2, 'Inertia_moment':0.0008, 'Height': 0.8, 'Is_new':False}
# Add supply that can after cut fits perfectly
#demand.loc['D5'] = {'Material': 1, 'Length': 3.50, 'Area': 0.19, 'Inertia_moment':0.0008, 'Height': 0.80}
#demand.loc['D6'] = {'Material': 1, 'Length': 5.50, 'Area': 0.18, 'Inertia_moment':0.00076, 'Height': 0.75}
#supply.loc['R6'] = {'Material': 1, 'Length': 9.00, 'Area': 0.20, 'Inertia_moment':0.0008, 'Height': 0.8, 'Is_new':False}
# Add element that fits the cut from D4 when allowing multiple assignment
demand.loc['D5'] = {'Material': 1, 'Length': 4.00, 'Area': 0.1, 'Inertia_moment':0.0005, 'Height': 0.50}

# create constraint dictionary
constraint_dict = {'Area' : '>=', 'Inertia_moment' : '>=', 'Length' : '>='}
# TODO add 'Material': '=='

hm.print_header('Simple Study Case')


result_simple = run_matching(demand=demand, supply = supply, constraints=constraint_dict, add_new=False, greedy_single=True, bipartite=True,
            milp=False, sci_milp=True)

#FIXME When testing with new elements. Why are the scores (LCA) identical even though we have different matching DataFrames. 

simple_pairs = hm.extract_pairs_df(result_simple)
simple_results = hm.extract_results_df(result_simple)

print(simple_pairs)
print(simple_results)


pass
# result_simple[0]['Match object'].display_graph()

### Add scatter plot:

# import matplotlib.pyplot as plt
# plt.scatter(demand.Length, demand.Area, s=50, c='b', marker="X", label='Demand')
# plt.scatter(supply.Length, supply.Area, s=50, c='r', marker="X", label='Supply') 
# plt.legend()
# plt.xlabel("Length")
# plt.ylabel("Area")
# for i, row in demand.iterrows():
#     plt.annotate(i, (row['Length']-0.6, row['Area']-0.004))
# for i, row in supply.iterrows():
#     if i != "R4":
#         plt.annotate(i, (row['Length']+0.2, row['Area']-0.003))
# plt.show()

# simple_pairs = hm.extract_pairs_df(result_simple)
# print(simple_pairs)


"""
### Test from JSON files with Slettelokka data 
hm.print_header("SLETTELØKKA MATCHING")


DEMAND_JSON = r"MatchingAlgorithms\sample_demand_input.json"
SUPPLY_JSON = r"MatchingAlgorithms\sample_supply_input.json"
RESULT_FILE = r"MatchingAlgorithms\result.csv"
#read and clean demand df
demand = pd.read_json(DEMAND_JSON)
demand_header = demand.iloc[0]
demand.columns = demand_header
demand.drop(axis = 1, index= 0, inplace=True)
demand.reset_index(drop = True, inplace = True)
demand.index = ['D' + str(num) for num in demand.index]

demand.Length *=0.01
demand.Area *=0.0001
demand.Inertia_moment *=0.00000001
demand.Height *=0.01
#read and clean supply df
supply = pd.read_json(SUPPLY_JSON)
supply_header = supply.iloc[0]
supply.columns = supply_header
supply.drop(axis = 1, index= 0, inplace=True)
supply['Is_new'] = False
supply.reset_index(drop = True, inplace = True)
supply.index = ['R' + str(num) for num in supply.index]

# scale input from mm to m
supply.Length *=0.01
supply.Area *=0.0001
supply.Inertia_moment *=0.00000001
supply.Height *=0.01

#--- CREATE AND EVALUATE ---
result_slette = run_matching(demand=demand, supply = supply, constraints=constraint_dict, add_new=False, 
            milp=True, sci_milp = True)


slette_pairs = hm.extract_pairs_df(result_slette)
slette_results = hm.extract_results_df(result_slette)
print(slette_pairs)
print(slette_results)




# ====  Test with randomly generated elements ====
hm.print_header("RANDOM ELEMENTS n_D = 100, n_S = 200")
random.seed(3)

DEMAND_COUNT = 100
SUPPLY_COUNT = 200
MIN_LENGTH = 1.0
MAX_LENGTH = 10.0
MIN_AREA = 0.0025   # 5x5cm
MAX_AREA = 0.25     # 50x50cm

demand = pd.DataFrame()
demand['Length'] = [x/10 for x in random.choices(range(int(MIN_LENGTH*10), int(MAX_LENGTH*10)), k=DEMAND_COUNT)]        # [m], random between the range
demand['Area'] = demand.apply(lambda row: round((random.choice(range(0, int(MAX_AREA*10000)-int(MIN_AREA*10000))) /10000 /MAX_LENGTH * row['Length'] + MIN_AREA) * 10000)/10000, axis=1)        # [m2], random between the range but dependent on the length of the element
demand['Inertia_moment'] = demand.apply(lambda row: row['Area']**(2)/12, axis=1)   # derived from area assuming square section
demand['Height'] = demand.apply(lambda row: row['Area']**(0.5), axis=1)   # derived from area assuming square section
demand.index = ['D' + str(num) for num in demand.index]

supply = pd.DataFrame()
supply['Length'] = [x/10 for x in random.choices(range(int(MIN_LENGTH*10), int(MAX_LENGTH*10)), k=SUPPLY_COUNT)]        # [m], random between the range
supply['Area'] = supply.apply(lambda row: round((random.choice(range(0, int(MAX_AREA*10000)-int(MIN_AREA*10000))) /10000 /MAX_LENGTH * row['Length'] + MIN_AREA) * 10000)/10000, axis=1)        # [m2], random between the range but dependent on the length of the element
supply['Inertia_moment'] = supply.apply(lambda row: row['Area']**(2)/12, axis=1)   # derived from area assuming square section
supply['Height'] = supply.apply(lambda row: row['Area']**(0.5), axis=1)   # derived from area assuming square section
supply['Is_new'] = [False for i in range(SUPPLY_COUNT)]
supply.index = ['R' + str(num) for num in supply.index]

result_rndm1 = run_matching(demand=demand, supply = supply, constraints=constraint_dict, add_new=False, 
            milp=True, sci_milp = False)




### Test with random generated elements
hm.print_header("RANDOM ELEMENTS n_D = 200, n_S = 200")
random.seed(3)

DEMAND_COUNT = 200
SUPPLY_COUNT = 200
MIN_LENGTH = 1.0
MAX_LENGTH = 10.0
MIN_AREA = 0.0025   # 5x5cm
MAX_AREA = 0.25     # 50x50cm

demand = pd.DataFrame()
demand['Length'] = [x/10 for x in random.choices(range(int(MIN_LENGTH*10), int(MAX_LENGTH*10)), k=DEMAND_COUNT)]        # [m], random between the range
demand['Area'] = demand.apply(lambda row: round((random.choice(range(0, int(MAX_AREA*10000)-int(MIN_AREA*10000))) /10000 /MAX_LENGTH * row['Length'] + MIN_AREA) * 10000)/10000, axis=1)        # [m2], random between the range but dependent on the length of the element
demand['Inertia_moment'] = demand.apply(lambda row: row['Area']**(2)/12, axis=1)   # derived from area assuming square section
demand['Height'] = demand.apply(lambda row: row['Area']**(0.5), axis=1)   # derived from area assuming square section
demand.index = ['D' + str(num) for num in demand.index]

supply = pd.DataFrame()
supply['Length'] = [x/10 for x in random.choices(range(int(MIN_LENGTH*10), int(MAX_LENGTH*10)), k=SUPPLY_COUNT)]        # [m], random between the range
supply['Area'] = supply.apply(lambda row: round((random.choice(range(0, int(MAX_AREA*10000)-int(MIN_AREA*10000))) /10000 /MAX_LENGTH * row['Length'] + MIN_AREA) * 10000)/10000, axis=1)        # [m2], random between the range but dependent on the length of the element
supply['Inertia_moment'] = supply.apply(lambda row: row['Area']**(2)/12, axis=1)   # derived from area assuming square section
supply['Height'] = supply.apply(lambda row: row['Area']**(0.5), axis=1)   # derived from area assuming square section
supply['Is_new'] = [False for i in range(SUPPLY_COUNT)]
supply.index = ['R' + str(num) for num in supply.index]

result_rndm2 = run_matching(demand=demand, supply = supply, constraints=constraint_dict, add_new=False, 
            milp=True, sci_milp = False)


"""