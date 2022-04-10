import os
import json

promptUserId = "157252176350150656"
outputName = "example_dm"

openAiLines = []

for jsonFileName in os.listdir('input'):
    os.chdir('input')
    jsonFileName = os.listdir()[0]
    f = open(jsonFileName, mode="r", encoding="utf-8")
    data = json.load(f)

    print("Loaded " + jsonFileName)

    prompt = ""
    completion = " "
    previousId = ""

    for i in data["messages"]:
        content = i["content"].encode("ascii", "ignore").decode()
        userId = i["author"]["id"]
        msgType = i["type"]
        

        if msgType == "Default" or msgType == "Reply":
            if userId == promptUserId and previousId == "":
                prompt = content
                previousId = userId
            elif userId == promptUserId and userId == previousId:
                prompt += "\n" + content
                previousId = userId
            elif userId != promptUserId and userId == previousId:
                completion += "\n" + content
                previousId = userId
            elif userId == promptUserId and userId != previousId and previousId != "":
                prompt += "\n\n###\n\n"
                openAiLines.append({"prompt": prompt, "completion": completion})
                prompt = content
                previousId = userId
            elif userId != promptUserId and userId != previousId and previousId != "":
                completion = content
                previousId = userId

    os.chdir("../")

os.chdir("output")

with open(outputName + '.jsonl', 'w') as outputFile:
    for entry in openAiLines:
        json.dump(entry, outputFile)
        outputFile.write('\n')
