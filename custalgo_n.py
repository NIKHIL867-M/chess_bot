import heapq
import itertools

# --- Constants and Piece Values ---
PIECE_VALUES = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 1000}

# --- Move Ordering Heuristic ---
def move_order_score(move, board, player):
    from_sq, to_sq = move['from'], move['to']
    moving_piece = board[from_sq[0]][from_sq[1]]
    taken_piece = board[to_sq[0]][to_sq[1]]
    score = 0
    if taken_piece:
        score += PIECE_VALUES.get(taken_piece.upper(), 0) * 10 - PIECE_VALUES.get(moving_piece.upper(), 0)
    if move.get('promotion'):
        score += 80
    return score

# --- Board Evaluation ---
def evaluate_board(board, player):
    score = 0
    for row in board:
        for piece in row:
            if piece:
                value = PIECE_VALUES.get(piece.upper(), 0)
                # Use .startswith() to compare player color correctly
                if piece.startswith(player):
                    score += value
                else:
                    score -= value
    return score

# --- Alpha-Beta Pruning with Heap and tie-break counter ---
def alpha_beta_with_heap(board, depth, alpha, beta, maximizing_player, player,
                         generate_all_moves, is_valid_move, make_move, undo_move):
    if depth <= 0:
        return evaluate_board(board, player), None

    best_move = None
    move_heap = []
    counter = itertools.count()  # tie breaker

    all_moves = generate_all_moves(board, player)

    for move in all_moves:
        if not is_valid_move(board, move, player):
            continue
        score = move_order_score(move, board, player)
        heapq.heappush(move_heap, (-score, next(counter), move))

    while move_heap:
        _, _, move = heapq.heappop(move_heap)
        sr, sc = move['from']
        er, ec = move['to']
        captured_piece = board[er][ec]  # Save the captured piece
        make_move(board, move)
        new_score, _ = alpha_beta_with_heap(
            board, depth - 1, alpha, beta, not maximizing_player,
            'black' if player == 'white' else 'white',
            generate_all_moves, is_valid_move, make_move, undo_move
        )
        undo_move(board, move, captured_piece)  # Restore the captured piece

        if maximizing_player:
            if new_score > alpha:
                alpha = new_score
                best_move = move
        else:
            if new_score < beta:
                beta = new_score
                best_move = move
        if beta <= alpha:
            break  # Prune

    return (alpha if maximizing_player else beta), best_move

# --- Main AI Entry ---
def get_ai_move(board, player, depth, generate_all_moves, is_valid_move, make_move, undo_move):
    _, best_move = alpha_beta_with_heap(
        board, depth, float('-inf'), float('inf'), True, player,
        generate_all_moves, is_valid_move, make_move, undo_move
    )
    return best_move
