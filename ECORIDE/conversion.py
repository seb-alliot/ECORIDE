# conversion.py
with open("loadMsgs.json", "r", encoding="utf-16") as f:
    content = f.read()

with open("loadMsgs_utf8.json", "w", encoding="utf-8") as f:
    f.write(content)
