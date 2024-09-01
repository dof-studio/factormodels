# FF3_FactorBuilding.py
# This is the module building up the FF3 factors on given data
#

import numpy as np
import pandas as pd

from FF3_Utilities import pos
from FF3_Utilities import strint
from FF3_Utilities import yearmonth
from FF3_Utilities import inwhich_zone
from FF3_Utilities import ErrorCode

# Factor Utilities
class FactorUtils:
    
    # Const Members
    __int__ = 0
    __bigint__ = 2**100
    __float__ = 0.0
    __npfloat16__ = np.float16()
    __npfloat32__ = np.float32()
    __npfloat64__ = np.float64()
    
    # Data Members
    _data = None  # original data (optional)
    _in_list = [] # in_list initialization
    _in_set = {}  # in_set initialization
    
    ###########################################################################
    # API Functions
    #
    
    # Constructor
    def __init__(self, data = None, in_list = [], in_set = {}, *, 
                 copy = True) -> None:
        
        if data is not None:  
            if copy == True:
                self._data = data.copy()
            else:
                self._data = data
        
        if in_list is not None:
            if copy == True:
                self._in_list = in_list.copy()
            else:
                self._in_list = in_list
                
        if in_set is not None:
            if copy == True:
                self._in_set = in_set.copy()
            else:
                self._in_set = in_set
            
        return None
    
    # Boolean_lessthanzero
    def Boolean_lessthanzero(self, x, *,
            equal_as = True, handle_invalid = False, handle_none = True) -> bool:
        
        # if hancle none
        if handle_none == True:
            if x is None:
                return True
        else:
            if x is None:
                raise ErrorCode("Invalid input \\x\\! Nonetype is only passed when \\handle_none\\ is set to True.")
        
        if type(x) == type(self.__int__):
            if x == self.__int__:
                return equal_as
            elif x < self.__int__:
                return True
            else:
                return False
            
        elif type(x) == type(self.__bigint__):
            if x == self.__int__:
                return equal_as
            elif x < self.__int__:
                return True
            else:
                return False
            
        elif type(x) == type(self.__float__):
            if x == self.__float__:
                return equal_as
            elif x < self.__float__:
                return True
            else:
                return False
            
        elif type(x) == type(self.__npfloat16__):
            if x == self.__npfloat16__:
                return equal_as
            elif x < self.__npfloat16__:
                return True
            else:
                return False
    
        elif type(x) == type(self.__npfloat32__):
            if x == self.__npfloat32__:
                return equal_as
            elif x < self.__npfloat32__:
                return True
            else:
                return False
            
        elif type(x) == type(self.__npfloat64__):
            if x == self.__npfloat64__:
                return equal_as
            elif x < self.__npfloat64__:
                return True
            else:
                return False
            
        # Invalid
        else:
            if handle_invalid == True:
                return True
            else:
                raise ErrorCode("Invalid input \\x\\! Non-numerical variable is only passed when \\handle_invalid\\ is set to True.")
    
    # Boolean_containsin
    def Boolean_containsin(self, x, in_list = ["default"], *,
         handle_invalid = False, handle_none = True) -> bool:
        
        # if in_list is default, use the member
        if type(in_list) != type([]):
            raise ErrorCode("Invalid input \\in_list\\! A list is a must!")
        else:
            if in_list[0] == "default":
                in_list = self._in_list
    
        # if handle none
        if handle_none == True:
            if x is None:
                return True
        else:
            if x is None:
                raise ErrorCode("Invalid input \\x\\! Nonetype is only passed when \\handle_none\\ is set to True.")
        
        # If in_list is a list
        if type(in_list) == type([]):
            if x in in_list:
                return True
            else:
                return False
        
        # Invalid
        else:
            if handle_invalid == True:
                return True
            else:
                raise ErrorCode("Invalid setting \\in_list\\! Non-list variable is only passed when \\handle_invalid\\ is set to True.")

    # Boolean_notcontainsin
    def Boolean_notcontainsin(self, x, in_list = ["default"], *,
         handle_invalid = False, handle_none = True) -> bool:
        
        return not self.Boolean_containsin(x, in_list, 
         handle_invalid = handle_invalid,
         handle_none = handle_none)
    
    # Boolean_containsinset
    def Boolean_containsinset(self, x, in_set = {}, *,
         handle_invalid = False, handle_none = True) -> bool:
        
        # if in_set is default, use the member
        if len(in_set) == 0:
            in_set = self._in_set
        if type(in_set) != type({1}):
            print(type(in_set))
            print(in_set)
            raise ErrorCode("Invalid input \\in_set\\! A set is a must!")
    
        # if handle none
        if handle_none == True:
            if x is None:
                return True
        else:
            if x is None:
                raise ErrorCode("Invalid input \\x\\! Nonetype is only passed when \\handle_none\\ is set to True.")
        
        # If in_set is a set
        if type(in_set) == type({1}):
            if x in in_set:
                return True
            else:
                return False
        
        # Invalid
        else:
            if handle_invalid == True:
                return True
            else:
                raise ErrorCode("Invalid setting \\in_list\\! Non-list variable is only passed when \\handle_invalid\\ is set to True.")
    
    # Boolean_notcontainsinset
    def Boolean_notcontainsinset(self, x, in_set = {}, *,
         handle_invalid = False, handle_none = True) -> bool:
        
        return not self.Boolean_containsinset(x, in_set, 
         handle_invalid = handle_invalid,
         handle_none = handle_none)
    
    # End of Class

