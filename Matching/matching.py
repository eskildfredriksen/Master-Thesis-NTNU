# -*- coding: utf-8 -*-

import logging
import random
import sys
import time
from itertools import compress, product
from copy import copy, deepcopy
import igraph as ig
import numexpr as ne
import numpy as np
import pandas as pd
import pygad
from ortools.linear_solver import pywraplp
from ortools.sat.python import cp_model
from scipy.optimize import milp, LinearConstraint, NonlinearConstraint, Bounds
import helper_methods as hm
import LCA as lca
import itertools
from itertools import combinations


logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s_%(asctime)s_%(message)s',
    datefmt='%H:%M:%S',
    # filename='log.log',
    # filemode='w'
    )


class Matching():
    """Class describing the matching problem, with its constituent parts."""
    def __init__(self, demand, supply, score_function_string_demand, score_function_string_supply, manual_match_list = None, add_new=False, multi=False, constraints={}, solution_limit=120):
        """_summary_

        :param demand: _description_
        :type demand: _type_
        :param supply: _description_
        :type supply: _type_
        :param score_function_string: _description_
        :type score_function_string: _type_
        :param add_new: _description_, defaults to False
        :type add_new: bool, optional
        :param multi: _description_, defaults to False
        :type multi: bool, optional
        :param constraints: _description_, defaults to {}
        :type constraints: dict, optional
        :param solution_limit: stop matching algorithm when reaching this limit., defaults to 60 [s]
        :type solution_limit: int, optional
        """
        self.demand = demand.infer_objects()
        self.supply = supply.infer_objects()
        self.score_function_string_demand = score_function_string_demand
        self.score_function_string_supply = score_function_string_supply
        
        pd.set_option('display.max_columns', 10)

        self.demand['Score'] = self.demand.eval(score_function_string_demand)

        self.supply['Score'] = self.supply.eval(score_function_string_supply)

        if add_new: # just copy designed to supply set, so that they act as new products
            demand_copy = self.demand.copy(deep = True)
            try:
                # Rename Dx to Nx. This works only when the indices are already named "D"
                demand_copy.rename(index=dict(zip(self.demand.index.values.tolist(), [sub.replace('D', 'N') for sub in self.demand.index.values.tolist()] )), inplace=True)
            except AttributeError:
                pass
            self.supply = pd.concat((self.supply, demand_copy), ignore_index=False).infer_objects()
        else:
            self.supply = self.supply.infer_objects()
        self.multi = multi
        self.graph = None
        self.result = None  #saves latest result of the matching
        self.pairs = pd.DataFrame(None, index=self.demand.index.values.tolist(), columns=['Supply_id']) #saves latest array of pairs
        self.incidence = pd.DataFrame(np.nan, index=self.demand.index.values.tolist(), columns=self.supply.index.values.tolist())
        # self.weights = None
        self.constraints = constraints
        

        self.solution_time = None
        self.solution_limit = solution_limit           
       
        

        # create incidence and weight for the method
        self.incidence = self.evaluate_incidence()
        # if manual matching, modify incidence here
        if not manual_match_list is None:
            self.user_defined_pairs(manual_match_list)
        self.weights = self.evaluate_weights()

        logging.info("Matching object created with %s demand, and %s supply elements", len(demand), len(supply))

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result    

    def evaluate_incidence(self):
        """Returns incidence matrix with true values where the element fit constraint criteria"""    
        # TODO optimize the evaluation.
        # TODO add 'Distance' 'Price' 'Material' 'Density' 'Imperfections' 'Is_column' 'Utilisation' 'Group' 'Quality' 'Max_height' ?
        #TODO Create standalone method for evaluating one column Rj of the incidence matrix. Need this for cutoffs in greedy algorithm as well. 
        start = time.time()
        bool_array = np.full((self.demand.shape[0], self.supply.shape[0]), True) # initiate empty array
        for param, compare in self.constraints.items():
            cond_list = []
            for var in self.supply[param]:
                demand_array = self.demand[param].to_list()
                bool_col = ne.evaluate(f'{var} {compare} demand_array') # numpy array of boolean
                cond_list.append(bool_col)
            cond_array = np.column_stack(cond_list) #create new 2D-array of conditionals
            bool_array = ne.evaluate("cond_array & bool_array") # 
            #bool_array = np.logical_and(bool_array, cond_array)
        # for simplicity I restrict the incidence of new elements to only be True for the "new" equivalent
        inds = self.supply.index[self.supply.index.map(lambda s: 'N' in s)] # Get the indices for new elements
        if len(inds) > 0:
            diag_mat = np.full((len(inds), len(inds)), False)
            np.fill_diagonal(diag_mat, True) # create a diagonal with True on diag, False else. 
            bool_array = np.hstack((bool_array[:, :-len(inds)], diag_mat))

        end = time.time()
        logging.info("Create incidence matrix from constraints: %s sec", round(end - start,3))
        return pd.DataFrame(bool_array, columns= self.incidence.columns, index= self.incidence.index)

    def evaluate_column(self, supply_val, parameter, compare, current_bool):
        """evaluate_column Evaluates a column in the incidence matrix according to the constraints

        Parameters
        ----------
        supply_val : str
            _description_
        parameter : str
            _description_
        compare : str
            _description_
        current_bool : _type_
            _description_

        Returns
        -------
        boolean list
            list of boolean AND operation between current column and the evaluated constraint.
        """        
        demand_array = self.demand[parameter].to_numpy(dtype = float) # array of demand parameters to evaluate. 
        compare_array = ne.evaluate(f"{supply_val} {compare} demand_array")        
        return ne.evaluate("current_bool & compare_array")
            
    def evaluate_weights(self):
        """Return matrix of weights for elements in the incidence matrix. The lower the weight the better."""
        start = time.time()
        weights = np.full(self.incidence.shape, np.nan)
        el_locs0 = np.where(self.incidence) # tuple of rows and columns positions, as a list
        el_locs = np.transpose(el_locs0) # array of row-column pairs where incidence matrix is true. 
        # create a new dataframe with values from supply, except for the Length, which is from demand set (cut supply)
        eval_df = self.supply.iloc[el_locs0[1]].reset_index(drop=True)
        eval_df['Length'] = self.demand.iloc[el_locs0[0]]['Length'].reset_index(drop=True)
        eval_score = eval_df.eval(self.score_function_string_supply)
        weights[el_locs0[0], el_locs0[1]] = eval_score.to_numpy()     
        end = time.time()  
        logging.info("Weight evaluation of incidence matrix: %s sec", round(end - start, 3))
        return pd.DataFrame(weights, index = self.incidence.index, columns = self.incidence.columns)

    def user_defined_pairs(self, constraint_list_user):

        
        def evaluate_constraints_string(self, constraint_str):

            els = constraint_str.split(' ') # split the string at spaces
            dem = els[0]; sup = els[2] # the value of the incidence matrix to work on.
            try:
                match = self.incidence.loc[dem, sup]
            except:
                raise ValueError("The object cannot be found in the incidence matrix. Make sure that input string is correct.")
            if match: # test if the match is possible
                if els[1] == "NOT": #restrict matching
                    self.incidence.loc[dem, sup] = False # these two elements should not be matched. 
                elif els[1] == "AND": # lock matching. Set remaining items in col to False
                    self.incidence.loc[: , sup] = False # Set the whole column to False to restrict mathing of any elements.
                    self.incidence.loc[dem, :] = False
                    self.incidence.loc[dem , sup] = True # Set the only possible matching with supply True. 
                    #TODO This aproach does not allow for possible remaining cutoff to be used. Could be fixed, For example by splitting the forced match element into another cut of piece as well.


        if not isinstance(constraint_list_user, list):
            constraint_list_user = [constraint_list_user] # ensure that we're working on a list.
        # make all items lowercase
        constraint_list_user = list(map(str.lower, constraint_list_user))
        # for each string in the list. 
        for constraint in constraint_list_user:
            if not isinstance(constraint, str):
                raise TypeError # should be constraint
            evaluate_constraints_string(self, constraint_str = constraint)
            
        return None

    def add_pair(self, demand_id, supply_id):
        """Execute matrix matching"""
        # add to match_map:
        self.pairs.loc[demand_id, 'Supply_id'] = supply_id
        
    def add_graph(self):
        """Add a graph notation based on incidence matrix"""
        vertices = [0]*len(self.demand.index) + [1]*len(self.supply.index)
        num_rows = len(self.demand.index)
        edges = np.transpose(np.where(self.incidence))
        edges = [[edge[0], edge[1]+num_rows] for edge in edges]
        edge_weights = self.weights.to_numpy().reshape(-1,)
        edge_weights = edge_weights[~np.isnan(edge_weights)]
        # We need to reverse the weights, so that the higher the better. Because of this edge weights are initial score minus the replacement score:
        edge_weights = (np.array([self.demand.Score[edge[0]] for edge in edges ])+0.0000001) - edge_weights 
        # assemble graph
        graph = ig.Graph.Bipartite(vertices, edges)
        graph.es["label"] = edge_weights
        graph.vs["label"] = list(self.demand.index)+list(self.supply.index) #vertice names
        self.graph = graph

    def _matching_decorator(func):
        """Set of repetitive tasks for all matching methods"""
        def wrapper(self, *args, **kwargs):
            # Before:
            start = time.time()
            # empty result of previous matching:
            self.result = 0  
            self.pairs = pd.DataFrame(None, index=self.demand.index.values.tolist(), columns=['Supply_id'])
            # The actual method:
            func(self, *args, **kwargs)
            #Calculate the result of the matching
            self.calculate_result()
            # After:
            end = time.time()
            self.solution_time = round(end - start, 3)
            all_string_series = self.pairs.fillna('nan') # have all entries as string before search
            num_old = len(all_string_series.loc[all_string_series.Supply_id.str.contains('S')].Supply_id.unique())
            num_new = len(all_string_series.loc[all_string_series.Supply_id.str.contains('N')].Supply_id.unique())
            num_matched = len(self.pairs.dropna())
            logging.info("Matched %s old and %s new elements to %s demand elements (%s %%) using %s. Resulting in score %s, in %s seconds.", 
                num_old, num_new, num_matched, round(100 * num_matched / len(self.pairs), 2), func.__name__, round(self.result, 2), round(end - start, 3))
            return [self.result, self.pairs]
        return wrapper
    
    def calculate_result(self):
        """Evaluates the result based on the final matching of elements"""
        # if rows without pairing, remove those    
        local_pairs = self.pairs.dropna()
        #get the index of columns in weight df which are paired
        #TODO Make the supply and demand id_s numerical 
        col_inds = local_pairs.Supply_id.apply(lambda label: self.weights.columns.get_loc(label))
        row_inds = list( map(lambda name: self.weights.index.get_loc(name), local_pairs.index) )
        #row_inds = np.arange(0, local_pairs.shape[0], 1) # the row inds are the same here and in the weights
        self.result = (self.weights.to_numpy()[row_inds, col_inds]).sum()
        # add the score of original elements that are not substituted
        mask = self.pairs.Supply_id.isna().to_numpy()
        original_score = self.demand.Score[mask].sum()
        self.result += original_score

    ### MATCHING ALGORITHMS

    @_matching_decorator
    def match_brute_DEPRECIATED(self, plural_assign=False):
        """Brute forces all possible solutions"""
        
        weights = self.weights
        n_columns=len(self.weights.columns)
        arrays=[]
        bestmatch=[]
        lowest_lca=10e10

        for combination in combinations(range(n_columns), 1):
            arr = np.zeros(n_columns)
            arr[list(combination)] = 1
            arrays.append(arr.tolist())
        for subset in itertools.permutations(arrays,len(self.demand)):
            subset_df=pd.DataFrame(data=list(subset),index=weights.index,columns=weights.columns)
            multiplum=weights.multiply(subset_df,fill_value=-1)
            invalid_solution=multiplum.isin([-1]).any().any()
            if not invalid_solution:
                sum=multiplum.values.sum()
                if sum<lowest_lca:
                    lowest_lca=sum
                    bestmatch=subset_df
        coordinates_of_pairs = [(f"D{x}", bestmatch.columns[y]) for x, y in zip(*np.where(bestmatch.values == 1))]
        for pair in coordinates_of_pairs:
            self.add_pair(pair[0],pair[1])
        pass

    @_matching_decorator
    def match_brute_DEPRECIATED_vol2(self, plural_assign=False):
        """Brute forces all possible solutions"""
        
        weights = self.weights
        count=0
        bestmatch=[]
        lowest_lca=10e10
        possible_solutions=hm.extract_brute_possibilities(self.incidence)
        for subset in itertools.product(*possible_solutions):
            count+=1
            subset_df=pd.DataFrame(data=list(subset),index=weights.index,columns=weights.columns)
            sum=subset_df.sum()
            invalid_solution=(sum>1).any()
            if not invalid_solution:
                multiplum=weights.multiply(subset_df,fill_value=0)
                LCAsum=multiplum.values.sum()
                if LCAsum<lowest_lca:
                    lowest_lca=LCAsum
                    bestmatch=subset_df
        coordinates_of_pairs = [(f"D{x}", bestmatch.columns[y]) for x, y in zip(*np.where(bestmatch.values == 1))]
        for pair in coordinates_of_pairs:
            self.add_pair(pair[0],pair[1])
        # TODO implement it
        pass


    @_matching_decorator
    def match_brute_DEPRECIATED_vol3(self, plural_assign=False):
        """Brute forces all possible solutions"""
        
        weights = self.weights
        bestmatch=[]
        lowest_lca=10e10
        possible_solutions=hm.extract_brute_possibilities(self.incidence)

        for subset in itertools.product(*possible_solutions):
            column_sum=np.sum(list(subset),axis=0)[:-1]
            invalid_solution=len([*filter(lambda x:x>1,column_sum)])>0
            if not invalid_solution:
                subset_df=pd.DataFrame(data=list(subset),index=weights.index,columns=weights.columns)
                multiplum=weights.multiply(subset_df,fill_value=0)
                LCAsum=multiplum.values.sum()
                if LCAsum<lowest_lca:
                    lowest_lca=LCAsum
                    bestmatch=subset_df
        coordinates_of_pairs = [(f"D{x}", bestmatch.columns[y]) for x, y in zip(*np.where(bestmatch.values == 1))]
        for pair in coordinates_of_pairs:
            self.add_pair(pair[0],pair[1])
        # TODO implement it
        pass

    @_matching_decorator
    def match_brute(self, plural_assign=False):
        """Brute forces all possible solutions"""
        weights = self.weights
        bestmatch=[]
        lowest_lca=10e10
        possible_solutions=hm.extract_brute_possibilities(self.incidence)
        arrayweights=weights.to_numpy()
        for subset in itertools.product(*possible_solutions):
            column_sum=np.sum(list(subset),axis=0)[:-1]
            invalid_solution=len([*filter(lambda x:x>1,column_sum)])>0
            if not invalid_solution:
                multiplum=np.multiply(arrayweights,subset)
                LCAsum=np.nansum(multiplum)
                if LCAsum<lowest_lca:
                    lowest_lca=LCAsum
                    bestmatch=subset
        bestmatch=pd.DataFrame(data=list(bestmatch),index=weights.index,columns=weights.columns)
        coordinates_of_pairs = [(f"D{x}", bestmatch.columns[y]) for x, y in zip(*np.where(bestmatch.values == 1))]
        for pair in coordinates_of_pairs:
            self.add_pair(pair[0],pair[1])
        pass

    @_matching_decorator
    def match_greedy(self, plural_assign=False):
        """_summary_

        Args:
            plural_assign (bool, optional): _description_. Defaults to False.
        """
        #"""Algorithm that takes one best element at each iteration, based on sorted lists, not considering any alternatives."""

        sorted_weights = self.weights.join(self.demand.Score)


        sorted_weights = sorted_weights.sort_values(by='Score', axis=0, ascending=False)
        sorted_weights = sorted_weights.drop(columns=['Score'])
        #sorted_weights.replace(np.nan, np.inf, inplace=True)  

        score = self.supply.Score.copy()

        for i in range(sorted_weights.shape[0]):
            row_id = sorted_weights.iloc[[i]].index[0]
            vals = np.array(sorted_weights.iloc[[i]])[0]
