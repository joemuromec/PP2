import json

with open("Practice4\json\sample-data.json", "r") as file:
    data = json.load(file)
    print("Interface Status")
    print("================================================================================")
    print(f"{"DN":<50} {"Description":<21} {"Speed":8} {"MTU":<6}")
    print("-------------------------------------------------- --------------------  ------  ------")
    for item in data['imdata']:
        attributes = item['l1PhysIf']['attributes'] 
        dn = attributes.get('dn', '')
        desc = attributes.get('descr', '')
        speed = attributes.get('speed', '')
        mtu = attributes.get('mtu', '')
        print(f"{dn:<50} {desc:<21} {speed:8} {mtu:<6}")
     