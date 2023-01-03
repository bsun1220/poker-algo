import copy
import numpy as np
import random
from poker_tools import return_hand_winner
from poker_bot import PokerBotTemplate

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
        self.recent_round = None
        
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
        assert(self.has_started)
        assert(len(self.player_names) > 1)
        cards = self.cards.copy()
        assert(len(cards) == 52)
        
        #draw hands
        hands_ref = {}
        hands = random.sample([*cards], 2 * len(self.player_list))
        cards = cards.difference(hands)
        assert(len(cards) == 52 - 2 * len(self.player_list))
        
        index = 0
        stacks = {}
        for player in self.player_names:
            hands_ref[player] = {hands[index], hands[index+1]}
            stacks[player] = self.player_names[player][1]
            index += 2
        
        hands_ref_copy = hands_ref.copy()
        stacks_copy = stacks.copy()
        
        pre_state = {"round":self.round, "stacks":stacks}
        for player in self.player_names:
            self.player_names[player][0].initialize_strategy(copy.deepcopy(pre_state))
            
        player_list = self.player_list.copy()
        
        self.round += 1
        preflop_state = self.play_preflop(hands_ref, pre_state, player_list)
        for player in self.player_names:
            self.player_names[player][1] = preflop_state["stacks"][player]
        
        if len(preflop_state["player_list"]) == 1:
            name = preflop_state["player_list"][0].name
            self.player_names[name][1] += preflop_state["pot"]
            self.adjust()
            self.recent_round = {
                "game_history":preflop_state["game_history"],
                "hands_ref":hands_ref_copy,
                "stacks":stacks_copy,
                "winner":{name:preflop_state["pot"]}
            }
            return

        names_left = set()
        for player in preflop_state["player_list"]:
            names_left.add(player.name)
        
        for name in hands_ref.copy():
            if name not in names_left:
                hands_ref.pop(name)
        
        if preflop_state["all_in"]:
            assert(len(cards) == 52 - 2 * len(self.player_list))
            flop = set(random.sample([*cards], 5))
            results = self.play_showdown(flop, hands_ref, preflop_state["pot"])
            for player in results:
                self.player_names[player][1] += results[player]
            self.adjust()
            self.recent_round = {
                "game_history":preflop_state["game_history"],
                "hands_ref":hands_ref_copy,
                "stacks":stacks_copy,
                "flop":flop,
                "winner":results
            }
            return 
        
        flop = set(random.sample([*cards], 2))
        cards = cards.difference(flop)
        
        rounds = ["Postflop", "Turn", "River"]
        postflop_state = preflop_state
        for i in range(3):
            added_card = random.sample([*cards], 1)
            flop.update(added_card)
            cards = cards.difference(added_card)
            postflop_state["flop"] = flop.copy()
            postflop_state["prog"] = rounds[i]
            postflop_state = self.play_postflop(hands_ref, postflop_state, player_list)
            
            for player in postflop_state["stacks"]:
                self.player_names[player][1] = postflop_state["stacks"][player]
            
            if len(postflop_state["player_list"]) == 1:
                name = postflop_state["player_list"][0].name
                self.player_names[name][1] += postflop_state["pot"]
                self.adjust()
                self.recent_round = {
                    "game_history":postflop_state["game_history"],
                    "hands_ref":hands_ref_copy,
                    "stacks":stacks_copy,
                    "flop":flop,
                    "winner":{name:postflop_state["pot"]}
                }
                return
            
            names_left = set()
            for player in preflop_state["player_list"]:
                names_left.add(player.name)
        
            for name in hands_ref.copy():
                if name not in names_left:
                    hands_ref.pop(name)
            
            if postflop_state["all_in"]:
                num_to_add = 5 - len(postflop_state["flop"])
                assert(len(cards) == 52 - 2 * len(self.player_list) - 3 - i)
                added_cards = set(random.sample([*cards], num_to_add))
                postflop_state["flop"].update(added_cards)
                cards = cards.difference(added_cards)
                results = self.play_showdown(postflop_state["flop"], hands_ref, postflop_state["pot"])
                
                for player in results:
                    self.player_names[player][1] += results[player]
                self.adjust()
                self.recent_round = {
                    "game_history":postflop_state["game_history"],
                    "hands_ref":hands_ref_copy,
                    "stacks":stacks_copy,
                    "flop":flop,
                    "winner":results
                }
                return
        
        results = self.play_showdown(postflop_state["flop"], hands_ref, postflop_state["pot"])
        for player in results:
            self.player_names[player][1] += results[player]
        self.adjust()
        self.recent_round = {
            "game_history":postflop_state["game_history"],
            "hands_ref":hands_ref_copy,
            "stacks":stacks_copy,
            "flop":flop,
            "winner":results
        }
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
            amount = stacks[player_list[1].name]
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
                    game_history.append((name, "CheckAction", "Preflop", call_amount))
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
                    game_history.append((name, "CheckAction", "Preflop", call_amount))
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
        
    def play_postflop(self, hands_ref, state, player_list):
        amount_call = {}
        stacks = {}
        blinds = self.blinds
        
        for player in state["player_list"]:
            name = player.name
            amount_call[name] = 0
            stacks[name] = state["stacks"][name]
        
        completed_betting = False
        num_iter = 0
        game_history = state["game_history"]
        all_in = False  
        pot = state["pot"]
        min_raise = state["min_raise"]
        flop = state["flop"]
        player_list = state["player_list"]
        i = 0
        
        while not completed_betting:
            name = player_list[i].name
            forced_all_in = amount_call[name] > stacks[name]
            call_amount = min(amount_call[name], stacks[name])
            
            player_state = {
                "prog":state["prog"],
                "position":i,
                "all_in":all_in,
                "game_history":game_history.copy(),
                "stack_size":stacks,
                "hand":hands_ref[name],
                "pot":pot,
                "flop":flop.copy(),
                "call_amount":call_amount,
                "min_raise": min_raise
            }
            action = player_list[i].play(player_state)
            if all_in:
                if action[0] == "CheckAction":
                    stacks[name] -= call_amount
                    amount_call[name] = 0
                    game_history.append((name, "CheckAction", state["prog"], call_amount))
                    pot += call_amount
                    num_iter += 1
                    i = 0 if i + 1 >= len(player_list) else i + 1
                else:
                    player_list.pop(i)
                    i = 0 if i >= len(player_list) else i
                    game_history.append((name, "FoldAction", state["prog"], 0))
            else:
                if action[0] == "CheckAction":
                    stacks[name] -= call_amount
                    game_history.append((name, "CheckAction", state["prog"], call_amount))
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
                        game_history.append((name, "FoldAction", state["prog"], 0))
                    else:
                        min_raise = action[1] * 2
                        pot += action[1] + call_amount
                        num_iter = 1
                        game_history.append((name, "RaiseAction", state["prog"], action[1]))
                        stacks[name] -= (action[1] + call_amount)
                        if stacks[name] == 0:
                            all_in = True
                        i = 0 if i + 1 >= len(player_list) else i + 1
                        for player in amount_call:
                            amount_call[player] += action[1]
                else:
                    player_list.pop(i)
                    i = 0 if i >= len(player_list) else i
                    game_history.append((name, "FoldAction", state["prog"], 0))
            if num_iter == len(player_list) or len(player_list) == 1:
                completed_betting = True
        final_state = {}
        final_state["stacks"] = stacks
        final_state["game_history"] = game_history
        final_state["pot"] = pot
        final_state["player_list"] = player_list
        final_state["min_raise"] = min_raise
        final_state["all_in"] = all_in
        final_state["flop"] = flop
        return final_state
    
    def play_showdown(self, flop, hands_ref, pot):
        result, _ = return_hand_winner(flop, hands_ref, pot)
        return result
    
    def read_results(self, result):
        print("round " + str(self.round - 1))
        print("blinds are {},{}".format(self.blinds[0], self.blinds[1]))
        print("starting stack is {}".format(self.starting_pot))
        print("----------")
        for player in result["hands_ref"]:
            cards = [*result["hands_ref"][player]]
            stack = result["stacks"][player]
            print("{} has a stack of ${} and is holding {}{} {}{}"
                  .format(player, stack, cards[0][0], 
                          cards[0][1], cards[1][0], cards[1][1]))
        print("----------")
        if "flop" in result:
            let_str = "Flop was "
            for card in result["flop"]:
                let_str += (str(card[0]) + str(card[1]) + " ")
            print(let_str)
        print("----------")
        for play in result["game_history"]:
            print("On {}, {} did a {} with ${}".format(play[2], play[0], play[1], play[3]))
        print("----------")
        winners = result["winner"].keys()
        pot_total = sum([*result["winner"].values()])
        let_str = ' '.join(winners)
        print("winners are " +let_str + " with a pot of $" + str(pot_total))
        print()
    
    def adjust(self):
        to_remove = set()
        for player in self.player_names:
            if self.player_names[player][1] <= 0:
                to_remove.add(player)
        
        for player in to_remove:
            self.player_names.pop(player)
        
        for i in range(len(self.player_list) - 1, -1, -1):
            name = self.player_list[i].name
            if name in to_remove:
                self.player_list.pop(i)
        
        front = self.player_list.pop(0)
        self.player_list.append(front)