import delimited "/Users/alexandersax/Google Drive/Side Projects/lol_analysis/data/teams.csv", clear
merge m:1 matchid using "/Users/alexandersax/Google Drive/Side Projects/lol_analysis/data/matches.dta"

gen earlydragon=firstdragontime < 10*60*1000
xi: regress winner i.earlydragon*firstdragon

regress winner firstbaron
regress winner firstinhib
