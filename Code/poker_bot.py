import numpy as np
import random
from poker_tools import range_simulate, hand_simulate, return_hand_winner

class PokerBotTemplate:
    def __init__(self, name):
        self.name = name
        self.saved_state = {}
        pass
    
    def initialize_strategy(self, state):
        pass
    
    def play(self, state):
        '''
        return tuple (Action, Amount)
        '''
        return ("CheckAction", state["call_amount"])