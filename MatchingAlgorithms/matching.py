# -*- coding: utf-8 -*-

import sys
from itertools import product, compress
import pandas as pd
import numpy as np
import igraph as ig
import matplotlib.pyplot as plt
from ortools.linear_solver import pywraplp
import numexpr as ne
# import random
# import math

class Matching():
    """Class describing the matching problem, with its constituent parts"""
    def __init__(self, demand, supply, add_new=False, multi=False, constraints = {}):
        self.demand = demand
        if add_new:
            # add perfectly matching new elements to supply
            demand_copy = demand.copy(deep = True)
            demand_copy['Is_new'] = True # set them as new elements
            self.supply = pd.concat((supply, demand_copy), ignore_index=True)
        else:
            self.supply = supply
        self.multi = multi
        self.graph = None
        self.result = None  #saves latest result of the matching
        self.pairs = pd.DataFrame(None, index=self.demand.index.values.tolist(), columns=['Supply_id']) #saves latest array of pairs
        self.incidence = pd.DataFrame(np.nan, index=self.demand.index.values.tolist(), columns=self.supply.index.values.tolist())
        self.constraints = constraints

    def evaluate(self):
        """Populates incidence matrix with weights based on the criteria"""
        # TODO add 'Distance'
        # TODO add 'Price'
        # TODO add 'Material'
        # TODO add 'Density'
        # TODO add 'Imperfections'
        # TODO add 'Is_column'
        # TODO add 'Utilisation'
        # TODO add 'Group'
        # TODO add 'Quality'
        # TODO add 'Max_height' ?
        
        
        match_new = lambda sup_row : row[1] <= sup_row['Length'] and row[2] <= sup_row['Area'] and row[3] <= sup_row['Inertia_moment'] and row[4] <= sup_row['Height'] and sup_row['Is_new'] == True
        match_old = lambda sup_row : row[1] <= sup_row['Length'] and row[2] <= sup_row['Area'] and row[3] <= sup_row['Inertia_moment'] and row[4] <= sup_row['Height'] and sup_row['Is_new'] == False
        for row in self.demand.itertuples():
            bool_match_new = self.supply.apply(match_new, axis = 1).tolist()
            bool_match_old = self.supply.apply(match_old, axis = 1).tolist()
            
            self.incidence.loc[row[0], bool_match_new] = calculate_lca(row[1], self.supply.loc[bool_match_new, 'Area'], is_new=True)
            self.incidence.loc[row[0], bool_match_old] = calculate_lca(row[1], self.supply.loc[bool_match_old, 'Area'], is_new=False)


    def add_pair(self, demand_id, supply_id):
        """Execute matrix matching"""
        # add to match_map:
        self.pairs.loc[demand_id, 'Supply_id'] = supply_id
        # remove already used:
        try:
            self.incidence.drop(demand_id, inplace=True)
            self.incidence.drop(supply_id, axis=1, inplace=True)
        except KeyError:
            pass

    def add_graph(self):
        """Add a graph notation based on incidence matrix"""
        vertices = [0]*len(self.demand.index) + [1]*len(self.supply.index)
        edges = []
        weights = []

        is_na = self.incidence.isna()
        row_inds = np.arange(self.incidence.shape[0]).tolist()
        col_inds = np.arange(len(self.demand.index), len(self.demand.index)+ self.incidence.shape[1]).tolist()
        for i in row_inds:
            combs = list(product([i], col_inds) )
            mask =  ~is_na.iloc[i]
            edges.extend( (list(compress(combs, mask) ) ) )
            weights.extend(list(compress(self.incidence.iloc[i], mask)))
        weights = 1 / np.array(weights)
        graph = ig.Graph.Bipartite(vertices,  edges)
        graph.es["label"] = weights
        graph.vs["label"] = list(self.demand.index)+list(self.supply.index) #vertice names
        self.graph = graph

    def display_graph(self):
        """Plot the graph and matching result"""
        if self.graph:
            # TODO add display of matching
            fig, ax = plt.subplots(figsize=(20, 10))
            ig.plot(
                self.graph,
                target=ax,
                layout=self.graph.layout_bipartite(),
                vertex_size=0.4,
                vertex_label=self.graph.vs["label"],
                palette=ig.RainbowPalette(),
                vertex_color=[v*80+50 for v in self.graph.vs["type"]],
                edge_width=self.graph.es["label"],
                edge_label=[round(1/w,2) for w in self.graph.es["label"]]  # invert weight, to see real LCA
            )
            plt.show()

    def match_bipartite_graph(self):
        """Match using Maximum Bipartite Graphs to find best indyvidual mapping candidates"""
        # TODO multiple assignment won't work.

        # empty result of previous matching:
        self.result = None  
        self.pairs = pd.DataFrame(None, index=self.demand.index.values.tolist(), columns=['Supply_id'])

        if not self.graph:
            self.add_graph()
        bipartite_matching = ig.Graph.maximum_bipartite_matching(self.graph, weights=self.graph.es["label"])
        for match_edge in bipartite_matching.edges():
            self.add_pair(match_edge.source_vertex["label"], match_edge.target_vertex["label"])
        self.result = sum(bipartite_matching.edges()["label"])
        return [self.result, self.pairs]

    def match_bin_packing(self):
        # empty result of previous matching:
        self.result = None  
        self.pairs = pd.DataFrame(None, index=self.demand.index.values.tolist(), columns=['Supply_id'])
        #TODO
        return [self.result, self.pairs]

    def match_nested_loop(self):
        # empty result of previous matching:
        self.result = None  
        self.pairs = pd.DataFrame(None, index=self.demand.index.values.tolist(), columns=['Supply_id'])
        #TODO
        return [self.result, self.pairs]

    def match_knapsacks(self):
        # empty result of previous matching:
        self.result = None  
        self.pairs = pd.DataFrame(None, index=self.demand.index.values.tolist(), columns=['Supply_id'])
        #TODO

        def constraint_inds():
            """Construct the constraint array"""
            rows = self.demand.shape[0]
            cols = self.supply.shape[0]
            bool_arrray = np.full((rows, cols), False)

            # iterate through constraints
            for key, val in self.constraints.items():
                cond_list = []
                for var in self.supply[key]:
                    array = self.demand[key]
                    col = ne.evaluate(f'array {val} var')
                    cond_list.append(col) # add results to cond_list
                conds = np.column_stack(cond_list) # create 2d array of tests
                bool_array = np.logical_or(bool_array, conds)

            constraint_inds = np.transpose(np.where(bool_array)) # convert to nested list if [i,j] indices
            return constraint_inds

        data = {}
        data ['lengths'] = demand.Length.astype(float)
        data['values'] = demand.Area.astype(float)
        
        assert len(data['lengths']) == len(data['values']) # The same check is done indirectly in the dataframe
        data['num_items'] = len(data['values'])
        data['all_items'] = range(data['num_items'])
        data['areas'] = demand.Area

        data['bin_capacities'] = supply.Length # these would be the bins
        data['bin_areas'] = supply.Area.to_numpy(dtype = int)
        data['num_bins'] = len(data['bin_capacities'])
        data['all_bins'] = range(data['num_bins'])

        #get constraint ids
        c_inds = constraint_inds()

        # create solver
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if solver is None:
            print('SCIP Solver is unavailable')
            return

        # --- Variables ---
        # x[i,j] = 1 if item i is backed in bin j. 0 else
        x = {}
        for i in data['all_items']:
            for j in data['all_bins']:
                x[i,j] = solver.BoolVar(f'x_{i}_{j}') 
  
        print(f'Number of variables = {solver.NumVariables()}') 

        # --- Constraints ---
        # each item can only be assigned to one bin
        for i in data['all_items']:
            solver.Add(sum(x[i,j] for j in data['all_bins']) <= 1)

        # the amount packed in each bin cannot exceed its capacity.
        for j in data['all_bins']:
            solver.Add(
                sum(x[i,j] * data['lengths'][i] for i in data['all_items'])
                    <= data['bin_capacities'][j])

        # fix the variables where the area of the element is too small to fit
        # in this case it is the supply element 0 which has an area of 10
        for inds in c_inds:
            i = int(inds[0])
            j = int(inds[1])
            solver.Add(x[i,j] == 0)

        print(f'Number of contraints = {solver.NumConstraints()}')
        # --- Objective ---
        # maximise total value of packed items
        objective = solver.Objective()
        for i in data['all_items']:
            for j in data['all_bins']:
              objective.SetCoefficient(x[i,j], float(data['areas'][i]))      
        objective.SetMaximization()
        # Starting solver
        print('Starting solver')
        status = solver.Solve()
        print('Computation done')
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:

            results = {}
            print('Solution found! \n ------RESULTS-------\n')
            total_length = 0
            for j in data['all_bins']:
                results[j] = []
                print(f'Bin {j}')
                bin_length = 0
                bin_value = 0
                for i in data['all_items']:
                    if x[i, j].solution_value() > 0:
                        results[j].append(i)
                        print(
                            f"Item {i} Length: {data['lengths'][i]} area: {data['areas'][i]}"
                        )
                        bin_length += data['lengths'][i]
                        bin_value += data['areas'][i]
                print(f'Packed bin lengths: {bin_length}')
                print(f'Packed bin value: {bin_value}')
                total_length += bin_length
                print(f'Total packed Lenghtst: {total_length}\n')

        # return the results as a DataFrame like the bin packing problem
        # Or a dictionary. One key per bin/supply, and a list of ID's for the
        # elements which should go within that bin. 

        return [self.result, self.pairs]


