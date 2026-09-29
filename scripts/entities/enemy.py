from scripts.config import PINK
from scripts.entities.fighter import Fighter
from scripts.ai.brain import Brain


class Enemy(Fighter):
    def __init__(self,position):
        super().__init__(position,PINK)
        self.facing=-1
        self.state="observar"
        self.brain=Brain()

    def decide(self,dt,player,drop,platforms):
        self.brain.decide(self,dt,player,drop,platforms)