#            if np.any(vals):    # checks if not empty row (no matches)
            if sum(~np.isnan(vals)) > 0: # check if there it at least one element not np.nan
                lowest = np.nanmin(vals)
                col_id = sorted_weights.columns[np.where(vals == lowest)][0]
                self.add_pair(row_id, col_id)
                if plural_assign:
                    # check if this column makes sense if remaining rows (score < initial_score-score_used), remove if not
                    # sorted_weights[col_id] = sorted_weights[col_id].apply(hm.remove_alternatives, args=(self.supply.loc[col_id].Score))
                    score.loc[col_id] = score.loc[col_id] - lowest
                    sorted_weights[col_id] = sorted_weights[col_id].apply((lambda x: hm.remove_alternatives(x, score.loc[col_id])))
                else:
                    # empty the column that was used
                    sorted_weights[col_id] = np.nan

    @_matching_decorator
    def match_greedy_DEPRECIATED(self, plural_assign=False):
        """Algorithm that takes one best element at each iteration, based on sorted lists, not considering any alternatives."""
        # TODO consider opposite sorting (as we did in Gh), small chance but better result my occur
        demand_sorted = self.demand.copy(deep =True)
        supply_sorted = self.supply.copy(deep =True)
        #Change indices to integers for both demand and supply
        demand_sorted.index = np.array(range(len(demand_sorted.index)))
        supply_sorted.index = np.array(range(len(supply_sorted.index)))

        #sort the supply and demand
        #demand_sorted.sort_values(by=['Length', 'Area'], axis=0, ascending=False, inplace = True)
        demand_sorted.sort_values(by=['Score'], axis=0, ascending=False, inplace = True)
        #supply_sorted.sort_values(by=['Is_new', 'Length', 'Area'], axis=0, ascending=True, inplace = True)
        supply_sorted.sort_values(by=['Is_new', 'Score'], axis=0, ascending=True, inplace = True) # FIXME Need to make this work "optimally"
        incidence_np = self.incidence.copy(deep=True).values      

        columns = self.supply.index.to_list()
        rows = self.demand.index.to_list()
        min_length = self.demand.Length.min() # the minimum lenght of a demand element
        
        for demand_tuple in demand_sorted.itertuples():            
            match=False
            logging.debug("-- Attempt to find a match for %s", demand_tuple.Index)                
            for supply_tuple in supply_sorted.itertuples():                 
                if incidence_np[demand_tuple.Index,supply_tuple.Index]:           
                    match=True
                    self.add_pair(rows[demand_tuple.Index], columns[supply_tuple.Index])
                if match:
                    new_length = supply_tuple.Length - demand_tuple.Length
                    if plural_assign and new_length >= min_length:                    
                        # shorten the supply element:
                        supply_sorted.loc[supply_tuple.Index, "Length"] = new_length
                        
                        temp_row = supply_sorted.loc[supply_tuple.Index].copy(deep=True)
                        temp_row['LCA'] = temp_row.Length * temp_row.Area * lca.TIMBER_REUSE_GWP
                        supply_sorted.drop(supply_tuple.Index, axis = 0, inplace = True)
                        
                        #new_ind = supply_sorted['LCA'].searchsorted([False ,temp_row['LCA']], side = 'left') #get index to insert new row into #TODO Can this be sorted also by 'Area' and any other constraint?
                        new_ind = supply_sorted[supply_sorted['Is_new'] == False]['LCA'].searchsorted(temp_row['LCA'], side = 'left')
                        part1 = supply_sorted[:new_ind].copy(deep=True)
                        part2 = supply_sorted[new_ind:].copy(deep=True)
                        supply_sorted = pd.concat([part1, pd.DataFrame(temp_row).transpose().infer_objects(), part2]) #TODO Can we make it simpler
                        
                        new_incidence_col = self.evaluate_column(new_length, "Length", self.constraints['Length'], incidence_np[:, supply_tuple.Index])
                        #new_incidence_col = self.evaluate_column(supply_tuple.Index, new_length, "Length", self.constraints["Length"], incidence_np[:, supply_tuple.Index])
                        #incidence__np[:, columns.index(supply_tuple.Index)] = new_incidence_col

                        #incidence_copy.loc[:, columns[supply_tuple.Index]] = new_incidence_col #TODO If i get the indicies to work. Try using this as an np array instead of df.
                        incidence_np[:,supply_tuple.Index] = new_incidence_col
                        
                        logging.debug("---- %s is a match, that results in %s m cut.", supply_tuple.Index, supply_tuple.Length)
                    else:
                        #self.result += calculate_lca(supply_row.Length, supply_row.Area, is_new=supply_row.Is_new)
                        logging.debug("---- %s is a match and will be utilized fully.", supply_tuple.Index)
                        supply_sorted.drop(supply_tuple.Index, inplace = True)
                    break
                        
            else:
                logging.debug("---- %s is not matching.", supply_tuple.Index)

    @_matching_decorator
    def match_bipartite_graph(self):
        """Match using Maximum Bipartite Graphs. A maximum matching is a set of edges such that each vertex is
        incident on at most one matched edge and the weight of such edges in the set is as large as possible."""
        # TODO multiple assignment won't work OOTB.
        if not self.graph:
            self.add_graph()
        if self.graph.is_connected():
            # TODO separate disjoint graphs for efficiency
            logging.info("graph contains unconnected subgraphs that could be separated")
        bipartite_matching = ig.Graph.maximum_bipartite_matching(self.graph, weights=self.graph.es["label"])
        for match_edge in bipartite_matching.edges():
            self.add_pair(match_edge.source_vertex["label"], match_edge.target_vertex["label"])  
        

    # TODO (SIGURD) WORK IN PROGRESS: MAKING A NEW GENETIC ALGORITHM
    @_matching_decorator
    def match_genetic_algorithm_RANDOM(self):
        """Genetic algorithm with the initial population with random solutions (not necessary an actual solution)"""
        #ASSUMING THAT WE WANT TO OPTIMIZE ON MINIMIZING LCA
        number_of_demand_elements = len(self.demand)
        
        """NOTE NEEDED IF NEW ELEMENTS ARE NOT CONCIDERED
        supply_names = self.supply.index.tolist()
        index_first_new = self.supply.index.tolist().index("N0")
        supply_names_only_reuse = supply_names[:index_first_new]
        solutions_per_population = len(supply_names_only_reuse) * 100
        """
        weights_new = hm.transform_weights(self.weights) #Create a new weight matrix with only one column representing all new elements
        weights_1d_array = weights_new.to_numpy().flatten()
        weights = np.array_split(weights_1d_array, number_of_demand_elements)
        max_weight = np.max(weights_1d_array[~np.isnan(weights_1d_array)])
        supply_names = weights_new.columns
        chromosome_length = len(supply_names) * len(self.demand)
        requested_number_of_chromosomes = len(supply_names)**2
        
        """Old way of making random population! Works quite nice, dont want to delete it yet"""
        #initial_population = np.array(([[random.randint(0,1) for x in range(chromosome_length)] for y in range(requested_number_of_chromosomes)]))
        #Initializing a random population
        initial_population = hm.create_random_population_genetic(chromosome_length, requested_number_of_chromosomes, probability_of_0=0.9, probability_of_1=0.1)
        solutions_per_population = len(initial_population)

        def fitness_func(solution, solution_idx):
            """Fitness function to calculate fitness value of chromosomes
            Genetic algorithm expects a maximization fitness function => when we are minimizing lca we must divide by 1/LCA"""
            fitness = 0
            reward = 0
            solutions = np.array_split(solution, number_of_demand_elements)
            penalty = -max_weight
            indexes_of_matches = []
            for i in range(len(solutions)):
                num_matches_in_bracket = 0
                for j in range(len(solutions[i])):
                    if solutions[i][j] == 1:
                        if np.isnan(weights[i][j]): #Element cannot be matched => penalty
                            fitness += penalty #Penalty
                        else:
                            reward += weights[i][j] #LCA of match
                            num_matches_in_bracket += 1
                            new_element_index = len(solutions[i])-1
                            if not j == new_element_index: #Means that a supply element (not a new element) is matched with a demand element
                                indexes_of_matches.append(j)
                            
                if num_matches_in_bracket > 1:
                    fitness += 10*penalty #Penalty for matching multiple supply elemenets to the same demand element
                elif num_matches_in_bracket < 1:
                    fitness += penalty #Penalty for not matching at all
            
            index_duplicates = {x for x in indexes_of_matches if indexes_of_matches.count(x) > 1}
            if len(index_duplicates) > 0: #Means some supply elements are assigned the same demand element
                fitness = -10e10
            elif reward != 0:
                fitness += 100/reward
                  
            return fitness
        
        def fitness_func_matrix(solution, solution_idx):
            #TODO (SIGURD): Decrease run-time by doing matrix-multiplication to evaluate fitness of solution rather than double for-loop
            fitness = 0
            return fitness
            
        #Using pygad-module
        #TODO: Try parallization-module in pygad!
        """Parameters are set by use of trial and error. These parameters have given a satisfactory solution"""
        ga_instance = pygad.GA(
            initial_population=initial_population,
            num_generations=int((len(self.demand)+len(self.supply))),
            num_parents_mating=int(np.ceil(solutions_per_population/2)),
            fitness_func=fitness_func,
            # binary representation of the problem with help from: https://blog.paperspace.com/working-with-different-genetic-algorithm-representations-python/
            # (also possible with: gene_space=[0, 1])
            #mutation_by_replacement=True,
            gene_type=int,
            parent_selection_type="sss",    # steady_state_selection() https://pygad.readthedocs.io/en/latest/README_pygad_ReadTheDocs.html#steady-state-selection
            keep_elitism= int(np.ceil(solutions_per_population/2)),
            #keep_parents=-1, #-1 => keep all parents, 0 => keep none
            crossover_type="single_point",
            mutation_type = "random",
            #mutation_num_genes=int(solutions_per_population/5), Not needed if mutation_probability is set
            mutation_probability = 0.4,
            mutation_by_replacement=True,
            random_mutation_min_val=0,
            random_mutation_max_val=1,   # upper bound exclusive, so only 0 and 1
            #save_best_solutions=True, #Needs a lot of memory
            )

        ga_instance.run()
        logging.debug(ga_instance.initial_population)
        logging.debug(ga_instance.population)
        solution, solution_fitness, solution_idx = ga_instance.best_solution()
        extracted_results = hm.extract_genetic_solution(weights_new, solution, number_of_demand_elements)
        printed_results = hm.print_genetic_solution(self.weights, solution, number_of_demand_elements)
        for index, row in extracted_results.iterrows():
            self.add_pair(index, row["Matches from genetic"])

    @_matching_decorator
    def match_genetic_algorithm_ALL_POSSIBILITIES(self):
        """Genetic algorithm than only uses a subset of possible solutions as the initial population"""
        #ASSUMING THAT WE WANT TO OPTIMIZE ON MINIMIZING LCA
        number_of_demand_elements = len(self.demand)
        weights_new = hm.transform_weights(self.weights) #Create a new weight matrix with only one column representing all new elements
        weights_1d_array = weights_new.to_numpy().flatten()
        weights = np.array_split(weights_1d_array, number_of_demand_elements)
        max_weight = np.max(weights_1d_array[~np.isnan(weights_1d_array)])
        supply_names = weights_new.columns
    
        #Initial population as a subset of actual possible solutions
        new_sol = hm.create_initial_population_genetic(hm.transform_weights(self.incidence*1), size_of_population = len(supply_names)**2, include_invalid_combinations=False)


        def fitness_func(solution, solution_idx):
            """Fitness function to calculate fitness value of chromosomes
            Genetic algorithm expects a maximization fitness function => when we are minimizing lca we must divide by 1/LCA"""
            fitness = 0
            reward = 0
            solutions = np.array_split(solution, number_of_demand_elements)
            penalty = -max_weight
            indexes_of_matches = []
            for i in range(len(solutions)):
                num_matches_in_bracket = 0
                for j in range(len(solutions[i])):
                    if solutions[i][j] == 1:
                        if np.isnan(weights[i][j]): #Element cannot be matched => penalty
                            fitness += penalty #Penalty
                        else:
                            reward += weights[i][j] #LCA of match
                            num_matches_in_bracket += 1
                            new_element_index = len(solutions[i])-1
                            if not j == new_element_index: #Means that a supply element (not a new element) is matched with a demand element
                                indexes_of_matches.append(j)
                            
                if num_matches_in_bracket > 1:
                    fitness += 10*penalty #Penalty for matching multiple supply elemenets to the same demand element
                elif num_matches_in_bracket < 1:
                    fitness += penalty #Penalty for not matching at all
            
            index_duplicates = {x for x in indexes_of_matches if indexes_of_matches.count(x) > 1}
            if len(index_duplicates) > 0: #Means some supply elements are assigned the same demand element
                fitness = -10e10
            elif reward != 0:
                fitness += 100/reward
                  
            return fitness
        
        def fitness_func_matrix(solution, solution_idx):
            #TODO (SIGURD): Decrease run-time by doing matrix-multiplication to evaluate fitness of solution rather than double for-loop
            fitness = 0
            return fitness
        
        #TODO: Try parallaization
        """Parameters are set by use of trial and error. These parameters have given a satisfactory solution"""
        ga_instance = pygad.GA(
            initial_population=new_sol,
            num_generations=int((len(self.demand)+len(self.supply))),
            num_parents_mating=int(np.ceil(len(new_sol)/2)),
            fitness_func=fitness_func,
            # binary representation of the problem with help from: https://blog.paperspace.com/working-with-different-genetic-algorithm-representations-python/
            # (also possible with: gene_space=[0, 1])
            gene_type=int,
            parent_selection_type="sss",    # steady_state_selection() https://pygad.readthedocs.io/en/latest/README_pygad_ReadTheDocs.html#steady-state-selection
            keep_elitism= int(np.ceil(len(new_sol)/4)),
            #keep_parents=-1, #-1 => keep all parents, 0 => keep none
            crossover_type="single_point", 
            mutation_type = "random",
            #mutation_num_genes=int(solutions_per_population/5), Not needed if mutation_probability is set
            mutation_probability = 0.2,
            mutation_by_replacement=True,
            random_mutation_min_val=0,
            random_mutation_max_val=1,   # upper bound exclusive, so only 0 and 1
            )
        ga_instance.run()
        logging.debug(ga_instance.initial_population)
        logging.debug(ga_instance.population)
        solution, solution_fitness, solution_idx = ga_instance.best_solution()
        extract_solution = hm.extract_genetic_solution(weights_new, solution, number_of_demand_elements)
        printed_results = hm.print_genetic_solution(self.weights, solution, number_of_demand_elements)
        for index, row in extract_solution.iterrows():
            self.add_pair(index, row["Matches from genetic"])

    @_matching_decorator
    def match_genetic_algorithm_DEPRECIATED(self):
        """Match using Evolutionary/Genetic Algorithm"""
        # TODO implement the method
        # supply capacity - length:
        capacity = self.supply['Length'].to_numpy()
        lengths = self.demand['Length'].to_numpy()
        # demand_mapping (column - demand):
        initial_population = np.zeros((len(self.supply), len(self.demand)))
        # for each column add one random 0/1.
        for col in range(len(self.demand)):
            row = random.randint(0, len(self.supply)-1)
            initial_population[row, col] = random.randint(0, 1)
        def fitness_func(solution, solution_idx):
            # output = np.sum(solution*function_inputs) #score!
            total_length = np.sum(solution*lengths)
            if np.sum(total_length > capacity) != len(capacity):
                output = 10e4  # penalty
            elif np.argwhere(np.sum(solution, axis=0) > 1):
                output = 10e4  # penalty
            else:
                # score:
                output = np.sum(solution*self.demand['Length'])
            fitness = 1.0 / output
            return fitness
        ga_instance = pygad.GA(
            num_generations=30,
            num_parents_mating=2,
            fitness_func=fitness_func,
            sol_per_pop=10,
            num_genes=initial_population.size, #len(initial_population),
            # binary representation of the problem with help from: https://blog.paperspace.com/working-with-different-genetic-algorithm-representations-python/
            # (also possible with: gene_space=[0, 1])
            init_range_low=0,
            random_mutation_min_val=0,
            init_range_high=2,   # upper bound exclusive, so only 0 and 1
            random_mutation_max_val=2,   # upper bound exclusive, so only 0 and 1
            mutation_by_replacement=True,
            gene_type=int,
            parent_selection_type="sss",    # steady_state_selection() https://pygad.readthedocs.io/en/latest/README_pygad_ReadTheDocs.html#steady-state-selection
            keep_parents=1,
            crossover_type="single_point",  # https://pygad.readthedocs.io/en/latest/README_pygad_ReadTheDocs.html#steady-state-selection
            mutation_type="random",  # https://pygad.readthedocs.io/en/latest/README_pygad_ReadTheDocs.html#steady-state-selection
            mutation_num_genes=1,
            # mutation_percent_genes=10,
            initial_population=initial_population
            )
        ga_instance.run()
        logging.debug(ga_instance.initial_population)
        logging.debug(ga_instance.population)
        solution, solution_fitness, solution_idx = ga_instance.best_solution() 
        logging.debug("Parameters of the best solution: %s", solution)
        logging.debug("Fitness value of the best solution = %s", solution_fitness)
        # TODO Don't use the method as it is :)
        self.result += 1234 #calculate_score(supply_row.Length, supply_row.Area, is_new=supply_row.Is_new)

    @_matching_decorator
    def match_mixed_integer_programming_DEPRECIATED(self):
        """Match using SCIP - Solving Constraint Integer Programs, branch-and-cut algorithm, type of mixed integer programming (MIP)"""
        def constraint_inds():
            """Construct the constraint array"""
            rows = self.demand.shape[0]
            cols = self.supply.shape[0]
            bool_array = np.full((rows, cols), False)
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
        # --- Create the data needed for the solver ---        
        data = {} # initiate empty dictionary
        data['lengths'] = self.demand.Length.astype(float)
        data['areas'] = self.demand.Area.astype(float)
        assert len(data['lengths']) == len(data['areas']) # The same check is done indirectly in the dataframe
        data['num_items'] = len(data['areas'])
        data['all_items'] = range(data['num_items'])
        data['all_items'] = range(data['num_items'])
        data['bin_capacities'] = self.supply.Length # these would be the bins
        data['num_bins'] = len(data['bin_capacities'])
        data['all_bins'] = range(data['num_bins'])
        #get constraint ids
        c_inds = constraint_inds()
        # create solver
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if solver is None:
            logging.debug('SCIP Solver is unavailable')
            return
        # --- Variables ---
        # x[i,j] = 1 if item i is backed in bin j. 0 else
        var_array = np.full((self.incidence.shape), 0)
        x = {}
        for i in data['all_items']:
            for j in data['all_bins']:
                x[i,j] = solver.BoolVar(f'x_{i}_{j}') 
        logging.debug('Number of variables = %s', solver.NumVariables()) 
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
        for inds in c_inds:
            i = int(inds[0])
            j = int(inds[1])
            solver.Add(x[i,j] == 0)
        logging.debug('Number of contraints = %s', solver.NumConstraints())
        # --- Objective ---
        # maximise total value of packed items
        # coefficients
        coeff_array = self.weights.replace(np.nan, self.weights.max().max() * 1000).to_numpy() # play with different values here. 
        objective = solver.Objective()
        for i in data['all_items']:
            for j in data['all_bins']:
                objective.SetCoefficient(x[i,j], 1 / coeff_array[i,j]) # maximise the sum of 1/sum(weights)
                #objective.SetCoefficient(x[i,j], float(data['areas'][i]))      
        objective.SetMaximization()
        #objective.SetMinimization()
        # Starting solver
        status = solver.Solve()
        logging.debug('Computation done')
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            score = 0
            for i in data['all_items']:
                for j in data['all_bins']:
                    if x[i,j].solution_value() > 0: 
                        self.pairs.iloc[i] = j # add the matched pair. 
                        score += coeff_array[i, j]
                        continue # only one x[0, j] can be 1. the rest are 0. Continue
            self.result = score           
            results = {}
            logging.debug('Solution found! \n ------RESULTS-------\n')
            total_length = 0
            for j in data['all_bins']:
                results[j] = []
                logging.debug('Bin %s', j)
                bin_length = 0
                bin_value = 0
                for i in data['all_items']:
                    if x[i, j].solution_value() > 0:
                        results[j].append(i)
                        logging.debug("Item %s Length: %s area: %s", i, data['lengths'][i], data['areas'][i])
                        bin_length += data['lengths'][i]
                        bin_value += data['areas'][i]
                logging.debug('Packed bin lengths: %s', bin_length)
                logging.debug('Packed bin value: %s', bin_value)
                total_length += bin_length
                logging.debug('Total packed Lenghtst: %s\n', total_length)
        # return the results as a DataFrame like the bin packing problem
        # Or a dictionary. One key per bin/supply, and a list of ID's for the
        # elements which should go within that bin. 
        # TODO temp result:
        return [self.result, self.pairs]

    @_matching_decorator
    def match_mixed_integer_programming(self):
        """This method is the same as the previous one, but uses a CP model instead of a MIP model in order to stop at a given number of 
        feasible solutions. """
        #TODO Evaluate if the cost function is the best we can have. 
        # the CP Solver works only on integers. Consequently, all values are multiplied by 1000 before solving the
        m_fac = 10000
        # --- Create the data needed for the solver ---        
        data = {} # initiate empty dictionary
        data['lengths'] = (self.demand.Length * m_fac).astype(int)
        data['values'] = (self.demand.Area * m_fac).astype(int)
        assert len(data['lengths']) == len(data['values']) # The same check is done indirectly in the dataframe
        data['num_items'] = len(data['values']) # don't need this. TODO Delete it. 
        data['all_items'] = range(data['num_items'])
        #data['areas'] = self.demand.Area
        data['bin_capacities'] = (self.supply.Length * m_fac).astype(int)  # these would be the bins
        #data['bin_areas'] = self.supply.Area.to_numpy(dtype = int)
        data['num_bins'] = len(data['bin_capacities'])
        data['all_bins'] = range(data['num_bins'])
        #get constraint ids
        #c_inds = constraint_inds()
        c_inds = np.transpose(np.where(~self.incidence)) # get the position of the substitutions that cannot be used
        # create model
        model = cp_model.CpModel()
        # --- Variables ---
        # x[i,j] = 1 if item i is backed in bin j. 0 else
        var_array = np.full((self.incidence.shape), 0) #TODO Implement this for faster extraction of results later. Try to avoid nested loops
        x = {}
        for i in data['all_items']:
            for j in data['all_bins']:
                x[i,j] = model.NewBoolVar(f'x_{i}_{j}')   
        #logging.debug(f'Number of variables = {solver.NumVariables()}') 
        # --- Constraints ---
        # each item can only be assigned to one bin
        for i in data['all_items']:
            model.AddAtMostOne(x[i, j] for j in data['all_bins'])
        # the amount packed in each bin cannot exceed its capacity.
        for j in data['all_bins']:
            model.Add(sum(x[i, j] * data['lengths'][i]
            for i in data['all_items']) <= data['bin_capacities'][j])
        # from the already calculated incidence matrix we add constraints to the elements i we know
        # cannot fit into bin j.
        for inds in c_inds:
            i = int(inds[0])
            j = int(inds[1])
            model.Add(x[i,j] == 0)
            #model.AddHint(x[i,j], 0)    
        # --- Objective ---
        # maximise total inverse of total score
        # coefficients
        coeff_array = self.weights.values * m_fac
        np.nan_to_num(coeff_array, False, nan = 0.0)
        #coeff_array = coeff_array.replace(np.nan, coeff_array.max().max() * 1000).to_numpy() # play with different values here. 
        #coeff_array = coeff_array.astype(int)
        objective = []
        for i in data['all_items']:
            for j in data['all_bins']:
                objective.append(
                    #cp_model.LinearExpr.Term(x[i,j], coeff_array[i,j])
                    cp_model.LinearExpr.Term(x[i,j], (self.demand.Score[i]*m_fac+1 - coeff_array[i,j]))
                    )          
        #model.Maximize(cp_model.LinearExpr.Sum(objective))
        model.Maximize(cp_model.LinearExpr.Sum(objective))
        # --- Solve ---
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.solution_limit
        status = solver.Solve(model)
        test = solver.ObjectiveValue()
        index_series = self.supply.index
        # --- RESULTS ---
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            score = 0
            for i in data['all_items']:
                for j in data['all_bins']:
                    if solver.Value(x[i,j]) > 0: 
                        self.pairs.iloc[i] = index_series[j] # add the matched pair.                         
                        break # only one x[0, j] can be 1. the rest are 0. Continue or break?
            
    @_matching_decorator
    def match_scipy_milp(self):
        max_time = self.solution_limit

        weights = np.nan_to_num(self.weights.to_numpy().astype(float), nan = 0) 
        score = self.demand.Score.to_numpy(dtype = float).reshape((-1,1)) 
        costs = np.subtract(score, weights).reshape((-1,))
        
        # What should be the costs of assigning an element?
        # parameters x
        x_mat = np.zeros(self.weights.shape, dtype= int) # need to flatten this to use scipy
        x_arr = np.reshape(x_mat, (-1, ))
        # parameter bounds
        lb = np.full_like(x_arr, 0)
        ub = np.where(self.weights.isna().to_numpy().reshape((-1,)), 0 ,1)
        bounds = Bounds(lb = lb, ub = ub)#, ub = np.full_like(x_arr, 1)) # can modify these later to restrict solutions that we already know are infeasible.
        # constraints
        #Try creating a constraints list
        rows, cols = x_mat.shape
        A1 = np.zeros((rows, rows*cols))
        # fill a with ones: 
        for i in range(rows):
            A1[i, i*cols : (i+1)*cols] = 1
        cons = [] # Constraints dictionary
        max_constr = lambda vec: np.sum(vec)
        constraints1 = LinearConstraint(A = A1 , lb = 0, ub = 1)
        A2 = np.zeros((cols, rows * cols))
        demand_lengths = self.demand.Length.to_numpy()
        #constraints2 = LinearConstraint(A = A2, lb = 0, ub = self.supply.Length)
        for j in range(cols):
            A2[j, j::cols] = demand_lengths
            #A2[j, j*rows : (j+1)*rows] = demand_lengths
        constraints2 = LinearConstraint(A = A2, lb = 0., ub = self.supply.Length.to_numpy())    
        integrality = np.full_like(x_arr, True) # force decision variables to be 0 or 1
        constraints = [constraints1, constraints2]       
        # Run optimisation:
        time_limit = max_time
        options = {'disp':False, 'time_limit': time_limit, 'presolve' : True}
        #TODO Make sure once more that the costs here are the same as what we describe in the text.
        res = milp(c=  (costs+0.0000001)* (-1), constraints = constraints, bounds = bounds, integrality = integrality, options = options)
        #res = milp(c= -np.ones_like(x_arr), constraints = constraints, bounds = bounds, integrality = integrality, options = options)
        # ======= POST PROCESS ===========
        try:
            assigment_array = res.x.reshape(rows, cols) 
        except AttributeError:# If no solution res.x is None. No substitutions exists. 
            assigment_array = np.zeros_like(x_mat)
        demand_ind, supply_ind = np.where(assigment_array == 1)
        demand_id = self.demand.index[demand_ind]
        supply_id = self.supply.index[supply_ind]
        self.pairs.loc[demand_id] = supply_id.to_numpy().reshape((-1,1))
        # Create dataframe to see if constraints are kept. 
        #capacity_df = pd.concat([self.pairs, self.demand.Length], axis = 1).groupby('Supply_id').sum()
        #compare_df = capacity_df.join(self.supply.Length, how = 'inner', lsuffix = ' Assigned', rsuffix = ' Capacity')
        #compare_df['OK'] = np.where(compare_df['Length Assigned'] <= compare_df['Length Capacity'], True, False)
        
  
