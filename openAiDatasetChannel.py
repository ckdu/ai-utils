import os
import json
import random

#yearToSave = "2021"
maxFractionUsersPerRank = 1
messagesPerUser = 1
blacklistedIds = ["4321", "1234"]
openAiLines = []
outputName = "example_channel"

for jsonFileName in os.listdir('input'):
    messagesPerId = {}

    os.chdir('input')
    f = open(jsonFileName, mode="r", encoding="utf-8")
    data = json.load(f)
    
    print("Loaded " + jsonFileName)

    completion = " " + os.path.splitext(jsonFileName)[0]

    for i in data["messages"]:
        content = i["content"].encode("ascii", "ignore").decode()
        userId = i["author"]["id"]
        isBot = i["author"]["isBot"]

        if not isBot and content and not userId in blacklistedIds: #and i["timestamp"][:4] == yearToSave:
            if not content[:1] == "!" and not content[:1] == "?" and not content[:1] == "," and not "!val" in content and not "http" in content:
                if userId in messagesPerId:
                    messagesPerId[userId].append(content)
                else:
                    messagesPerId[userId] = [content]

    selectUsers = []
    
    for id, messages in messagesPerId.items():
        #if len(messages) >= 13:
            selectUsers.append(messages)
        
    maxUsers = int(len(selectUsers) * maxFractionUsersPerRank)
    selectUsers = random.sample(selectUsers, maxUsers)

    for i in range(len(selectUsers)):
        selectUsers[i] = random.sample(selectUsers[i], messagesPerUser)
    
    for i in range(len(selectUsers)):
        prompt = ""
        
        for message in selectUsers[i]:
            prompt += message + "\n"

        prompt += "\n###\n\n"
        
        openAiLines.append({"prompt": prompt, "completion": completion})

    os.chdir("../")

os.chdir("output")

random.shuffle(openAiLines)

with open(outputName + '.jsonl', 'w') as outputFile:
    for entry in openAiLines:
        json.dump(entry, outputFile)
        outputFile.write('\n')

