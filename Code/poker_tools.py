import numpy as np
import random

def draw(ret_list = [], num_iter = 0, deck = None):
    if num_iter <= 0 or len(deck) == 0:
        return ret_list
    
    random_index = random.randint(0, len(deck))
    value = deck.pop(random_index)
    ret_list.append(value)
    return draw(ret_list, num_iter - 1, deck)
                
def preflop(num_players):
    assert type(num_players) == int
    assert num_players >= 0
    assert num_players <= 10
    
    hands = []
    for player in range(num_players):
        hands.append(draw([], 2, lst))
    return hands

def return_hand_winner(flop = set(), player_hands = {}, pot = 0):
    
    value_map = {"2":0, "3":1, "4":2, "5":3, "6":4, "7":5, "8":6, "9":7, "10":8, "J":9, "Q":10, "K":11,"A":12}
    suits = {"Spade", "Diamond", "Heart", "Club"}
    straights = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    winning_dict = {9:"Straight Flush", 8:"4 of a Kind", 7:"Full House", 
                    6:"Flush", 5:"Straight", 4:"3 of a Kind", 3:"Two Pair",
                    2:"Pair", 1: "High Card"}
    
    winning_hand_combo = {}
    max_num = -1
    for player in player_hands:
        combo = flop.copy()
        combo.update(player_hands[player])
        assert(len(combo) == 7)
        score = -1
        
        number_count = {}
        suit_count = {}
        for card in combo:
            suit, number = card
            number_count[number] = 1 if number not in number_count else number_count[number] + 1
            suit_count[suit] = 1 if suit not in suit_count else suit_count[suit] + 1
        
        #check straight flush
        for suit in suits:
            if suit not in suit_count or suit_count[suit] < 5:
                continue
            
            for i in range(9, -1, -1):
                total_count = 0
                for card_value in straights[i:i+5]:
                    if(suit, card_value) not in combo:
                        break
                    total_count += 1
                
                if total_count == 5:
                    score = 9 * (13**5) + i
                    break
        
        if score != -1:
            winning_hand_combo[player] = score
            max_num = max(max_num, score)
            continue 
        
        #check 4 of a kind
        kicker = -1
        for number in number_count:
            if number_count[number] == 4:
                score = max(score, 8 * (13 ** 5) + value_map[number] * 13)
            else:
                kicker = max(kicker, value_map[number])

        if score != -1:
            score = score + kicker
            winning_hand_combo[player] = score
            max_num = max(max_num, score)
            continue
        
        #full house
        three_kind, two_kind = -1, -1
        for number in number_count:
            if number_count[number] == 3:
                three_kind = max(three_kind, value_map[number])
            elif number_count[number] == 2:
                two_kind = max(two_kind, value_map[number])

        if three_kind != -1 and two_kind != -1:
            score = 7 * (13**5) + three_kind * 13 + two_kind
            winning_hand_combo[player] = score
            max_num = max(max_num, score)
            continue
        
        #flush
        for suit in suits:
            if suit not in suit_count or suit_count[suit] < 5:
                continue
            
            max_suited_value = -1
            for card in combo:
                if card[0] != suit:
                    continue
                
                max_suited_value = max(max_suited_value, value_map[card[1]])
            
            score = 6*(13 **5) + max_suited_value
            break
        
        if score != -1:
            winning_hand_combo[player] = score
            max_num = max(max_num, score)
            continue
        
        #check straight
        for i in range(9, -1, -1):
            total_count = 0
            for card_value in straights[i:i+5]:
                if card_value not in number_count:
                    break
                total_count += 1

            if total_count == 5:
                score = 5 * (13**5) + i
                break
        
        if score != -1:
            winning_hand_combo[player] = score
            max_num = max(max_num, score)
            continue 
        
        #three of a kind
        if three_kind != -1:
            values = list(number_count.keys())
            values_list = [value_map[x] for x in values]
            values_list.remove(three_kind)
            values_list.sort()
            kicker1, kicker2 = values_list[-1], values_list[-2]
            
            score = (4 * 13 ** 5) + (three_kind * 13 ** 4) + kicker1 * 13 + kicker2
            winning_hand_combo[player] = score
            max_num = max(max_num, score)
            continue
        
        #2 pair / pair
        if two_kind != -1:
            second_kind = -1
            for number in number_count:
                if value_map[number] != two_kind and number_count[number] == 2:
                    second_kind = max(value_map[number], second_kind)
            
            values = list(number_count.keys())
            values_list = [value_map[x] for x in values]
            values_list.remove(two_kind)
            values_list.sort()
            if second_kind != -1:
                values_list.remove(second_kind)
                kicker = values_list[-1]
                
                if second_kind > two_kind:
                    two_kind, second_kind = second_kind, two_kind
                
                score = (3 * 13 ** 5) + (two_kind * 13 ** 4) + (second_kind * 13 ** 3) + kicker
                winning_hand_combo[player] = score
                max_num = max(max_num, score)
                continue
            else:
                kicker1, kicker2, kicker3 = values_list[-1], values_list[-2], values_list[-3]
                score = (2 * 13 ** 5) + (two_kind * 13 ** 4) + (kicker1 * 13 ** 3)
                score += (kicker2 * 13 ** 2) + (kicker3 * 13)
                winning_hand_combo[player] = score
                max_num = max(max_num, score)
                continue
    
        #check high card
        values = list(number_count.keys())
        values_list = [value_map[x] for x in values]
        values_list.sort()
        score = (1 * 13 ** 5) + (values_list[-1] * 13 ** 4) + (values_list[-2] * 13 ** 3) + (values_list[-3] * 13 ** 2)
        score += (values_list[-4] * 13 ** 1) + (values_list[-5])
        winning_hand_combo[player] = score
        max_num = max(max_num, score)

    # 6-number designation: 1 = [hand_ranking] 2 - 6[internal ranking]
    new_hand = winning_hand_combo.copy()
    for player in new_hand:
        if winning_hand_combo[player] != max_num:
            winning_hand_combo.pop(player)

    for player in winning_hand_combo:
        winning_hand_combo[player] = round(pot/len(winning_hand_combo))
    
    val = max_num // (13 ** 5)
        
    return winning_hand_combo, winning_dict[val]

                
