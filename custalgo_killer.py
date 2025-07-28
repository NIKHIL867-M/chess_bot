# custalgo_killer.py – Killer Move Search Chess AI

import time
import copy

INFINITY = float('inf')
KILLER_MOVES = {}  # {depth: [killer1, killer2]}

def killer_iterative_deepening(board, max_time, get_legal_moves, make_move, undo_move, evaluate, max_depth=5):
    global KILLER_MOVES
    KILLER_MOVES = {}
    start_time = time.time()
    best_move = None

    for depth in range(1, max_depth + 1):
        move, _ = killer_alpha_beta(
            board, depth, -INFINITY, INFINITY,
            True, get_legal_moves, make_move, undo_move, evaluate,
            start_time, max_time
        )
        if move:
            best_move = move
        if time.time() - start_time >= max_time:
            break
    return best_move

def killer_alpha_beta(board, depth, alpha, beta, maximizing_player,
                     get_legal_moves, make_move, undo_move, evaluate,
                     start_time, max_time, current_depth=0):
    if time.time() - start_time >= max_time:
        return None, 0

    if depth == 0:
        return None, evaluate(board)

    best_move = None
    moves = get_legal_moves(board)
    killers = KILLER_MOVES.get(current_depth, [])
    ordered_moves = killers + [m for m in moves if m not in killers]

    if maximizing_player:
        max_eval = -INFINITY
        for move in ordered_moves:
            sr, sc = move['from']
            er, ec = move['to']
            captured_piece = board[er][ec]
            make_move(board, move)
            _, eval_score = killer_alpha_beta(
                board, depth - 1, alpha, beta, False,
                get_legal_moves, make_move, undo_move, evaluate,
                start_time, max_time, current_depth + 1
            )
            undo_move(board, move, captured_piece)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            if max_eval > alpha:
                alpha = max_eval
            if alpha >= beta:
                # Store killer move
                if current_depth not in KILLER_MOVES:
                    KILLER_MOVES[current_depth] = []
                if move not in KILLER_MOVES[current_depth]:
                    KILLER_MOVES[current_depth].append(move)
                    KILLER_MOVES[current_depth] = KILLER_MOVES[current_depth][:2]
                break
        return best_move, max_eval
    else:
        min_eval = INFINITY
        for move in ordered_moves:
            sr, sc = move['from']
            er, ec = move['to']
            captured_piece = board[er][ec]
            make_move(board, move)
            _, eval_score = killer_alpha_beta(
                board, depth - 1, alpha, beta, True,
                get_legal_moves, make_move, undo_move, evaluate,
                start_time, max_time, current_depth + 1
            )
            undo_move(board, move, captured_piece)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            if min_eval < beta:
                beta = min_eval
            if alpha >= beta:
                # Store killer move
                if current_depth not in KILLER_MOVES:
                    KILLER_MOVES[current_depth] = []
                if move not in KILLER_MOVES[current_depth]:
                    KILLER_MOVES[current_depth].append(move)
                    KILLER_MOVES[current_depth] = KILLER_MOVES[current_depth][:2]
                break
        return best_move, min_eval

# Example usage wrapper
def get_killer_ai_move(
    board, player, depth, generate_all_moves, is_valid_move, make_move, undo_move,
    max_time=2.0, eval_fn=None
):
    """Replacement for get_ai_move, using killer algorithm and iterative deepening."""
    # You likely already have an evaluate function or can define:
    if eval_fn is None:
        def eval_fn(b):
            # Just simple count, you can plug your own.
            PIECE_VALUES = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 1000}
            score = 0
            for row in b:
                for piece in row:
                    if piece:
                        value = PIECE_VALUES.get(piece.upper(), 0)
                        if piece.startswith(player):
                            score += value
                        else:
                            score -= value
            return score

    # Provide "get_legal_moves" where only moves for 'player' are generated:
    def get_legal_moves_for_player(b):
        return generate_all_moves(b, player)

    # Support make/undo with captured pieces
    def move_maker(b, m):
        sr, sc = m['from']
        er, ec = m['to']
        b[er][ec] = b[sr][sc]
        b[sr][sc] = None

    def undo_maker(b, m, captured):
        sr, sc = m['from']
        er, ec = m['to']
        b[sr][sc] = b[er][ec]
        b[er][ec] = captured

    return killer_iterative_deepening(
        board, max_time, get_legal_moves_for_player, move_maker, undo_maker, eval_fn, max_depth=depth
    )
