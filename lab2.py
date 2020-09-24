# MIT 6.034 Lab 2: Games
# Written by 6.034 staff

from game_api import *
from boards import *
from toytree import GAME1

INF = float('inf')

# Please see wiki lab page for full description of functions and API.

#### Part 1: Utility Functions #################################################

def is_game_over_connectfour(board):
    """Returns True if game is over, otherwise False."""
    
    # Check if there's a chain greater than 4
    chains = board.get_all_chains()
    for chain in chains:
        if len(chain) >= 4:
            return True

    # Check if columns are filled
    filled = []
    for col in range(board.num_cols):
        filled.append(board.is_column_full(col))

    if False not in filled:
        return True

    return False

def next_boards_connectfour(board):
    """Returns a list of ConnectFourBoard objects that could result from the
    next move, or an empty list if no moves can be made."""
    
    # Check if game over
    if is_game_over_connectfour(board):
        return []

    # Iterate through columns
    next_boards = []
    for col in range(board.num_cols):
        if not board.is_column_full(col):
            next_boards.append(board.add_piece(col))

    return next_boards

def endgame_score_connectfour(board, is_current_player_maximizer):
    """Given an endgame board, returns 1000 if the maximizer has won,
    -1000 if the minimizer has won, or 0 in case of a tie."""
    
    # Check if there's a chain of 4
    chains = board.get_all_chains()
    for chain in chains:
        if len(chain) >= 4:
            if is_current_player_maximizer:
                return -1000
            else:
                return 1000
    # tie otherwise
    return 0


def endgame_score_connectfour_faster(board, is_current_player_maximizer):
    """Given an endgame board, returns an endgame score with abs(score) >= 1000,
    returning larger absolute scores for winning sooner."""
    
    # Score function: (1000 + col*rows*100) - (pieces used)*100
    max_score = 1000 + board.num_rows*board.num_cols*100
    used_pieces = board.count_pieces()

    # Check if there's a chain of 4
    chains = board.get_all_chains()
    for chain in chains:
        if len(chain) >= 4:
            score = max_score - used_pieces*100
            if is_current_player_maximizer:
                return (-1*score)
            else:
                return score
    # tie otherwise
    return 0


def heuristic_connectfour(board, is_current_player_maximizer):
    """Given a non-endgame board, returns a heuristic score with
    abs(score) < 1000, where higher numbers indicate that the board is better
    for the maximizer."""

    current_player_chain = board.get_all_chains(current_player=True)
    other_player_chain = board.get_all_chains(current_player=False)

    """
    Score algorithm:
    Give length of chain a weight
    Multiple by the number of chains of certain length
    Get raw score 
    
    Compare raw score between players
    """
    def score(chains):
        score = 0
        conversion = {
        4: 100,
        3: 100,
        2: 50,
        1: 25,
        0: 0
        }
        for chain in chains:
            score += conversion[len(chain)]
        return score

    heuristic = score(current_player_chain) - score(other_player_chain)
    if is_current_player_maximizer:
        return heuristic
    else:
        return -1*heuristic


# Now we can create AbstractGameState objects for Connect Four, using some of
# the functions you implemented above.  You can use the following examples to
# test your dfs and minimax implementations in Part 2.

