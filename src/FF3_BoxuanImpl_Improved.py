# FF3_BoxuanImpl_Improved.py
# This is the main executable file to reproduce FF3 results
#

import os as os
import numpy as np
import pandas as pd

from FF3_Utilities import gc
from FF3_Utilities import file_exists
from FF3_Utilities import timeseries
from FF3_Utilities import plainize
from FF3_Utilities import insert_str
from FF3_Utilities import sapplyon
from FF3_Utilities import matchon
from FF3_Utilities import dictvalues_astype
from FF3_Utilities import dictkeys_astype
from FF3_Utilities import dictkeys_newnames
from FF3_Utilities import keep_valuesin
from FF3_Utilities import dapply
from FF3_Utilities import ErrorCode
from FF3_Utilities import PlotGraph
from FF3_Utilities import LoadDirData

from FF3_Utilities import save_as
from FF3_Utilities import load_from

from FF3_FactorBuilding import FactorUtils
from FF3_FactorBuilding import FactorSMB
from FF3_FactorBuilding import FactorHML

###############################################################################
#
# Important!
# > The following paths should be properly set, and all of the directories
#   should be existed, empty ones.
# > Please set the global parameters based on your requirement. 
#   But favorably, you should at least permit the program to automatically 
#   save the final data of the generated three factors.
#   [Param] _g_sav_final:  Setting True to obtain the final FF3 factors
#   [Param] _g_low_memory: Setting True to remove some unused variable to control the memory use

# Directroy related params
data_sav = r"C:\Users\happy\Desktop\资产定价\Project\Data\processes"

# (Import) Path related prarms
data_fundamentals = r"C:\Users\happy\Desktop\资产定价\Project\Data\original\CRSP Compustat Merged - Fundamentals Annual\CRSP Compustat Merged - Fundamentals Annual.dta"
data_monthly = r"C:\Users\happy\Desktop\资产定价\Project\Data\original\CRSP Monthly Stock\CRSP Monthly Stock.dta"
data_riskfree = r"C:\Users\happy\Desktop\资产定价\Project\Data\original\rf\rf.dta"

# Class Initialization
smb = FactorSMB()
hml = FactorHML()

# Global Parameters
_g_sav_final = True
_g_low_memory = True

