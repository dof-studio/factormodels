# FF3_BoxuanAnalysis_Improved.py
# This is the main executable file to analysis results obtained from FF3
#

import os as os
import numpy as np
import pandas as pd
import scipy as sp

from FF3_Utilities import pd_plainize
from FF3_Utilities import matchon
from FF3_Utilities import dapply
from FF3_Utilities import pdapply
from FF3_Utilities import grpname_to_ndpairs
from FF3_Utilities import df_fprintf
from FF3_Utilities import ErrorCode

from FF3_FactorBuilding import FactorSMB
from FF3_FactorBuilding import FactorHML
from FF3_FactorBuilding import FactorUtils

from FF3_ReturnAnalysis import GroupedAnalysis

###############################################################################
#
# Reliability!
# > The codes in this file tightly rely on variables generated through the
#   process of building up the replicated Fama French Three Factors.
#   Therefore, it is not only a recommendation but a must to priorly execute
#   all lines of codes within the main function of the BoxuanImpl_Improved.py.

###############################################################################
#
# Important!
# > The following paths should be properly set, and all of the directories
#   should be existed, empty ones.
# > Please set the global parameters based on your requirement. 
#   Unlike the BoxuanImpl_Improved.py, in this file, temporary variables
#   are extremely small in terms of size, therefore it not necessary to
#   rush to remove them out from the memory.
#   As a result, the parameter _g_low_memory is not activated here.
#   [Param] _g_sav_final:  Setting True to obtain the final FF3 factors
#   [Param] _g_low_memory: Setting True to remove some unused variable to control the memory use

alalysis_sav = r"C:\Users\happy\Desktop\资产定价\Project\Data\alalysis"

# Class Initialization
smb = FactorSMB()
hml = FactorHML()
grp = GroupedAnalysis()

# Global Parameters
_g_sav_final = True
_g_low_memory = True

