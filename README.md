# Repo of `factormodels`
This repository includes a comprehensive library to conduct empirical asset pricing tasks specifically focus on financial factors. It is public for use now.

# How to use it?
Use classes and functions. The way to build factors has been generalized. Calling functions and methods is everything you are going to do. By leveraging our library, you can create whatever factors you want.

* To Create Factors: Derive your new class from the father class `__FactorBase__` in file `FF3_FactorBuilding.py` or modify sample classes `FactorSMB` and `FactorHML` to achieve similar functionalities.

* To Test Grouped Returns: Use the class `GroupedAnalysis` in file `FF3_ReturnAnalysis.py`, which provides three main computational tools `grouped_stat`, `grouped_panelillust`, `grouped_olsstat` that are all very useful in group analysis in asset pricing.

# What's inside?

#### Module Functions:

* src/`FF3_FactorBuilding.py`

* src/`FF3_ReturnAnalysis.py`

* src/`FF3_Utilities.py`

#### Example on FF3 Factors

* src/`FF3_BoxuanAnalysis_Improved.py`

* src/`FF3_BoxuanImpl_Improved.py`

#### Example Performance

* res/`FF3_Validation_with_Famas.xlsx`

# About the author
Nathmath from DOF Studio, on Aug 22, 2024.

Nathmath is/was a Master's student of NYU MSFE program.
