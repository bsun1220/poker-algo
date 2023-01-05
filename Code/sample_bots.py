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

class StratPlayer(PokerBotTemplate):
    def initialize_strategy(self, state):
        cards = set()
        suits = {"Spade", "Diamond", "Heart", "Club"}
        numbers = {"2":0, "3":1, "4":2, "5":3, "6":4, "7":5, "8":6, "9":7, "10":8, "J":9, "Q":10, "K":11,"A":12}

        for number in numbers:
            for suit in suits:
                cards.add((suit, number))
        
        self.cards = cards
        self.has_raised = False
    
    def play(self, state):
        flop = set() if "flop" not in state else state["flop"]
        len_players = len(state["stack_size"])
        for action in state["game_history"]:
            if action[1] == "FoldAction":
                len_players -= 1
        
        villain_dict = {}
        for i in range(len_players):
            villain_dict[i] = {}
        
        hero = state["hand"]
        
        equity, __ = range_simulate(hero, villain_dict, flop, self.cards, 10000)
        
        if self.has_raised:
            bluff = random.random() > 0.5
            if bluff:
                return ("CheckAction", 0)
            else:
                if equity < 0.5:
                    return ("FoldAction", 0)
                return ("RaiseAction", min(state["stack_size"][self.name], 5 * state["min_raise"]))

        if state["prog"] == "Preflop":
            bluff = random.random() > 0.6
            if equity < 1/(len_players * 1.5) and not bluff:
                return ("FoldAction", 0)
            else:
                self.has_raised = True
                return ("RaiseAction", 2 * state["min_raise"])
        elif state["prog"] == "Postflop":
            if equity < state["call_amount"] / (state["pot"] + state["call_amount"]):
                return ("FoldAction", 0)
            else:
                return ("CheckAction", 0)
        elif state["prog"] == "Turn":
            if equity < state["call_amount"] / (state["pot"] + state["call_amount"]):
                return ("FoldAction", 0)
            else:
                self.has_raised = True
                return ("RaiseAction", state["min_raise"])
        elif state["prog"] == "River":
            return ("CheckAction", 0)
        else:
            print ("Fail")
        
        return ("CheckAction", 0)