# poker-algo

Poker AI Monte Carlo Simulator

Using the PokerGame class, you can initialize a Poker Engine for which to submit your bots to. The PowerGame supports various functions including add_player (where you add your bot to the game), initialize_game (which locks in participants and starts game), play_round (which will simulate a game), return_results (which gives stack sizes), and read_results (which gives outcome of a certain round). The engine plays regular poker with some added rules : when someone goes all in, the bot can only check or fold. No side pots are allowed. 
</br>
To create a bot, simply use the PokerBotTemplate class as your parent class and use the play method. The play method has a single parameter state. State will be a dictionary with various values in the game. 
</br>
key "prog" links to state of the game (preflop, postflop, turn, river).
</br>
key "position" links to integer stating position in game. 0 is Small Blind, 1 is Big Blind, 2 ,..,
</br>
key "all_in" links to a boolean whether someone has went all in or not. Actions are restricted to check or fold
</br>
key "game_history" provides a list of sequential events in tuple (name, action, time, amount)
</br>
key stack_size provides a dictionary of everyone in the table and their stacks
</br>
key hand refers to your current hand
</br>
key pot refers to current pot
</br>
flop refers to flop of cards. Cards are organized in tuple form (suit, number)
</br>
call_amount refers to amount for call / check
</br>
mine_raise refers to minimum amount you must raise (without counting amount to call
</br></br>
Some additional rules include that invalid actions result in the bot folding. There are sample bots in sample_bots.py which include a 
player that always checks or calls. Someone that always raises. And a player with a 50% of folding and 50% of checking / calling. 


