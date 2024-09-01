# FF3_Utilities.py
# This is the module providing functions and exceptions
#

import os as os
import pickle as pickle
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Garbage control
def gc(obj) -> None:
    '''
    How to use gc()? 
    If you want to remove a variable "x" from the memory, use x = gc(x).
    Then, it will be set to a NoneType, and consequently, removed from your memory.
    '''
    obj = None
    return obj

# Repetation
def rep(obj, times = 1) -> list:
    '''
    How to use the rep()?
    If you want to repeat 1 for ten times, just use rep(1, times = 10),
    the function will return a [1,1,1, ..., 1] with 10 elements.
    '''
    _ls = list(range(times))
    for i in range(len(_ls)):
        _ls[i] = obj
    return _ls

# Pandas Dataframe plainize
def pd_plainize(data:pd.DataFrame) -> list:
    
    rlen = len(data.columns)
    tlen = len(data.index) * len(data.columns)
    ls = rep(0, tlen)
    for i in range(len(data.index)):
        for j in range(len(data.columns)):
            pos = i * rlen + j
            ls[pos] = data.iloc[i,j]
    return ls

# OLS regression
def ols(y:pd.Series, x:pd.DataFrame) -> tuple[any]:

    _x = sm.add_constant(x)
    model = sm.OLS(y, _x)
    results = model.fit()
    return model, results

# OLS regression's summary
def ols_summary(y:pd.Series, x:pd.DataFrame) -> None:
    
    _x = sm.add_constant(x)
    model = sm.OLS(y, _x)
    results = model.fit()
    print(results.summary())
    return None

