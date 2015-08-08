import delimited "/Users/alexandersax/Google Drive/Side Projects/lol_analysis/data/lanes.csv", clear

// Shorten variable names
ren *_zerototen *_0_10
ren *_tentotwenty *_10_20
ren *_twentytothirty *_20_30
ren *_thirtytoend *_30_end

// Differences in lane
ren csdiffpermindeltas_* csdiffpm_* 
ren damagetakendiffpermindeltas_* dmgdiffpm_*
ren xpdiffpermindeltas_* xpdiffpm_*
ren golddiffpermin_* gdiffpm_*

// Raw amounts
ren damagetakenpermindeltas_* dmgpm_*
ren goldpermindeltas_* gpm_*
ren xppermindeltas_* xppm_*
ren creepspermindeltas_* cspm_*


// In case some originally got cut off
ren *_zer* *_0_10
ren *_ten* *_10_20
ren *_twe* *_20_30
ren *_thi* *_30_end


order *, alpha
//hist golddiffpermin_zerototen
replace gdiffpm_0_10 = round(gdiffpm_0_10/30)

gen killdiferential = killsatten + assistsatten -deathsatten
gen xpkill = abs(xpdiffpm_0_10)*killdiferential
gen goldkill = abs(gdiffpm_0_10)*killdiferential

local winlane "killsatten deathsatten assistsatten csdiffpm_0_10 xpdiffpm_0_10 gdiffpm_0_10"

// All pass the linktest
logit winner `winlane' if role=="SOLO" & lane=="TOP"
//linktest, nolog

logit winner `winlane' if role=="SOLO" & lane=="MIDDLE"
//linktest, nolog

logit winner `winlane' if role=="NONE" & lane=="JUNGLE"
//linktest, nolog

local carrywinlane "csdiffpm_0_10"
logit winner `winlane' if role=="DUO_CARRY" & lane=="BOTTOM"
//linktest, nolog
local supportwinlane "deathsatten assistsatten gdiffpm_0_10 "
logit winner `supportwinlane' if role=="DUO_SUPPORT" & lane=="BOTTOM"
//linktest, nolog


replace lane = "BOT" if lane == "BOTTOM"
replace lane = "JG" if lane == "JUNGLE"
replace lane = "MID" if lane == "MIDDLE"
replace role = "" if role == "NONE" | role == "SOLO"
replace role = "CARRY" if role == "DUO_CARRY"
replace role = "SUPPORT" if role == "DUO_SUPPORT"

gen lane_role = lane+role
gen matchid_team = string(matchid,"%13.0g") + "_" + string(team)
quietly: ds
local reshapedvars = "`r(varlist)'"
local reshapedvars : subinstr local reshapedvars "lane_role" ""
local reshapedvars : subinstr local reshapedvars "matchid_team" ""
local reshapedvars : subinstr local reshapedvars "winner" ""
di "`reshapedvars'"
quietly: reshape wide `reshapedvars' , i(matchid_team) j(lane_role) string
gen teamgolddiff = gdiffpm_0_10BOTSUPPORT + gdiffpm_0_10BOTCARRY ///
					+ gdiffpm_0_10MID + gdiffpm_0_10TOP ///
					+ gdiffpm_0_10JG 
// Stepwise feature selection controlling for team gold
//stepwise, pe(.1) forward : logit winner killsattenBOTSUPPORT  deathsattenBOTSUPPORT assistsattenBOTSUPPORT csdiffpm_0_10BOTSUPPORT xpdiffpm_0_10BOTSUPPORT gdiffpm_0_10BOTSUPPORT teamgolddiff
//stepwise, pe(.1) forward : logit winner killsattenBOTCARRY  deathsattenBOTCARRY assistsattenBOTCARRY csdiffpm_0_10BOTCARRY xpdiffpm_0_10BOTCARRY gdiffpm_0_10BOTCARRY teamgolddiff
//stepwise, pe(.1) forward : logit winner killsattenMID  deathsattenMID assistsattenMID csdiffpm_0_10MID xpdiffpm_0_10MID gdiffpm_0_10MID teamgolddiff
//stepwise, pe(.1) forward : logit winner killsattenTOP  deathsattenTOP assistsattenTOP csdiffpm_0_10TOP xpdiffpm_0_10TOP gdiffpm_0_10TOP teamgolddiff
//stepwise, pe(.1) forward : logit winner killsattenJG  deathsattenJG assistsattenJG csdiffpm_0_10JG xpdiffpm_0_10JG gdiffpm_0_10JG teamgolddiff

// Basic (by hand) analysis finds that these variables are significant
probit winner ///
		deathsattenBOTSUPPORT ///
		xpdiffpm_0_10MID ///
		gdiffpm_0_10TOP ///
		csdiffpm_0_10JG ///
		teamgolddiff

probit winner ///
		gdiffpm_0_10TOP  ///
		gdiffpm_0_10MID ///
		gdiffpm_0_10JG ///
		gdiffpm_0_10BOTCARRY ///
		gdiffpm_0_10BOTSUPPORT
		
// They predict the correct outcome 88% of the time
predict predicted
lfit, group(10) tab // Quite good!
gen residuals =  winner - predicted
gen correct = (residuals < 0.5)
summarize correct


//But team gold predicts the correct outcome almost as well
//probit winner teamgolddiff
//drop predicted residuals correct
// They predict the correct outcome 84% of the time
//predict predicted
//lfit, group(10) tab // VERY good!
//gen residuals =  winner - predicted
//gen correct = (residuals < 0.5)
//summarize correct

//preserve
//replace xpdiffpm_0_10MID = round(xpdiffpm_0_10MID/20)
//collapse winner, by(xpdiffpm_0_10MID)
//twoway bar winner xpdiffpm_0_10MID 
//restore

