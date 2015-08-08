import delimited "/Users/alexandersax/Google Drive/Side Projects/lol_analysis/data/kills.csv", clear
merge m:1 matchid using "/Users/alexandersax/Google Drive/Side Projects/lol_analysis/data/matches.dta"

gen kill_min = floor(timestamp/60000)
gen kills = 1
replace matchduration = floor(matchduration/60)
replace timetoitem0 = floor(timetoitem0/60/1000)
replace timetoitem1 = floor(timetoitem1/60/1000)
replace timetoitem2 = floor(timetoitem2/60/1000)
replace timetoitem3 = floor(timetoitem3/60/1000)

//keep if participantchampion == "evelynn" & lane=="JUNGLE"
keep if killerteamwinner==1

//preserve

// Create an observation with 0 kills to mark beginning of match
bysort matchid: gen firstexampleofmatch = (_n==1)
expand 2 if firstexampleofmatch==1, gen(dup)
replace kill_min = 0 if dup==1
replace kills = 0 if dup==1


// Create another observation with 0 kills to mark end of match
drop dup
bysort matchid: replace firstexampleofmatch = (_n==1)
expand 2 if firstexampleofmatch==1, gen(dup) 
replace kill_min = matchduration if dup==1
replace kills = 0 if dup==1


gen mykill  = participantid == killerid & kills == 1
gen mydeath  = (participantid == victimid & kills == 1)

// Assume everyone contributes equally and award a portion of the kill
gen kill_participation = (participantid == killerid | assist==1 & kills == 1)/(1 + n_assists)
gen bool_kill_participation  = (kill_participation > 0)

// Collapse by kill_min
collapse (sum) kills mykill mydeath (first) matchduration ///
	(sum) kill_participation bool_kill_participation ///
	(first) timetoitem0 timetoitem1 timetoitem2 timetoitem3 ///
	, by(kill_min matchid)

// Fill in timeseries info
sort matchid kill_min
tsset matchid kill_min
tsfill
replace kills = 0 if matchduration == .
replace mydeath = 0 if matchduration == .
replace mykill = 0 if matchduration == .
replace kill_participation = 0 if matchduration == .

// Now collapse by matchid
collapse (sum) totalkills=kills (mean) avgkills=kills (sd) sdkills=kills ///
	(sum) totalmydeaths=mydeath (mean) avgmydeaths=mydeath (sd) sdmydeaths=mydeath ///
	(sum) totalmykills=mykill (mean) avgmykills=mykill (sd) sdmykills=mykill ///
	(sum) totalkillpart=kill_participation (mean) avgkillpart=kill_participation (sd) sdkillpart=kill_participation ///
	(mean) avgboolkillpart=bool_kill_participation ///
	(mean) timetoitem0 timetoitem1 timetoitem2 timetoitem3 ///
	(count) activematches=matchid ///
	, by(kill_min)

rename kill_min min
//serrbar avgkills sdkills min, scale (1.96) 
tsset min
tssmooth ma smoothmykills=avgmykills, window(1 1 1)
label var smoothmykills "my kills/min"

tssmooth ma smoothkillpart=avgkillpart, window(1 1 1)
label var smoothkillpart "kill participation/min"

tssmooth ma smoothboolkillpart=avgboolkillpart, window(1 1 1)
label var smoothboolkillpart "kills participated in/min"

tssmooth ma smoothmydeaths=avgmydeaths, window(1 1 1)
label var smoothmydeaths "my deaths/min"

gen killpowerratio = smoothmykills/smoothmydeaths
gen powerratio = smoothboolkillpart/smoothmydeaths
twoway tsline avgkills
//twoway tsline smoothboolkillpart smoothmydeaths

//restore
//preserve

//collapse (sum) kills, by(position_x position_y)