#when villain hands are known
def hand_simulate(hero, villains, flop, starter, num_sim):
    assert(len(starter) == 52)
    cards = starter.copy()
    check_set = set()
    
    for card in hero:
        cards.remove(card)
        check_set.add(card)
    
    for card in flop:
        cards.remove(card)
        check_set.add(card)
    
    for player in villains:
        for card in villains[player]:
            cards.remove(card)
            check_set.add(card)
        
    num_to_draw = 5 - len(flop)
    assert(num_to_draw > 0)
    assert(len(check_set) == 2 + len(flop) + 2 * len(villains))
    
    player_hands = villains.copy()
    player_hands["Hero"] = hero.copy()
    
    num_win = 0
    win_dict = {"Straight Flush":0, "4 of a Kind":0, "Full House":0, "Flush":0, "Straight":0,
                "3 of a Kind":0, "Two Pair":0, "Pair":0, "High Card":0}
    
    for i in range(num_sim):
        flop_copy = flop.copy()
        added_cards = random.sample([*cards], num_to_draw)
        flop_copy.update(added_cards)
        
        results, winning_combo = return_hand_winner(flop_copy, player_hands, 100)
        win_dict[winning_combo] += 1
        
        num_win = num_win if "Hero" not in results else num_win + 1/(len(results))
    
    for victor in win_dict:
        win_dict[victor] = round(win_dict[victor]/num_sim,2)
    
    return round(num_win/num_sim, 5), win_dict

def make_range(set_direct):
    suits = {"Spade", "Diamond", "Heart", "Club"}
    numbers = {"2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"}
    ranges = []
    
    if "S" in set_direct:
        for hand in set_direct["S"]:
            assert hand[0] != hand[1]
            assert hand[0] in numbers and hand[1] in numbers
            
            for suit in suits:
                hands = {(suit, hand[0]), (suit, hand[1])}
                ranges.append(hands)
    
    if "P" in set_direct:
        for hand in set_direct["P"]:
            for suit1 in suits:
                for suit2 in suits:
                    if suit1 == suit2:
                        continue
                    assert hand in numbers
                    hands = {(suit1, hand), (suit2, hand)}
                    ranges.append(hands)
    
    if "O" in set_direct:
        for hand in set_direct["O"]:
            assert hand[0] != hand[1]
            assert hand[0] in numbers and hand[1] in numbers
            for suit1 in suits:
                for suit2 in suits:
                    if suit1 == suit2:
                        continue
                    hands = {(suit1, hand[0]), (suit2, hand[1])}
                    ranges.append(hands)
    return ranges
                
                
                
def range_simulate(hero, villains, flop, starter, num_sim):
    assert(len(starter) == 52)
    assert(num_sim > 0)
    assert(len(flop) <= 5)
    cards = starter.copy()
    
    check_set = set()
    for card in hero:
        cards.remove(card)
        check_set.add(card)
    
    for card in flop:
        cards.remove(card)
        check_set.add(card)
        
    assert len(check_set) == 2 + len(flop)
    
    villains_range = {}
    
    for villain in villains:
        villains_range[villain] = make_range(villains[villain])
    
    for villain in villains_range:
        for i in range(len(villains_range[villain])-1, -1, -1):
            for card in check_set:
                if card in villains_range[villain][i]:
                    villains_range[villain].pop(i)
                    break
    
    num_win = 0
    win_dict = {"Straight Flush":0, "4 of a Kind":0, "Full House":0, "Flush":0, "Straight":0,
                "3 of a Kind":0, "Two Pair":0, "Pair":0, "High Card":0}
    
    num_to_draw = 5 - len(flop)
    
    for i in range(num_sim):
        flop_copy = flop.copy()
        cards_copy = cards.copy()
        
        player_hands = {"Hero":hero}
        
        for villain1 in villains_range:
            hand = None
            if len(villains_range[villain1]) == 0:
                hand = set(random.sample([*cards_copy], 2))
            else:
                hand = random.sample(villains_range[villain1], 1)[0]
            cards_copy = cards_copy.difference(hand)
            player_hands[villain1] = hand
            
            for villain2 in villains_range:
                if villain1 == villain2:
                    continue
                for i in range(len(villains_range[villain2])-1, -1, -1):
                    for card in hand:
                        if card in villains_range[villain2][i]:
                            villains_range[villain2].pop(i)
                            break
        
        added_flop_cards = random.sample([*cards_copy], num_to_draw)
        flop_copy.update(added_flop_cards)
        
        results, winning_combo = return_hand_winner(flop_copy, player_hands, 100)
        win_dict[winning_combo] += 1
        
        num_win = num_win if "Hero" not in results else num_win + 1/(len(results))
    
    for victor in win_dict:
        win_dict[victor] = round(win_dict[victor]/num_sim,2)
    
    return round(num_win/num_sim, 5), win_dict