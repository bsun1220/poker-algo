import numpy as np
import random

class PokerGame:
    def __init__(self, max_players = 10, starting_pot = 1000, blinds = (5, 10)):
        
        assert(type(max_players) == int and max_players > 0 and max_players <= 10)
        assert(type(starting_pot) == int and starting_pot > 0)
        assert(len(blinds) == 2 and type(blinds[0]) == int and type(blinds[1]) == int)
        assert(blinds[0] > 0 and blinds[1] > 0 and blinds[1] > blinds[0])
        
        
        #sb is first, bb is second, third away
        self.player_list = []
        self.player_names = {}
        
        cards = set()
        suits = {"Spade", "Diamond", "Heart", "Club"}
        numbers = {"2":0, "3":1, "4":2, "5":3, "6":4, "7":5, "8":6, "9":7, "10":8, "J":9, "Q":10, "K":11,"A":12}

        for number in numbers:
            for suit in suits:
                cards.add((suit, number))
        
        self.cards = cards
        self.max_players = max_players
        self.starting_pot = starting_pot
        #first is small blind, second is big blind
        self.blinds = blinds
        
        self.has_started = False
    
    def add_player(self, poker_bot):
        if self.has_started:
            print("Cannot add player, match has started")
            return
        
        assert(issubclass(poker_bot.__class__, PokerBotTemplate))
        assert(poker_bot.name not in self.player_names)
        if len(self.player_list) == self.max_players:
            print("No more players can join")
            return
        self.player_list.append(poker_bot)
        self.player_names[poker_bot.name] = 0
    
    def initialize_game(self):
        self.has_started = True
        for player in self.player_list:
            self.player_names[player.name] = (player, self.starting_pot)
    
    def return_results(self):
        if not self.has_started:
            print("Game has not started yet")
            return
        new_result = {}
        for player in self.player_names:
            new_result[player] = self.player_names[player][1]
        return new_result
    
    def play_round(self):
        cards = self.cards.copy()
        
        #draw hands
        hands_ref = {}
        hands = random.sample([*cards], 2 * len(self.player_list))
        
        index = 0
        for player in self.player_names:
            hands_ref[player] = {hands[index], hands[index+1]}
            index += 2
        
        return hands_ref
    
    def preflop(self):
        pass
    
    def turn(self):
        pass
    
    def river(self):
        pass