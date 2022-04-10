import os
import json
import random

targetUserId = "157252176350150656"
minCharsTarget = 1
minCharsPrompt = 1

outputName = "example_target"

#completionName = "john"

openAiLines = []

for jsonFileName in os.listdir('input'):
    messagesById = {}

    try:
        os.chdir('input')
        f = open(jsonFileName, mode="r", encoding="utf-8")
        data = json.load(f)

        print("Loaded " + jsonFileName)

        for i in data["messages"]:
            messageId = i["id"]
            name = i["author"]["name"]
            content = i["content"].encode("ascii", "ignore").decode()

            if len(content) >= minCharsPrompt and content.count("\n") == 0:
                messagesById[messageId] = name + ": " + content
            else:
                messagesById[messageId] = ""

        for i in data["messages"]:
            content = i["content"].encode("ascii", "ignore").decode()
            userId = i["author"]["id"]
            msgType = i["type"]

            if msgType == "Reply" and userId == targetUserId and len(content) >= minCharsTarget and i["reference"] and content.count("\n") == 0:
                if i["reference"]["messageId"] in messagesById and len(messagesById[i["reference"]["messageId"]]) >= 1:
                    referenceMsg = messagesById[i["reference"]["messageId"]]

                    if not 'completionName' in vars():
                        completionName = i["author"]["name"]

                    if completionName != referenceMsg.split(": ")[0]:
                        prompt = referenceMsg + " -> " + completionName + ":"
                        completion = " " + content + "\n"
                        openAiLines.append({"prompt": prompt, "completion": completion})

    except:
        print("Couldn't process " + jsonFileName + " due to an error")
        os.chdir("../")
    else:
        os.chdir("../")
        

os.chdir("output")

with open(outputName + '.jsonl', 'w') as outputFile:
    for entry in openAiLines:
        json.dump(entry, outputFile)
        outputFile.write('\n')
