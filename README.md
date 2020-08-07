# Toontown-VP-After-Death
After the VP battle is over, the VP falls down into the SBHQ lobby for all Toons to see.

To get this working, simply drag the two Distributed files into the toontown/coghq folder of your Toontown source code. Make sure to hook them up to the dc file, spawn it in toontown/hood/CSHoodDataAI.py, optionally hook it up to a Magic Word, and finally hook the VP's "enterVictory" function in DistributedSellbotBossAI.py, and you're good to go!
