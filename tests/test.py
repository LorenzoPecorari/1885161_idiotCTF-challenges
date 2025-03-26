import requests

base_url = "http://localhost:5000"

def create_chal():
    data = {
        "title": "chal del cazzo",
        "description": "è proprio una chal del cazzo, vedi qui",
        "flag":"ctf{chaldelcazzo}",
        "points": 50,
        "contest_id": 1,
        "category": "stego"
    }
    print(requests.post(base_url+"/challenges", json=data).text)

def all_chals():
     return requests.get(base_url+"/challenges?contest_id=1").json()

def get_chal():
    return requests.get(base_url+"/challenges/1").json()

def put_chal(d):
    return requests.put(base_url+"/challenges/1", json=d).json()

def delete_chal():
    return requests.delete(base_url+"/challenges/1").json()

create_chal()
c = get_chal()
print(c)
#print(c)
#c["data"]["objects"][0]["title"] = "titolow weee"
#c["data"]["objects"][0]["points"] = 1
#print(put_chal(c["data"]["objects"][0]))
#print(get_chal())
#print(delete_chal())
#print(get_chal())
print(all_chals())

