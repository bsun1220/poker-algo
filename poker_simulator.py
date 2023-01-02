import copy
import numpy as np
import random

class PokerGame:
    def __init__(self, max_players = 10, starting_pot = 1000, blinds = (5, 10)):
        
        assert(type(max_players) == int and max_players > 0 and max_players <= 10)
        assert(type(starting_pot) == int and starting_pot > 0)
        assert(len(blinds) == 2 and type(blinds[0]) == int and type(blinds[1]) == int)
        assert(blinds[0] > 0 and blinds[1] > 0 and blinds[1] > blinds[0])
        
        #sb is first, bb is second, third = under the gun
        self.round = 1
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
            self.player_names[player.name] = [player, self.starting_pot]
    
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
        stacks = {}
        for player in self.player_names:
            hands_ref[player] = {hands[index], hands[index+1]}
            stacks[player] = self.player_names[player][1]
            index += 2
        
        state = {"round":self.round, "stacks":stacks}
        for player in self.player_names:
            self.player_names[player][0].initialize_strategy(copy.deepcopy(state))
            
        player_list = self.player_list.copy()
        
        self.round += 1
        preflop_state = self.play_preflop(hands_ref, state, player_list)
        
        return
    
    def play_preflop(self, hands_ref, state, player_list):
        amount_call = {}
        stacks = {}
        blinds = self.blinds
        
        for player in self.player_names:
            amount_call[player] = blinds[1]
            stacks[player] = self.player_names[player][1]
        
        completed_betting = False
        num_iter = 0
        i = 1 if len(player_list) == 2 else 2
        game_history = []
        all_in = False
        
        pot = 0
        
        min_raise = blinds[1]
        
        if stacks[player_list[0].name] < blinds[0]:
            all_in = True
            amount = stacks[player_list[0].name]
            stacks[player_list[0].name] = 0
            pot += amount
            amount_call[player_list[0].name] = 0
        else: 
            pot += blinds[0]
            stacks[player_list[0].name] -= blinds[0]
            amount_call[player_list[0].name] -= blinds[0]
        
        if stacks[player_list[1].name] < blinds[1]:
            all_in = True
            amount = stacks[player_list[1].name][1]
            stacks[player_list[1].name] = 0
            pot += amount
        else:
            pot += blinds[1]
            stacks[player_list[1].name] -= blinds[1]     
        amount_call[player_list[1].name] = 0
        
        while not completed_betting:
            name = player_list[i].name
            forced_all_in = amount_call[name] > stacks[name]
            call_amount = min(amount_call[name], stacks[name])
            
            player_state = {
                "prog":"preflop",
                "position":i,
                "all_in":all_in,
                "game_history":game_history.copy(),
                "stack_size":stacks,
                "hand":hands_ref[name],
                "pot":pot,
                "call_amount":call_amount,
                "min_raise": min_raise
            }
            action = player_list[i].play(player_state)
            if all_in:
                if action[0] == "CheckAction":
                    stacks[name] -= call_amount
                    amount_call[name] = 0
                    game_history.append((name, "CheckAction", "Preflop", min_raise))
                    pot += call_amount
                    num_iter += 1
                    i = 0 if i + 1 >= len(player_list) else i + 1
                else:
                    player_list.pop(i)
                    i = 0 if i >= len(player_list) else i
                    game_history.append((name, "FoldAction", "Preflop", 0))
            else:
                if action[0] == "CheckAction":
                    stacks[name] -= call_amount
                    game_history.append((name, "CheckAction", "Preflop", min_raise))
                    num_iter += 1
                    amount_call[name] = 0
                    pot += call_amount
                    i = 0 if i + 1 >= len(player_list) else i + 1
                    if forced_all_in:
                        all_in = True
                elif action[0] == "RaiseAction":
                    if action[1] + call_amount > stacks[name] or action[1] < min_raise:
                        player_list.pop(i)
                        i = 0 if i + 1 >= len(player_list) else i + 1
                        game_history.append((name, "FoldAction", "Preflop", 0))
                    else:
                        min_raise = action[1] * 2
                        pot += action[1] + call_amount
                        num_iter = 1
                        game_history.append((name, "RaiseAction", "Preflop", action[1]))
                        stacks[name] -= (action[1] + call_amount)
                        if stacks[name] == 0:
                            all_in = True
                        i = 0 if i + 1 >= len(player_list) else i + 1
                        for player in amount_call:
                            amount_call[player] += action[1]
                else:
                    player_list.pop(i)
                    i = 0 if i >= len(player_list) else i
                    game_history.append((name, "FoldAction", "Preflop", 0))
            if num_iter == len(player_list) or len(player_list) == 1:
                completed_betting = True
        
        final_state = {}
        final_state["stacks"] = stacks
        final_state["game_history"] = game_history
        final_state["pot"] = pot
        final_state["player_list"] = player_list
        final_state["min_raise"] = min_raise
        final_state["all_in"] = all_in
        return final_state
        
    def play_postflop(self):
        pass
    
    def play_turn(self):
        pass
    
    def play_river(self):
        pass
    
    def play_showdown(self):
        pass