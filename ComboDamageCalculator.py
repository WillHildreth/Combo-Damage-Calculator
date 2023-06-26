import json
from math import floor

playerCharFile = "./CharacterStats/Neco&Mech.json"
enemyCharFile = "./CharacterStats/v.sion.json"
comboScript = "./ComboScripts/cnm_2a5k.combo"

with open(playerCharFile) as jsonData:
    playerCharData = json.load(jsonData)
#print(playerCharData["5[c]"])

with open(enemyCharFile) as jsonData:
    enemyCharData = json.load(jsonData)

with open(comboScript) as scriptData:
    comboData = scriptData.readline()


currMod = 1.0
currCorr = 1.0
currHit = 0
currRevBeat = 0
currDamage = 0
currBracket = "100"

for token in comboData.split(' '):
    match token.lower():
        case "stand":
            currMod = 1.0
            print("Set Stance: Stand\n")
        case "crouch":
            currMod = 1.08
            print("Set Stance: Crouch\n")
        case "jump":
            currMod = 0.88
            print("Set Stance: Jump\n")

        case "otg":
            currCorr *= 0.6
            print("OTG Penalty Applied\n")

        case "rebeat":
            currRevBeat = min(currRevBeat + 0.35, 0.55)
            print("Reverse Beat Penalty Applied\n")

        case _:
            subTokens = token.replace(')','').split('(')
            moveName = subTokens[0]
            hitRangeStart = 1       # default values 
            hitRangeEnd = 999       #
            if len(subTokens) > 1:      # if there is something in parethesis
                hitRangeTokens = subTokens.split(':')
                hitRangeEnd = hitRangeTokens[0]
                if len(hitRangeTokens) > 1:     # if a colon is used to denote start:end
                    hitRangeStart = hitRangeTokens[0]
                    hitRangeEnd = hitRangeTokens[1]

            print(token, hitRangeStart, hitRangeEnd)
                    
            for i in range(hitRangeStart, hitRangeEnd):
                print(moveName)
                break
                
                #
                # Damage Calculation
                #

                hitIndex = 1
                while True:       # count up to the hit we're on
                    if playerCharData[moveName][hitIndex]["hitsOn"] + playerCharData[moveName][hitIndex]["maxHits"] >= i:
                        break
                    hitIndex += 1
                    
                    
                newDamage = playerCharData[moveName][hitIndex]["damage"]           # raw damage
                newDamage *= max(32.0-currHit,1)/32.0                       # adjust for hitcount
                newDamage *= currMod                                        # adjust for stand/jump/crouch
                newDamage *= currCorr                                       # adjust for correction value
                newDamage *= enemyCharData["health"][0][currBracket]        # adjust for current health bracket
                newDamage = floor(newDamage)                                # round final number down


                #
                # Update Combo State
                #

                # add the damage
                currDamage += newDamage

                # increase the combo counter
                currHit += 1

                # adjust correction value if necessary
                if playerCharData[moveName][hitIndex]["prorationType"] == "o":
                    newCorr = min(playerCharData[moveName][hitIndex]["prorationVal"], currCorr)
                    if newCorr != currCorr:
                        print("Correction Value Adjusted (O):", str(currCorr), "->", str(newCorr))
                        currCorr = newCorr
                elif playerCharData[moveName][hitIndex]["prorationType"] == "m":
                    newCorr = currCorr * playerCharData[moveName][0]["prorationVal"]
                    print("Correction Value Adjusted (M):", str(currCorr), "->", str(newCorr))
                    currCorr = newCorr

                # adjust health bracket if necessary
                if currDamage > 2855:
                    currBracket = "75"
                if currDamage > 5710:
                    currBracket = "50"
                if currDamage > 8565:
                    currBracket = "25"
                

                print("Raw Damage:", str(playerCharData[moveName][hitIndex]["damage"]))
                print("True Damage:", str(newDamage))
                print("Combo Damage:", str(currDamage), "\n")

                if i + 1 >= playerCharData[moveName][0]["maxHits"]:
                    break