# OLS regression's dataframe
def ols_dataframe(y:pd.Series, x:pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    
    _x = sm.add_constant(x)
    model = sm.OLS(y, _x)
    results = model.fit()
    
    pdf = pd.DataFrame()
    pdf["coef"] = results.params
    pdf["serr"] = results.uncentered_tss # a bug, but I don't know where the serr is
    pdf["t-val"] = results.tvalues
    pdf["p-val"] = results.pvalues
    pdf["n"] = results.nobs
    pdf["r2"] = results.rsquared
    pdf["r2_adjusted"] = results.rsquared_adj
    pdf["f-val"] = results.fvalue
    pdf["f-p-val"] = results.f_pvalue
    pdf["aic"] = results.aic
    pdf["bic"] = results.bic
    pdf["log-likelihood"] = results.llf
    pdf["mse_model"] = results.mse_model
    pdf["mse_resid"] = results.mse_resid
    pdf["mse_total"] = results.mse_total
    
    residual = results.resid
    
    return pdf, residual

# OLS regression's dataframe's column names
def ols_dataframe_names() -> list:
    
    ls =[ "coef","serr","t-val","p-val",
         "n","r2","r2_adjusted","f-val","f-p-val",
         "aic","bic","log-likelihood","mse_model","mse_resid","mse_total"] 
    return ls
    
# OLS regression's dataframe's column names
def ols_dataframe_multinames() -> list:
    
    ls =[ "coef","serr","t-val","p-val"] 
    return ls

# File Exists
def file_exists(pathlike) -> bool:
    '''
    Function file_exists() trys to see whether a given filepath is 
    related to an existed file. If so, it will return True, otherwise, 
    a False will be obtained.
    For example, file_exists("abc.bin") will return False if it is missed.
    '''
    return os.path.isfile(pathlike)

# Find the indices of an element
def pos(lst, x) -> list:
    '''
    Function pos() returns all of the indices in \\lst\\ that match the value of \\x\\.
    For example, pos([1,2,2,3], 2) will return a list of [1,2].
    '''
    counts = lst.count(x)
    if counts == 0:
        return []
    
    # Reserve some space
    find = list(range(counts))
    starts = 0
    for i in range(0, counts, 1):
        ret = lst.index(x, starts)
        find[i] = ret
        starts = ret + 1
    return find

# Stringize an integer with padding
def strint(integer, padtype = "%06") -> str:
    
    if isinstance(integer, int) == False:
        return str(integer)
    
    stri = str(integer)
    cat = ""
    if padtype[0] == "%":
        padtype = padtype[1:len(padtype)]
        rep = padtype[0]
        rlen = int(padtype[1:len(padtype)])
        if len(stri) >= rlen:
            return stri
        rlen = rlen - len(stri)
        for i in range(0,rlen,1):
            cat += rep
        return cat + stri
    
    return stri

# Stringize a float with precision
def strfloat(floater, digits = 2):
    format_str = '{:.%df}' % digits
    return format_str.format(floater)

# Year-Month ("YYYY-MM-DD ..." format) to int
def yearmonth(datetime, starts_at = "1900-01", starts_at_beginning = True) -> int:
    
    dat = str(datetime)[0:7]
    year_x = int(dat[0:4])
    month_x = int(dat[5:7])
    base_year = int(starts_at[0:4])
    base_month = int(starts_at[5:7])
    
    months = (year_x - base_year) * 12
    months += month_x - base_month
    if starts_at_beginning == True:
        months += 1
    
    return months

# In which zone (floater only, returing -1 meaning None)
def inwhich_zone(x, _zone:list[tuple] = []) -> int:
    
    for i in range(len(_zone)):
        z = _zone[i]
        if x >= z[0] and x < z[1]:
            return i
    return -1

# Generate a time serie from a given list
#   YEAR  YEAR-MONTH
#   YEAR  YEAR-MONTH
#   ...   ...
def timeseries(timestamps, wh_year = 0, wh_month = 5, refresh_month = 7) -> pd.DataFrame:
    
    years = timestamps.copy()
    months = timestamps.copy()
    
    for i in range(len(timestamps)):
        
        years[i] = timestamps[i][wh_year:(wh_year + 4)]
        months[i] = years[i] + "-" + timestamps[i][wh_month:(wh_month + 2)]
        
        if int(timestamps[i][wh_month:(wh_month + 2)]) < refresh_month:
            years[i] = str(int(years[i]) - 1)
    
    df = pd.DataFrame({"Year":years, "YearMonth":months})
    return df

# Plainize a multidimensional data
def plainize(data, *, kname = "Keys", vname = "Values") -> pd.DataFrame:
    
    if type(data) == type({}):
        keys = data.keys()
        values = data.values()
        pds = pd.DataFrame({kname : keys,
                            vname : values})
        return pds
        
    else:
        raise ErrorCode("Unsupported type \\" + str(type(data)) + "\\!")

# Insert something into array-liked strings
def insert_str(data, insert = "-", at = 3) -> np.array:
    
    if type(data) != type(np.array([1])):
        data = np.array(data).astype(str)
    
    for i in range(len(data)):
        dlen = len(data[i])
        data[i] = data[i][0:(at+1)] + insert + data[i][(at+1):dlen]
    return data

# Series apply on a data frame
def sapplyon(data, on, func) -> pd.DataFrame:
    
    oncol = data[on]
    for i in range(len(oncol)):
        oncol.iloc[i] = func(oncol.iloc[i])
    data[on] = oncol
    
    return data

# Match two dataframes on a column
def matchon(left, right, on, how = "inner") -> pd.DataFrame:
    
    return pd.merge(left, right, how = how, on = on)

# Dict values' type transformation
def dictvalues_astype(dict_, type_to = int, *, type_intern = None) -> dict:
    
    ndict = {}
    if type_intern is not None:
        for k in dict_.keys():
            new_v = type_to(type_intern(dict_[k]))
            ndict[k] = new_v
    else:
        for k in dict_.keys():
            new_v = type_to(dict_[k])
            ndict[k] = new_v
    return ndict

# Dict keys' type transformation
def dictkeys_astype(dict_, type_to = int, *, type_intern = None) -> dict:
    
    ndict = {}
    if type_intern is not None:
        for k in dict_.keys():
            new_k = type_to(type_intern(k))
            ndict[new_k] = dict_[k]
    else:
        for k in dict_.keys():
            new_k = type_to(k)
            ndict[new_k] = dict_[k]
    return ndict

# Dict keys' new name subsitution
def dictkeys_newnames(dict_, new_keys) -> dict:
    if len(new_keys) != len(list(dict_.keys())):
        raise ErrorCode("Renamed keys must have the same length as the origial ones!")
    neo_dict = {}
    old_keys = list(dict_.keys())
    for i in range(len(dict_.keys())):
        k = old_keys[i]
        neo_dict[new_keys[i]] = dict_[k].copy()
    return neo_dict

# Keep values in ...
def keep_valuesin(df, column, values_in = []) -> pd.DataFrame:
    
    validRows = []
    for i in range(len(df)):
        if df[column].iloc[i] in values_in:
            validRows.append(i)
    return df.iloc[validRows,:].copy()
    
# Dict apply
def dapply(dict_, func) -> dict:
    
    ndict = {}
    for k in dict_.keys():
        ndict[k] = func(dict_[k])
    return ndict

# pd.DataFrame apply
def pdapply(pd_, func, *, copy = True) -> dict:
    
    npd = pd_
    if copy == True:
        npd = pd_.copy()
    for i in range(len(npd.index)):
        for j in range(len(npd.columns)):
            npd.iloc[i, j] = func(npd.iloc[i, j])
    return npd

# Group name to N-dimensional pairs
def grpname_to_ndpairs(groupnames:list,
        seperate = "_",
        groupsassign = ["L", "L"],
        *,
        safe = [],
        sort = True,
        ) -> tuple[dict[tuple]]:
    '''
    About the returned result! 
    A tuple, while:
        > ret[0] is a dict using groupname to get the pair.
        > ret[1] is a dict using the pair to get the groupname.
    '''
    
    if type(groupnames) != type([]):
        raise ErrorCode("Input \\groupnames\\ must be a list!")
    elif len(groupnames) == 0:
        raise ErrorCode("Input \\groupnames\\ must contain more than 0 groups!")
    
    g2p = {} # groupname to pairs
    p2g = {} # pairs to groupname
    dimension = len(groupsassign)
    
    # Create g2p
    for g in groupnames:
        # The pair of this groupname
        pairs = []
        for i in range(dimension):
            pairs.append(-1)
        
        # Split it and try to get the number of each group
        splits = g.split(seperate)
        no = -1
        for i in range(len(splits)):
            # Starts with the annotation
            if splits[i].startswith(groupsassign[no+1]):
                # Not in the safe
                _cont_ = False
                for s in safe:
                    if splits[i].startswith(s):
                        _cont_ = True
                        break
                if _cont_ == True:
                    continue
                # Truly with the group annotation
                # No += 1
                no += 1
                # Give the number
                num = int(splits[i][len(groupsassign[no]):])
                # Go adding the group
                pairs[no] = num
        g2p[g] = tuple(pairs)
                        
    # Then p2g
    for g in groupnames:
        p = g2p[g]
        p2g[p] = g

    return g2p, p2g

# DataFrame printf (floater)
def df_fprintf(data:pd.DataFrame, digits = 2, *, copy = True) -> pd.DataFrame:
    
    pdf = data
    if copy == True:
        pdf = data.copy()
    rows = list(range(len(data.index)))
    cols = list(range(len(data.columns)))
    
    for i in rows:
        for j in cols:
            pdf.iloc[i, j] = strfloat(pdf.iloc[i, j], digits)
            
    return pdf

# Save as a pickle
def save_as(x, filepath) -> None:
    
    with open(filepath, 'wb') as file:
        pickle.dump(x, file)
    return None

# Load from a pickle
def load_from(filepath) -> any:
    
    loaded = []
    with open(filepath, 'rb') as file:
        loaded = pickle.load(file)
    return loaded

# Exception Definition
class ErrorCode(Exception):
    
    # Constructor
    def __init__(self, message) -> None:
        super().__init__(message)
        return None

# Interfaces for graph ploting
class PlotGraph:
    
    # Constant Members
    __validTypes__ = ["l", "b"]
    
    # Data Members
    _data = []
    _type = ""

    ###########################################################################
    # Internal Functions
    #
    
    # Line Graph
    def __lineGraph__(self, *, args:dict) -> None:
        
        # Check the "x" "y" column
        if "x" not in list(self._data.columns):
            raise ErrorCode("No column named x in the var \\data\\!")
        if "y" not in list(self._data.columns):
            raise ErrorCode("No column named y in the var \\data\\!")
        
        # Plot Settings
        _col = "b"
        _title = ""
        _xlim = []
        _ylim = []
        _xlabel = "x"
        _ylabel = "y"
        _xrot = 0
        _yrot = 0
        
        # col
        if "col" in args:
            _col = args["col"]
        else:
            _col = "b"
            
        # title
        if "title" in args:
            _title = args["title"]
        else:
            _title = "Line Graph"
            
        # xlim
        if "xlim" in args:
            tmp = args["xlim"]
            if len(tmp) != 2:
                raise ErrorCode("Invalid xlim in the var \\args\\!")
            else:
                _xlim = tmp
        else:
            _xlim = [min(self._data["x"]), max(self._data["x"])]
        
        # ylim
        if "ylim" in args:
            tmp = args["ylim"]
            if len(tmp) != 2:
                raise ErrorCode("Invalid ylim in the var \\args\\!")
            else:
                _ylim = tmp
        else:
            _ylim = [min(self._data["y"]), max(self._data["y"])]
            
        # xlabel
        if "xlabel" in args:
            _xlabel = args["xlabel"]
        else:
            _xlabel = "x"
            
        # ylabel
        if "ylabel" in args:
            _ylabel = args["ylabel"]
        else:
            _ylabel = "y"
            
        # xrot
        if "xrot" in args:
            _xrot = args["xrot"]
        else:
            _xrot = 0
            
        # yrot
        if "yrot" in args:
            _yrot = args["yrot"]
        else:
            _yrot = 0
        
        # plot
        plt.plot(self._data["x"], self._data["y"], color = _col)
        plt.title(_title)
        plt.xlim(_xlim)
        plt.ylim(_ylim)
        plt.xlabel(_xlabel)
        plt.ylabel(_ylabel)
        plt.xticks(rotation = _xrot)
        plt.yticks(rotation = _yrot)
        
        # set font
        plt.rcParams['font.family'] = 'SimHei'
        plt.rcParams['axes.unicode_minus'] = False
        
        # show
        plt.show()
        
        return None
    
    # Bar Graph
    def __barGraph__(self, *, args:dict) -> None:
        
        # Check the "x" "y" column
        if "x" not in list(self._data.columns):
            raise ErrorCode("No column named x in the var \\data\\!")
        if "y" not in list(self._data.columns):
            raise ErrorCode("No column named y in the var \\data\\!")
        
        # Plot Settings
        _col = "b"
        _title = ""
        _xlim = []
        _ylim = []
        _xlabel = "x"
        _ylabel = "y"
        
        # col
        if "col" in args:
            _col = args["col"]
        else:
            _col = "b"
            
        # title
        if "title" in args:
            _title = args["title"]
        else:
            _title = "Line Graph"
            
        # xlim
        if "xlim" in args:
            tmp = args["xlim"]
            if len(tmp) != 2:
                raise ErrorCode("Invalid xlim in the var \\args\\!")
            else:
                _xlim = tmp
        else:
            _xlim = []
        
        # ylim
        if "ylim" in args:
            tmp = args["ylim"]
            if len(tmp) != 2:
                raise ErrorCode("Invalid ylim in the var \\args\\!")
            else:
                _ylim = tmp
        else:
            _ylim = [min(self._data["y"]), max(self._data["y"])]
            
        # xlabel
        if "xlabel" in args:
            _xlabel = args["xlabel"]
        else:
            _xlabel = "x"
            
        # ylabel
        if "ylabel" in args:
            _ylabel = args["ylabel"]
        else:
            _ylabel = "y"
            
        # xrot
        if "xrot" in args:
            _xrot = args["xrot"]
        else:
            _xrot = 0
            
        # yrot
        if "yrot" in args:
            _yrot = args["yrot"]
        else:
            _yrot = 0
        
        # plot
        plt.bar(x = self._data["x"], height = self._data["y"], color = _col)
        plt.title(_title)
        if len(_xlim) > 0:
            plt.xlim(_xlim)
        plt.ylim(_ylim)
        plt.xlabel(_xlabel)
        plt.ylabel(_ylabel)
        plt.xticks(rotation = _xrot)
        plt.yticks(rotation = _yrot)
                
        # set font
        plt.rcParams['font.family'] = 'SimHei'
        plt.rcParams['axes.unicode_minus'] = False
        
        # show
        plt.show()
        
        # show
        plt.show()
        
        return None
    
    ###########################################################################
    # API Functions
    #
    
    # Constructor
    def __init__(self, data, type = "l") -> None:
        
        self._data = data
        if type not in self.__validTypes__:
            raise ErrorCode("Invalid Graph Type in the var \\type\\!")
        self._type = type
        return None
        
    # Plot
    def plot(self, *, args = None) -> None:
        
        # "l"
        if self._type == "l":
            if args == None:
                self.__lineGraph__(args = {})
            elif type(args) != type({}):
                raise ErrorCode("Invalid Dict Argument in the var \\args\\!")
            else:
                self.__lineGraph__(args = args)
        
        # "b"
        elif self._type == "b":
            if args == None:
                self.__barGraph__(args = {})
            elif type(args) != type({}):
                raise ErrorCode("Invalid Dict Argument in the var \\args\\!")
            else:
                self.__barGraph__(args = args)
            
        return None

# Load structural data from a directory
class LoadDirData:
    
    # Const Members
    __attr__ = "LoadDirData"
    __version__ = "0"
    __supportedFormats__ = [".xls",".xlsx",".csv",".dta"]
    
    # Data Members
    _dir = ""     # str
    _paths = []   # list[]
    _files = []   # list[list]
    _rawdat = []  # list[list[pd.DataFrame]], raw data imported
    _mrgdat = []  # list[pd.DataFrame], imported, merged data
    _clrdat = []  # list[pd.DataFrame], cleared data (rows removed)
    
    _append = []
    
    ###########################################################################
    # Internal Functions
    #
    
    # Is a file
    def __isFile__(self, path) -> int:
        if os.path.isfile(path):
            return  1 # meaning a file
        elif os.path.isdir(path):
            return  0 # meaning a directory
        else:
            return -1 # meaning does not exist
    
    # Having suffix as ...
    def __isSuffix__(self, path, *, format = ".dta") -> int:
        # Allow any files
        if format == None:
            return 1
        
        # Filter a certain kind of file
        if path.endswith(format):
            return 1
        else:
            return 0
        
    # Remove Rows Containing ... (copy mode)
    def __rmRows__(self, df, containing = ["没有单位"], colnum = 0) -> pd.DataFrame:
        
        cols = len(df.columns)
        if colnum >= cols:
            raise ErrorCode("Invalid column index in the var \\colnum\\!")
        colnam = list(df.columns)[colnum]
        
        valid_rows = []
        res = list(df[colnam].isin(containing))
        for i in range(len(res)):
            if res[i] == False:
                valid_rows.append(i)
        
        neo_df = df.iloc[valid_rows,:].copy()
        return neo_df
      
    ###########################################################################
    # API Functions
    #
    
    # Constructor
    def __init__(self, dir, *, format = ".dta", interupt = False) -> None:
        
        # Import All Filepaths
        self._dir = dir
        self._paths = os.listdir(dir)
        for i in range(len(self._paths)):
            self._paths[i] = self._dir + "\\" + self._paths[i]
            if self.__isFile__(self._paths[i]) == 1:
                if self.__isSuffix__(path = self._paths[i], format = format) == 1:
                    self._files.append([self._paths[i]])
            elif self.__isFile__(self._paths[i]) == 0:
                _tmp = os.listdir(self._paths[i])
                for j in range(len(_tmp)):
                    _tmp[j] = self._paths[i] + "\\" + _tmp[j]
                _sel = []
                for j in range(len(_tmp)):
                    if self.__isSuffix__(path = _tmp[j], format = format) == 1:
                        _sel.append(_tmp[j])
                self._files.append(_sel)
            else:
                raise ErrorCode("Invalid Filepath in the var \\dir\\!")
            self._files.sort()
        
        # Interupt
        if interupt == True:
            return None
        
        # Import All DataSets
        for i in range(len(self._files)):
            data = []
            for j in range(len(self._files[i])):
                # excel
                if self.__isSuffix__(self._files[i][j], format = ".xls") == 1:
                    datmp = pd.read_excel(self._files[i][j])
                    data.append(datmp)
                elif self.__isSuffix__(self._files[i][j], format = ".xlsx") == 1:
                    datmp = pd.read_excel(self._files[i][j])
                    data.append(datmp)
                # csv
                elif self.__isSuffix__(self._files[i][j], format = ".csv") == 1:
                    datmp = pd.read_csv(self._files[i][j])
                    data.append(datmp)
                # dta
                elif self.__isSuffix__(self._files[i][j], format = ".dta") == 1:
                    datmp = pd.read_stata(self._files[i][j])
                    data.append(datmp)
                # Unsupported Format
                else:
                    raise ErrorCode("Unsupported File: \\" + self._files[i][j] + "\\!")
            self._rawdat.append(data)
        
        # Merge All DataSets
        for i in range(len(self._rawdat)):
            pgtmp = []
            for j in range(len(self._rawdat[i])):
                page = self._rawdat[i][j]
                if j == 0:
                    pgtmp = page
                else:
                    pgtmp = pgtmp.append(page)
            self._mrgdat.append(pgtmp)
            
        return None
    
    # Refill Cleared Data in the _clrdat
    def rf_clrdat(self, *, containing = ["没有单位"], on_colnum = 0) -> list[pd.DataFrame]:
        
        self.clrdat = []
        for i in range(len(self._mrgdat)):
            ret = self.__rmRows__(df = self._mrgdat[i], containing = containing, colnum = on_colnum)
            self._clrdat.append(ret)
            
        return self._clrdat
    
    # Append some appends, and return the appended
    def ap_append(self, append = [], *, appendclr = False) -> list:
        if appendclr == True:
            self._append = []
        for a in append:
            self._append.append(a)
        return self._append
    
    # Remove a certain element, and return the remained
    def ap_remove(self, remove = [], *, appendclr = False) -> list:
        if appendclr == True:
            self._append = []
        for r in remove:
            if r not in self._append:
                raise ErrorCode("Invalid remove element in the var \\remove\\!")
        for r in remove:
            self._append.remove(r)
        return self._append
    
    # Clear all extant appends
    def ap_clrall(self, appendclr = True) -> list:
        if appendclr == True:
            self._append = []
        return self._append
    
    # Save all members as a pickle
    def sv_aspickle(self, filepath, *, append = [], appendclr = False) -> None:
        if appendclr == True:
            self._append = []
        for a in append:
            self._append.append(a)
        fp = filepath
        if self.__isFile__(filepath) != 1:
            raise ErrorCode("Input filepath is not a \\file\\!")
        if self.__isSuffix__(filepath, format = ".pickle") != 1:
            raise ErrorCode("Input filepath is not a \\.pickle\\!")
        _sav_parse = {
            "__attr__" : self.__attr__,
            "__supportedFormats__" : self.__supportedFormats__,
            "__version__" : self.__version__,
            
            "_dir" : self._dir,
            "_paths" : self._paths,
            "_files" : self._files,
            "_rawdat" : self._rawdat,
            "_mrgdat" : self._mrgdat,
            "_clrdat" : self._clrdat,
            
            "_append" : self._append}
        save_as(_sav_parse, fp)
        return None
    
    # Load all members from a pickle (self <- self)
    def ld_frompickle(self, filepath, *, append = [], appendclr = False) -> any:
        if self.__isFile__(filepath) != 1:
            raise ErrorCode("Input filepath is not a \\file\\!")
        if self.__isFormat__(filepath, format = ".pickle") != 1:
            raise ErrorCode("Input filepath is not a \\.pickle\\!")
        _sav_parse = load_from(filepath)
        self.__attr__ = _sav_parse["__attr__"]
        self.__supportedFormats__ = _sav_parse["__supportedFormats__"]
        self.__version__ = _sav_parse["__version__"]
        
        self._dir = _sav_parse["_dir"]
        self._paths = _sav_parse["_paths"]
        self._files = _sav_parse["_files"]
        self._rawdat = _sav_parse["_rawdat"]
        self._mrgdat = _sav_parse["_mrgdat"]
        self._clrdat = _sav_parse["_clrdat"]
        
        self._append = _sav_parse["_append"]
        if appendclr == True:
            self._append = []
        for a in append:
            self._append.append(a)
        return self
    
# End of this file