# Base class for factor
class __FactorBase__:
    
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

    # Remove some non-suitable samples
    # in  <- pd.DataFrame annually
    # out -> pd.DataFrame annually, with some filtered rows removed
    # Note: No Column in this function will be renamed!
    # [params] method: you must chose one from the tuple provided
    #             for "sample", only the invalid sample will be removed
    #             for "identity", all the samples with the same identity will be removed
    # [params] bycol_identity can be None, where "identity" method will throw an error
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    def remove_some_samples(self, use = "default", *,
           bycol_identity = None,
           bycol_chk,
           rmrows = ["default"],
           method = ("sample", "identity"),
           astype = None, 
           copy = True) -> pd.DataFrame:
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type(pd.DataFrame()):
            if use == "default":
                use = self._data
            else:
                raise ErrorCode("Invalid input data in the var \\use\\!")
                
        # If uses the default rmrows
        if type(rmrows) == type([]):
            if rmrows[0] == "default":
                rmrows = ["default"]
        else:
            raise ErrorCode("Invalid input criterion functions in the var \\rmrows\\!")
        
        # If use it None, return None
        if use is None:
            raise ErrorCode("Invalid input data in the var \\use\\!")
        
        # Checking if the cols exist
        # Special! allow somehow None
        if method == "identity":
            if bycol_identity not in use.columns:
                raise ErrorCode("Invalid column name in the var \\bycol_identity\\ when the method is chosen as 'identity'!")
        if bycol_chk not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_chk\\!")
        
        # Change the type of the DataFrame
        uses = []
        if copy == True:
            uses = use.copy()
        else:
            uses = use
        if astype is not None:
            uses = uses.astype(astype)
        # Do not specifically change the nominal columns' types
        
        #######################################################################
        #
        # Try and test the rmrows's returned value
        if type(self.__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
            raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")

        # Try and see whether the method is valid
        if type(method) == type(()):
            raise ErrorCode("Invalid selected method in the var \\method\\! You must select any one of the default tuple as your \\method\\ parameter, rather than using the default tuple directly!")
        elif type(method) != type(""):
            raise ErrorCode("Invalid selected method in the var \\method\\! You must select any one of the default tuple as your \\method\\ parameter, rather than using any other invalid input!")
        elif method not in ["sample", "identity"]:
            raise ErrorCode("Invalid selected method in the var \\method\\! You must select any one of the default tuple as your \\method\\ parameter, rather than using any other invalid string!")
        
        # Remove invalid rows
        validRows = []
        # method sample
        if method == "sample":
            for i in range(len(uses)):
                cri = self.__rm_invalid__(x = uses[bycol_chk].iloc[i], funcs = rmrows)
                if cri == False:
                    validRows.append(i)
        # method identity
        elif method == "identity":
            idents = []
            for i in range(len(uses)):
                cri = self.__rm_invalid__(x = uses[bycol_chk].iloc[i], funcs = rmrows)
                if cri == True:
                    idents.append(uses[bycol_identity].iloc[i])
            idents = list(set(idents))
            bldels = list(uses[bycol_identity].isin(idents))
            for i in range(len(bldels)):
                if bldels[i] == False:
                    validRows.append(i)
        # build up two sets
        # get the difference of the sets as the valid rows
        kpvalids = uses.iloc[validRows,:].copy()
        
        return kpvalids
    
    # Drop identical samples
    # in  <- pd.DataFrame annually
    # out -> pd.DataFrame annually, with identical rows removed
    # Note: No Column in this function will be renamed!
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    # [params] bycol_on: list of column names to be regarded as identical signitures
    def drop_identical_samples(self, use = "default", *,
           bycol_on = [],
           rmrows = ["default"],
           astype = None, 
           copy = True) -> pd.DataFrame:
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type(pd.DataFrame()):
            if use == "default":
                use = self._data
            else:
                raise ErrorCode("Invalid input data in the var \\use\\!")
                
        # If uses the default rmrows
        if type(rmrows) == type([]):
            if rmrows[0] == "default":
                rmrows = ["default"]
        else:
            raise ErrorCode("Invalid input criterion functions in the var \\rmrows\\!")
        
        # If use it None, return None
        if use is None:
            raise ErrorCode("Invalid input data in the var \\use\\!")
        
        # If bycol_on is not a list or an empty list
        if type(bycol_on) != type([]):
            raise ErrorCode("Invalid specified type in the var \\bycol_on\\!")
        if len(bycol_on) == 0:
            raise ErrorCode("By_columns_on list in the var \\bycol_on\\ should be a non-empty list!")
        
        # Checking if the cols exist
        for i in range(len(bycol_on)):
            if bycol_on[i] not in use.columns:
                raise ErrorCode("Invalid column name in the var \\bycol_on\\'s \\"+ bycol_on[i] + "\\ element!")
        
        # Change the type of the DataFrame
        uses = []
        if copy == True:
            uses = use.copy()
        else:
            uses = use
        if astype is not None:
            uses = uses.astype(astype)
        # Do not specifically change the nominal columns' types
        
        #######################################################################
        #
        # Try and test the rmrows's returned value
        if type(self.__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
            raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")
            
        # Make things together as a tmp list
        mk = []
        for i in range(len(uses)):
            tmp = ""
            for bn in bycol_on:
                tmp += str(uses[bn].iloc[i])
            mk.append(tmp)
        
        # Use a dict to save duplicated rows
        # the key is elms in the mk, the value is the rows used
        mkdict = {}
        for i in range(len(mk)):
            mkdict[mk[i]] = i
        # continue
        vals = list(mkdict.values())
        identuses = uses.iloc[vals,:].copy()
            
        return identuses
    
    # Collect Stock-Indexed Return Sheets
    # in  <- pd.DataFrame monthly
    # out -> dict{Index : pd.DataFrame}, with stockcode indexed
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    #          *use NoneType to avoid manually settings on a certain factor
    def collect_stkindexed_sheets(self, use = "default", *, 
            bycol_stkid, 
            bycol_datetime,
            stockid_as = "StkID",
            datetime_as = "DateTime",
            rmrows = ["default"], 
            astype = None, 
            copy = True) -> dict:
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type(pd.DataFrame()):
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
        if bycol_stkid not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_stkid\\!")
        if bycol_datetime not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_datetime\\!")
        
        # Change the type of the DataFrame
        uses = []
        if copy == True:
            uses = use.copy()
        else:
            uses = use
        if astype is not None:
            uses = uses.astype(astype)
        uses[bycol_stkid] = uses[bycol_stkid].astype(int)
        uses[bycol_datetime] = uses[bycol_datetime].astype(str)
        
        # Change the column name to be matched
        StkID = stockid_as
        DateTime = datetime_as
        cl = list(uses.columns)
        id_s = list(uses.columns).index(bycol_stkid)
        id_d = list(uses.columns).index(bycol_datetime)
        cl[id_s] = StkID
        cl[id_d] = DateTime
        uses.columns = cl
        
        #######################################################################
        #
        # Try and test the rmrows's returned value
        if rmrows is not None:
            if type(self.__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
                raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")

        # Remove invalid rows
        kpvalids = []
        if rmrows is not None:
            valRows = []
            for i in range(len(uses)):
                tup = (uses[StkID].iloc[i])
                cri = self.__rm_invalid__(x = tup, funcs = rmrows)
                if cri == False:
                    valRows.append(i)
            kpvalids = uses.iloc[valRows,:].copy()
        else:
            kpvalids = uses # do not copy since nothing's been done
        
        # Find all stock indices
        uniqueids = list(set(kpvalids[StkID]))
        stkdicts = {}
        
        # Create dicts for all stocks (indexed)
        for i in range(len(uniqueids)):
            
            id = uniqueids[i]
            poses = pos(list(kpvalids[StkID]), id)
            
            # Add each row into the pandas.DataFrame
            pds = []
            if len(poses) == 1:
                pds = kpvalids.iloc[(poses[0]):(poses[0]+1),:].copy()
            else:
                pds = kpvalids.iloc[poses,:].copy()
            
            # Add new elements into the dict
            stkdicts[id] = pds
                
        return stkdicts
    
    # Collect Time-Indexed Return Sheets
    # in  <- pd.DataFrame monthly
    # out -> dict{Index : pd.DataFrame}, with datetime indexed
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    #          *use NoneType to avoid manually settings on a certain factor
    def collect_timeindexed_sheets(self, use = "default", *, 
            bycol_datetime,
            bycol_stkid,
            stockid_as = "StkID",
            datetime_as = "DateTime",
            datetime_type = int,
            rmrows = ["default"], 
            astype = None, 
            copy = True) -> dict:
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type(pd.DataFrame()):
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
        if bycol_datetime not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_datetime\\!")
        if bycol_stkid not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_stkid\\!")
        
        # Change the type of the DataFrame
        uses = []
        if copy == True:
            uses = use.copy()
        else:
            uses = use
        if astype is not None:
            uses = uses.astype(astype)
        uses[bycol_datetime] = uses[bycol_datetime].astype(str)
        uses[bycol_stkid] = uses[bycol_stkid].astype(int)
        
        # Change the column name to be matched
        StkID = stockid_as
        DateTime = datetime_as
        cl = list(uses.columns)
        id_s = list(uses.columns).index(bycol_stkid)
        id_d = list(uses.columns).index(bycol_datetime)
        cl[id_s] = StkID
        cl[id_d] = DateTime
        uses.columns = cl
        
        #######################################################################
        #
        # Try and test the rmrows's returned value
        if rmrows is not None:
            if type(self.__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
                raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")

        # Remove invalid rows
        kpvalids = []
        if rmrows is not None:
            valRows = []
            for i in range(len(uses)):
                tup = (uses[DateTime].iloc[i])
                cri = self.__rm_invalid__(x = tup, funcs = rmrows)
                if cri == False:
                    valRows.append(i)
            kpvalids = uses.iloc[valRows,:].copy()
        else:
            kpvalids = uses # do not copy since nothing's been done
        
        # Find all datetimes
        uniquedts = list(set(kpvalids[DateTime]))
        uniquedts = list(np.array(uniquedts).astype(datetime_type))
        stkdicts = {}
        
        # Create dicts for all stocks (indexed)
        for i in range(len(uniquedts)):
            
            dt = uniquedts[i]
            poses = pos(list(kpvalids[DateTime].astype(datetime_type)), dt)
            
            # Add each row into the pandas.DataFrame
            pds = []
            if len(poses) == 1:
                pds = kpvalids.iloc[(poses[0]):(poses[0]+1),:].copy()
            else:
                pds = kpvalids.iloc[poses,:].copy()
           
            # Add new elements into the dict
            stkdicts[dt] = pds
                
        return stkdicts
    
    # Collect Time-Stock-Indexed Data Sheets
    # in  <- pd.DataFrame monthly
    # out -> dict{Index : dict{Index : pd.DataFrame}}, with datetime, stock indexed
    #                                                       ^ outside ^ inside  
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    #          *use NoneType to avoid manually settings on a certain factor
    def collect_timestkindexed_sheets(self, use = "default", *,
            bycol_datetime,
            bycol_stkid,
            stockid_as = "StkID",
            datetime_as = "DateTime",
            datetime_type = int,
            rmrows = ["default"], 
            astype = None, 
            copy = True) -> dict:
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type(pd.DataFrame()):
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
        if bycol_datetime not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_datetime\\!")
        if bycol_stkid not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_stkid\\!")
        
        # Change the type of the DataFrame
        uses = []
        if copy == True:
            uses = use.copy()
        else:
            uses = use
        if astype is not None:
            uses = uses.astype(astype)
        uses[bycol_datetime] = uses[bycol_datetime].astype(str)
        uses[bycol_stkid] = uses[bycol_stkid].astype(int)
        
        # Change the column name to be matched
        StkID = stockid_as
        DateTime = datetime_as
        cl = list(uses.columns)
        id_s = list(uses.columns).index(bycol_stkid)
        id_d = list(uses.columns).index(bycol_datetime)
        cl[id_s] = StkID
        cl[id_d] = DateTime
        uses.columns = cl
        
        #######################################################################
        #
        # Try and test the rmrows's returned value
        if rmrows is not None:
            if type(self.__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
                raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")

        # Remove invalid rows
        kpvalids = []
        if rmrows is not None:
            valRows = []
            for i in range(len(uses)):
                tup = (uses[DateTime].iloc[i])
                cri = self.__rm_invalid__(x = tup, funcs = rmrows)
                if cri == False:
                    valRows.append(i)
            kpvalids = uses.iloc[valRows,:].copy()
        else:
            kpvalids = uses # do not copy since nothing's been done
        
        # Find all datetimes
        uniquedts = list(set(kpvalids[DateTime]))
        uniquedts = list(np.array(uniquedts).astype(datetime_type))
        stkdicts = {}
        # Create dicts for all stocks (indexed)
        for i in range(len(uniquedts)):
            
            dt = uniquedts[i]
            poses = pos(list(kpvalids[DateTime].astype(datetime_type)), dt)
            
            # Add each row into the pandas.DataFrame
            pds = []
            if len(poses) == 1:
                pds = kpvalids.iloc[(poses[0]):(poses[0]+1),:].copy()
            else:
                pds = kpvalids.iloc[poses,:].copy()
            # Add new elements into the dict
            stkdicts[dt] = pds
            
        # The second indexed within each time's page
        tstkdicts = {}
        # Create dicts for all stocks (double indexed)
        for k in stkdicts.keys():
            
            # Temp stkpages
            tmppage = {}
            
            # Create unique ids for stkids
            uniquedts = list(set(stkdicts[k][StkID]))
            
            for i in range(len(uniquedts)):
                
                dt = uniquedts[i]
                poses = pos(list(stkdicts[k][StkID]), dt)
                
                # Add each row into the pandas.DataFrame
                pds = []
                if len(poses) == 1:
                    pds = stkdicts[k].iloc[(poses[0]):(poses[0]+1),:].copy()
                else:
                    pds = stkdicts[k].iloc[poses,:].copy()
               
                # Add new elements into the dict
                tmppage[dt] = pds
            
            # Append the whole page to the bigger dict
            tstkdicts[k] = tmppage
                
        return tstkdicts
    
    # Collect Time-Indexed Weighted Data Sheets
    # in  <- dict{Index : dict{Index : pd.DataFrame}}, with datetime indexed
    # out -> (dict, dict{Index : pd.DataFrame}), with datetime indexed, with a new column "Weights" generated for each page 
    #         ^ this containing the computed, weighted value, which is a dict{Index: numerical}
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    #          *use NoneType to avoid manually settings on a certain factor
    def collect_weighton(self, use = "default", *, 
            bycol_toweighton,
            bycol_tovalueon,
            toweighton_as = "ToWeightOn",
            tovalueon_as = "ToValueOn",
            tovalue_naas = 0,
            rmrows = ["default"], 
            astype = None, 
            copy = True) -> dict:
        
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
            if bycol_toweighton not in use[k].columns:
                raise ErrorCode("Invalid column name in the var \\bycol_toweighton\\!")
        for k in use.keys():
            if bycol_tovalueon not in use[k].columns:
                raise ErrorCode("Invalid column name in the var \\bycol_tovalueon\\!")
                
        
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
            uses[k][bycol_toweighton] = uses[k][bycol_toweighton].astype(float)
            uses[k][bycol_tovalueon] = uses[k][bycol_tovalueon].astype(float)
        
        # Change the column name to be matched
        ToWeightOn = toweighton_as
        ToValueOn = tovalueon_as
        Weights = "Weights"
        for k in uses.keys():
            cl = list(uses[k].columns)
            id_t = list(uses[k].columns).index(bycol_toweighton)
            id_v = list(uses[k].columns).index(bycol_tovalueon)
            cl[id_t] = ToWeightOn
            cl[id_v] = ToValueOn
            uses[k].columns = cl
        
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
                for i in range(len(uses)):
                    tup = (uses[k][ToWeightOn].iloc[i], uses[k][ToValueOn].iloc[i])
                    cri = self.__rm_invalid__(x = tup, funcs = rmrows)
                    if cri == False:
                        valRows.append(i)
                kpvalids[k] = uses[k].iloc[valRows,:].copy()
        else:
            kpvalids = uses # do not copy since nothing's been done
            
        # Give the uses back
        uses = kpvalids
        
        # Values created
        vdict = {}
        
        # For each page, create a new row containing the weight
        for k in uses.keys():
            
            # Get the page to be used
            page = uses[k]
            
            # Create a new row containing the weight
            twon_ = np.array(page[ToWeightOn])
            tvon_ = np.array(page[ToValueOn])
            
            # NaN processing
            tvon_ = np.array(pd.Series(tvon_).fillna(value = tovalue_naas))
            
            # Compute the weight of each row
            w_total = np.sum(twon_)
            weights_ = np.multiply(twon_, 1.0/w_total)
            values_ = np.sum(np.multiply(weights_, tvon_))
            
            # Append a new row and a new element
            uses[k][Weights] = weights_
            vdict[k] = values_
            
        return vdict, uses
    
    # Group-by Factors
    # in  <- dict{Index : pd.DataFrame}, with datetime indexed
    # out -> (dict, dict{Index : pd.DataFrame}), with
    #        i: a series of new rows named "Grouped_..." generated
    #       ii: a new row named "JointGroup" generated
    #      iii: a new row named "InGroupWeight" generated
    #     *the first dict is somehow an internal dict, which is for debugging use
    # [params] use:    dict{Index : pd.DataFrame}, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    #                  specially, None meaning skip that process
    # [params] bycol_factors        : list of strs, specify the factors to be grouped by
    # [params] bycol_factor_spliton : list of strs, specify reference columns that the threshold to be computed
    # [params] bycol_factor_spchosen: list of list of values, the chosen values to be included in the spliton
    # [params] bycol_factor_nameas  : list of list strs, specify the new names of factors grouped, while for each, the length must be the same as that of the list "groups"
    #          *use NoneType to avoid manually settings on a certain factor
    # [params] groups: a list of integers, number of groups for each factor, 
    # [params] method: a str, two methods of computing the in-group weights
    #            "simple": using the simple average to compute the weight, which is 1/n
    #            "on"    : using a certain column to compute the weight, where the other param "on" should be specified
    # [params] on    : (optional) a str, indicating the "weight-on" column, and must be numerical
    # [params] allocs: (optional) a list of list of floaters, and the length must be the integer "groups", indicating the percentages (in decimals, but with 1% rounded) of each group, satisfying that the sum of members should be equal to 1
    # [params] fstyr : a dict, indexed by stock id, while the value shows the first year to be included (to compare)
    # [params] bycol_factor_fstyr: (optional) the column name of the column showing the current year, which will be used to compare to the first valid year
    # [params] bycol_factor_stkid: (optional) the column name of the column showing the stock id, which will help find the stock from the dict \fstyr
    def groupby_factors(self, use = "default", *,
           bycol_factors = [], 
           bycol_factor_spliton = [],
           bycol_factor_spchosen = [],
           bycol_factor_nameas = [],
           groups = [],
           method = ("simple", "on"),
           on = None,
           allocs = [],
           fstyr = {},
           bycol_factor_fstyr = None,
           bycol_factor_stkid = None,
           fstyrcmp_type = float,
           nonename_as = "NotClassified",
           rmrows = ["default"], 
           astype = None, 
           copy = True) -> (dict, dict):
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type({}):
            if use == "default":
                use = self._data
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
            
        # If use is not a dict, return an error
        if type(use) != type({}):
            raise ErrorCode("Invalid variable type in the var \\use\\! It should be a dict indexed by time")
            
        # Checking if the cols exist
        for k in use.keys():
            for i in range(len(bycol_factors)):
                if bycol_factors[i] not in use[k].columns:
                    raise ErrorCode("Invalid column name in the var \\bycol_factors\\'s \\"+ bycol_factors[i] + "\\ element!")
        if len(bycol_factor_spliton) > 0:
            for k in use.keys():
                for i in range(len(bycol_factor_spliton)):
                    if bycol_factor_spliton[i] is not None:
                        if bycol_factor_spliton[i] not in use[k].columns:
                            raise ErrorCode("Invalid column name in the var \\bycol_factor_spliton\\'s \\"+ bycol_factor_spliton[i] + "\\ element!")
        if len(bycol_factor_spliton) > 0:
            for i in range(len(bycol_factor_spliton)):
                if bycol_factor_spliton[i] is not None:
                    if (len(bycol_factor_spchosen) <= i) or (len(bycol_factor_spchosen[i]) == 0):
                        raise ErrorCode("Invalid split values chosen in the var \\bycol_factor_spchosen\\'s \\"+ str(i) + "\\'s element!")
        
        # Check if groups' length does not match to that of factor
        if len(groups) != len(bycol_factors):
            raise ErrorCode("Invalid parameter \\groups\\! It must be a list of integers speciying the number of groups to be grouped in each factor!")
        
        # If fstyr is not a dict
        if type(fstyr) != type({}):
            raise ErrorCode("Invalid parameter \\fstyr\\! It must be a stock code indexed dict!")
        
        # If fstyr is an empty dict, give it a none
        if len(fstyr) == 0:
            fstyr = None
        elif len(fstyr) > 0:
            for k in use.keys():
                if bycol_factor_fstyr is not None:
                    if bycol_factor_fstyr not in use[k].columns:
                        raise ErrorCode("Invalid column name in the var \\bycol_factor_fstyr\\!")
                else:
                    raise ErrorCode("Invalid column name in the var \\bycol_factor_fstyr\\!")
            for k in use.keys():
                if bycol_factor_stkid is not None:
                    if bycol_factor_stkid not in use[k].columns:
                        raise ErrorCode("Invalid column name in the var \\bycol_factor_stkid\\!")
                else:
                    raise ErrorCode("Invalid column name in the var \\bycol_factor_stkid\\!")
                        
        # Change the type of the DataFrame
        uses = []
        if copy == True:
            uses = use.copy()
        else:
            uses = use
        if astype is not None:
            for k in uses.keys():
                uses[k] = uses[k].astype(astype)
        # Do not change the type to individual columns
        
        # Create new names for factors in different groups
        # \factorname + "_" + (\nameas or "group" + \n)
        # Factor -> Group
        NewNames = []
        if len(bycol_factor_nameas) != 0:
            if len(bycol_factor_nameas) != len(groups):
                raise ErrorCode("Manually assigned names to each group of each factor must be allocated into a \\" + str(len(groups)) + "\\-length list !")
        else:
            bycol_factor_nameas = []
            for i in range(len(bycol_factors)):
                bycol_factor_nameas.append([])
        # continue
        for i in range(len(bycol_factors)):
            namesfact = []
            for j in range(groups[i]):
                namestmp = ""
                
                # Not specified the name
                if (bycol_factor_nameas[i] == []) or (bycol_factor_nameas[i] == [None]):
                    namestmp = bycol_factors[i] + "_group_" + str(j+1)
                # With specified names
                else:
                    namestmp = bycol_factors[i] + "_" + bycol_factor_nameas[i][j]
                    
                namesfact.append(namestmp)
            NewNames.append(namesfact)
        
        # Non-classfied groupname
        NonNames = nonename_as
        
        # Pre-process the allocs
        if len(allocs) == 0:
            for i in range(len(bycol_factors)):
                allocs.append([])
        elif len(allocs) != len(bycol_factors):
            raise ErrorCode("Invalid input allocs in the var \\allocs\\! It should have the same length with factor numbers, or empty!")
        for i in range(len(allocs)):
            # Empty allocs
            if allocs[i] is None or len(allocs[i]) == 0:
                for j in range(groups[j]):
                    allocs[i].append(1.0/groups[i])
            # Invalid specification
            elif len(allocs[i]) != groups[i]:
                raise ErrorCode("Invalid input allocs in the var \\allocs\\! Each list of specified percentages should be with the same length as the nth's parameter \\groups\\!")
            # Non-valid sums
            elif np.sum(allocs[i]) != 1.0:
                adj = np.sum(allocs[i]) / 1.0
                for j in range(len(allocs[i])):
                    allocs[i][j] = allocs[i][j] / adj
                
        #######################################################################
        #
        # Try and test the rmrows's returned value
        if rmrows is not None:
            if type(super().__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
                raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")

        # Remove invalid rows
        kpvalids = {}
        if rmrows is not None:
            for k in uses.keys():
                valRows = []
                for i in range(len(uses[k])):
                    tup = []
                    for j in range(len(bycol_factors)):
                        tup.append(uses[k][bycol_factors[j]].iloc[i])
                    tup = tuple(tup)
                    cri = super().__rm_invalid__(x = tup, funcs = rmrows)
                    if cri == False:
                        valRows.append(i)
                kpvalids[k] = uses[k].iloc[valRows,:].copy()
        else:
            kpvalids = uses # do not copy since nothing's been done
            
        # Rename back
        uses = kpvalids
        
        # Try and see whether the method is valid
        if type(method) == type(()):
            raise ErrorCode("Invalid selected method in the var \\method\\! You must select any one of the default tuple as your \\method\\ parameter, rather than using the default tuple directly!")
        elif type(method) != type(""):
            raise ErrorCode("Invalid selected method in the var \\method\\! You must select any one of the default tuple as your \\method\\ parameter, rather than using any other invalid input!")
        elif method not in ["simple", "on"]:
            raise ErrorCode("Invalid selected method in the var \\method\\! You must select any one of the default tuple as your \\method\\ parameter, rather than using any other invalid string!")
        
        # If method is on, then try to see whether the column "on" exists
        if method == "on":
            for k in uses.keys():
                if on not in uses[k].columns:
                    raise ErrorCode("Invalid selected weight-on parameter in the var \\on\\! The column on should exist!")
        
        # Compute the threshold for each page, each group, and each factor
        page_factor_thres = {} # dict[dict[list[tuple()]]]
        #                        ^ index: datetime
        #                             ^ index: bycol_factors
        #                                  ^ index: \which_group(no.)
        #                                       ^ tuple(lowend, hiend)
        # Each page
        for k in uses.keys():
            # Factor tmps
            ftmps = {}
            # Each factor
            for f in range(len(bycol_factors)):
                # Lowend-Hiend tmps
                ind = [] # list of tuples
                
                # If I have to sort some values ...
                if len(bycol_factor_spliton) > 0 and (bycol_factor_spliton[f] is not None):
                    # a initial pd.Series
                    baseptr = uses[k][bycol_factors[f]]
                    splitptr = uses[k][bycol_factor_spliton[f]]
                    splitptr = list(splitptr.isin(bycol_factor_spchosen[f]))
                    posptr = pos(splitptr, True)
                    # a splited pd.Series
                    thisptr = baseptr.iloc[posptr]
                    # a 1%-precision percentile
                    # length is 101, for the first representing the 0%
                    pct = []
                    for i in range(0,101,1):
                        pct.append(np.percentile(thisptr, i))
                    # for each percentile [)
                    findex = 0
                    tindex = 0
                    for i in range(len(allocs[f])):
                        rnds = int(np.round(allocs[f][i] * 100))
                        findex = int(tindex)
                        tindex += int(rnds)
                        ind.append((pct[int(findex)], pct[int(tindex)]))
                
                # Directly grouping in an increasing sequence
                else:
                    # a pd.Series
                    thisptr = uses[k][bycol_factors[f]]
                    # a 1%-precision percentile
                    # length is 101, for the first representing the 0%
                    pct = []
                    for i in range(0,101,1):
                        pct.append(np.percentile(thisptr, i))
                    # for each percentile [)
                    findex = 0
                    tindex = 0
                    for i in range(len(allocs[f])):
                        rnds = np.round(allocs[f][i] * 100)
                        findex = int(tindex)
                        tindex += int(rnds)
                        ind.append((pct[int(findex)], pct[int(tindex)]))
        
                # Append this factor
                ftmps[bycol_factors[f]] = ind
            
            # Append this page
            page_factor_thres[k] = ftmps
    
        # Add group signitures to each group 
        # Page -> Factor -> A column generated
        # Each page
        for k in uses.keys():
            # This pointer
            thisptr = uses[k]  # Do not copy since nothing's done
            # Each factor
            for f in range(len(bycol_factors)):
                # Grouping signitures
                grpcol = list(range(len(thisptr)))   # list of strings
                # I tried to avoid re-allocation to speed up this loop
                # For each row
                for i in range(len(thisptr)):
                    # In which zone, returning the index of the group
                    iwz = inwhich_zone(thisptr[bycol_factors[f]].iloc[i], page_factor_thres[k][bycol_factors[f]])
                    
                    if iwz == -1:
                        # Meeting the max group
                        iwz = len(page_factor_thres[k][bycol_factors[f]]) - 1
                    
                    # If None,
                    # or the current inclusion time is required
                    if fstyr is None:
                        # Normally assign a group
                        grpname = NewNames[f][iwz]
                        grpcol[i] = grpname
                    else:
                        this_stkid = thisptr[bycol_factor_stkid].iloc[i]
                        if fstyrcmp_type is not None:
                            if fstyrcmp_type(thisptr[bycol_factor_fstyr].iloc[i]) >= fstyrcmp_type(fstyr[this_stkid]):
                                # Normally assign a group
                                grpname = NewNames[f][iwz]
                                grpcol[i] = grpname
                            else:
                                # Assign a NoneName
                                grpcol[i] = NonNames
                        else:
                            if thisptr[bycol_factor_fstyr].iloc[i] >= fstyr[this_stkid]:
                                # Normally assign a group
                                grpname = NewNames[f][iwz]
                                grpcol[i] = grpname
                            else:
                                # Assign a NoneName
                                grpcol[i] = NonNames
                
                # Append a new column
                uses[k]["Grouped_" + bycol_factors[f]] = grpcol
        
        # Create a joint-group
        # Each page
        for k in uses.keys():
            # This pointer
            thisptr = uses[k]  # Do not copy since nothing's done
            # New column name
            mcname = "JointGroup"
            # Grouping signitures
            grpcol = list(range(len(thisptr)))   # list of strings
            # I tried to avoid re-allocation to speed up this loop
            # For each grouped column
            for i in range(len(thisptr)):
                grpcol[i] = ""
                for f in range(len(bycol_factors)):
                    grpcol[i] += "_" + str(thisptr["Grouped_" + bycol_factors[f]].iloc[i])
            # Assign a new column
            uses[k][mcname] = grpcol
            
        # Compute the weight for the joint-group
        # Each page
        for k in uses.keys():
            # This pointer
            thisptr = uses[k]  # Do not copy since nothing's done
            # New column name
            wtname = "InGroupWeight"
            # Weight list
            weightcol = list(range(len(thisptr)))   # list of strings
            # I tried to avoid re-allocation to speed up this loop
            # Weight dict, indexed by the "JointGroup"
            weightdict = {}
            
            # If method == "simple", collect the number as n, and weight 1/n
            if method == "simple":
                
                # Fill the dict
                for i in range(len(thisptr)):
                    if thisptr["JointGroup"].iloc[i] not in weightdict.keys():
                        weightdict[thisptr["JointGroup"].iloc[i]] = 1
                    else:
                        weightdict[thisptr["JointGroup"].iloc[i]] += 1
                # Another for loop to compute the weight
                for i in range(len(thisptr)):
                    weightcol[i] = 1.0 / weightdict[thisptr["JointGroup"].iloc[i]]
                        
            # If method == "on", cumulatively add the value to the dict,
            # and finally, use the individual value / total value as the weight
            elif method == "on":
                
                # Fill the dict
                for i in range(len(thisptr)):
                    if thisptr["JointGroup"].iloc[i] not in weightdict.keys():
                        weightdict[thisptr["JointGroup"].iloc[i]] = thisptr[on].iloc[i]
                    else:
                        weightdict[thisptr["JointGroup"].iloc[i]] += thisptr[on].iloc[i]
                # Another for loop to compute the weight
                for i in range(len(thisptr)):
                    weightcol[i] = thisptr[on].iloc[i] / weightdict[thisptr["JointGroup"].iloc[i]]
                    
            # Append the column
            uses[k][wtname] = weightcol
            
        return page_factor_thres, uses
    
    # Collect monthly returns in groups
    # in  <- dict{Index : pd.DataFrame}, with datetime indexed
    # out -> dict{Index : pd.DataFrame} with GroupName indexed, with columns of datetimes and "Returns" generated
    # [params] use:    dict{Index : pd.DataFrame}, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    #                  specially, None meaning skip that process
    # [params] tmref : pd.DataFrame, with two columns generated from the function \timeseries
    # [params] retref: dict{Index : pd.DataFrame}, with stockcode indexed
    #         *No column name will be changed and they will directly generate new data frames
    # [params] groupnames: list, containing all group names to be included
    # [params] reweights: bool, if True, weights will be recomputed if missing values encountering
    def collect_monthly_returns(self, use = "default", *,
            tmref:pd.DataFrame,
            retref:dict[pd.DataFrame],
            bycol_use_stkid,
            bycol_use_group,
            bycol_use_weight,
            bycol_retref_datetime,
            bycol_retref_return,
            returnas = "Returns",
            groupnames = [],
            reweights = False,
            rmrows = ["default"], 
            astype = None, 
            copy = True) -> dict:
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type({}):
            if use == "default":
                use = self._data
            else:
                raise ErrorCode("Invalid input data in the var \\use\\!")
        
        # If tmref is not a dataframe
        if type(tmref) != type(pd.DataFrame()):
            raise ErrorCode("Invalid input data in the var \\tmref\\!")
            
        # If tmref is not a dict
        if type(retref) != type({}):
            raise ErrorCode("Invalid input data in the var \\retref\\!")
                
        # If uses the default rmrows
        if type(rmrows) == type([]):
            if rmrows[0] == "default":
                rmrows = ["default"]
        elif rmrows is not None:
            raise ErrorCode("Invalid input criterion functions in the var \\rmrows\\! While this can be a None in this instance!")
        
        # If use it None, return None
        if use is None:
            raise ErrorCode("Invalid input data in the var \\use\\!")
            
        # If groupnames is not a list or with length 0
        if type(groupnames) != type([]):
            raise ErrorCode("Invalid input type in the var \\groupnames\\!")
        if len(groupnames) == 0:
            raise ErrorCode("Invalid input length in the var \\groupnames\\! It must contain at least one group!")
        
        # Checking if the cols exist
        for k in use.keys():
            if bycol_use_group not in use[k].columns:
                raise ErrorCode("Invalid column name in the var \\bycol_use_group\\!")
        for k in use.keys():
            if bycol_use_weight not in use[k].columns:
                raise ErrorCode("Invalid column name in the var \\bycol_use_weight\\!")
        for k in use.keys():
            if bycol_use_stkid not in use[k].columns:
                raise ErrorCode("Invalid column name in the var \\bycol_use_stkid\\!")
        # continue
        for k in retref.keys():
            if bycol_retref_datetime not in retref[k].columns:
                raise ErrorCode("Invalid column name in the var \\bycol_retref_datetime\\!")
        for k in retref.keys():
            if bycol_retref_return not in retref[k].columns:
                raise ErrorCode("Invalid column name in the var \\bycol_retref_return\\!")
        
        # Change the type of the DataFrame
        uses = []
        retrefs = []
        if copy == True:
            uses = use.copy()
            retrefs = retref.copy()
        else:
            uses = use
            retrefs = retref
        if astype is not None:
            for k in uses.keys():
                uses[k] = uses[k].astype(astype)
            for k in retrefs.keys():
                retrefs[k] = retrefs[k].astype(astype)
        for k in uses.keys():
            uses[k][bycol_use_group] = uses[k][bycol_use_group].astype(str)
        for k in retrefs.keys():
            retrefs[k][bycol_retref_return] = retrefs[k][bycol_retref_return].astype(float)
        # Column names will not be changed specifically
        
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
                for i in range(len(uses)):
                    tup = (uses[k][bycol_use_group].iloc[i], uses[k][bycol_use_weight].iloc[i])
                    cri = self.__rm_invalid__(x = tup, funcs = rmrows)
                    if cri == False:
                        valRows.append(i)
                kpvalids[k] = uses[k].iloc[valRows,:].copy()
        else:
            kpvalids = uses # do not copy since nothing's been done
            
        # Give the uses back
        uses = kpvalids
        
        # Create the returned dict
        # dict      -> pd.DataFrame
        # ^ groupname
        #              ^
        #              Year  Year-Month  Returns
        #              1996  1996-01     0.0314
        #              ...   ...         ...
        retdict = {}
        for g in groupnames:
            retdict[g] = tmref.copy()
            # Generate the new column "Returns"
            retdict[g][returnas] = 0.0
        
        # Transform the retrefs' time into the str format
        # retref is stock indexed
        for k in retrefs.keys():
            times_ = list(retrefs[k][bycol_retref_datetime])
            for t in range(len(times_)):
                times_[t] = str(times_[t])[0:7]
            retrefs[k][bycol_retref_datetime] = times_
            
        # Iterate the tmref and create returns based on groups and returns
        for i in range(len(tmref)):
            
            # Substract the year to refer to and the year-month to refer to
            fy = int(tmref.iloc[i, 0])      # int
            fym = str(tmref.iloc[i, 1])     # str
            
            # Get the page of group to be used
            page = uses[fy]
            
            # For each group
            for g in groupnames:
                
                # Which rows are in the group
                poses = pos(list(page[bycol_use_group]), g)
                
                # The vector of weights and stkids
                weights_v = list(page[bycol_use_weight].iloc[poses])
                stkids_v = list(page[bycol_use_stkid].iloc[poses])
                
                # The vector of returns
                returns_v = stkids_v.copy()
                for ids in range(len(stkids_v)):
                    times_ = list(retrefs[stkids_v[ids]][bycol_retref_datetime])
                    tmposes = pos(times_, fym)
                    rttmp = np.nan  # What if the stock is no longer included
                    if len(tmposes) == 1:
                        # Included
                        rttmp = retrefs[stkids_v[ids]][bycol_retref_return].iloc[tmposes[0]]
                    if np.isnan(rttmp) == False:
                        returns_v[ids] = rttmp
                    else:
                        returns_v[ids] = 0.0 # return as 0
                        weights_v[ids] = 0.0 # weight as 0
                
                # Reevaluate the weights (with nans droped)
                if reweights == True:
                    wsum = np.sum(np.array(weights_v))
                    weights_v = np.multiply(np.array(weights_v), 1.0 / wsum)
                
                # Compute the weighted return
                wret = np.sum(np.multiply(np.array(weights_v), 
                                      np.array(returns_v)))
                
                retdict[g][returnas].iloc[i] = wret
        
        return retdict
    
    # Collect firm numbers in groups
    # in  <- dict{Index : pd.DataFrame}, with datetime indexed
    # out -> dict{Index : pd.DataFrame} with GroupName indexed, with columns of datetimes and "Numbers" generated
    # [params] use:    dict{Index : pd.DataFrame}, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    #                  specially, None meaning skip that process
    # [params] bycol_use_group: the column name of the joint group
    def collect_annually_firmnums(self, use = "default", *,
            bycol_use_group,
            firmsnumas = "Numbers",
            groupnames = [],
            rmrows = ["default"], 
            astype = None, 
            copy = True) -> dict:
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type({}):
            if use == "default":
                use = self._data
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
            
        # If groupnames is not a list or with length 0
        if type(groupnames) != type([]):
            raise ErrorCode("Invalid input type in the var \\groupnames\\!")
        if len(groupnames) == 0:
            raise ErrorCode("Invalid input length in the var \\groupnames\\! It must contain at least one group!")
        
        # Checking if the cols exist
        for k in use.keys():
            if bycol_use_group not in use[k].columns:
                raise ErrorCode("Invalid column name in the var \\bycol_use_group\\!")

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
            uses[k][bycol_use_group] = uses[k][bycol_use_group].astype(str)
        # Column names will not be changed specifically
        
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
                for i in range(len(uses)):
                    tup = (uses[k][bycol_use_group].iloc[i])
                    cri = self.__rm_invalid__(x = tup, funcs = rmrows)
                    if cri == False:
                        valRows.append(i)
                kpvalids[k] = uses[k].iloc[valRows,:].copy()
        else:
            kpvalids = uses # do not copy since nothing's been done
            
        # Give the uses back
        uses = kpvalids
        
        # Create the returned dict
        # dict      -> pd.DataFrame
        # ^ groupname
        #              ^
        #              DateTime     Returns
        #              1996         0.0314
        #              ...          ...
        retdict = {}
        for g in groupnames:
            # Generate the new page as g
            # Generate the new column "Numbers"
            retdict[g] = pd.DataFrame({"DateTime":list(uses.keys()), firmsnumas:0})
            
        # Groupname set
        groupnames_set = set(groupnames)
            
        # DateTime, keys
        dttime = list(uses.keys())
        
        # Iterate the uses and try to collect the number of firms of each group
        for i in range(len(dttime)):
            
            # Try to get the current datetime
            k = dttime[i]
            
            # Get the page of group to be used
            page = uses[k]
            
            # Set up the dict
            dc = {}
            for g in groupnames:
                dc[g] = int(0)
            
            # Iterate the page
            # Get the group and increase the number
            for il in range(len(page)):
                if page[bycol_use_group].iloc[il] in groupnames_set:
                    dc[page[bycol_use_group].iloc[il]] += 1
                
            # For each group and time,
            # Fill the retdict
            for g in groupnames:
                retdict[g][firmsnumas].iloc[i] = dc[g]
        
        return retdict
    
    # End of Class
    
# SIZE/SMB factor
class FactorSMB(__FactorBase__):
    
    ###########################################################################
    # API Functions
    #
    
    # Constructor
    def __init__(self, data = None, copy = True) -> None:
        
        super().__init__(data = data, copy = copy)          
        return None
            
    # Collect market values
    # in  <- pd.DataFrame monthly
    # out -> pd.DataFrame monthly, with a now columns named "MktValue" generated
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    def collect_market_values(self, use = "default", *,
            bycol_price, 
            bycol_shares,
            rmrows = ["default"], 
            rmprices = [],
            absprice = True,
            astype = None, 
            copy = True) -> pd.DataFrame:
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type(pd.DataFrame()):
            if use == "default":
                use = super().__rm_invalid__
            else:
                raise ErrorCode("Invalid input data in the var \\use\\!")
                
        # If uses the default rmrows
        if type(rmrows) == type([]):
            if rmrows[0] == "default":
                rmrows = ["default"]
        else:
            raise ErrorCode("Invalid input criterion functions in the var \\rmrows\\!")
        
        # If use it None, return None
        if use is None:
            raise ErrorCode("Invalid input data in the var \\use\\!")
        
        # Checking if the cols exist
        if bycol_price not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_price\\!")
        if bycol_shares not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_shares\\!")
        
        # Change the type of the DataFrame
        uses = []
        if copy == True:
            uses = use.copy()
        else:
            uses = use
        if astype is not None:
            uses = uses.astype(astype)
        uses[bycol_price] = uses[bycol_price].astype(float)
        uses[bycol_shares] = uses[bycol_shares].astype(float)
        
        # Change the column name to be matched
        MktPrice = "MktPrice"
        MktShares = "MktShares"
        MktValue = "MktValue"
        cl = list(uses.columns)
        id_p = list(uses.columns).index(bycol_price)
        id_s = list(uses.columns).index(bycol_shares)
        cl[id_p] = MktPrice
        cl[id_s] = MktShares
        uses.columns = cl
        
        #######################################################################
        #
        # Try and test the rmrows's returned value
        if type(super().__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
            raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")

        # Remove invalid rows
        valRows = []
        for i in range(len(uses)):
            tup = (uses[MktPrice].iloc[i], uses[MktShares].iloc[i])
            prc = uses[MktPrice].iloc[i]
            cri = super().__rm_invalid__(x = tup, funcs = rmrows)
            if prc in rmprices:
                cri = True
            if cri == False:
                valRows.append(i)
        kpvalids = uses.iloc[valRows,:].copy()
        
        # Collect the market value as a new column
        mktvals = np.multiply(np.array(kpvalids[MktPrice]),
                              np.array(kpvalids[MktShares]))
        if absprice == True:
            mktvals = np.abs(mktvals)
        kpvalids[MktValue] = mktvals
        
        return kpvalids
    
    # End of Class
    
# BM/ME HML factor
class FactorHML(__FactorBase__):
    
    ###########################################################################
    # API Functions
    #
    
    # Constructor
    def __init__(self, data = None, copy = True) -> None:
        
        super().__init__(data = data, copy = copy)          
        return None
    
    # Collect book values
    # in  <- pd.DataFrame annually
    # out -> pd.DataFrame annually, with a now columns named "BokValue" generated
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    def collect_book_values(self, use = "default", *,
           bycol_normequity, 
           bycol_defferedtax,
           bycol_prefferedstock,
           rmrows = ["default"], 
           astype = None, 
           copy = True) -> pd.DataFrame:
       
       #######################################################################
       #
       # If uses the default use
       if type(use) != type(pd.DataFrame()):
           if use == "default":
               use = super()._data
           else:
               raise ErrorCode("Invalid input data in the var \\use\\!")
               
       # If uses the default rmrows
       if type(rmrows) == type([]):
           if rmrows[0] == "default":
               rmrows = ["default"]
       else:
           raise ErrorCode("Invalid input criterion functions in the var \\rmrows\\!")
        
       # If use it None, return None
       if use is None:
           raise ErrorCode("Invalid input data in the var \\use\\!")
       
       # Checking if the cols exist
       if bycol_normequity not in use.columns:
           raise ErrorCode("Invalid column name in the var \\bycol_normequity\\!")
       if bycol_defferedtax not in use.columns:
           raise ErrorCode("Invalid column name in the var \\bycol_defferedtax\\!")
       if bycol_prefferedstock not in use.columns:
           raise ErrorCode("Invalid column name in the var \\bycol_prefferedstock\\!")
        
       # Change the type of the DataFrame
       uses = []
       if copy == True:
           uses = use.copy()
       else:
           uses = use
       if astype is not None:
           uses = uses.astype(astype)
       uses[bycol_normequity] = uses[bycol_normequity].astype(float)
       uses[bycol_defferedtax] = uses[bycol_defferedtax].astype(float)
       uses[bycol_prefferedstock] = uses[bycol_prefferedstock].astype(float)
       
       # Change the column name to be matched
       NormEquity = "NormEquity"
       DefTax = "DefTax"
       PrefStk = "PrefStk"
       BokValue = "BokValue"
       cl = list(uses.columns)
       id_n = list(uses.columns).index(bycol_normequity)
       id_d = list(uses.columns).index(bycol_defferedtax)
       id_p = list(uses.columns).index(bycol_prefferedstock)
       cl[id_n] = NormEquity
       cl[id_d] = DefTax
       cl[id_p] = PrefStk
       uses.columns = cl
       
       #######################################################################
       #
       # Try and test the rmrows's returned value
       if type(super().__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
           raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")
       
       # Remove invalid rows
       valRows = []
       for i in range(len(uses)):
           tup = (uses[NormEquity].iloc[i], 
                  uses[DefTax].iloc[i],
                  uses[PrefStk].iloc[i])
           cri = super().__rm_invalid__(x = tup, funcs = rmrows)
           if cri == False:
               valRows.append(i)
       kpvalids = uses.iloc[valRows,:].copy()
       
       # Collect the book value as a new column
       eqptax = np.add(np.array(kpvalids[NormEquity]),
                             np.array(kpvalids[DefTax]))
       eqptaxmpref = np.subtract(np.array(eqptax),
                             np.array(kpvalids[PrefStk]))
       kpvalids[BokValue] = eqptaxmpref
       
       return kpvalids
    
    # Match SIZE to BM dataframe (to refresh portfolios in Junes)
    # in  <- pd.DataFrame annually
    # out -> a dict{dict{Time-Stk Indexed data}}
    #        a pd.DataFrame annually, with
    #        i: a new row named "Matched_DateTime" generated (till, monthly)
    #       ii: a new row named "Matched_YearAs"   generated (year t)
    #      iii: a new row named "Matched_BokValue" generated (thousands)
    #       iv: a new row named "Matched_MktValue" generated (thousands)
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] sizedf: pd.DataFrame, the data frame containing the SIZE column
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    #          *use NoneType to avoid manually settings on a certain factor
    # [params] method: two methods of how to match the SIZE to BM are provided
    #     default: fisical year ending in t-1 / December, t-1
    #     average: (12) till Dec, but moving average
    #              (6)  till Jun, but moving average
    #              (.)  till ANY(given), but moving average
    #     * one of the two methods must be specified when passing an arg
    # [params] refmonth: the given reference month to be computed as the matched book value
    def match_size_to_bm(self, use = "default", sizedf = "args", *,
            bycol_use_stkid,
            bycol_use_datetime,
            bycol_use_fyear,
            bycol_use_fyearendmonth,
            bycol_use_bokvalue,
            bycol_use_otherskept = [],
            bycol_sizedf_stkid,
            bycol_sizedf_datetime,
            bycol_sizedf_mktvalue,
            bycol_sizedf_otherskept = [],
            method = ("default", "average"),
            refmonth = 12,
            delnonmatch = False,
            rmrows = ["default"], 
            astype = None, 
            copy = True) -> pd.DataFrame:
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type(pd.DataFrame()):
            if use == "default":
                use = super()._data
            else:
                raise ErrorCode("Invalid input data in the var \\use\\!")
        
        # If left the default sizedf
        if type(sizedf) != type(pd.DataFrame()):
            if type(sizedf) == type(""):
                raise ErrorCode("Invalid input data in the var \\sizedf\\! Do not use the default string as an arg!")
            else:
                raise ErrorCode("Invalid input data in the var \\sizedf\\! A pd.DataFrame must be passed in!")
                
        # If uses the default rmrows
        if type(rmrows) == type([]):
            if rmrows[0] == "default":
                rmrows = ["default"]
        elif rmrows is not None:
            raise ErrorCode("Invalid input criterion functions in the var \\rmrows\\!")
        
        # If use it None, return None
        if use is None:
            raise ErrorCode("Invalid input data in the var \\use\\!")
        # If sizedf it None, return None
        if sizedf is None:
            raise ErrorCode("Invalid input data in the var \\sizedf\\!")
       
        # Checking if the cols exist
        if bycol_use_stkid not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_use_stkid\\!")
        if bycol_use_datetime not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_use_datetime\\!")
        if bycol_use_fyear not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_use_fyear\\!")
        if bycol_use_fyearendmonth not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_use_fyearendmonth\\!")
        if bycol_use_bokvalue not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_use_bokvalue\\!")
        if type(bycol_use_otherskept) == type(pd.DataFrame()):
            bycol_use_otherskept = [bycol_use_otherskept]
        if type(bycol_use_otherskept) != type([]):
            raise ErrorCode("Invalid type in the var \\bycol_use_otherskept\\!")
        for o in bycol_use_otherskept:
            if o not in use.columns:
                raise ErrorCode("Invalid column name in the var \\bycol_use_otherskept\\!")
        # continue
        if bycol_sizedf_stkid not in sizedf.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_sizedf_stkid\\!")
        if bycol_sizedf_datetime not in sizedf.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_sizedf_stkid\\!")
        if bycol_sizedf_mktvalue not in sizedf.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_sizedf_mktvalue\\!")
        if type(bycol_sizedf_otherskept) == type(pd.DataFrame()):
            bycol_sizedf_otherskept = [bycol_sizedf_otherskept]
        if type(bycol_sizedf_otherskept) != type([]):
            raise ErrorCode("Invalid type in the var \\bycol_sizedf_otherskept\\!")
        for o in bycol_sizedf_otherskept:
            if o not in use.columns:
                raise ErrorCode("Invalid column name in the var \\bycol_sizedf_otherskept\\!")
        
        # Change the type of the DataFrame
        uses = []
        sizedfs = []
        if copy == True:
            uses = use.copy()
            sizedfs = sizedf.copy()
        else:
            uses = use
            sizedfs = sizedf
        if astype is not None:
            uses = uses.astype(astype)
            sizedfs = sizedfs.astype(astype)
        uses[bycol_use_stkid] = uses[bycol_use_stkid].astype(int)
        uses[bycol_use_datetime] = uses[bycol_use_datetime].astype(str)
        uses[bycol_use_fyear] = uses[bycol_use_fyear].astype(int)
        uses[bycol_use_fyearendmonth] = uses[bycol_use_fyearendmonth].astype(int)
        uses[bycol_use_bokvalue] = uses[bycol_use_bokvalue].astype(float)
        # continue
        sizedfs[bycol_sizedf_stkid] = sizedfs[bycol_sizedf_stkid].astype(int)
        sizedfs[bycol_sizedf_datetime] = sizedfs[bycol_sizedf_datetime].astype(str)
        sizedfs[bycol_sizedf_mktvalue] = sizedfs[bycol_sizedf_mktvalue].astype(float)
    
        # Change the column name to be matched
        StkID = "StkID"
        DateTime = "DateTime"
        FYear = "FYear"
        FYearEndMonth = "FYearEndMonth"
        BokValue = "BokValue"
        MktValue = "MktValue"
        Matched_DateTime = "Matched_DateTime"
        Matched_YearAs = "Matched_YearAs"
        Matched_BokValue = "Matched_BokValue"
        Matched_MktValue = "Matched_MktValue"
        uscl = list(uses.columns)
        id_id = list(uses.columns).index(bycol_use_stkid)
        id_dt = list(uses.columns).index(bycol_use_datetime)
        id_fy = list(uses.columns).index(bycol_use_fyear)
        id_fm = list(uses.columns).index(bycol_use_fyearendmonth)
        id_bk = list(uses.columns).index(bycol_use_bokvalue)
        uscl[id_id] = StkID
        uscl[id_dt] = DateTime
        uscl[id_fy] = FYear
        uscl[id_fm] = FYearEndMonth
        uscl[id_bk] = BokValue
        uses.columns = uscl
        # continue
        szcl = list(sizedfs.columns)
        id_id = list(sizedfs.columns).index(bycol_sizedf_stkid)
        id_dt = list(sizedfs.columns).index(bycol_sizedf_datetime)
        id_mk = list(sizedfs.columns).index(bycol_sizedf_mktvalue)
        szcl[id_id] = StkID
        szcl[id_dt] = DateTime
        szcl[id_mk] = MktValue
        sizedfs.columns = szcl
        
        #######################################################################
        #
        # Try and test the rmrows's returned value
        if rmrows is not None:
            if type(super().__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
                raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")
            
        # Try and see whether the method is valid
        if type(method) == type(()):
            raise ErrorCode("Invalid selected method in the var \\method\\! You must select any one of the default tuple as your \\method\\ parameter, rather than using the default tuple directly!")
        elif type(method) != type(""):
            raise ErrorCode("Invalid selected method in the var \\method\\! You must select any one of the default tuple as your \\method\\ parameter, rather than using any other invalid input!")
        elif method not in ["default", "average"]:
            raise ErrorCode("Invalid selected method in the var \\method\\! You must select any one of the default tuple as your \\method\\ parameter, rather than using any other invalid string!")
        
        # Remove invalid rows
        usevalids = []
        szvalids = []
        if rmrows is not None:
            valRows = []
            for i in range(len(uses)):
                tup = (uses[FYear].iloc[i], 
                       uses[FYearEndMonth].iloc[i],
                       uses[BokValue].iloc[i])
                cri = super().__rm_invalid__(x = tup, funcs = rmrows)
                if cri == False:
                    valRows.append(i)
            usevalids = uses.iloc[valRows,:].copy()
        else:
            usevalids = uses # Do not copy since nothing's changed
        # continue
        if rmrows is not None:
            valRows = []
            for i in range(len(sizedfs)):
                tup = (sizedfs[MktValue].iloc[i])
                cri = super().__rm_invalid__(x = tup, funcs = rmrows)
                if cri == False:
                    valRows.append(i)
            szvalids = sizedfs.iloc[valRows,:].copy()
        else:
            szvalids = sizedfs # Do not copy since nothing's changed
        
        # Matching
        mc_datetime = []
        mc_yearas = []
        mc_bokvalue = []
        mc_mktvalue = []
        
        # Generate a month-based datetime column for sizedf
        DateTime_M = "DateTime_M"
        szdt = list(szvalids[DateTime].astype(str))
        for i in range(len(szdt)):
            # YYYY-MM
            szdt[i] = str(szdt[i])[0:7]
        szvalids[DateTime_M] = szdt
        
        # Create a time-stock indexed dict for szvalids
        # dict{TimeIndexed: dict{StkIndexed: data}}
        szval2dict = self.collect_timestkindexed_sheets(
            use = szvalids,
            rmrows = None,
            bycol_datetime = DateTime_M,
            bycol_stkid = StkID,
            datetime_as = DateTime_M,
            stockid_as = StkID,
            datetime_type = str)
        
        # Generate a stock number/time number set for sizedf
        # The reason why using a set is that when finding by a key,
        # the complexity is only O(1)
        szstk = set(szvalids[StkID].astype(int))
        sztm = set(szval2dict.keys())
        
        # -> "default" method
        if method == "default":
            
            ################################################
            # need to modify
            
            # Set refmonth as 12
            refmonth = 12
            
            # Get the row iloc num
            _i_FYear = list(usevalids.columns).index(FYear)
            _i_StkID = list(usevalids.columns).index(StkID)
            _i_BokValue = list(usevalids.columns).index(BokValue)
            
            # For each row, matching it with the december's mktvalue
            for i in range(len(usevalids)):
                
                # Get the YYYY-MM of each row
                fyear = str(usevalids.iloc[i, _i_FYear])
                fyearm = fyear + "-" + strint(refmonth, "%02")
                
                # Get the stock ID of each row
                sid = int(usevalids.iloc[i, _i_StkID])
                
                # Try to match the YYYY-MM in the sizedf
                if fyearm not in sztm:
                    mc_datetime.append(None)
                    mc_yearas.append(None)
                    mc_bokvalue.append(None)
                    mc_mktvalue.append(None)
                    continue
                
                # Try to match the stock ID in the sizedf by szval2dict
                if sid not in szstk:
                    mc_datetime.append(None)
                    mc_yearas.append(None)
                    mc_bokvalue.append(None)
                    mc_mktvalue.append(None)
                    continue
                    
                # All True, 
                # If findable, directly find the book and market value
                thisptr = []
                if sid not in szval2dict[fyearm].keys():
                    mc_datetime.append(None)
                    mc_yearas.append(None)
                    mc_bokvalue.append(None)
                    mc_mktvalue.append(None)
                    continue
                else:
                    thisptr = szval2dict[fyearm][sid]
                    
                # Intersect
                mc_datetime.append(fyearm)
                mc_yearas.append(int(fyear) + 1)
                mc_bokvalue.append(usevalids.iloc[i, _i_BokValue])
                mc_mktvalue.append(thisptr[MktValue].iloc[0])
                
        # -> "average" method
        elif method == "average":
            
            # check refmonth
            if refmonth > 12 or refmonth < 0:
                ErrorCode("Invalid refmonth in the var \\refmonth\\! Only 1 to 12 is accepted!")
                
            # Get the row iloc num
            _i_FYear = list(usevalids.columns).index(FYear)
            _i_StkID = list(usevalids.columns).index(StkID)
            _i_UseDtime = list(usevalids.columns).index(DateTime)
            _i_BokValue = list(usevalids.columns).index(BokValue)
            
            # For each row, matching it with the december's mktvalue
            for i in range(len(usevalids)):
                
                # Get the YYYY-MM of each row (adjusted)
                fyear = str(usevalids.iloc[i, _i_FYear])
                fyearm = ""
                if refmonth > 6:
                    fyearm = str(int(fyear) + 0) + "-" + strint(refmonth, "%02")
                else:
                    fyearm = str(int(fyear) + 1) + "-" + strint(refmonth, "%02")
                
                # Get the stock ID of each row
                sid = int(usevalids.iloc[i, _i_StkID])
                
                # Try to match the YYYY-MM in the sizedf
                if fyearm not in sztm:
                    mc_datetime.append(None)
                    mc_yearas.append(None)
                    mc_bokvalue.append(None)
                    mc_mktvalue.append(None)
                    continue
                
                # Try to match the stock ID in the sizedf by szval2dict
                if sid not in szstk:
                    mc_datetime.append(None)
                    mc_yearas.append(None)
                    mc_bokvalue.append(None)
                    mc_mktvalue.append(None)
                    continue
                    
                # All True, 
                # If findable, directly find the book and market value
                thisptr = []
                if sid not in szval2dict[fyearm].keys():
                    mc_datetime.append(None)
                    mc_yearas.append(None)
                    mc_bokvalue.append(None)
                    mc_mktvalue.append(None)
                    continue
                else:
                    thisptr = szval2dict[fyearm][sid]
                
                # Adjust the book value
                target_year = int(fyear) + 1
                weight_tm1 = 1
                weight_t = 0
                
                # If we can find the next one, give t some weights
                if i < len(usevalids) - 1:
                    if int(usevalids.iloc[(i+1), _i_StkID]) == sid:
                        if int(usevalids.iloc[(i+1), _i_FYear]) == target_year:
                            # use tm1_int and base_int to compute weights
                            tm1_ym = str(usevalids.iloc[i, _i_UseDtime])[0:7]
                            tm1_int = yearmonth(tm1_ym)
                            base_int = yearmonth(str(target_year) + "-" + str(refmonth))
                            # reweight
                            weight_t = (base_int - tm1_int) / 12
                            weight_tm1 = 1 - weight_t
                
                # Recompute the averaged BokValue
                bkvl_new = usevalids.iloc[i, _i_BokValue] * weight_tm1 + usevalids.iloc[(i+1), _i_BokValue] * weight_t
                
                mc_datetime.append(fyearm)
                mc_yearas.append(int(fyear) + 1)
                mc_bokvalue.append(bkvl_new)
                mc_mktvalue.append(thisptr[MktValue].iloc[0])
                
        # Append four new columns
        usesappend = usevalids.copy()
        usesappend[Matched_DateTime] = mc_datetime
        usesappend[Matched_YearAs] = mc_yearas
        usesappend[Matched_BokValue] = mc_bokvalue
        usesappend[Matched_MktValue] = mc_mktvalue
        
        # If asked to delete None rows
        if delnonmatch == True:
            usesappend = self.remove_some_samples(
                use = usesappend,
                bycol_identity = None,
                bycol_chk = Matched_BokValue,
                rmrows = ["default"],
                method = "sample")
        
        return szval2dict, usesappend
    
    # Collect book-to-market values
    # in  <- pd.DataFrame annually
    # out -> pd.DataFrame annually, with a now columns named "Matched_B2MValue" generated
    # [params] use:    pd.DataFrame, "defualt" meaning the self._data
    # [params] rmrows: criterion functions, ["defualt"] meaning the self.__rm_invalid__
    #          *use NoneType to avoid manually settings on a certain factor
    def collect_bm_values(self, use = "default", *,
           bycol_mc_bokvalue, 
           bycol_mc_mktvalue,
           rmrows = ["default"], 
           astype = None, 
           copy = True) -> pd.DataFrame:
        
        #######################################################################
        #
        # If uses the default use
        if type(use) != type(pd.DataFrame()):
            if use == "default":
                use = super()._data
            else:
                raise ErrorCode("Invalid input data in the var \\use\\!")
               
        # If uses the default rmrows
        if type(rmrows) == type([]):
            if rmrows[0] == "default":
                rmrows = ["default"]
        elif rmrows is not None:
            raise ErrorCode("Invalid input criterion functions in the var \\rmrows\\!")
        
        # If use it None, return None
        if use is None:
            raise ErrorCode("Invalid input data in the var \\use\\!")
       
        # Checking if the cols exist
        if bycol_mc_bokvalue not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_mc_bokvalue\\!")
        if bycol_mc_mktvalue not in use.columns:
            raise ErrorCode("Invalid column name in the var \\bycol_mc_mktvalue\\!")
        
        # Change the type of the DataFrame
        uses = []
        if copy == True:
            uses = use.copy()
        else:
            uses = use
        if astype is not None:
            uses = uses.astype(astype)
        uses[bycol_mc_bokvalue] = uses[bycol_mc_bokvalue].astype(float)
        uses[bycol_mc_mktvalue] = uses[bycol_mc_mktvalue].astype(float)
       
        # Change the column name to be matched
        Matched_BokValue = "Matched_BokValue"
        Matched_MktValue = "Matched_MktValue"
        Matched_B2MValue = "Matched_B2MValue"
        cl = list(uses.columns)
        id_b = list(uses.columns).index(bycol_mc_bokvalue)
        id_m = list(uses.columns).index(bycol_mc_mktvalue)
        cl[id_b] = Matched_BokValue
        cl[id_m] = Matched_MktValue
        uses.columns = cl
        
        #######################################################################
        #
        # Try and test the rmrows's returned value
        if rmrows is not None:
            if type(super().__rm_invalid__(x = (None), funcs = rmrows)) != type(True):
                raise ErrorCode("Invalid rmrows function in the var \\rmrows\\! The criterion function should accept tuples as inputs and return a bool indicating whether to remove that variable!")
            
        # Remove invalid rows
        if rmrows is not None:
            valRows = []
            for i in range(len(uses)):
                tup = (uses[Matched_BokValue].iloc[i], 
                       uses[Matched_MktValue].iloc[i])
                cri = super().__rm_invalid__(x = tup, funcs = rmrows)
                if cri == False:
                    valRows.append(i)
            kpvalids = uses.iloc[valRows,:].copy()
        else:
            kpvalids = uses # Do it without copy since nothing's done
        
        # Collect the book-to-market value as a new column
        b2mkt = np.divide(np.array(kpvalids[Matched_BokValue]),
                              np.array(kpvalids[Matched_MktValue]))
        kpvalids[Matched_B2MValue] = b2mkt
        
        return kpvalids
    
    # End of Class
    
# End of this file