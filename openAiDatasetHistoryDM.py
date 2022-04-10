import os
import json
import random

promptUserId = "157252176350150656"
maxTimeBetweenMessagesMin = 15
percentKeep = 1
blacklist = ["bad", "words", "here"]
whitelist = ["hi", "hello", "sup", "hey", "gm", "yo"]
outputName = "example_dm_history"

openAiLines = []

for jsonFileName in os.listdir('input'):
    os.chdir('input')
    f = open(jsonFileName, mode="r", encoding="utf-8")
    data = json.load(f)

    print("Loaded " + jsonFileName)

    def diff(current, previous):
        return (((int(current) >> 22) - (int(previous) >> 22)) / 60000) <= maxTimeBetweenMessagesMin 

    prompt = ""
    completion = " "
    previousId = ""
    previousMsgId = ""

    for i in data["messages"]:
        content = i["content"].encode("ascii", "ignore").decode()
        userId = i["author"]["id"]
        msgId = i["id"]
        msgType = i["type"]

        if msgType == "Default" or msgType == "Reply":
            # when it's Q's first message
            if userId == promptUserId and previousId == "":
                prompt = "Q:\n" + content
                previousId = userId
                previousMsgId = msgId

            # when it's Q again and in short interval
            elif userId == promptUserId and userId == previousId and diff(msgId, previousMsgId):
                prompt += "\n" + content
                previousId = userId
                previousMsgId = msgId

            # when it's Q again but it's been a long time
            elif userId == promptUserId and userId == previousId and not diff(msgId, previousMsgId):
                prompt = "Q:\n" + content
                previousId = userId
                previousMsgId = msgId

            # when it's A again and in short interval
            elif userId != promptUserId and userId == previousId and diff(msgId, previousMsgId):
                completion += "\n" + content
                previousId = userId
                previousMsgId = msgId

            # when it's A again but it's been a long time
            elif userId != promptUserId and userId == previousId and not diff(msgId, previousMsgId):
                previousId = ""
                previousMsgId = ""

            # when it changes from A to Q and in short interval
            elif userId == promptUserId and userId != previousId and previousId != "" and diff(msgId, previousMsgId):
                openAiLines.append({"prompt": prompt + "\n", "completion": completion})
                prompt += "\n" + completion + "\n\nQ:\n" + content
                previousId = userId
                previousMsgId = msgId

            # when it changes from A to Q but it's been a long time
            elif userId == promptUserId and userId != previousId and previousId != "" and not diff(msgId, previousMsgId):
                openAiLines.append({"prompt": prompt + "\n", "completion": completion})
                prompt = "Q:\n" + content
                completion = " "
                previousId = userId
                previousMsgId = msgId

            # when it changes from Q to A and in short interval
            elif userId != promptUserId and userId != previousId and previousId != "" and diff(msgId, previousMsgId):
                completion = "\nA:\n" + content
                previousId = userId
                previousMsgId = msgId

            # when it changes from Q to A but it's been a long time
            elif userId != promptUserId and userId != previousId and previousId != "" and not diff(msgId, previousMsgId):
                previousId = ""
                previousMsgId = ""

    os.chdir("../")

previousPrompt = ""
openAiCommonLines = [[]]
j = 0

for entry in openAiLines:
    currentPrompt = entry["prompt"]
    
    if previousPrompt == "":
        previousPrompt = currentPrompt

    if currentPrompt[:len(previousPrompt)] == previousPrompt[:len(previousPrompt)]:
        openAiCommonLines[j].append(entry)
    else:
        j += 1
        openAiCommonLines.append([entry])

    previousPrompt = currentPrompt

openAiCommonLines = random.sample(openAiCommonLines, int(percentKeep * len(openAiCommonLines)))

os.chdir("output")

line = 1
with open(outputName + '.jsonl', 'w') as outputFile:
    for entry in openAiCommonLines:
        fp = entry[0]["prompt"]
        if len(fp) > 9 or (bool([wl for wl in whitelist if(wl in fp.lower())])):
            if not (bool([bl for bl in blacklist if(bl in str(entry).lower())])):
                for secondEntry in entry:
                    json.dump(secondEntry, outputFile)
                    outputFile.write('\n')
                    line += 1
