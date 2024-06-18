"""
Here lie the functions necessary to play the childhood game chopsticks, in addition to an AI capable of consistently 
drawing or winning (as the game is zero-sum if played perfectly). For more information on the rules of the game, visit
https://en.wikipedia.org/wiki/Chopsticks_(hand_game)
"""


# predetermined dictionary of state scores for the minimax algorithm - saves user computation time 
import json
with open("possible_state_dict.json") as f:
    possible_state_dict = json.load(f)
possible_state_dict[0] = possible_state_dict.pop("0")
possible_state_dict[1] = possible_state_dict.pop("1")

class Chopstick:
    def __init__(self, max_depth):
        # maximum search depth for the minimax algorithm - no greater value is needed to improve performance 
        self.max_depth = max_depth
        

    def hit(self, player_hand, opponent_hand):
        # outcome if one player uses their turn to hit one of their opponent's hands
        new_hand = player_hand + opponent_hand
        if new_hand >= 5:
            new_hand = 0
        return new_hand


    def standardize_format(self, result):
        # reformats hands to prevent equivalent hands from reading differently 
        # (e.g., one finger on hand #1 and 4 fingers on hand #2 is equivalent to four fingers on hand #1 and 1 finger on hand #2)
        result = sorted(result)
        result = "".join(map(str, result))
        return result


    def possible_hits(self, state, player):
        # all possible outcome states if a turn is used to hit
        hits = set()

        states = state.split("|")
        opponent = 1 - player
        player_hand = states[player]
        opponent_hand = states[opponent]

        player_left = int(player_hand[0])
        player_right = int(player_hand[1])
        opponent_left = int(opponent_hand[0])
        opponent_right = int(opponent_hand[1])

        possible_moves = [
            [player_left, opponent_left, 0],
            [player_left, opponent_right, 1],
            [player_right, opponent_left, 0],
            [player_right, opponent_right, 1]
        ]

        for player_fingers, opponent_fingers, hand in possible_moves:
            if player_fingers != 0 and opponent_fingers != 0:
                hit_result = self.hit(player_fingers, opponent_fingers)
                opponent_new_hand = [opponent_left, opponent_right]
                opponent_new_hand[hand] = hit_result
                opponent_new_hand = self.standardize_format(opponent_new_hand)
                new_state = states.copy()
                new_state[opponent] = opponent_new_hand
                new_state = "|".join(new_state)
                hits.add(new_state)

        return list(hits) 


    def possible_splits(self, state, player):
        # all possible outcome states if a turn is used to "split" (reorganize the fingers of a player)
        splits = set()

        states = state.split("|")
        hand = states[player]
        left = int(hand[0])
        right = int(hand[1])

        for finger in range(1, left+1):
            split_result = left-finger, right+finger
            if split_result[0] <= 4 and split_result[1] <= 4:
                split_result = self.standardize_format(split_result)
                new_state = states.copy()
                new_state[player] = split_result
                new_state = "|".join(new_state)
                splits.add(new_state)
        for finger in range(1, right+1):
            split_result = left+finger, right-finger
            if split_result[0] <= 4 and split_result[1] <= 4:
                split_result = self.standardize_format(split_result)
                new_state = states.copy()
                new_state[player] = split_result
                new_state = "|".join(new_state)
                splits.add(new_state)
        
        if state in splits: 
            splits.remove(state)

        return list(splits)


    def get_available_states(self, state, player):
        # all possible outcome states which can be achieved from an initial state given a player's turn
        available_states = []

        states = state.split("|")
        states = [self.standardize_format(states[0]), self.standardize_format(states[1])]
        state = "|".join(states)

        if self.evaluate(state) != 0:
            raise ValueError("Do Not Pass a Winning State into this Function.")
        
        available_states += self.possible_hits(state, player)
        available_states += self.possible_splits(state, player)

        return available_states


    def evaluate(self, state):
        # determine if the game is over and there is a winner
        states = state.split("|")
        if states[0] == "00":
            return -100
        if states[1] == "00":
            return 100    
        return 0


    def minimax(self, state, depth, player):
        # determine score resulting from a state given a player's turn, assuming both players make the optimal choices
        score = self.evaluate(state)
        if score != 0:
            return score
        
        if depth > self.max_depth:
            return score
        
        possible_states = self.get_available_states(state, player)
        if player == 0:
            next_player = 1
            best = -1000
            for possible_state in possible_states:
                if possible_state in possible_state_dict[player] and abs(possible_state_dict[player][possible_state]) > 50:
                    score = possible_state_dict[player][possible_state]
                else:
                    score = self.minimax(possible_state, depth + 1, next_player)
                    if score > 0:
                        score -= 1
                    elif score < 0:
                        score += 1
                possible_state_dict[player][possible_state] = score
                best = max(best, score)
            return best
        if player == 1:
            next_player = 0
            best = 1000
            for possible_state in possible_states:
                if possible_state in possible_state_dict[player] and abs(possible_state_dict[player][possible_state]) > 50:
                    score = possible_state_dict[player][possible_state]
                else:
                    score = self.minimax(possible_state, depth + 1, next_player)
                    if score > 0:
                        score -= 1
                    elif score < 0:
                        score += 1 
                possible_state_dict[player][possible_state] = score
                best = min(best, score)
            return best
        
        
    def find_best_state(self, state, player):
        # determine the best choice for a player based on the minimax score for each choice
        possible_states = self.get_available_states(state, player)

        if player == 0:
            best_score = -1000
            for possible_state in possible_states:
                score = self.minimax(possible_state, 0, 1)
                if score > best_score:
                    best_state = possible_state
                    best_score = score

        if player == 1:
            best_score = 1000
            for possible_state in possible_states:
                score = self.minimax(possible_state, 0, 0)
                if score < best_score:
                    best_state = possible_state
                    best_score = score

        return best_state


    def spectate_AI(self):
        # watch the AI play against itself
        state = "11|11"
        player = 0
        print("Player     State     Turn #")
        turns = 0
        while True:
            
            print(player, "        ", state, "   ", turns)
            if self.evaluate(state) != 0:
                print("Completed!")
                print(f"Number of Turns: {turns}")
                break

            state = self.find_best_state(state, player)
            player = 1 - player
            turns +=  1
    
    def play_AI(self, player_choice = 0):
        # play against the AI to master chopsticks
        state = "11|11"
        player = 0
        print("Player     State     Turn #")
        for turns in range(120):

            print(player, "        ", state, "   ", turns)
            if self.evaluate(state) < 0 and player_choice == 1:
                print("You Won!")
                break
            elif self.evaluate(state) > 0 and player_choice == 0:
                print("You Won!")
                break
            elif self.evaluate(state) != 0:
                print("The AI Won!")
                break

            if player != player_choice:
                state = self.find_best_state(state, player)
            if player == player_choice:
                state = input()
                state = state[:2] + "|" + state[2:]
            player = 1 - player