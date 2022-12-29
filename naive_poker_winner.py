import numpy as np
import random
import heapq

suits = {"Spade", "Diamond", "Heart", "Club"}
numbers = {"2":0, "3":1, "4":2, "5":3, "6":4, "7":5, "8":6, "9":7, "10":8, "J":9, "Q":10, "K":11,"A":12}
numbers_ord = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
numbers_ord_na = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

def find_max(winning_hand_combo, pot):
    max_value = max(winning_hand_combo.values())
    new_winning_hand = winning_hand_combo.copy()
    for hand in new_winning_hand:
        if winning_hand_combo[hand] != max_value:
            winning_hand_combo.pop(hand)
    for hand in winning_hand_combo:
        winning_hand_combo[hand] = pot/len(winning_hand_combo)
    return winning_hand_combo

def win_determination(flop = {}, player_hands = {}, pot = 0):
    assert(len(flop) == 5)
    assert(len(player_hands) > 1)
    
    #check straight flush
    winning_hand_combo = {}
    for player in player_hands:
        hand = flop.copy()
        hand.update(player_hands[player])
        
        for value in suits:
            for i in range(9, -1, -1):
                found_suit = False
                sum_total = 0
                for number in numbers_ord[i:i+5]:
                    if (value, number) in hand:
                        sum_total += 1
                    
                if sum_total == 5 and player not in winning_hand_combo:
                    winning_hand_combo[player] = i
                    break
    
    if len(winning_hand_combo) != 0:
        return find_max(winning_hand_combo, pot)
    
    #check four-of-a-kind - all on the board
    for i in range(len(numbers_ord_na) - 1, -1, -1):
        found_four_of_a_kind = True
        number = numbers_ord_na[i]
        for value in suits:
            if (value, number) not in flop:
                found_four_of_a_kind = False
                break
        
        if found_four_of_a_kind:
            fifth_card = None
            for card in flop:
                if card[1] != number:
                    fifth_card = card
            max_card = numbers[fifth_card[1]]
            
            #find the max
            for player in player_hands:
                for card in player_hands[player]:
                    if numbers[card[1]] > max_card:
                        max_card = numbers[card[1]]
            
            #check players with the max
            if max_card == numbers[fifth_card[1]]:
                print(player_hands)
                for player in player_hands:
                    winning_hand_combo[player] = pot/len(player_hands)
                return winning_hand_combo
            else:
                for player in player_hands:
                    for card in player_hands[player]:
                        if numbers[card[1]] == max_card:
                            winning_hand_combo[player] = 0
                
                for winner in winning_hand_combo:
                    winning_hand_combo[winner] = pot/len(winning_hand_combo)
                
                return winning_hand_combo
            
            break
        
    #check four-of-a-kind - 1 holder
    for player in player_hands:
        hand = flop.copy()
        hand.update(player_hands[player])
        for i in range(len(numbers_ord_na) - 1, -1, -1):
            number = numbers_ord_na[i]
            found_four_of_a_kind = True
            for value in suits:
                if (value, number) not in hand:
                    found_four_of_a_kind = False
                    break
            
            if found_four_of_a_kind:
                winning_hand_combo[player] = pot
                return winning_hand_combo
            
    #full house algo
    max_win_count = -1
    for player in player_hands:
        hand = flop.copy()
        hand.update(player_hands[player])
        count_map = {}
        for card in hand:
            count_map[card[1]] = 1 if card[1] not in count_map else count_map[card[1]] + 1
        
        three_value = -1
        two_value = -1
        for count in count_map:
            if count_map[count] == 3:
                three_value = max(three_value, numbers[count])
            elif count_map[count] == 2:
                two_value = max(two_value, numbers[count])
        
        if three_value == -1 or two_value == -1:
            break
        
        max_win_count = max(max_win_count, 13 * three_value + two_value)
        winning_hand_combo[player] = 13 * three_value + two_value
    
    if max_win_count != -1:
        new_winning_hand = winning_hand_combo.copy()
        for player in new_winning_hand:
            if winning_hand_combo[player] != max_win_count:
                winning_hand_combo.pop(player)
        
        for player in winning_hand_combo:
            winning_hand_combo[player] = pot / len(winning_hand_combo)
        return winning_hand_combo
    
    #Flush
    max_number_suit = -1
    for player in player_hands:
        hand = flop.copy()
        hand.update(player_hands[player])
        
        count_map = {}
        count_max = {}
        for card in hand:
            suit, number = card
            count_map[suit] = 1 if suit not in count_map else count_map[suit] + 1
            count_max[suit] = numbers[number] if suit not in count_max else max(count_max[suit], numbers[number])
        
        for suit in count_map:
            if count_map[suit] == 5:
                winning_hand_combo[player] = count_max[suit]
                max_number_suit = max(max_number_suit, count_max[suit])
                break
        
    if max_number_suit != -1:
        new_winning_hand_combo = winning_hand_combo.copy()
        for hand in new_winning_hand_combo:
            if winning_hand_combo[hand] != max_number_suit:
                winning_hand_combo.pop(hand)
        
        for hand in winning_hand_combo:
            winning_hand_combo[hand] = pot/len(winning_hand_combo)
        
        return winning_hand_combo
    
    #Straight
    max_number_straight = -1
    for player in player_hands:
        hand = flop.copy()
        hand.update(player_hands[player])
        
        count_map = set()
        for card in hand:
            number = card[1]
            count_map.add(number)
        
        if len(count_map) < 5:
            break
        
        for i in range(9, -1, -1):
            count_sum = 0
            for number in numbers_ord[i:i+5]:
                if number not in count_map:
                    break
                count_sum += 1
            
            if count_sum == 5:
                winning_hand_combo[player] = i
                max_number_straight = max(max_number_straight, i)
                break
    
    if max_number_straight != -1:
        new_winning_hand_combo = winning_hand_combo.copy()
        for hand in new_winning_hand_combo:
            if winning_hand_combo[hand] != max_number_straight:
                winning_hand_combo.pop(hand)
        
        for hand in winning_hand_combo:
            winning_hand_combo[hand] = pot/len(winning_hand_combo)
        
        return winning_hand_combo
    
    #three-of-a-kind
    max_num = -1
    for player in player_hands:
        hand = flop.copy()
        hand.update(player_hands[player])
        
        count = {}
        for card in hand:
            number = card[1]
            count[number] = 1 if number not in count else count[number] + 1
        
        iter_number = -1
        for number in count:
            iter_number = iter_number if count[number] != 3 else numbers[number] * 169
        
        if iter_number == -1:
            continue
        
        second_high = -1
        for number in count:
            value = numbers[number]
            if value != iter_number/169:
                second_high = max(second_high, value)
        
        iter_number += second_high * 13
        
        third_high = -1
        for number in count:
            value = numbers[number]
            if value != second_high and value != iter_number/169:
                third_high = max(third_high, value)
        
        iter_number += third_high
        winning_hand_combo[player] = iter_number
        max_num = max(iter_number, max_num)
    
    if max_num != -1:
        new_hand = winning_hand_combo.copy()
        for player in new_hand:
            if winning_hand_combo[player] != max_num:
                winning_hand_combo.pop(player)
        
        for player in winning_hand_combo:
            winning_hand_combo[player] = pot/len(winning_hand_combo)
        
        return winning_hand_combo
    
    #two-pair
    max_calc = -1
    for player in player_hands:
        hand = flop.copy()
        hand.update(player_hands[player])
        
        count_map = {}
        for card in hand:
            number = card[1]
            count_map[number] = 1 if number not in count_map else count_map[number] + 1
        
        max_num = -1
        for number in count_map:
            max_num = max_num if count_map[number] != 2 else max(max_num, numbers[number])
        
        if max_num == -1:
            continue
        
        second_pair = -1
        for number in count_map:
            if count_map[number] == 2 and numbers[number] != max_num:
                second_pair = max(second_pair, numbers[number])
        
        if second_pair == -1:
            continue
        
        kicker = -1
        for number in count_map:
            if numbers[number] != second_pair and numbers[number] != max_num:
                kicker = max(kicker, numbers[number])
        
        value = max_num * 169 + second_pair * 13 + kicker
        
        winning_hand_combo[player] = value
        max_calc = max(max_calc, value)
    
    if max_calc != -1:
        new_hand = winning_hand_combo.copy()
        for player in new_hand:
            if winning_hand_combo[player] != max_calc:
                winning_hand_combo.pop(player)
        
        for player in winning_hand_combo:
            winning_hand_combo[player] = pot/len(winning_hand_combo)
        
        return winning_hand_combo
    
    #pair
    max_num = -1
    for player in player_hands:
        hand = flop.copy()
        hand.update(player_hands[player])
        
        count_map = {}
        for card in hand:
            number = card[1]
            count_map[number] = 1 if number not in count_map else count_map[number] + 1
        
        found_pair = -1
        lst = []
        for number in count_map:
            if count_map[number] == 2:
                found_pair = numbers[number]
            else:
                lst.append(numbers[number])
        
        if found_pair == -1:
            continue
        
        lst.sort()
        lst = lst[-3:]
        value = found_pair * (13**3) + lst[-1] * (13**2) + lst[-2] * (13) + lst[-3]
        winning_hand_combo[player] = value
        max_num = max(max_num, value)
    
    if max_num != -1:
        new_hand = winning_hand_combo.copy()
        for player in new_hand:
            if winning_hand_combo[player] != max_num:
                winning_hand_combo.pop(player)
            
        for player in winning_hand_combo:
            winning_hand_combo[player] = pot/len(winning_hand_combo)
        
        return winning_hand_combo
    
    max_num = -1
    for player in player_hands:
        hand = flop.copy()
        hand.update(player_hands[player])
        
        lst = []
        for card in hand:
            lst.append(numbers[card[1]])
        
        lst.sort()
        lst = lst[-5:]
        value = lst[-1]*(13**4) + lst[-2]*(13**3) + lst[-3]*(13**2) + lst[-4]*(13**1) + lst[-5]
        winning_hand_combo[player] = value
        max_num = max(max_num, value)
    
    if max_num != -1:
        new_hand = winning_hand_combo.copy()
        for player in new_hand:
            if winning_hand_combo[player] != max_num:
                winning_hand_combo.pop(player)
            
        for player in winning_hand_combo:
            winning_hand_combo[player] = pot/len(winning_hand_combo)
        
        return winning_hand_combo