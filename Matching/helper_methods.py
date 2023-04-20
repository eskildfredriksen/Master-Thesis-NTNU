import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import igraph as ig
import logging
import LCA as lca
import itertools
import random
from fpdf import FPDF
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==== HELPER METHODS ====
# This file contains various methods used for testing and development. 

def extract_pairs_df(dict_list):
    """Creates a dataframe with the matching pairs all evaluated matching methods. 
    input: list of dictionaries for each matching method
    output: dataframe with the matching pairs of all methods."""
    sub_df = []
    cols = []
    for run in dict_list:
        sub_df.append(run['Match object'].pairs)
        cols.append(run['Name'])
    df = pd.concat(sub_df, axis = 1)
    df.columns = cols
    return df

def extract_results_df(dict_list, column_name):
    """Creates a dataframe with the scores from each method"""
    sub_df = []
    cols = []
    for run in dict_list:
        sub_df.append(run['Match object'].result)
        cols.append(run['Name'])
    df = pd.DataFrame(sub_df, index= cols)    
    df=df.rename(columns={0: column_name})
    return df.round(3)

def remove_alternatives(x, y):
    if x > y:
        return np.nan
    else:
        return x

def transform_weights(weights):
    """Transform the weight matrix to only contain one column with new elements in stead of one column for each new element

    Args:
        DataFrame: weight matrix

    Returns:
        DataFrame: weight matrix
    """
    weights = weights.copy(deep = True)
    cols=list(weights.columns)[-len(weights):]
    weights["N"]=weights[cols].sum(axis=1)
    weights = weights.drop(columns=cols)
    return weights

def create_random_data_demand(demand_count, demand_lat, demand_lon, new_lat, new_lon, demand_gwp=lca.TIMBER_GWP,gwp_price=lca.GWP_PRICE,new_price_per_m2=lca.NEW_ELEMENT_PRICE_TIMBER, length_min = 1, length_max = 15.0, area_min = 0.15, area_max = 0.15):
    """Create two dataframes for the supply and demand elements used to evaluate the different matrices"""
    np.random.RandomState(2023) #TODO not sure if this is the right way to do it. Read documentation
    demand = pd.DataFrame()
   
    # create element lenghts
    demand['Length'] = ((length_max/2 + 1) - length_min) * np.random.random_sample(size = demand_count) + length_min
    # create element areas independent of the length. Can change this back to Artur's method later, but I want to see the effect of even more randomness. 
    demand['Area'] = ((area_max + .001) - area_min) * np.random.random_sample(size = demand_count) + area_min
    # intertia moment
    demand['Inertia_moment'] = demand.apply(lambda row: row['Area']**(2)/12, axis=1)   # derived from area assuming square section
    # height - assuming square cross sections
    demand['Height'] = np.power(demand['Area'], 0.5)
    # gwp_factor
    demand['Gwp_factor'] = demand_gwp
    demand["Demand_lat"]=demand_lat
    demand["Demand_lon"]=demand_lon
    demand["Supply_lat"]=new_lat
    demand["Supply_lon"]=new_lon
    demand["Price_per_m2"]=new_price_per_m2
    demand["Gwp_price"]=gwp_price

    # Change index names
    demand.index = map(lambda text: 'D' + str(text), demand.index)
    return demand.round(4)

