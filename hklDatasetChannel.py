import json
import os
import hickle as hkl
import numpy as np

for jsonFileName in os.listdir('input'):
    rank = jsonFileName.split(".")[0]

    #yearToSave = "2021"

    hklFileName = rank + ".hkl"

    os.chdir('input')
    f = open(jsonFileName, mode="r", encoding="utf-8")

    data = json.load(f)
    f.close()
    os.chdir('../')

    messagesPerId = {}
    rankObjects = []

    blacklistedIds = ["4321", "1234"]
    for i in data["messages"]:
        content = i["content"].encode("ascii", "ignore").decode()
        userId = i["author"]["id"]
        isBot = i["author"]["isBot"]

        if not isBot and content and not userId in blacklistedIds:
            if not content[:1] == "!" and not content[:1] == "?" and not content[:1] == ",":
                #if i["timestamp"][:4] == yearToSave:
                    if userId in messagesPerId:
                        messagesPerId[userId] += " " +  content
                    else:
                        messagesPerId[userId] = content

    # print(len(messagesPerId))

    for id, messages in messagesPerId.items():
        rankObjects.append({"rank": rank, "messages": messages})

    os.chdir('output')

    npMessages = np.array(rankObjects)
    hkl.dump(npMessages, hklFileName, mode='w', compression='gzip')

    #loaded = hkl.load(hklFileName).tolist()
    #print(loaded[0])

    os.chdir('../')
