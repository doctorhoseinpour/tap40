import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
app = FastAPI()


class Mission:
    def __init__(self, msg: str , count: int =0 , time: float = 0 ):
        self.msg = msg
        self.count = count
        self.time = time
        self.award1 = award1
        self.award2 = award2

class MissionModel(BaseModel):
    pass

class Driver:
    def __init__(self, id: int, name: str,money: int, discount: int, missions: Mission = []):
        self.id = id
        self.name = name
        self.missions = missions
        self.money = money
        self.discount = discount




@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/all_missions")
def show_missions() -> List[MissionModel]:
    for mission in all_missions:
        m = MissionModel()#mission
        
if __name__ == "__main__":
    drivers = []
    all_missions = []
    uvicorn.run(app, host="0.0.0.0", port=8000)
