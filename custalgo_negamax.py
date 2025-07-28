# custalgo_negamax.py
def negamax(board, player, depth, evaluate, generate_moves, is_valid_move, make_move, undo_move):
    color = 1 if player == 'white' else -1

    def search(b, d, color_sign):
        if d == 0:
            return color_sign * evaluate(b, player), None
        best_score = -float('inf')
        best_move = None
        moves = generate_moves(b, player)
        for move in moves:
            if not is_valid_move(b, move, player):
                continue
            sr, sc = move['from']
            er, ec = move['to']
            captured = b[er][ec]
            make_move(b, move)
            score, _ = search(b, d - 1, -color_sign)
            undo_move(b, move, captured)
            score = -score
            if score > best_score:
                best_score = score
                best_move = move
        return best_score, best_move

    _, move = search(board, depth, color)
    return move

def get_negamax_ai_move(board, player, depth, generate_moves, is_valid_move, make_move, undo_move):
    # Simple evaluation: material only
    piece_values = {'p': 1, 'h': 3, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}
    def evaluate(b, wrt_player):
        score = 0
        for row in b:
            for p in row:
                if p:
                    color, desc = p.split("(")
                    val = piece_values.get(desc[0].lower(), 0)
                    if color == wrt_player:
                        score += val
                    else:
                        score -= val
        return score
    return negamax(board, player, depth, evaluate, generate_moves, is_valid_move, make_move, undo_move)