def create_random_data_supply(supply_count,demand_lat, demand_lon,supply_coords,supply_gwp=lca.TIMBER_REUSE_GWP,gwp_price=lca.GWP_PRICE,reused_prise_per_m2=lca.REUSED_ELEMENT_PRICE_TIMBER, length_min = 1, length_max = 15.0, area_min = 0.15, area_max = 0.15):
    np.random.RandomState(2023) #TODO not sure if this is the right way to do it. Read documentation
    supply = pd.DataFrame()
    supply['Length'] = ((length_max + 1) - length_min) * np.random.random_sample(size = supply_count) + length_min
    supply['Area'] = ((area_max + .001) - area_min) * np.random.random_sample(size = supply_count) + area_min
    supply['Inertia_moment'] = supply.apply(lambda row: row['Area']**(2)/12, axis=1)   # derived from area assuming square section
    supply['Height'] = np.power(supply['Area'], 0.5)
    supply['Gwp_factor'] = supply_gwp
    supply["Demand_lat"]=demand_lat
    supply["Demand_lon"]=demand_lon
    supply["Location"]=0
    supply["Supply_lat"]=0
    supply["Supply_lon"]=0
    supply["Price_per_m2"]=reused_prise_per_m2
    supply["Gwp_price"]=gwp_price
    
    for row in range(len(supply)):
        lokasjon=random.randint(0, len(supply_coords)-1)
        supply.loc[row,"Supply_lat"]=supply_coords.loc[lokasjon,"Lat"]
        supply.loc[row,"Supply_lon"]=supply_coords.loc[lokasjon,"Lon"]
        supply.loc[row,"Location"]=supply_coords.loc[lokasjon,"Place"]
    supply.index = map(lambda text: 'S' + str(text), supply.index)

    return supply.round(4)


def extract_brute_possibilities(incidence_matrix):
    """Extracts all matching possibilities based on the incidence matrix.

    Args:
        Dataframe: incidence matrix

    Returns:
        list: three-dimensional list
    """

    binary_incidence = incidence_matrix*1 #returnes incidence matrix with 1 and 0 instead od True/False
    
    three_d_list=[]
    incidence_list=binary_incidence.values.tolist()
    for row in incidence_list:
        rowlist=[]
        for i in range(len(row)):
            if row[i]==1:
                newlist=[0]*len(row)
                newlist[i]=1
                rowlist.append(newlist)
        three_d_list.append(rowlist)
    return three_d_list 

def display_graph(matching, graph_type='rows', show_weights=True, show_result=True):
    """Plot the graph and matching result"""
    if not matching.graph:
        matching.add_graph()
    weight = None
    if show_weights:
        # weight = list(np.absolute(np.array(self.graph.es["label"]) - 8).round(decimals=2)) 
        weight = list(np.array(matching.graph.es["label"]).round(decimals=2)) 
    edge_color = None
    edge_width = matching.graph.es["label"]
    if show_result and not matching.pairs.empty:
        edge_color = ["gray"] * len(matching.graph.es)
        edge_width = [0.7] * len(matching.graph.es)
        # TODO could be reformatted like this https://igraph.readthedocs.io/en/stable/tutorials/bipartite_matching.html#tutorials-bipartite-matching
        not_found = 0
        for index, pair in matching.pairs.iterrows():
            source = matching.graph.vs.find(label=index) 
            try:
                target = matching.graph.vs.find(label=pair['Supply_id'])
                edge = matching.graph.es.select(_between = ([source.index], [target.index]))
                edge_color[edge.indices[0]] = "black" #"red"
                edge_width[edge.indices[0]] = 2.5
            except ValueError:
                not_found+=1
        if not_found > 0:
            logging.error("%s elements not found - probably no new elements supplied.", not_found)
    vertex_color = []
    for v in matching.graph.vs:
        if 'D' in v['label']:
            vertex_color.append("lightgray")
        elif 'S' in v['label']:
            vertex_color.append("slategray")
        else:
            vertex_color.append("pink")
    layout = matching.graph.layout_bipartite()
    if graph_type == 'rows':
        layout = matching.graph.layout_bipartite()
    elif graph_type == 'circle':
        layout = matching.graph.layout_circle()
    if matching.graph:
        fig, ax = plt.subplots(figsize=(15, 10))
        ig.plot(
            matching.graph,
            target=ax,
            layout=layout,
            vertex_size=0.4,
            vertex_label=matching.graph.vs["label"],
            palette=ig.RainbowPalette(),
            vertex_color=vertex_color,
            edge_width=edge_width,
            edge_label=weight,
            edge_color=edge_color,
            edge_curved=0.15
        )
        plt.show()
