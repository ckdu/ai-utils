import json
import os
import hickle as hkl
import numpy as np

oneOutput = False

f = open("input.json", mode="r", encoding="utf-8")

data = json.load(f)
f.close()

messagesPerId = {}

for i in data["messages"]:
    content = i["content"].encode()
    userId = i["author"]["id"]
    isBot = i["author"]["isBot"]

    if not isBot and content:
        if userId in messagesPerId:
            messagesPerId[userId].append(content)
        else:
            messagesPerId[userId] = [content]

os.chdir('output')

if oneOutput:
    npMessages = np.array(messagesPerId)
    hkl.dump(npMessages, "output.hkl", mode='w', compression='gzip')
    
    data = hkl.load("output.hkl")
    print(data)

else:
    for id, messages in messagesPerId.items():
        npMessages = np.array(messages)
        fileName = id + ".hkl"
        
        hkl.dump(npMessages, fileName, mode='w', compression='gzip')
        
        data = hkl.load(fileName)
        print(data)