# Program Entry Point (main function)
if __name__ == "__main__":
    
    # IMPORT ESSENTIAL DATA
    clrdat = [0,1,2]
    if file_exists(data_fundamentals) == False:
        raise ErrorCode("Path \\data_fundamentals\\ does not exist!")
    if file_exists(data_monthly) == False:
        raise ErrorCode("Path \\data_monthly\\ does not exist!")
    if file_exists(data_riskfree) == False:
        raise ErrorCode("Path \\data_riskfree\\ does not exist!")
    clrdat[0] = pd.read_stata(data_fundamentals)
    clrdat[1] = pd.read_stata(data_monthly)
    clrdat[2] = pd.read_stata(data_riskfree)
    
    # SIZE CALCULATION
    sizes_ = smb.collect_market_values(
        use = clrdat[1],
        bycol_price="PRC",
        bycol_shares="SHROUT")
    # save_as(sizes_, data_sav + "\\sizes_.pickle")
    
    # BE CALCULATION
    bequity_ = hml.collect_book_values(
        use = clrdat[0],
        bycol_normequity = "seq",
        bycol_defferedtax = "txditc",
        bycol_prefferedstock = "pstk")
    # save_as(bequity_ , data_sav + "\\bequity_.pickle")
    
    # GET THE RISK-FREE DATA INDEXED BY THE DATETIME
    rf_raw = insert_str(clrdat[2]["date"])
    s_rf = clrdat[2]
    s_rf["date"] = rf_raw                   # reassign the date
    s_rf["rf"] = np.multiply(
        np.array(s_rf["rf"]), 0.01)         # recalculate the return in decimal
    s_rf.columns = ["DateTime", "RF"]       # rename the columns
    # save_as(s_rf , data_sav + "\\s_rf.pickle")
    
    # REMOVE THOSE HAVING NEGATIVE BE VALUES
    utils = FactorUtils()
    bequity_dup_negatives = hml.remove_some_samples(
        use = bequity_,
        bycol_identity = "LPERMCO",
        bycol_chk = "BokValue",
        rmrows = [utils.Boolean_lessthanzero],
        method = "sample")         # Arbitary! original paper's testimony is vague)
    # save_as(bequity_dup_negatives , data_sav + "\\bequity_dup_negatives.pickle")
    beq2 = hml.remove_some_samples(
        use = bequity_,
        bycol_identity = "LPERMCO",
        bycol_chk = "BokValue",
        rmrows = [utils.Boolean_lessthanzero],
        method = "identity")       # Alternative!
    # save_as(beq2 , data_sav + "\\beq2.pickle")
    
    # REMOVE THOSE HAVING NON-NYSE, NON-AMEX, NON-NASDAQ FIRMS
    utils = FactorUtils(in_set = {"N", "A", "Q"})
    sizes_dup_nonmain = smb.remove_some_samples(
        use = sizes_,
        bycol_identity = None,
        bycol_chk = "PRIMEXCH",
        rmrows = [utils.Boolean_notcontainsinset],
        method = "sample")
    # save_as(sizes_dup_nonmain , data_sav + "\\sizes_dup_nonmain.pickle")
    
    # REMOVE THOSE HAVING SHRCD BIGGER THAN 20
    utils = FactorUtils(in_set = set(range(21,1000,1)))
    sizes_dup2_valshrcd = smb.remove_some_samples(
        use = sizes_dup_nonmain,
        bycol_identity = None,
        bycol_chk = "SHRCD",
        rmrows = [utils.Boolean_containsinset],
        method = "sample")
    # save_as(sizes_dup2_valshrcd , data_sav + "\\sizes_dup2_valshrcd.pickle")
    
    ###########################################################################
    # gc
    if _g_low_memory == True:
        clrdat = gc(clrdat)
        sizes_ = gc(sizes_)
        bequity_ = gc(bequity_)
        sizes_dup_nonmain = gc(sizes_dup_nonmain)
    
    # DROP THE ROWS WITH THE SAME STKID AND DATETIME
    bequity_dup_rmduped = hml.drop_identical_samples(
        use = bequity_dup_negatives,
        bycol_on = ["LPERMCO", "datadate"])
    # save_as(bequity_dup_rmduped , data_sav + "\\bequity_dup_rmduped.pickle")
    sizes_dup_rmduped = smb.drop_identical_samples(
        use = sizes_dup2_valshrcd,
        bycol_on = ["PERMCO", "date"])
    # save_as(sizes_dup_rmduped , data_sav + "\\sizes_dup_rmduped.pickle")
    
    # MATCH SIZES INTO BE DATAFRAME
    bequity_matched_2 = hml.match_size_to_bm(
        use = bequity_dup_rmduped,                # uniqueness
        sizedf = sizes_dup_rmduped,               # uniqueness
        rmrows = None,
        bycol_use_stkid = "LPERMCO",
        bycol_use_datetime = "datadate",
        bycol_use_fyear = "fyear",
        bycol_use_fyearendmonth = "fyr",
        bycol_use_bokvalue = "BokValue",
        bycol_sizedf_stkid = "PERMCO",
        bycol_sizedf_datetime = "date",
        bycol_sizedf_mktvalue = "MktValue",
        method = "default")
    bequity_matched_ = bequity_matched_2[1]
    sizes_timestkind_ = bequity_matched_2[0]
    # save_as(bequity_matched_2 , data_sav + "\\bequity_matched_2.pickle")
    # save_as(bequity_matched_ , data_sav + "\\bequity_matched_.pickle")
    # save_as(sizes_timestkind_ , data_sav + "\\sizes_timestkind_.pickle")
    
    ###########################################################################
    # gc
    if _g_low_memory == True:
        bequity_matched_2 = gc(bequity_matched_2)
    
    # DROP ROWS CONTAINING NONE-TYPE VALUES AFTER MATCHING
    bequity_matched_clr = hml.remove_some_samples(
        use = bequity_matched_,
        bycol_chk = "Matched_MktValue",
        method = "sample")
    # save_as(bequity_matched_clr , data_sav + "\\bequity_matched_clr.pickle")
    
    # COMPUTE BE/ME FACTOR
    bequity_matched_clr_bm = hml.collect_bm_values(
        use = bequity_matched_clr,
        bycol_mc_bokvalue = "Matched_BokValue", 
        bycol_mc_mktvalue = "Matched_MktValue")
    # save_as(bequity_matched_clr_bm , data_sav + "\\bequity_matched_clr_bm.pickle")
    
    ###########################################################################
    # gc
    if _g_low_memory == True:
        bequity_matched_clr = gc(bequity_matched_clr)
    
    # STOCK INDEXED - MONTHLY DATA
    sizes_stkind = smb.collect_stkindexed_sheets(
        use = sizes_dup_rmduped,
        rmrows = None,
        bycol_stkid = "PERMCO",
        bycol_datetime = "date",
        stockid_as = "PERMCO")
    # save_as(sizes_stkind , data_sav + "\\sizes_stkind.pickle")
    
    # TIME INDEXED - YEARLY DATA
    bequity_tmind = hml.collect_timeindexed_sheets(
        use = bequity_matched_clr_bm,
        rmrows = None,
        bycol_datetime = "Matched_YearAs",
        bycol_stkid = "StkID",
        datetime_as = "Matched_YearAs",
        datetime_type = float)
    bequity_tmind = dictkeys_astype(bequity_tmind, int)
    # save_as(bequity_tmind , data_sav + "\\bequity_tmind.pickle")
    
    # TIME INDEXED WITH A COLUMN PRIMEXCH APPENDED - YEARLY DATA
    def ap_matchadd(_bequity:dict, _sizes:pd.DataFrame,  *,
                    bycol_bequity_src:str,
                    bycol_sizes_src:str,
                    bycol_on:str) -> dict:
        searches = list(_sizes[bycol_sizes_src])
        ones = list(_sizes[bycol_on])
        pdf = pd.DataFrame({"s":searches,"on":ones})
        fb = FactorHML()
        npdf = fb.drop_identical_samples(use = pdf, bycol_on = ["s"])
        npdfs = list(npdf["s"])
        
        ndict = {}
        for k in _bequity.keys():
            thisptr = _bequity[k]
            ocol = list(thisptr[bycol_bequity_src])
            ncol = list(ocol)
            for i in range(len(ocol)):
                ncol[i] = npdf["on"].iloc[npdfs.index(ocol[i])]
            thisptr_new = thisptr.copy()
            thisptr_new[bycol_on] = ncol
            ndict[k] = thisptr_new
            
        return ndict
    bequity_tmind_exc = ap_matchadd(
        bequity_tmind,
        sizes_dup_rmduped,
        bycol_bequity_src = "StkID",
        bycol_sizes_src = "PERMCO",
        bycol_on = "PRIMEXCH")
    # save_as(bequity_tmind_exc , data_sav + "\\bequity_tmind_exc.pickle")
    
    # STOCK INDEXED - YEARLY DATA (TO COMPUTE THOSE LISTED FOR 2 YEARS)
    bequity_stkind = hml.collect_stkindexed_sheets(
        use = bequity_matched_clr_bm,
        rmrows = None,
        bycol_stkid = "StkID",
        bycol_datetime = "Matched_YearAs",
        datetime_as = "Matched_YearAs")
    # save_as(bequity_stkind , data_sav + "\\bequity_stkind.pickle")
    
    # COMPUTE THE FIRST VALID YEAR FOR A STOCK TO BE INCLUDED IN THE TEST
    def gr_1stvalidyr(_stkindexed:dict, *,
        bycol_yearas,
        yearas_type = int,
        startrow = 1,
        nonevalue = 10010) -> dict:
        
        vyeardict = {}
        for k in _stkindexed.keys():
            if len(_stkindexed[k][bycol_yearas]) < (startrow + 1):
                vyeardict[k] = nonevalue
            else:
                ls = list(_stkindexed[k][bycol_yearas])
                ls.sort()
                vyeardict[k] = yearas_type(ls[startrow])
        return vyeardict
    bequity_1stvalyr = gr_1stvalidyr(
        _stkindexed = bequity_stkind,
        bycol_yearas = "Matched_YearAs",
        yearas_type = float)
    bequity_1stvalyr = dictvalues_astype(bequity_1stvalyr, int, type_intern = float)
    # save_as(bequity_1stvalyr , data_sav + "\\bequity_1stvalyr.pickle")
    
    # MAKE GROUPING IN EACH YEAR
    bequity_grouped = hml.groupby_factors(
        use = bequity_tmind_exc,
        rmrows = None,
        bycol_factors = ["Matched_MktValue", "Matched_B2MValue"],
        bycol_factor_spliton = ["PRIMEXCH", None],
        bycol_factor_spchosen = [["N"],[]],
        bycol_factor_nameas = [["S","B"], ["L","M","H"]],
        groups = [2, 3],
        method = "on",
        on = "Matched_MktValue",
        allocs = [[0.5, 0.5], [0.3, 0.4, 0.3]],
        fstyr = bequity_1stvalyr,
        bycol_factor_fstyr = "Matched_YearAs",
        bycol_factor_stkid = "StkID",
        fstyrcmp_type = float,
        nonename_as = "NaG")
    # save_as(bequity_grouped , data_sav + "\\bequity_grouped.pickle")
    
    # CREATE THE TIME SERIES OF THE MONTHLY STOCK RETURN
    xts = timeseries(list(set(sizes_dup_rmduped["date"].astype(str))),
        refresh_month = 7)
    xts = xts.sort_values("YearMonth")
    # save_as(xts , data_sav + "\\xts.pickle")
    xts_sel = xts.iloc[24:(len(xts)),:]
    # save_as(xts_sel , data_sav + "\\xts_sel.pickle")
    
    # GENERATE THE MONTHLY RETURNS OF GROUPS
    grped_monthly_ret = hml.collect_monthly_returns(
        use = bequity_grouped[1],
        rmrows = None,
        tmref = xts_sel, 
        retref = sizes_stkind,
        bycol_use_stkid = "StkID",
        bycol_use_group = "JointGroup",
        bycol_use_weight = "InGroupWeight",
        bycol_retref_datetime = "DateTime",
        bycol_retref_return = "RET",
        groupnames = ['_Matched_MktValue_B_Matched_B2MValue_H',
         '_Matched_MktValue_B_Matched_B2MValue_L',
         '_Matched_MktValue_B_Matched_B2MValue_M',
         '_Matched_MktValue_S_Matched_B2MValue_H',
         '_Matched_MktValue_S_Matched_B2MValue_L',
         '_Matched_MktValue_S_Matched_B2MValue_M'],
        reweights = False)
    # save_as(grped_monthly_ret , data_sav + "\\grped_monthly_ret.pickle")
    grped_monthly_retneo = dictkeys_newnames(
        dict_ = grped_monthly_ret,
        new_keys = ['BH', 'BL', 'BM',
                    'SH', 'SL', 'SM'])
    # save_as(grped_monthly_retneo , data_sav + "\\grped_monthly_retneo.pickle")
    
    # BUILDING UP THE SMB AND HML FACTORS
    _ret_SL = grped_monthly_retneo['SL'][["YearMonth", "Returns"]]
    _ret_SM = grped_monthly_retneo['SM'][["YearMonth", "Returns"]]
    _ret_SH = grped_monthly_retneo['SH'][["YearMonth", "Returns"]]
    _ret_BL = grped_monthly_retneo['BL'][["YearMonth", "Returns"]]
    _ret_BM = grped_monthly_retneo['BM'][["YearMonth", "Returns"]]
    _ret_BH = grped_monthly_retneo['BH'][["YearMonth", "Returns"]]
    # save_as(_ret_SL , data_sav + "\\_ret_SL.pickle")
    # save_as(_ret_SM , data_sav + "\\_ret_SM.pickle")
    # save_as(_ret_SH , data_sav + "\\_ret_SH.pickle")
    # save_as(_ret_BL , data_sav + "\\_ret_BL.pickle")
    # save_as(_ret_BM , data_sav + "\\_ret_BM.pickle")
    # save_as(_ret_BH , data_sav + "\\_ret_BH.pickle")
    _fact_SGROUP = np.multiply(
        np.add(np.add(_ret_SL["Returns"], _ret_SM["Returns"]), _ret_SH["Returns"]), 1.0/3)
    _fact_BGROUP = np.multiply(
        np.add(np.add(_ret_BL["Returns"], _ret_BM["Returns"]), _ret_BH["Returns"]), 1.0/3)
    _fact_SMB = np.subtract(_fact_SGROUP, _fact_BGROUP)
    _fact_SMB[_fact_SMB.isin([0.0]) == True] = np.nan
    # save_as(_fact_SMB , data_sav + "\\_fact_SMB.pickle")
    _fact_HGROUP = np.multiply(
        np.add(_ret_SH["Returns"], _ret_BH["Returns"]), 1.0/2)
    _fact_LGROUP = np.multiply(
        np.add(_ret_SL["Returns"], _ret_BL["Returns"]), 1.0/2)
    _fact_HML = np.subtract(_fact_HGROUP, _fact_LGROUP)
    _fact_HML[_fact_HML.isin([0.0]) == True] = np.nan
    # save_as(_fact_HML , data_sav + "\\_fact_HML.pickle")
    
    # (GLOBAL STOCKS) TIME INDEXED - MONTHLY DATA
    sizes_all_tmind = smb.collect_timeindexed_sheets(
        use = sizes_dup2_valshrcd,
        rmrows = None,
        bycol_datetime = "date", 
        bycol_stkid = "PERMCO",
        datetime_as = "date",
        datetime_type = str)
    # save_as(sizes_all_tmind , data_sav + "\\sizes_all_tmind.pickle")
    
    # (GLOBAL STOCKS) TIME INDEXED AVERAGE RETURNS - MONTHLY DATA
    mktret = smb.collect_weighton(
        use = sizes_all_tmind,
        rmrows = None,
        bycol_toweighton = "MktValue",
        bycol_tovalueon = "RET",
        toweighton_as = "MktValue",
        tovalueon_as = "Return")
    # save_as(mktret , data_sav + "\\mktret.pickle")
    
    # GET THE MARKET AVERAGED RETURN FOR EACH MONTH AS A DATAFRAME
    s_mktret = plainize(mktret[0], 
        kname = "DateTime",
        vname = "Return")
    s_mktret = s_mktret.sort_values(by = "DateTime")
    s_mktret = sapplyon(s_mktret, "DateTime", lambda x:x[0:7])
    # save_as(s_mktret , data_sav + "\\s_mktret.pickle")
    
    # COMBINE THE RISK-FREE AND MARKET RETURN INTO ONE DATAFRAME
    s_mktrsk = matchon(s_rf, s_mktret, on = "DateTime", how = "inner")
    s_mktrsk["PREMIUM"] = np.subtract(s_mktrsk["Return"], s_mktrsk["RF"])
    # save_as(s_mktrsk , data_sav + "\\s_mktrsk.pickle")
    s_mktrsk_sel = s_mktrsk.iloc[24:540,:]
    # save_as(s_mktrsk_sel , data_sav + "\\s_mktrsk_sel.pickle")
    
    # APPEND THREE FACTORS TOGETHER
    s_mktrsk_3fact = s_mktrsk_sel.copy()
    s_mktrsk_3fact["SMB"] = list(_fact_SMB).copy()  # a list is a must, to ignore indices
    s_mktrsk_3fact["HML"] = list(_fact_HML).copy()  # a list is a must, to ignore indices
    # save_as(s_mktrsk_3fact , data_sav + "\\s_mktrsk_3fact.pickle")
    # s_mktrsk_3fact.to_excel(data_sav + "\\s_mktrsk_3fact.xlsx")
    
    # SAVE THE FINAL FF3 FACTORS INTO THE HARD DISK DRIVE
    if _g_sav_final == True:
        s_mktrsk_3fact.to_excel(data_sav + "\\s_mktrsk_3fact.xlsx")
        print("Factor Saved!")
    
    print("Finished!")

# End of this file