"""Converts the best solution a column containing the supply matches for each demand element. 
    This column is added to the weight-matrix in order to visually check if the matching makes sense
    - weights: Pandas Dafarame
    - best_solution: 1d-list with 0's and 1's
    - number_of_demand_elements: integer

    Returns a pandas dataframe
    """
def extract_genetic_solution(weights, best_solution, number_of_demand_elements):
    """Converts the best solution into a column containing the supply matches for each demand element. 
    This column is added to the weight-matrix in order to visually check if the matching makes sense

    Args:
        weights (DataFrame): weight matrix
        best_solution (list): list of integers containing the best solution from genetic algorithm
        number_of_demand_elements (int): number of demand elements

    Returns:
        DataFrame: The weight matrix with a new column containing the matches for each demand element
    """
    result = weights.copy(deep = True)
    buckets = np.array_split(best_solution, number_of_demand_elements)
    weight_cols = weights.columns.values.tolist()
    match_column = []
    for i in range(len(buckets)):
        index = np.where(buckets[i] == 1)[0] #Finding matches
        if len(index) == 0 or len(index) > 1: #This happens either if a match is not found or multiple supply-elements are matched with the same demand elemend => invalid solution
            match = f"N{i}" #Set match to New element. 
            if len(index) > 1:
                logging.info("OBS: Multiple supply matched with one demand")
        else:
            match = weight_cols[index[0]]
            if match == "N":
                match = f"N{i}"
        match_column.append(match)
    result["Matches from genetic"] = match_column
    return result

def print_genetic_solution(weights, best_solution, number_of_demand_elements):
    """Prints the genetic solution in a readable way to visually evaluate if the solution makes sence. Used for debugging

    Args:
        weights (DataFrame): weight matrix
        best_solution (list): list of integers containing the best solution from genetic algorithm
        number_of_demand_elements (int): number of demand elements

    Returns:
        DataFrame: The weight matrix with a new column containing the matches for each demand element
    """
    result = weights.copy(deep = True)
    buckets = np.array_split(best_solution, number_of_demand_elements)
    weight_cols = weights.columns.values.tolist()
    weight_cols = list(map(lambda x: x.replace("N0", "N"), weight_cols))
    weight_cols.append("N0")
    match_column = []
    for i in range(len(buckets)):
        index = np.where(buckets[i] == 1)[0] #Finding matches
        if len(index) == 0:
            match = ["No match"]
        else:
            match = [weight_cols[x] for x in index]
        match_column.append(match)
    result["Matches from genetic"] = match_column
    return result

def export_dataframe_to_csv(dataframe, file_location):
    """Exports a dataframe to a csv file

    Args:
        dataframe (DataFrame): dataframe
        file_location (string): location of the new file
    """
    dataframe.to_csv(file_location)

def import_dataframe_from_csv(file_location):
    """Creates a dataframe from a csv file in a given file location

    Args:
        file_location (string): location of imported csv-file

    Returns:
        DataFrame: dataframe
    """
    dataframe = pd.read_csv(file_location)
    row_names = list(dataframe.index)
    new_row_names = list(dataframe["Unnamed: 0"])
    row_dict = {row_names[i]: new_row_names[i] for i in range(len(row_names))}
    dataframe.drop(columns=["Unnamed: 0"], inplace = True)
    dataframe.rename(index=row_dict, inplace = True)
    return dataframe


