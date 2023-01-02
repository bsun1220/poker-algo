import numpy as np
import random
from poker_tools import range_simulate, hand_simulate, return_hand_winner
from poker_bot import PokerBotTemplate

class FishPlayer(PokerBotTemplate):
    def __init__(self, name):
        super().__init__(name)

class RaisePlayer(PokerBotTemplate):
    def __init__(self, name):
        super().__init__(name)
    
    def play(self, state):
        if state["stack_size"][self.name] < state["min_raise"]:
            return ("CheckAction", state["call_amount"])
        
        return ("RaiseAction", state["min_raise"])

class CheckOrFoldPlayer(PokerBotTemplate):
    def __init__(self, name):
        super().__init__(name)
    
    def play(self, state):
        check = random.random() > 0.5
        if check:
            return ("CheckAction", 0)
        return ("FoldAction", 0)