# class Elements(pd.DataFrame):
#     def read_json(self):
#         super().read_json()
#         self.columns = self.iloc[0]
#         self.drop(axis = 1, index= 0, inplace=True)
#         self.reset_index(drop = True, inplace = True)


def calculate_lca(length, area, gwp=28.9, is_new=True):
    """ Calculate Life Cycle Assessment """
    # TODO add distance, processing and other impact categories than GWP
    if not is_new:
        gwp = gwp * 0.0778
    lca = length * area * gwp
    return lca


if __name__ == "__main__":

    # read input arguments
    PATH = sys.argv[0]
    #DEMAND_JSON = sys.argv[1]
    #SUPPLY_JSON = sys.argv[2]
    #RESULT_FILE = sys.argv[3]

    DEMAND_JSON = r"MatchingAlgorithms\sample_demand_input.json"
    SUPPLY_JSON = r"MatchingAlgorithms\sample_supply_input.json"
    RESULT_FILE = r"MatchingAlgorithms\result.csv"

    #read and clean demand df
    demand = pd.read_json(DEMAND_JSON)
    demand_header = demand.iloc[0]
    demand.columns = demand_header
    demand.drop(axis = 1, index= 0, inplace=True)
    demand.reset_index(drop = True, inplace = True)
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
    supply.Length *=0.01
    supply.Area *=0.0001
    supply.Inertia_moment *=0.00000001
    supply.Height *=0.01

    import time

    matching = Matching(demand, supply, add_new=True, multi=False)
    
    start = time.time()
    matching.evaluate()
    end = time.time()
    print("Weight evaluation execution time: "+str(round(end - start,3))+"sec")

    start = time.time()
    matching.match_bipartite_graph()
    end = time.time()
    print(f"Matched: {len(matching.pairs['Supply_id'].unique())} to {matching.pairs['Supply_id'].count()} elements ({100*matching.pairs['Supply_id'].count()/len(demand)}%), resulting in LCA (GWP): {round(matching.result, 2)}kgCO2eq, in: {round(end - start,3)}sec.")

    matching.pairs.to_csv(RESULT_FILE)
    # matching.display_graph()