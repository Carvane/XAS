import json

PATH_DATA = "data/agent.json"             

def createAgent(
        nameAgent: str,
        model: str | None = None,
        instruction: str | None = None,
        enablePosting: bool | None = None,
        imageGeneration: bool | None = None,
        conversationId: int | None = None,
        algorithm: str | None = None,
        maxPostAgeHours: int | None = None,
        minElo: int | None = None,
        calculateEloVersion: int | None = None,
    ):

    with open(PATH_DATA, "r", encoding="utf-8") as file:
        agents = json.load(file)

    if nameAgent not in agents:
        agents[nameAgent] = {
            "config": {
                "model": model,
                "instruction": instruction,
                "enablePosting": enablePosting,
                "imageGeneration": imageGeneration,
                "conversationId": conversationId,
                "searchOptions": {
                    "algorithm": algorithm,
                    "maxPostAgeHours": maxPostAgeHours,
                    "minElo": minElo,
                    "calculateEloVersion": calculateEloVersion,
                    "monitoredAccounts": f"ma/{nameAgent}.json",
                    "processedPostIds": f"psi/{nameAgent}.json"
                }
            },
            "secret": f".secret/{nameAgent}.json"
        }

        with open(PATH_DATA, "w", encoding="utf-8") as file:
            json.dump(agents, file, indent=4, ensure_ascii=False)

    else:
        print(f'Agent "{nameAgent}" already exists.')

def updateAgent(
        nameAgent: str,
        model: str | None = None,
        instruction: str | None = None,
        enablePosting: bool | None = None,
        imageGeneration: bool | None = None,
        conversationId: int | None = None,
        algorithm: str | None = None,
        maxPostAgeHours: int | None = None,
        minElo: int | None = None,
        calculateEloVersion: int | None = None,
    ):
    
        with open(PATH_DATA, "r", encoding="utf-8") as file:
            agents = json.load(file)

        if nameAgent in agents:
            config = agents[nameAgent]["config"]
            searchOptions = config["searchOptions"]

            configUpdates = {
                "model": model,
                "instruction": instruction,
                "enablePosting": enablePosting,
                "imageGeneration": imageGeneration,
                "conversationId": conversationId
            }

            searchUpdates = {
                "algorithm": algorithm,
                "maxPostAgeHours": maxPostAgeHours,
                "minElo": minElo,
                "calculateEloVersion": calculateEloVersion
            }

            for key, value in configUpdates.items():
                if value is not None:
                    config[key] = value

            for key, value in searchUpdates.items():
                if value is not None:
                    searchOptions[key] = value

            with open(PATH_DATA, "w", encoding="utf-8") as file:
                json.dump(agents, file, indent=4, ensure_ascii=False)

        else:
            print(f'Agent "{nameAgent}" does not exist.')

def getAgents(PATH: str):
    with open(PATH, "r", encoding="utf-8") as file:
        agents = json.load(file)

    return agents
    


#createAgent("testowy")
updateAgent(nameAgent="testowy", algorithm="latest")