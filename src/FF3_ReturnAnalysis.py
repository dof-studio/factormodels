# FF3_ReturnAnalysis.py
# This is the module providing methods for analyzing data of returns
#

import os as os
import numpy as np
import pandas as pd

from FF3_Utilities import ols_dataframe
from FF3_Utilities import ols_dataframe_names
from FF3_Utilities import ols_dataframe_multinames

from FF3_Utilities import ErrorCode
from FF3_Utilities import PlotGraph
from FF3_Utilities import LoadDirData

# Class to perform analysis of grouped data
class GroupedAnalysis:
    
    # Data Members
    _data = None # original data (optional)

    ###########################################################################
    # Internal Functions
    #
    
    # Kernel - is none
    def __is_none__(self, x) -> bool:
        
        if x is None:
            return True
        else:
            return False
    
    # Kernel - whether this var should be removed
    # [params] x    : variable(s) to be tested, either a list,tuple, or a scalar
    # [params] logic: "or"  meaning whether one invalid returns invalid
    #                 "and" meaning only all are invalid returns invalid
    # [params] funcs: criterion functions, must handle Nonetype at the very first place
    def __rm_invalid__(self, x, logic = "or", funcs = ["default"]) -> bool:
        
        # if invalid logic
        if logic not in ["and", "or", "AND", "OR"]:
            raise ErrorCode("Invalid logic direction, \\logic\\ should be either 'and' or 'or'!")
        
        # if default funcs
        if type(funcs) != type([]):
            raise ErrorCode("Invalid function input, \\funcs\\ should be a list containing a function, or functions!")
        if funcs[0] == "default":
            funcs = [self.__is_none__,
                     np.isnan,
                     np.isinf,
                     np.isneginf]
        elif type(funcs[0]) == type(""):
            raise ErrorCode("Invalid function input, \\funcs\\ should be a list containing functions, but not non-default strings!")
        
        # if x is a list or a tuple
        if type(x) == type([]) or type(x) == type(()):
            ret = 0
            for it in x:
                ft = 0
                for f in funcs:
                    if f(it) == True:
                        ft += 1
                        if logic in ["or", "OR"]:
                            break
                    else:
                        ft += 0
                if ft > 0:
                    ret += 1
                else:
                    ret += 0
            # AND
            if logic in ["and", "AND"]:
                if ret == len(x):
                    return True
                else:
                    return False
            # OR
            else:
                if ret > 0:
                    return True
                else:
                    return False
            
        # else, regarding x is a scalar
        else:
            ret = 0
            ft = 0
            for f in funcs:
                if f(x) == True:
                    ft += 1
                    if logic in ["or", "OR"]:
                        break
                else:
                    ft += 0
            if ft > 0:
                ret += 1
            else:
                ret += 0
            if ret > 0:
                return True
            else:
                return False   
    
    ###########################################################################
    # API Functions
    #
    
    # Constructor
    def __init__(self, data = None, copy = True) -> None:
        
        if data is not None:  
            if copy == True:
                self._data = data.copy()
            else:
                self._data = data
          
        return None
    
    # Grouped Statistics of DataFrames
    # in  <- : dict{Index: pd.DataFrame}, with groupname indexed
    # out -> : dict{Index: dict{Index: scalar}}, with groupname(outside) and statname(inside) indexed
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    #          *use NoneType to avoid manually settings on a certain factor
    # [params] bycol_staton: str, the column name on the column to be performed by a statistical function
    # [params] stat_func   : function, a statistical function which accpets a vector as the input and output a numerical scalar
    #                        list of functions, with the same meaning
    # [params] stat_nameas : str, specify the internal dict's key name
    #                        list of strings, with the same meaning
    # [params] stat_intype : a kind of type, if is not None, it will firstly be converted into that type and then apply the statistical function
    # [params] appended    : Nonetype or a dict, if not a Nonetype, the keys must be the same with the keys of the input \use
    def grouped_stat(self, use = "default", *,
           bycol_staton,
           stat_func = [np.mean],
           stat_nameas = ["DefaultStatName"],
           stat_intype = np.array,
           appended = None,
           rmrows = ["default"],
           astype = None, 
           copy = True) -> dict[any]:
            
        #######################################################################
        #
        # If uses the default use
        if type(use) != type({}):
            if use == "default":
                use = self.__rm_invalid__
            else:
                raise ErrorCode("Invalid input data in the var \\use\\!")
                
        # If uses the default rmrows
        if type(rmrows) == type([]):
            if rmrows[0] == "default":
                rmrows = ["default"]
        elif rmrows is not None:
            raise ErrorCode("Invalid input criterion functions in the var \\rmrows\\! While this can be a None in this instance!")
        
        # If use it None, return None
        if use is None:
            raise ErrorCode("Invalid input data in the var \\use\\!")
        
        # Checking if the cols exist
        for k in use.keys():
            if bycol_staton not in use[k].columns:
                raise ErrorCode("Invalid column name in the var \\bycol_staton\\!")
        
        # If the function is None
        if stat_func is None:
            raise ErrorCode("Invalid statistical function provided in the var \\stat_func\\!")
        
        # If the appended is not None, check the names
        if appended is not None:
            for n in appended.keys():
                if n not in use.keys():
                    raise ErrorCode("Invalid appended dict in the var \\appended\\! While not Nonetype, it must have the very same keys with the input \\use\\!")
        
        # If stat_func is a list 
        if type(stat_func) == type([]):
            if len(stat_func) == 0:
                raise ErrorCode("The length of \\stat_func\\ and \\stat_nameas\\ must be strictly positive!")
            if type(stat_nameas) != type([]):
                raise ErrorCode("The type of \\stat_func\\ and \\stat_nameas\\ should be either lists or strings!")
            else:
                if len(stat_func) != len(stat_nameas):
                    raise ErrorCode("The length of \\stat_func\\ and \\stat_nameas\\ should be explicitly the same!")
        else:
            if type(stat_nameas) != type(""):
                raise ErrorCode("The type of \\stat_func\\ and \\stat_nameas\\ should be either lists or strings!")
            else:
                # make them into a list
                stat_func = [stat_func]
                stat_nameas = [stat_nameas]
        
        # Change the type of the DataFrame
        uses = []
        if copy == True:
            uses = use.copy()
        else:
            uses = use
        if astype is not None:
            for k in uses.keys():
                uses[k] = uses[k].astype(astype)
        for k in uses.keys():
            uses[k][bycol_staton] = uses[k][bycol_staton].astype(float)
        # Column names will not be changed in this function
        
        #######################################################################
        #
        # Try and test the rmrows's returned value
        if rmrows is not None:
            if type(self.__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
                raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")

        # Remove invalid rows
        kpvalids = {}
        if rmrows is not None:
            for k in uses.keys():
                valRows = []
                for i in range(len(uses[k])):
                    tup = (uses[k][bycol_staton].iloc[i])
                    cri = self.__rm_invalid__(x = tup, funcs = rmrows)
                    if cri == False:
                        valRows.append(i)
                kpvalids[k] = uses[k].iloc[valRows,:].copy()
        else:
            kpvalids = uses # do not copy since nothing's been done
            
        # Rename back
        uses = kpvalids
        
        # Create a new dict
        # which has the same keys() with uses but the values of each page is a statistical scalar
        statdict = {}
        if appended is not None:
            statdict = appended.copy()
        else:
            statdict = {}
            for k in uses.keys():
                statdict[k] = {}
        
        # For each page, apply the function properly
        for k in uses.keys():
            
            # For each function and name
            for i in range(len(stat_func)):
                
                # Perform the type transformation
                lst = []
                if stat_intype is not None:
                    lst = stat_intype(uses[k][bycol_staton])
                else:
                    lst = uses[k][bycol_staton]
                
                # Perform the statistical function and get the returned value
                ret = stat_func[i](lst)
                
                statdict[k][stat_nameas[i]] = ret
            
        return statdict
    
    # Grouped Panel Illustration
    # in  <- : dict{Index: dict{Index: Value}}, with groupname indexed, the output of grouped_stat()
    # out -> : pd.DataFrame, which is an illustration of some certain statistical data
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] stat_key     : the name of the key used, declaring the stat kind to be used
    # [params] g2pairs      : g2p dict, the output of \grpname_to_ndpairs
    # [params] g2pairs_names: list of 2 elements, with names of its dimension
    def grouped_panelillust(self, use = "default", *,
           stat_key:str,
           stat_key_typeas = float,
           g2pairs:dict,
           g2pairs_names = ["D1", "D2"],
           astype = None, 
           copy = True) -> pd.DataFrame:
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type({}):
            if use == "default":
                use = self.__rm_invalid__
            else:
                raise ErrorCode("Invalid input data in the var \\use\\!")
                
        # If use it None, return None
        if use is None:
            raise ErrorCode("Invalid input data in the var \\use\\!")
            
        # If the stat_key is not a string
        if type(stat_key) != type(""):
            raise ErrorCode("Invalid input type in the var \\stat_key\\! It must be a string!")
        
        # Checking if the cols exist
        for k in use.keys():
            if stat_key not in use[k].keys():
                raise ErrorCode("Invalid key name in the var \\stat_key\\!")
        
        # If the g2pairs is not a dict
        if type(g2pairs) != type({}):
            raise ErrorCode("Invalid statistical function provided in the var \\stat_func\\!")
        
        # If the dim of g2pairs is not 2
        # Or if the dim of g2pairs_names is not 2
        for k in g2pairs.keys():
            if len(g2pairs[k]) != 2:
                raise ErrorCode("Invalid dimension in the var \\g2pair\\! It must contains a 2-dim tuple as a pair!")
        if len(g2pairs_names) != 2:
           raise ErrorCode("Invalid dimension in the var \\g2pair_pair\\! It must contains a 2 variable names for the two dimension!") 
        
        #######################################################################
        #
        # Create the set for two dims
        dim_1 = set() # for columns
        dim_2 = set() # for rows
        for k in g2pairs.keys():
            tp1, tp2 = g2pairs[k]
            dim_1.add(tp1)
            dim_2.add(tp2)
        dim_1_list = list(dim_1)
        dim_2_list = list(dim_2)
        dim_1_list.sort()
        dim_2_list.sort()
        
        # Create a column of zero (float)
        col0 = []
        for i in range(len(dim_2_list)):
            col0.append(stat_key_typeas())
        
        # Create the panel
        panel = pd.DataFrame()
        for i in range(len(dim_1_list)):
            if i == 0:
                panel[g2pairs_names[0] + "_" + str(dim_1_list[i])] = col0
            else:
                panel[str(dim_1_list[i])] = col0
        rowindex = list(panel.index.astype(str))
        rowindex[0] = g2pairs_names[1] + "_" +  str(dim_2_list[0])
        panel.index = rowindex
        
        # Fill the panel
        for k in use.keys():
            
            # Look up, and find the pair
            tp1, tp2 = g2pairs[k]
            
            # Look up, and find the value
            val = stat_key_typeas(use[k][stat_key])
            
            # Look up, and find the index of the two dimension
            dm1 = dim_1_list.index(tp1)
            dm2 = dim_2_list.index(tp2)
            
            panel.iloc[dm2, dm1] = val
        
        return panel
    
    # Grouped OLS Regression
    # in  <- : dict{Index: dict{Index: Value}}, with groupname indexed, the output of grouped_stat()
    # out -> : tuple(dict{Index: dict{Index: scalar}}, dict{Index: pd.DataFrame})
    #                ^
    #                stat-like appended                ^
    #                                                  original regression DataFrame
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    #          *use NoneType to avoid manually settings on a certain factor
    # [params] stat_nameas : str, specify the internal dict's key name
    #                        list of strings, with the same meaning
    #               !! !! !! Specifically, they should match the columns of the ols-output dataframe
    # [params] appended    : Nonetype or a dict, if not a Nonetype, the keys must be the same with the keys of the input \use
    def grouped_olsstat(self, use = "default", *,
           bycol_x:list,
           bycol_y:str,
           stat_nameas = ["coef", "serr", "t-val", "p-val", "r2"],
           appended = None,
           rmrows = ["default"],
           astype = None, 
           copy = True) -> tuple[dict, dict]:
            
        #######################################################################
        #
        # If uses the default use
        if type(use) != type({}):
            if use == "default":
                use = self.__rm_invalid__
            else:
                raise ErrorCode("Invalid input data in the var \\use\\!")
                
        # If uses the default rmrows
        if type(rmrows) == type([]):
            if rmrows[0] == "default":
                rmrows = ["default"]
        elif rmrows is not None:
            raise ErrorCode("Invalid input criterion functions in the var \\rmrows\\! While this can be a None in this instance!")
        
        # If use it None, return None
        if use is None:
            raise ErrorCode("Invalid input data in the var \\use\\!")
        
        # Checking if the cols exist
        for k in use.keys():
            for x in bycol_x:
                if x not in use[k].columns:
                    raise ErrorCode("Invalid column name in the var \\bycol_x\\!")
            if bycol_y not in use[k].columns:
                raise ErrorCode("Invalid column name in the var \\bycol_y\\!")
            
        # If the appended is not None, check the names
        if appended is not None:
            for n in appended.keys():
                if n not in use.keys():
                    raise ErrorCode("Invalid appended dict in the var \\appended\\! While not Nonetype, it must have the very same keys with the input \\use\\!")
        
        # OLS names
        olsnames = set(ols_dataframe_names())
        olsmultis = set(ols_dataframe_multinames())
        
        # If the nameas is not in the ols_dataframe_names
        for n in stat_nameas:
            if n not in olsnames:
                raise ErrorCode("Invalid ols output column name in the var \\stat_nameas\\! It shoud be one, or more in the ols_dataframe_names() returned list!")
        
        # Change the type of the DataFrame
        uses = []
        if copy == True:
            uses = use.copy()
        else:
            uses = use
        if astype is not None:
            for k in uses.keys():
                uses[k] = uses[k].astype(astype)
        for k in uses.keys():
            for x in bycol_x:
                uses[k][x] = uses[k][x].astype(float)
        # Column names will not be changed in this function
        
        #######################################################################
        #
        # Try and test the rmrows's returned value
        if rmrows is not None:
            if type(self.__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
                raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")

        # Remove invalid rows
        kpvalids = {}
        if rmrows is not None:
            for k in uses.keys():
                valRows = []
                for i in range(len(uses[k])):
                    tup = []
                    for x in bycol_x:
                        tup.append(uses[k][x].iloc[i])
                    tup = tuple(tup)
                    cri = self.__rm_invalid__(x = tup, funcs = rmrows)
                    if cri == False:
                        valRows.append(i)
                kpvalids[k] = uses[k].iloc[valRows,:].copy()
        else:
            kpvalids = uses # do not copy since nothing's been done
            
        # Rename back
        uses = kpvalids
        
        # For each page, perform the ols regression
        olspages = {}
        for k in uses.keys():
            olspages[k] = ols_dataframe(
                y = uses[k][bycol_y],
                x = uses[k][bycol_x])[0]
        
        # Create a new dict
        # which has the same keys() with uses but the values of each page is a statistical scalar
        statdict = {}
        if appended is not None:
            statdict = appended.copy()
        else:
            statdict = {}
            for k in uses.keys():
                statdict[k] = {}
        
        # For each page, apply the ols'returning values properly
        for k in uses.keys():
            
            # For each ols-param
            for i in range(len(stat_nameas)):
                
                # If it is a multi-name
                # Then iterate each row
                if stat_nameas[i] in olsmultis:
                    
                    inds = list(olspages[k].index)
                    
                    # For each variable 
                    for r in range(len(inds)):
                        
                        # New name
                        neoname = stat_nameas[i] + "_" + str(inds[r])
                        
                        # New value
                        neovalue = olspages[k][stat_nameas[i]].iloc[r]
                        
                        statdict[k][neoname] = neovalue
                        
                # Else if only one row
                else:
                    statdict[k][stat_nameas[i]] = olspages[k][stat_nameas[i]].iloc[0]
            
        return statdict, olspages
    

# End of this file