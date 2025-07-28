# custalgo_meta.py

import random
import custalgo_n
import custalgo_killer
import custalgo_mcts
import custalgo_negamax


def evaluate_board(board, player):
    """
    Simple material-based evaluation for your 8x8 board array.
    Positive score means advantage for 'player'.
    """
    piece_values = {'p': 1, 'h': 3, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}
    score = 0
    for row in board:
        for p in row:
            if p:
                color, desc = p.split("(")
                value = piece_values.get(desc[0].lower(), 0)
                if color == player:
                    score += value
                else:
                    score -= value
    return score


# Configuration of your AI modules and their selection weights
ALGO_CONFIG = [
    {"module": custalgo_n, "weight": 0.4},
    {"module": custalgo_killer, "weight": 0.3},
    {"module": custalgo_mcts, "weight": 0.2},
    {"module": custalgo_negamax, "weight": 0.1},
    # Add more algorithms here as you develop them
]


def get_ai_move(board, player, depth, generate_all_moves, is_valid_move, make_move, undo_move, return_score=False):
    """
    Meta AI that asks all configured AI algorithms for their move,
    evaluates moves, and picks the best by weighted randomness.

    Returns chosen move as {'from': (row,col), 'to': (row,col)} or (move, score) if return_score=True.
    """
    scored_moves = []
    
    for algo in ALGO_CONFIG:
        module = algo["module"]
        weight = algo["weight"]
        try:
            move = module.get_ai_move(
                board, player, depth, generate_all_moves,
                is_valid_move, make_move, undo_move
            )
            if not move:
                continue
            
            # Validate the move with your rules (extra safety)
            if not is_valid_move(board, move['from'], move['to'], player):
                continue
            
            # Apply move temporarily to evaluate resulting board
            sr, sc = move['from']
            er, ec = move['to']
            captured = board[er][ec]
            make_move(board, move)
            score = evaluate_board(board, player)
            undo_move(board, move, captured)
            
            scored_moves.append((score, move, weight))
            print(f"[{module.__name__}] Move: {move}, Score: {score:.2f}, Weight: {weight}")
        
        except Exception as e:
            print(f"[MetaSelector] Error in {module.__name__}: {e}")
    
    if not scored_moves:
        print("[MetaSelector] No valid moves from any algorithm.")
        if return_score:
            return None, 0
        else:
            return None
    
    # Sort moves descending by eval score (best first)
    scored_moves.sort(key=lambda x: x[0], reverse=True)
    top_n = min(3, len(scored_moves))
    top_moves = scored_moves[:top_n]
    
    moves = [entry[1] for entry in top_moves]
    weights = [entry[2] for entry in top_moves]
    
    chosen_move = random.choices(moves, weights=weights, k=1)[0]
    
    if return_score:
        for score, move, _ in scored_moves:
            if move == chosen_move:
                return chosen_move, score
        return chosen_move, 0
    else:
        print(f"[MetaSelector] Final chosen move: {chosen_move}")
        return chosen_move
