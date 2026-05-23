import json

with open("data/logs.json", "r") as file:
    logs = json.load(file)

error_logs = [log for log in logs if log["level"] == "ERROR"]

print(error_logs)