def run_matching(demand, supply, score_function_string, manual_match_strings = None, constraints = None, add_new = True, solution_limit = 100,
                bipartite = True, greedy_single = True, greedy_plural = True, genetic = False, milp = False, sci_milp = False):
    """Run selected matching algorithms and returns results for comparison.
    By default, bipartite, and both greedy algorithms are run. Activate and deactivate as wished."""
    #TODO Can **kwargs be used instead of all these arguments
    # create matching object 
    matching = Matching(demand=demand, supply=supply, score_function_string=score_function_string,manual_match_list=manual_match_strings,
                        constraints=constraints, add_new=add_new, multi = True, solution_limit=solution_limit)
    
    matches =[] # results to return
    headers = []
    if greedy_single:
        matching.match_greedy(plural_assign=False)
        matches.append({'Name': 'Greedy_single','Match object': copy(matching), 'Time': matching.solution_time, 'PercentNew': matching.pairs.isna().sum()})
    if greedy_plural:
        matching.match_greedy(plural_assign=True)
        matches.append({'Name': 'Greedy_plural', 'Match object': copy(matching), 'Time': matching.solution_time, 'PercentNew': matching.pairs.isna().sum()})
    if bipartite:
        matching.match_bipartite_graph()
        matches.append({'Name': 'Bipartite', 'Match object': copy(matching), 'Time': matching.solution_time, 'PercentNew': matching.pairs.isna().sum()})
    if milp:
        matching.match_mixed_integer_programming()
        matches.append({'Name': 'MILP','Match object': copy(matching), 'Time': matching.solution_time, 'PercentNew': matching.pairs.isna().sum()})
    if sci_milp:
        matching.match_scipy_milp()
        matches.append({'Name': 'MILP','Match object': copy(matching), 'Time': matching.solution_time, 'PercentNew': matching.pairs.isna().sum()})
    if genetic:
        #matching.match_genetic_algorithm()
        #matches.append({'Name': 'Genetic','Match object': copy(matching), 'Time': matching.solution_time, 'PercentNew': matching.pairs.isna().sum()})

        matching.match_genetic_algorithm_ALL_POSSIBILITIES()
        matches.append({'Name': 'Genetic all possibilities','Match object': copy(matching), 'Time': matching.solution_time, 'PercentNew': matching.pairs.isna().sum()})

        matching.match_genetic_algorithm_RANDOM()
        matches.append({'Name': 'Genetic random','Match object': copy(matching), 'Time': matching.solution_time, 'PercentNew': matching.pairs.isna().sum()})
    if brute:
        matching.match_brute()
        matches.append({'Name': 'Brute','Match object': copy(matching), 'Time': matching.solution_time, 'PercentNew': matching.pairs.isna().sum()})

    # TODO convert list of dfs to single df
    return matches


if __name__ == "__main__":
    #DEMAND_JSON = sys.argv[1]
    #SUPPLY_JSON = sys.argv[2]
    #RESULT_FILE = sys.argv[3]
    DEMAND_JSON = r"MatchingAlgorithms\sample_demand_input.json"
    SUPPLY_JSON = r"MatchingAlgorithms\sample_supply_input.json"
    RESULT_FILE = r"MatchingAlgorithms\result.csv"
    
    constraint_dict = {'Area' : '>=', 'Inertia_moment' : '>=', 'Length' : '>='} # dictionary of constraints to add to the method
    demand, supply = hm.create_random_data(demand_count=4, supply_count=5)
    score_function_string = "@lca.calculate_lca(length=Length, area=Area, gwp_factor=Gwp_factor, include_transportation=False)"
    result = run_matching(demand, supply, score_function_string=score_function_string, constraints = constraint_dict, add_new = True, sci_milp=False, milp=False, greedy_single=True, greedy_plural = False, bipartite=False, genetic=True)
    simple_pairs = hm.extract_pairs_df(result)
    simple_results = hm.extract_results_df(result)
    print("Simple pairs:")
    print(simple_pairs)
    print()
    print("Simple results")
    print(simple_results)