def add_graph_plural(demand_matrix, supply_matrix, weight_matrix, incidence_matrix):
    """Add a graph notation based on incidence matrix
    
    Not used
    """
    vertices = [0]*len(demand_matrix.index) + [1]*len(supply_matrix.index)
    num_rows = len(demand_matrix.index)
    edges = np.transpose(np.where(incidence_matrix))
    edges = [[edge[0], edge[1]+num_rows] for edge in edges]
    edge_weights = weight_matrix.to_numpy().reshape(-1,)
    edge_weights = edge_weights[~np.isnan(edge_weights)]
    # We need to reverse the weights, so that the higher the better. Because of this edge weights are initial score minus the replacement score:
    edge_weights = (np.array([demand_matrix.Score[edge[0]] for edge in edges ])+0.0000001) - edge_weights 
    # assemble graph
    graph = ig.Graph.Bipartite(vertices, edges)
    graph.es["label"] = edge_weights
    graph.vs["label"] = list(demand_matrix.index)+list(supply_matrix.index) #vertice names
    return graph


def count_matches(matches, algorithm):
    """Counts the number of plural matches for each supply element

    Args:
        matches (Pandas Dataframe): return dataframe of hm.extract_pairs_df()
        algorithm (str): Name of algorithm in "matches"

    Returns:
        Pandas Dataframe: A count for each supply element
    """
    return matches.pivot_table(index = [algorithm], aggfunc = 'size')


def create_report(metric, Rows):
    # Create a new PDF object
    # Create a new PDF object
    pdf = FPDF()
    
    # Add a page to the PDF
    pdf.add_page()
    
    # Set the background color
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(0, 0, 210, 297, "F")
    
    # Add the image to the PDF
    pdf.image("C:/Users/sigur/Downloads/NTNU-logo.png", x=10, y=10, w=30)
    
    # Set the font and size for the title
    pdf.set_font("Arial", size=36)
    #pdf.set_text_color(0, 64, 128)
    pdf.set_text_color(0, 80, 158)
    
    # Add the title to the PDF
    pdf.cell(0, 50, "Results from Element Matching", 0, 1, "C")
    pdf.ln(20)
    
    # Set the font and size for the tables
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.set_left_margin(28)
    
     # Calculate the X and Y positions for the tables
    table_x = (pdf.w - 180) / 2
    table_y1 = 120
    table_y2 = 185
    
    # Set cell alignment to center for table 1
    pdf.set_xy(table_x, table_y1)
    pdf.multi_cell(160, 7, txt="Table 1")
    pdf.ln(10)
    pdf.set_fill_color(247, 247, 247)
    pdf.set_draw_color(239, 239, 239)
    for i in range(1, 4):
        for j in range(1, 4):
            pdf.cell(50, 10, f"({i},{j})", 1, 0, "C", True)
        pdf.ln()
    pdf.ln(20)
    
    # Set cell alignment to center for table 2
    pdf.set_xy(table_x, table_y2)
    pdf.multi_cell(160, 7, txt="Table 2")
    pdf.ln(10)
    pdf.set_fill_color(96, 150, 208)
    pdf.set_draw_color(204, 204, 204)
    pdf.cell(50, 10, "Elements", 1, 0, "C", True)
    pdf.cell(50, 10, "Filename", 1, 0, "C", True)
    pdf.cell(50, 10, "Number of elements", 1, 1, "C", True)
    for i in range(Rows):
        pdf.set_fill_color(247, 247, 247)
        for j in range(3):
            pdf.cell(50, 10, f"Row {i+1}, Column {j+1}", 1, 0, "C", True)
        pdf.ln()
    pdf.ln(20)
    
    # Add the paragraph to the PDF
    pdf.set_font("Arial", size=12, style="I")
    pdf.cell(0, 10, f"Metric used: {metric}", 0, 1)
    
    # Add the date to the upper right corner of the PDF
    pdf.set_xy(170, 10)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, str(date.today().strftime("%B %d, %Y")), 0, 1, "R")
    
    
    

    
    # Save the PDF to a file
    pdf.output("C:/Users/sigur/Downloads/report2.pdf")


    

print_header = lambda matching_name: print("\n"+"="*(len(matching_name)+8) + "\n*** " + matching_name + " ***\n" + "="*(len(matching_name)+8) + "\n")