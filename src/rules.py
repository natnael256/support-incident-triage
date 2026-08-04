#This is for rules engine -> classify tickets by matching phrases against rules.yaml defined rules

import yaml

def load_rules(path):
    with open(path) as f:
        data = yaml.safe_load(f)
    rules = data.get("rules", [])

    if not rules:
        raise SystemExit(f"No rules found in {path}")
    return rules

def normalize(text):
    # Lowercase and collapse apostrophe variants so phrases match reliably.
    if not text:
        return ""
    return text.lower().replace("\u2019", "'")

def classify (ticket, rules):

    #return (severity , matched_ruled_name) for the first matching rule, or non in no match

    for rule in rules: 
        haystack = " ".join(
            normalize(ticket.get(field, "")) for field in rule["fields"]

        )
        for phrase in rule["any"]:
            if normalize(phrase) in haystack:
                return rule["severity"] , rule["name"]
    return None, None