# Program Entry Point (main function)
if __name__ == "__main__":
    
    ###############################################################################
    #
    # TO BE ANALYZED DATA'S PREPARATION
    #
        
    # MAKE A 5 TIMES 5 GROUP MAP IN EACH YEAR
    bequity_grouped_25 = hml.groupby_factors(
        use = bequity_tmind_exc,
        rmrows = None,
        bycol_factors = ["Matched_MktValue", "Matched_B2MValue"],
        bycol_factor_spliton = ["PRIMEXCH", None],
        bycol_factor_spchosen = [["N"],[]],
        bycol_factor_nameas = [["SIZE_L1","SIZE_L2","SIZE_L3","SIZE_L4","SIZE_L5"],
                               ["BEME_L1","BEME_L2","BEME_L3","BEME_L4","BEME_L5"]],
        groups = [5, 5],
        method = "on",
        on = "Matched_MktValue",
        allocs = [[0.2,0.2,0.2,0.2,0.2],
                  [0.2,0.2,0.2,0.2,0.2]],
        fstyr = bequity_1stvalyr,
        bycol_factor_fstyr = "Matched_YearAs",
        bycol_factor_stkid = "StkID",
        fstyrcmp_type = float,
        nonename_as = "NaG")
    # save_as(bequity_grouped_25 , alalysis_sav + "\\bequity_grouped_25.pickle")
    
    # GENERATE THE GROUPNAMES USED AND THE PAIRS OF INDICES
    groupnames = list(set(bequity_grouped_25[1][1980]["JointGroup"]))
    groupnames.sort()
    groupnames = groupnames[0:25]
    # save_as(groupnames , alalysis_sav + "\\groupnames.pickle")
    grouppairs = grpname_to_ndpairs(groupnames)
    group_g2p = grouppairs[0]
    group_p2g = grouppairs[1]
    # save_as(grouppairs , alalysis_sav + "\\grouppairs.pickle")
    
    # GENERATE THE MONTHLY RETURNS OF GROUPS
    grped_monthly_25_ret = hml.collect_monthly_returns(
        use = bequity_grouped_25[1],
        rmrows = None,
        tmref = xts_sel, 
        retref = sizes_stkind,
        bycol_use_stkid = "StkID",
        bycol_use_group = "JointGroup",
        bycol_use_weight = "InGroupWeight",
        bycol_retref_datetime = "DateTime",
        bycol_retref_return = "RET",
        returnas = "Returns",
        groupnames = groupnames,
        reweights = False)
    # save_as(grped_monthly_25_ret , alalysis_sav + "\\grped_monthly_25_ret.pickle")
    
    # DELETE THE SAMPLES OF THE FIRST 6 MONTHS OF 1980
    def dict_truncrows(dict_:dict[pd.DataFrame], first_ = 6) -> dict[pd.DataFrame]:
        neo_dict = {}
        for k in dict_.keys():
            len_ = len(dict_[k])
            neo_dict[k] = dict_[k].iloc[(first_):(len_),:].copy()
        return neo_dict
    grped_monthly_25_ret_trunc = dict_truncrows(
        grped_monthly_25_ret,
        first_ = 6)
    # save_as(grped_monthly_25_ret_trunc , alalysis_sav + "\\grped_monthly_25_ret_trunc.pickle")
    
    # SPLIT THE RETURN SAMPLES INTO TO FRAMES ACCORDING TO ITS TIME STAMP
    def dict_splitbytime(dict_:dict[pd.DataFrame], bycol_time, bytime = [],
                         *, timeastype = str, sort = True) -> list[dict[pd.DataFrame]]:
        if len(bytime) == 0:
            raise ErrorCode("Invalid parameter \\bytime\\! A list of strings should have length greater than 0!")
        bytime.sort()
        for k in dict_.keys():
            if bycol_time not in dict_[k].columns:
                raise ErrorCode("Invalid column name in the var \\bycol_time\\!")
        
        dict_copy = dict_.copy()
        if sort == True:
            for k in dict_copy.keys():
                dict_copy[k] = dict_copy[k].sort_values(bycol_time)
        
        retlist = []
        startpos = 0
        endpos = 0
        for i in range(len(bytime)):
            if i == len(bytime) - 1:
                break
            tmpdict = {}
            for k in dict_copy.keys():
                lst = list(dict_copy[k][bycol_time].astype(timeastype))
                startpos = lst.index(bytime[i])
                endpos = lst.index(bytime[i + 1])
                tmpdict[k] = dict_copy[k].iloc[(startpos):(endpos + 1),:].copy()
            
            retlist.append(tmpdict)
        
        return retlist
    grped_monthly_25_twogrps = dict_splitbytime(
        grped_monthly_25_ret_trunc,
        bycol_time = "YearMonth",
        bytime = ["1980-07","2000-12", "2020-12"],
        sort = False)
    grped_monthly_25_ret_early = grped_monthly_25_twogrps[0]
    grped_monthly_25_ret_later = grped_monthly_25_twogrps[1]
    # save_as(grped_monthly_25_twogrps , alalysis_sav + "\\grped_monthly_25_twogrps.pickle")
    # save_as(grped_monthly_25_ret_early , alalysis_sav + "\\grped_monthly_25_ret_early.pickle")
    # save_as(grped_monthly_25_ret_later , alalysis_sav + "\\grped_monthly_25_ret_later.pickle")
    
    # GET THE PREMIUM OF THE 25 RETURNS IN EACH TIME SPAN
    def ap_rename_dt(data, iname = "YearMonth", oname = "DateTime"):
        data[oname] = data[iname].copy()
        return data
    grped_monthly_25_ret_early_i = dapply(
        dict_ = grped_monthly_25_ret_early.copy(),
        func = ap_rename_dt)
    grped_monthly_25_ret_later_i = dapply(
        dict_ = grped_monthly_25_ret_later.copy(),
        func = ap_rename_dt)
    def ap_premium_at(data, timeref = s_rf, on = "DateTime", how = "inner",
                      retname = "Returns", rfname = "RF", newname = "PortPremium"):
        tmp = matchon(data, timeref, on = on, how = how)
        tmp[newname] = np.subtract(tmp[retname], tmp[rfname])
        return tmp
    grped_monthly_25_prem_early = dapply(
        dict_ = grped_monthly_25_ret_early,
        func = ap_premium_at)
    grped_monthly_25_prem_later = dapply(
        dict_ = grped_monthly_25_ret_later,
        func = ap_premium_at)
    # save_as(grped_monthly_25_prem_early , alalysis_sav + "\\grped_monthly_25_prem_early.pickle")
    # save_as(grped_monthly_25_prem_later , alalysis_sav + "\\grped_monthly_25_prem_later.pickle")
    
    # CONSTRUCT [MARKET_PREMIUM, SMB, HML] INTO THE DICT
    def ap_3factors_at(data, thrfact = s_mktrsk_3fact, on = "DateTime", how = "inner"):
        tmp = matchon(data, thrfact, on = on, how = how)
        return tmp
    grped_monthly_25_allfact_early = dapply(
        dict_ = grped_monthly_25_prem_early,
        func = ap_3factors_at)
    grped_monthly_25_allfact_later = dapply(
        dict_ = grped_monthly_25_prem_later,
        func = ap_3factors_at)
    # save_as(grped_monthly_25_allfact_early , alalysis_sav + "\\grped_monthly_25_allfact_early.pickle")
    # save_as(grped_monthly_25_allfact_later , alalysis_sav + "\\grped_monthly_25_allfact_later.pickle")
    
    # GENERATE THE MONTHLY MARKET VALUE OF GROUPS
    grped_monthly_25_mktval = hml.collect_monthly_returns(
        use = bequity_grouped_25[1],
        rmrows = None,
        tmref = xts_sel, 
        retref = sizes_stkind,
        bycol_use_stkid = "StkID",
        bycol_use_group = "JointGroup",
        bycol_use_weight = "InGroupWeight",
        bycol_retref_datetime = "DateTime",
        bycol_retref_return = "MktValue",
        returnas = "MarketValue",
        groupnames = groupnames,
        reweights = False)
    # save_as(grped_monthly_25_mktval , alalysis_sav + "\\grped_monthly_25_mktval.pickle")
    
    # DELETE THE SAMPLES OF THE FIRST 6 MONTHS OF 1980
    grped_monthly_25_mktval_trunc = dict_truncrows(
        grped_monthly_25_mktval,
        first_ = 6)
    # save_as(grped_monthly_25_mktval_trunc , alalysis_sav + "\\grped_monthly_25_mktval_trunc.pickle")
    
    # SPLIT THE NUMBER SAMPLES INTO TO FRAMES ACCORDING TO ITS TIME STAMP
    grped_monthly_25_mktval_twogrps = dict_splitbytime(
        grped_monthly_25_mktval_trunc,
        bycol_time = "YearMonth",
        bytime = ["1980-07","2000-12", "2020-12"],
        timeastype = str,
        sort = True)
    grped_monthly_25_mktval_early = grped_monthly_25_mktval_twogrps[0]
    grped_monthly_25_mktval_later = grped_monthly_25_mktval_twogrps[1]
    # save_as(grped_monthly_25_mktval_twogrps , alalysis_sav + "\\grped_monthly_25_mktval_twogrps.pickle")
    # save_as(grped_monthly_25_mktval_early , alalysis_sav + "\\grped_monthly_25_mktval_early.pickle")
    # save_as(grped_monthly_25_mktval_later , alalysis_sav + "\\grped_monthly_25_mktval_later.pickle")
    
    # GENERATE THE FIRM NUMBER IN EACH GROUP IN EACH YEAR
    grped_monthly_25_num = hml.collect_annually_firmnums(
        use = bequity_grouped_25[1],
        rmrows = None,
        bycol_use_group = "JointGroup",
        groupnames = groupnames)
    # save_as(grped_monthly_25_num , alalysis_sav + "\\grped_monthly_25_num.pickle")
    
    # SPLIT THE NUMBER SAMPLES INTO TO FRAMES ACCORDING TO ITS TIME STAMP
    grped_monthly_25_num_twogrps = dict_splitbytime(
        grped_monthly_25_num,
        bycol_time = "DateTime",
        bytime = ["1980", "2000", "2020"],
        timeastype = str,
        sort = True)
    grped_monthly_25_num_early = grped_monthly_25_num_twogrps[0]
    grped_monthly_25_num_later = grped_monthly_25_num_twogrps[1]
    # save_as(grped_monthly_25_num_twogrps , alalysis_sav + "\\grped_monthly_25_num_twogrps.pickle")
    # save_as(grped_monthly_25_num_early , alalysis_sav + "\\grped_monthly_25_num_early.pickle")
    # save_as(grped_monthly_25_num_later , alalysis_sav + "\\grped_monthly_25_num_later.pickle")
    
    ###############################################################################
    #
    # DATA ANALYSIS AND ILLUSTRATION
    #
    
    # Q1: REPORT IN-GROUP MARKET VALUE AND FIRM NUMBERS
    da_ingroup_mktvalue_early = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_mktval_early,
            rmrows = None,
            bycol_staton = "MarketValue",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x))))],
            stat_nameas = ["Mean", "SD", "Median", "t-val"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_mktvalue_early, 2)
    # save_as(da_ingroup_mktvalue_early , alalysis_sav + "\\da_ingroup_mktvalue_early.pickle")
    
    da_ingroup_mktvalue_later = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_mktval_later,
            rmrows = None,
            bycol_staton = "MarketValue",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x))))],
            stat_nameas = ["Mean", "SD", "Median", "t-val"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_mktvalue_later, 2)
    # save_as(da_ingroup_mktvalue_later , alalysis_sav + "\\da_ingroup_mktvalue_later.pickle")
    
    da_ingroup_num_early = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_num_early,
            rmrows = None,
            bycol_staton = "Numbers",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x))))],
            stat_nameas = ["Mean", "SD", "Median", "t-val"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_num_early, 2)
    # save_as(da_ingroup_num_early , alalysis_sav + "\\da_ingroup_num_early.pickle")
    
    da_ingroup_num_later = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_num_later,
            rmrows = None,
            bycol_staton = "Numbers",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x))))],
            stat_nameas = ["Mean", "SD", "Median", "t-val"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_num_later, 2)
    # save_as(da_ingroup_num_later , alalysis_sav + "\\da_ingroup_num_later.pickle")
    
    # Q1: REPORT MEAN AND STD DEVIATION TABLE
    da_ingroup_return_mean_early = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_early,
            rmrows = None,
            bycol_staton = "PortPremium",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x)))),
                         lambda x: sp.stats.skew(x)],
            stat_nameas = ["Mean", "SD", "Median", "t-val", "Skew"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 100.0)
    df_fprintf(da_ingroup_return_mean_early, 2)
    # save_as(da_ingroup_return_mean_early , alalysis_sav + "\\da_ingroup_return_mean_early.pickle")
    
    da_ingroup_return_sd_early = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_early,
            rmrows = None,
            bycol_staton = "PortPremium",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x)))),
                         lambda x: sp.stats.skew(x)],
            stat_nameas = ["Mean", "SD", "Median", "t-val", "Skew"]),
        stat_key = "SD",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 100.0)
    df_fprintf(da_ingroup_return_sd_early, 2)
    # save_as(da_ingroup_return_sd_early , alalysis_sav + "\\da_ingroup_return_sd_early.pickle")
    
    da_ingroup_return_tval_early = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_early,
            rmrows = None,
            bycol_staton = "PortPremium",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x)))),
                         lambda x: sp.stats.skew(x)],
            stat_nameas = ["Mean", "SD", "Median", "t-val", "Skew"]),
        stat_key = "t-val",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_return_tval_early, 2)
    # save_as(da_ingroup_return_tval_early , alalysis_sav + "\\da_ingroup_return_tval_early.pickle")
    
    da_ingroup_return_skew_early = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_early,
            rmrows = None,
            bycol_staton = "PortPremium",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x)))),
                         lambda x: sp.stats.skew(x)],
            stat_nameas = ["Mean", "SD", "Median", "t-val", "Skew"]),
        stat_key = "Skew",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_return_skew_early, 2)
    # save_as(da_ingroup_return_skew_early , alalysis_sav + "\\da_ingroup_return_skew_early.pickle")
    
    da_ingroup_return_mean_later = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_later,
            rmrows = None,
            bycol_staton = "PortPremium",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x)))),
                         lambda x: sp.stats.skew(x)],
            stat_nameas = ["Mean", "SD", "Median", "t-val", "Skew"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 100.0)
    df_fprintf(da_ingroup_return_mean_later, 2)
    # save_as(da_ingroup_return_mean_later , alalysis_sav + "\\da_ingroup_return_mean_later.pickle")
    
    da_ingroup_return_sd_later = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_later,
            rmrows = None,
            bycol_staton = "PortPremium",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x)))),
                         lambda x: sp.stats.skew(x)],
            stat_nameas = ["Mean", "SD", "Median", "t-val", "Skew"]),
        stat_key = "SD",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 100.0)
    df_fprintf(da_ingroup_return_sd_later, 2)
    # save_as(da_ingroup_return_sd_later , alalysis_sav + "\\da_ingroup_return_sd_later.pickle")
    
    da_ingroup_return_tval_later = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_later,
            rmrows = None,
            bycol_staton = "PortPremium",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x)))),
                         lambda x: sp.stats.skew(x)],
            stat_nameas = ["Mean", "SD", "Median", "t-val", "Skew"]),
        stat_key = "t-val",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_return_tval_later, 2)
    # save_as(da_ingroup_return_tval_later , alalysis_sav + "\\da_ingroup_return_tval_later.pickle")
    
    da_ingroup_return_skew_later = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_later,
            rmrows = None,
            bycol_staton = "PortPremium",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x)))),
                         lambda x: sp.stats.skew(x)],
            stat_nameas = ["Mean", "SD", "Median", "t-val", "Skew"]),
        stat_key = "Skew",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_return_skew_later, 2)
    # save_as(da_ingroup_return_skew_later , alalysis_sav + "\\da_ingroup_return_skew_later.pickle")
    
    # Q1: REPORT CAPM REGRESSION RESULT
    ols_capm_early = grp.grouped_olsstat(
        use = grped_monthly_25_allfact_early,
        rmrows = None,
        bycol_x = ["PREMIUM"],
        bycol_y = "PortPremium",
        stat_nameas = ["coef", "serr", "t-val", "p-val", "r2", "r2_adjusted", "mse_resid", "f-val"])
    ols_capm_result_early, ols_capm_orig_early = ols_capm_early
    # save_as(ols_capm_early , alalysis_sav + "\\ols_capm_early.pickle")
    # save_as(ols_capm_result_early , alalysis_sav + "\\ols_capm_result_early.pickle")
    # save_as(ols_capm_orig_early , alalysis_sav + "\\ols_capm_orig_early.pickle")
    
    ols_capm_later = grp.grouped_olsstat(
        use = grped_monthly_25_allfact_later,
        rmrows = None,
        bycol_x = ["PREMIUM"],
        bycol_y = "PortPremium",
        stat_nameas = ["coef", "serr", "t-val", "p-val", "r2", "r2_adjusted", "mse_resid", "f-val"])
    ols_capm_result_later, ols_capm_orig_later = ols_capm_later
    # save_as(ols_capm_later , alalysis_sav + "\\ols_capm_later.pickle")
    # save_as(ols_capm_result_later , alalysis_sav + "\\ols_capm_result_later.pickle")
    # save_as(ols_capm_orig_later , alalysis_sav + "\\ols_capm_orig_later.pickle")
    
    da_ingroup_capmreg_coef_b_early = pdapply(grp.grouped_panelillust(
        use = ols_capm_result_early,
        stat_key = "coef_PREMIUM",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_capmreg_coef_b_early, 2)
    # save_as(da_ingroup_capmreg_coef_b_early , alalysis_sav + "\\da_ingroup_capmreg_coef_b_early.pickle")
    
    da_ingroup_capmreg_tval_b_early = pdapply(grp.grouped_panelillust(
        use = ols_capm_result_early,
        stat_key = "t-val_PREMIUM",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_capmreg_tval_b_early, 2)
    # save_as(da_ingroup_capmreg_tval_b_early , alalysis_sav + "\\da_ingroup_capmreg_tval_b_early.pickle")
    
    da_ingroup_capmreg_coef_b_later = pdapply(grp.grouped_panelillust(
        use = ols_capm_result_later,
        stat_key = "coef_PREMIUM",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_capmreg_coef_b_later, 2)
    # save_as(da_ingroup_capmreg_coef_b_later , alalysis_sav + "\\da_ingroup_capmreg_coef_b_later.pickle")
    
    da_ingroup_capmreg_tval_b_later = pdapply(grp.grouped_panelillust(
        use = ols_capm_result_later,
        stat_key = "t-val_PREMIUM",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_capmreg_tval_b_later, 2)
    # save_as(da_ingroup_capmreg_tval_b_later , alalysis_sav + "\\da_ingroup_capmreg_tval_b_later.pickle")
    
    # Q1: REPORT FAMA FRENCH THREE FACTOR'S REGRESSION RESULT
    ols_tup_early = grp.grouped_olsstat(
        use = grped_monthly_25_allfact_early,
        rmrows = None,
        bycol_x = ["PREMIUM", "SMB", "HML"],
        bycol_y = "PortPremium",
        stat_nameas = ["coef", "serr", "t-val", "p-val", "r2", "r2_adjusted", "mse_resid", "f-val"])
    ols_result_early, ols_orig_early = ols_tup_early
    # save_as(ols_tup_early , alalysis_sav + "\\ols_tup_early.pickle")
    # save_as(ols_result_early , alalysis_sav + "\\ols_result_early.pickle")
    # save_as(ols_orig_early , alalysis_sav + "\\ols_orig_early.pickle")
    
    ols_tup_later = grp.grouped_olsstat(
        use = grped_monthly_25_allfact_later,
        rmrows = None,
        bycol_x = ["PREMIUM", "SMB", "HML"],
        bycol_y = "PortPremium",
        stat_nameas = ["coef", "serr", "t-val", "p-val", "r2", "r2_adjusted", "mse_resid", "f-val"])
    ols_result_later, ols_orig_later = ols_tup_later
    # save_as(ols_tup_later , alalysis_sav + "\\ols_tup_later.pickle")
    # save_as(ols_result_later , alalysis_sav + "\\ols_result_later.pickle")
    # save_as(ols_orig_later , alalysis_sav + "\\ols_orig_later.pickle")
    
    def depanel(panel:pd.DataFrame, sequence = 0, *, astype = float):
        '''
        Function 'depanel' makes a panel data frame into a sequentual list.
        [param] sequence: 0, meaning by using row sequence.
        [param] sequence: 1, meaning by using column sequence.
        '''
        df = panel.copy()
        df.astype(astype)
        
        ls = rep(astype(), len(df.index) * len(df.columns))
        if sequence == 0:
            for i in range(len(df.index)):
                for j in range(len(df.columns)):
                    ls[i * len(df.columns) + j] = df.iloc[i,j]
        elif sequence == 1:
            for j in range(len(df.columns)):
                for i in range(len(df.index)):
                    ls[j * len(df.index) + i] = df.iloc[i,j]
        else:
            raise ErrorCode("Input parameter \\sequence\\ could only be either 0 or 1!")
            
        return ls
    
    def degrouped(dict_:dict, *, grouptag = "GroupName"):
        d = {}
        if type(dict_) != type({}):
            raise ErrorCode("The input variable \\dict_\\ must be a dict indexed by its group names!")
        for k in dict_.keys():
            if type(dict_[k]) != type(pd.DataFrame()):
                raise ErrorCode("The input dict's each page must be a pandas DataFrame!")
            tmp = dict_[k].copy()
            tmp[grouptag] = k
            d[k] = tmp
        keys = list(d.keys())
        keys.sort()
        df = d[keys[0]]
        for i in range(1, len(keys)):
            df = pd.concat([df, d[keys[i]]])
        return df
    
    degrped_monthly_25_allfact_early = degrouped(grped_monthly_25_allfact_early)
    degrped_monthly_25_allfact_later = degrouped(grped_monthly_25_allfact_later)
    # save_as(degrped_monthly_25_allfact_early , alalysis_sav + "\\degrped_monthly_25_allfact_early")
    # save_as(degrped_monthly_25_allfact_later , alalysis_sav + "\\degrped_monthly_25_allfact_later")
    
    ols_tup_degrouped_early = grp.grouped_olsstat(
        use = {"All":degrped_monthly_25_allfact_early},
        rmrows = None,
        bycol_x = ["PREMIUM", "SMB", "HML"],
        bycol_y = "PortPremium",
        stat_nameas = ["coef", "serr", "t-val", "p-val", "r2", "r2_adjusted", "mse_resid", "f-val"])
    ols_result_degrouped_early, ols_orig_degrouped_early = ols_tup_degrouped_early
    # save_as(ols_tup_degrouped_early , alalysis_sav + "\\ols_tup_degrouped_early .pickle")
    # save_as(ols_result_degrouped_early , alalysis_sav + "\\ols_result_degrouped_early.pickle")
    # save_as(ols_orig_degrouped_early , alalysis_sav + "\\ols_orig_degrouped_early.pickle")
    
    ols_tup_degrouped_later = grp.grouped_olsstat(
        use = {"All":degrped_monthly_25_allfact_later},
        rmrows = None,
        bycol_x = ["PREMIUM", "SMB", "HML"],
        bycol_y = "PortPremium",
        stat_nameas = ["coef", "serr", "t-val", "p-val", "r2", "r2_adjusted", "mse_resid", "f-val"])
    ols_result_degrouped_later, ols_orig_degrouped_later = ols_tup_degrouped_later
    # save_as(ols_tup_degrouped_later , alalysis_sav + "\\ols_tup_degrouped_later .pickle")
    # save_as(ols_result_degrouped_later , alalysis_sav + "\\ols_result_degrouped_later.pickle")
    # save_as(ols_orig_degrouped_later , alalysis_sav + "\\ols_orig_degrouped_later.pickle")
    
    da_ingroup_reg_coef_b_early = pdapply(grp.grouped_panelillust(
        use = ols_result_early,
        stat_key = "coef_PREMIUM",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_coef_b_early, 2)
    # save_as(da_ingroup_reg_coef_b_early , alalysis_sav + "\\da_ingroup_reg_coef_b_early.pickle")
    
    da_ingroup_reg_tval_b_early = pdapply(grp.grouped_panelillust(
        use = ols_result_early,
        stat_key = "t-val_PREMIUM",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_tval_b_early, 2)
    # save_as(da_ingroup_reg_tval_b_early , alalysis_sav + "\\da_ingroup_reg_tval_b_early.pickle")
    
    da_ingroup_reg_coef_s_early = pdapply(grp.grouped_panelillust(
        use = ols_result_early,
        stat_key = "coef_SMB",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_coef_s_early, 2)
    # save_as(da_ingroup_reg_coef_s_early , alalysis_sav + "\\da_ingroup_reg_coef_s_early.pickle")
    
    da_ingroup_reg_tval_s_early = pdapply(grp.grouped_panelillust(
        use = ols_result_early,
        stat_key = "t-val_SMB",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_tval_s_early, 2)
    # save_as(da_ingroup_reg_tval_s_early , alalysis_sav + "\\da_ingroup_reg_tval_s_early.pickle")
    
    da_ingroup_reg_coef_h_early = pdapply(grp.grouped_panelillust(
        use = ols_result_early,
        stat_key = "coef_HML",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_coef_h_early, 2)
    # save_as(da_ingroup_reg_coef_h_early , alalysis_sav + "\\da_ingroup_reg_coef_h_early.pickle")
    
    da_ingroup_reg_tval_h_early = pdapply(grp.grouped_panelillust(
        use = ols_result_early,
        stat_key = "t-val_HML",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_tval_h_early, 2)
    # save_as(da_ingroup_reg_tval_h_early , alalysis_sav + "\\da_ingroup_reg_tval_h_early.pickle")
    
    da_ingroup_reg_r2_early = pdapply(grp.grouped_panelillust(
        use = ols_result_early,
        stat_key = "r2",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_r2_early, 2)
    # save_as(da_ingroup_reg_r2_early , alalysis_sav + "\\da_ingroup_reg_r2_early.pickle")
    
    da_ingroup_reg_se_early = pdapply(grp.grouped_panelillust(
        use = ols_result_early,
        stat_key = "mse_resid",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: np.sqrt(x) * 100)
    df_fprintf(da_ingroup_reg_se_early, 2)
    # save_as(da_ingroup_reg_se_early , alalysis_sav + "\\da_ingroup_reg_se_early.pickle")
    
    da_ingroup_reg_coef_b_later = pdapply(grp.grouped_panelillust(
        use = ols_result_later,
        stat_key = "coef_PREMIUM",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_coef_b_later, 2)
    # save_as(da_ingroup_reg_coef_b_later , alalysis_sav + "\\da_ingroup_reg_coef_b_later.pickle")
    
    da_ingroup_reg_tval_b_later = pdapply(grp.grouped_panelillust(
        use = ols_result_later,
        stat_key = "t-val_PREMIUM",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_tval_b_later, 2)
    # save_as(da_ingroup_reg_tval_b_later , alalysis_sav + "\\da_ingroup_reg_tval_b_later.pickle")
    
    da_ingroup_reg_coef_s_later = pdapply(grp.grouped_panelillust(
        use = ols_result_later,
        stat_key = "coef_SMB",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_coef_s_later, 2)
    # save_as(da_ingroup_reg_coef_s_later , alalysis_sav + "\\da_ingroup_reg_coef_s_later.pickle")
    
    da_ingroup_reg_tval_s_later = pdapply(grp.grouped_panelillust(
        use = ols_result_later,
        stat_key = "t-val_SMB",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_tval_s_later, 2)
    # save_as(da_ingroup_reg_tval_s_later , alalysis_sav + "\\da_ingroup_reg_tval_s_later.pickle")
    
    da_ingroup_reg_coef_h_later = pdapply(grp.grouped_panelillust(
        use = ols_result_later,
        stat_key = "coef_HML",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_coef_h_later, 2)
    # save_as(da_ingroup_reg_coef_h_later , alalysis_sav + "\\da_ingroup_reg_coef_h_later.pickle")
    
    da_ingroup_reg_tval_h_later = pdapply(grp.grouped_panelillust(
        use = ols_result_later,
        stat_key = "t-val_HML",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_tval_h_later, 2)
    # save_as(da_ingroup_reg_tval_h_later , alalysis_sav + "\\da_ingroup_reg_tval_h_later.pickle")
    
    da_ingroup_reg_r2_later = pdapply(grp.grouped_panelillust(
        use = ols_result_later,
        stat_key = "r2",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 1.0)
    df_fprintf(da_ingroup_reg_r2_later, 2)
    # save_as(da_ingroup_reg_r2_later , alalysis_sav + "\\da_ingroup_reg_r2_later.pickle")
    
    da_ingroup_reg_se_later = pdapply(grp.grouped_panelillust(
        use = ols_result_later,
        stat_key = "mse_resid",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: np.sqrt(x) * 100)
    df_fprintf(da_ingroup_reg_se_later, 2)
    # save_as(da_ingroup_reg_se_later , alalysis_sav + "\\da_ingroup_reg_se_later.pickle")
    
    # Q1: AGGREGATED PORTFOLIO'S BETAS AND THEIR RETURNS
    def df_colmean(data:pd.DataFrame) -> pd.DataFrame:
        neodf = data.iloc[0:1,:].copy()
        neodf.index = ["Mean"]
        for i in range(len(data.columns)):
            neodf.iloc[0, i] = np.mean(data.iloc[:,i])
        return neodf
    def df_colapply(data:pd.DataFrame, func, *, indname = "Applied", astype = None) -> pd.DataFrame:
        neodf = data.iloc[0:1,:].copy()
        neodf.index = [indname]
        if astype is None:
            for i in range(len(data.columns)):
                neodf.iloc[0, i] = func(data.iloc[:,i])
        else:
            for i in range(len(data.columns)):
                neodf.iloc[0, i] = func(astype(data.iloc[:,i]))
            
        return neodf
    
    # BM RATIO CONTROLED
    da_beta_df_colmean_early = df_colmean(da_ingroup_return_mean_early)
    da_beta_df_colmean_later = df_colmean(da_ingroup_return_mean_later)
    # save_as(da_beta_df_colmean_early , alalysis_sav + "\\da_beta_df_colmean_early.pickle")
    # save_as(da_beta_df_colmean_later , alalysis_sav + "\\da_beta_df_colmean_later.pickle")
    
    def df_rowmean(data:pd.DataFrame) -> pd.DataFrame:
        neodf = data.iloc[:,0:1].copy()
        neodf.columns = ["Mean"]
        for i in range(len(data.index)):
            neodf.iloc[i, 0] = np.mean(data.iloc[i,:])
        return neodf
    def df_rowapply(data:pd.DataFrame, func, *, indname = "Applied", astype = None) -> pd.DataFrame:
        neodf = data.iloc[:,0:1].copy()
        neodf.columns = [indname]
        if astype is None:
            for i in range(len(data.index)):
                neodf.iloc[i, 0] = func(data.iloc[i,:])
        else:
            for i in range(len(data.index)):
                neodf.iloc[i, 0] = func(astype(data.iloc[i,:]))
            
        return neodf
    
    # SIZE CONTROLED
    da_size_df_rowmean_early = df_rowmean(da_ingroup_return_mean_early)
    da_size_df_rowmean_later = df_rowmean(da_ingroup_return_mean_later)
    # save_as(da_size_df_rowmean_early , alalysis_sav + "\\da_size_df_rowmean_early.pickle")
    # save_as(da_size_df_rowmean_later , alalysis_sav + "\\da_size_df_rowmean_later.pickle")
    
    def pd_multiply(data:pd.DataFrame, y) -> pd.DataFrame:
        
        neodf = data.copy()
        if type(y) == type(float()) or type(y) == type(int()):
            for i in range(len(data.index)):
                for j in range(len(data.columns)):
                    neodf.iloc[i, j] = neodf.iloc[i, j] * y
        elif type(y) == type(pd.DataFrame()):
            if len(data.index) != len(y.index):
                raise ErrorCode("Input \\y\\ should have the same dimension with \\data\\!")
            if len(data.columns) != len(y.columns):
                raise ErrorCode("Input \\y\\ should have the same dimension with \\data\\!")
            for i in range(len(data.index)):
                for j in range(len(data.columns)):
                    neodf.iloc[i, j] = neodf.iloc[i, j] * y.iloc[i, j]
        else:
            raise ErrorCode("Invalid type of \\y\\!")
        
        return neodf
    def pd_divide(data:pd.DataFrame, y) -> pd.DataFrame:
        
        neodf = data.copy()
        if type(y) == type(float()) or type(y) == type(int()):
            for i in range(len(data.index)):
                for j in range(len(data.columns)):
                    neodf.iloc[i, j] = neodf.iloc[i, j] / y
        elif type(y) == type(pd.DataFrame()):
            if len(data.index) != len(y.index):
                raise ErrorCode("Input \\y\\ should have the same dimension with \\data\\!")
            if len(data.columns) != len(y.columns):
                raise ErrorCode("Input \\y\\ should have the same dimension with \\data\\!")
            for i in range(len(data.index)):
                for j in range(len(data.columns)):
                    neodf.iloc[i, j] = neodf.iloc[i, j] / y.iloc[i, j]
        else:
            raise ErrorCode("Invalid type of \\y\\!")
        
        return neodf
    
    da_beta_mean_mkt_early = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_early,
            rmrows = None,
            bycol_staton = "PREMIUM",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x))))],
            stat_nameas = ["Mean", "SD", "Median", "t-val"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 100.0)
    da_beta_mean_mkt_later = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_later,
            rmrows = None,
            bycol_staton = "PREMIUM",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x))))],
            stat_nameas = ["Mean", "SD", "Median", "t-val"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 100.0)
    # save_as(da_beta_mean_mkt_early , alalysis_sav + "\\da_beta_mean_mkt_early.pickle")
    # save_as(da_beta_mean_mkt_later , alalysis_sav + "\\da_beta_mean_mkt_later.pickle")
    
    da_beta_mean_smb_early = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_early,
            rmrows = None,
            bycol_staton = "SMB",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x))))],
            stat_nameas = ["Mean", "SD", "Median", "t-val"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 100.0)
    da_beta_mean_smb_later = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_later,
            rmrows = None,
            bycol_staton = "SMB",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x))))],
            stat_nameas = ["Mean", "SD", "Median", "t-val"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 100.0)
    # save_as(da_beta_mean_smb_early , alalysis_sav + "\\da_beta_mean_smb_early.pickle")
    # save_as(da_beta_mean_smb_later , alalysis_sav + "\\da_beta_mean_smb_later.pickle")
    
    da_beta_mean_hml_early = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_early,
            rmrows = None,
            bycol_staton = "HML",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x))))],
            stat_nameas = ["Mean", "SD", "Median", "t-val"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 100.0)
    da_beta_mean_hml_later = pdapply(
        grp.grouped_panelillust(
        use = grp.grouped_stat(
            use = grped_monthly_25_allfact_later,
            rmrows = None,
            bycol_staton = "HML",
            stat_func = [np.mean, np.std, np.median, 
                         lambda x: np.divide(np.mean(x), np.divide(np.std(x), np.sqrt(len(x))))],
            stat_nameas = ["Mean", "SD", "Median", "t-val"]),
        stat_key = "Mean",
        g2pairs = group_g2p,
        g2pairs_names = ["Size", "BM-Ratio"]).T, lambda x: x * 100.0)
    # save_as(da_beta_mean_hml_early , alalysis_sav + "\\da_beta_mean_hml_early.pickle")
    # save_as(da_beta_mean_hml_later , alalysis_sav + "\\da_beta_mean_hml_later.pickle")
    
    da_beta_betaval_early = df_colmean(pd_multiply(da_ingroup_reg_coef_b_early, 
                1))
    da_beta_betaval_later = df_colmean(pd_multiply(da_ingroup_reg_coef_b_later, 
                1))
    da_beta_b_mkt_early = df_colmean(pd_multiply(da_ingroup_reg_coef_b_early, 
                da_beta_mean_mkt_early))
    da_beta_b_mkt_later = df_colmean(pd_multiply(da_ingroup_reg_coef_b_later, 
                da_beta_mean_mkt_later))
    da_beta_s_smb_early = df_colmean(pd_multiply(da_ingroup_reg_coef_s_early, 
                da_beta_mean_smb_early))
    da_beta_s_smb_later = df_colmean(pd_multiply(da_ingroup_reg_coef_s_later, 
                da_beta_mean_smb_later))
    da_beta_h_hml_early = df_colmean(pd_multiply(da_ingroup_reg_coef_h_early, 
                da_beta_mean_hml_early))
    da_beta_h_hml_later = df_colmean(pd_multiply(da_ingroup_reg_coef_h_later, 
                da_beta_mean_hml_later))
    da_beta_dataframe_early = pd.DataFrame({
        "R(t)" : list(da_beta_df_colmean_early.iloc[0,:]),
        "s*SMB(t)" : list(da_beta_s_smb_early.iloc[0,:]),
        "h*HML(t)" : list(da_beta_h_hml_early.iloc[0,:]),
        "b*MKT(t)" : list(da_beta_b_mkt_early.iloc[0,:]),
        "Beta" : list(da_beta_betaval_early.iloc[0,:])
        }).T
    da_beta_dataframe_later = pd.DataFrame({
        "R(t)" : list(da_beta_df_colmean_later.iloc[0,:]),
        "s*SMB(t)" : list(da_beta_s_smb_later.iloc[0,:]),
        "h*HML(t)" : list(da_beta_h_hml_later.iloc[0,:]),
        "b*MKT(t)" : list(da_beta_b_mkt_later.iloc[0,:]),
        "Beta" : list(da_beta_betaval_later.iloc[0,:])
        }).T
    df_fprintf(da_beta_dataframe_early, 2)
    df_fprintf(da_beta_dataframe_later, 2)
    # save_as(da_beta_dataframe_early , alalysis_sav + "\\da_beta_dataframe_early.pickle")
    # save_as(da_beta_dataframe_later , alalysis_sav + "\\da_beta_dataframe_later.pickle")
    
    da_size_betaval_early = df_rowmean(pd_multiply(da_ingroup_reg_coef_b_early, 
                1))
    da_size_betaval_later = df_rowmean(pd_multiply(da_ingroup_reg_coef_b_later, 
                1))
    da_size_b_mkt_early = df_rowmean(pd_multiply(da_ingroup_reg_coef_b_early, 
                da_beta_mean_mkt_early))
    da_size_b_mkt_later = df_rowmean(pd_multiply(da_ingroup_reg_coef_b_later, 
                da_beta_mean_mkt_later))
    da_size_s_smb_early = df_rowmean(pd_multiply(da_ingroup_reg_coef_s_early, 
                da_beta_mean_smb_early))
    da_size_s_smb_later = df_rowmean(pd_multiply(da_ingroup_reg_coef_s_later, 
                da_beta_mean_smb_later))
    da_size_h_hml_early = df_rowmean(pd_multiply(da_ingroup_reg_coef_h_early, 
                da_beta_mean_hml_early))
    da_size_h_hml_later = df_rowmean(pd_multiply(da_ingroup_reg_coef_h_later, 
                da_beta_mean_hml_later))
    da_size_dataframe_early = pd.DataFrame({
        "R(t)" : list(da_size_df_rowmean_early.iloc[:,0]),
        "s*SMB(t)" : list(da_size_s_smb_early.iloc[:,0]),
        "h*HML(t)" : list(da_size_h_hml_early.iloc[:,0]),
        "b*MKT(t)" : list(da_size_b_mkt_early.iloc[:,0]),
        "Beta" : list(da_size_betaval_early.iloc[:,0])
        }).T
    da_size_dataframe_later = pd.DataFrame({
        "R(t)" : list(da_size_df_rowmean_later.iloc[:,0]),
        "s*SMB(t)" : list(da_size_s_smb_later.iloc[:,0]),
        "h*HML(t)" : list(da_size_h_hml_later.iloc[:,0]),
        "b*MKT(t)" : list(da_size_b_mkt_later.iloc[:,0]),
        "Beta" : list(da_size_betaval_later.iloc[:,0])
        }).T
    df_fprintf(da_size_dataframe_early, 2)
    df_fprintf(da_size_dataframe_later, 2)
    # save_as(da_size_dataframe_early , alalysis_sav + "\\da_size_dataframe_early.pickle")
    # save_as(da_size_dataframe_later , alalysis_sav + "\\da_size_dataframe_later.pickle")
    
# End of this file