# This AbstractGameState represents a new ConnectFourBoard, before the game has started:
state_starting_connectfour = AbstractGameState(snapshot = ConnectFourBoard(),
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "NEARLY_OVER" from boards.py:
state_NEARLY_OVER = AbstractGameState(snapshot = NEARLY_OVER,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "BOARD_UHOH" from boards.py:
state_UHOH = AbstractGameState(snapshot = BOARD_UHOH,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)


#### Part 2: Searching a Game Tree #############################################

# Note: Functions in Part 2 use the AbstractGameState API, not ConnectFourBoard.

def dfs_maximizing(state) :
    """Performs depth-first search to find path with highest endgame score.
    Returns a tuple containing:
     0. the best path (a list of AbstractGameState objects),
     1. the score of the leaf node (a number), and
     2. the number of static evaluations performed (a number)"""

    # queue will track state, and the path so far
    queue = [[state, [state]]]

    # has the best option thus far
    best = []
    evaluations_count = 0

    # Loops till queue exhausted
    while queue:
        # Check if at leaf node and pop element
        if queue[0][0].is_game_over():
            evaluations_count += 1
            if not best: 
                best = queue[0]
            if queue[0][0].get_endgame_score() > best[0].get_endgame_score():
                best = queue[0]
            queue.pop(0) 
        else:
            # pop and replace the first elements of the queue
            possible_states = queue[0][0].generate_next_states()
            steps_so_far = queue[0][1]
            queue.pop(0)

            new_states = []
            for s in possible_states:
                new_steps = steps_so_far.copy()
                new_steps.append(s)
                new_states.append([s, new_steps])

            queue = new_states + queue

    return (best[1], best[0].get_endgame_score(), evaluations_count)


# Uncomment the line below to try your dfs_maximizing on an
# AbstractGameState representing the games tree "GAME1" from toytree.py:
# pretty_print_dfs_type(dfs_maximizing(GAME1))

def minimax_endgame_search(state, maximize=True) :
    """Performs minimax search, searching all leaf nodes and statically
    evaluating all endgame scores.  Same return type as dfs_maximizing."""
    
    # queue will track state, the path so far, and minimax player
    queue = [[state, [state], maximize]]

    # has the best option thus far
    best = []
    evaluations_count = 0

    # Loops till queue exhausted
    while queue:
        # Check if at leaf node and pop element
        if queue[0][0].is_game_over():
            evaluations_count += 1
            player = queue[0][2]


            if not best: 
                best = queue[0]
            if maximize:
                if player: # both true and true
                    if queue[0][0].get_endgame_score() > best[0].get_endgame_score():
                        best = queue[0]
                else:
                    if queue[0][0].get_endgame_score() < best[0].get_endgame_score():
                        best = queue[0] 
            else:
                if not player: # both false and false
                    if queue[0][0].get_endgame_score() < best[0].get_endgame_score():
                        best = queue[0] 
                else:
                    if queue[0][0].get_endgame_score() > best[0].get_endgame_score():
                        best = queue[0]

            # if player == True and maximize == True:
            #     if queue[0][0].get_endgame_score() > best[0].get_endgame_score():
            #         best = queue[0]
            # elif player == False and maximize == False:
            #     if queue[0][0].get_endgame_score() < best[0].get_endgame_score():


            # queue[0][0].get_endgame_score() > best[0].get_endgame_score():
            #     best = queue[0]
            queue.pop(0) 
        else:
            # pop and replace the first elements of the queue
            possible_states = queue[0][0].generate_next_states()
            steps_so_far = queue[0][1]
            curr_player = queue[0][2]
            queue.pop(0)

            new_states = []
            for s in possible_states:
                new_steps = steps_so_far.copy()
                new_steps.append(s)
                new_states.append([s, new_steps, not curr_player])
            
            queue = new_states + queue

    return (best[1], best[0].get_endgame_score(maximize), evaluations_count)



# Uncomment the line below to try your minimax_endgame_search on an
# AbstractGameState representing the ConnectFourBoard "NEARLY_OVER" from boards.py:

pretty_print_dfs_type(minimax_endgame_search(state_NEARLY_OVER))


def minimax_search(state, heuristic_fn=always_zero, depth_limit=INF, maximize=True) :
    """Performs standard minimax search. Same return type as dfs_maximizing."""
    raise NotImplementedError


# Uncomment the line below to try minimax_search with "BOARD_UHOH" and
# depth_limit=1. Try increasing the value of depth_limit to see what happens:

# pretty_print_dfs_type(minimax_search(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=1))


def minimax_search_alphabeta(state, alpha=-INF, beta=INF, heuristic_fn=always_zero,
                             depth_limit=INF, maximize=True) :
    """"Performs minimax with alpha-beta pruning. Same return type 
    as dfs_maximizing."""
    raise NotImplementedError


# Uncomment the line below to try minimax_search_alphabeta with "BOARD_UHOH" and
# depth_limit=4. Compare with the number of evaluations from minimax_search for
# different values of depth_limit.

# pretty_print_dfs_type(minimax_search_alphabeta(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4))


def progressive_deepening(state, heuristic_fn=always_zero, depth_limit=INF,
                          maximize=True) :
    """Runs minimax with alpha-beta pruning. At each level, updates anytime_value
    with the tuple returned from minimax_search_alphabeta. Returns anytime_value."""
    raise NotImplementedError


# Uncomment the line below to try progressive_deepening with "BOARD_UHOH" and
# depth_limit=4. Compare the total number of evaluations with the number of
# evaluations from minimax_search or minimax_search_alphabeta.

# progressive_deepening(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4).pretty_print()


# Progressive deepening is NOT optional. However, you may find that 
#  the tests for progressive deepening take a long time. If you would
#  like to temporarily bypass them, set this variable False. You will,
#  of course, need to set this back to True to pass all of the local
#  and online tests.
TEST_PROGRESSIVE_DEEPENING = True
if not TEST_PROGRESSIVE_DEEPENING:
    def not_implemented(*args): raise NotImplementedError
    progressive_deepening = not_implemented


#### Part 3: Multiple Choice ###################################################

ANSWER_1 = ''

ANSWER_2 = ''

ANSWER_3 = ''

ANSWER_4 = ''


#### SURVEY ###################################################

NAME = None
COLLABORATORS = None
HOW_MANY_HOURS_THIS_LAB_TOOK = None
WHAT_I_FOUND_INTERESTING = None
WHAT_I_FOUND_BORING = None
SUGGESTIONS = None
