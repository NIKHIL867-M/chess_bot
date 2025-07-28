from custalgo_n import get_ai_move

def is_valid_move(board, start, end, turn, en_passant_target=None, castling_rights=None):
    sr, sc = start
    er, ec = end
    piece = board[sr][sc]
    target = board[er][ec]

    if not piece or not piece.startswith(turn):
        return False

    name = piece[piece.index('(')+1]  # get 'p', 'r', etc.
    dr, dc = er - sr, ec - sc
    abs_dr, abs_dc = abs(dr), abs(dc)

    # Don't allow capture of same color
    if target and target.startswith(turn):
        return False

    # Pawn
    if name == 'p':
        direction = -1 if turn == 'white' else 1
        start_row = 6 if turn == 'white' else 1
        promotion_row = 0 if turn == 'white' else 7

        # Standard move forward
        if dc == 0:
            # Single step forward
            if dr == direction and not target:
                return True
            # Double step from starting position
            if sr == start_row and dr == 2*direction and not target and not board[sr+direction][sc]:
                return True
        
        # Capture diagonally
        elif abs_dc == 1 and dr == direction:
            # Normal capture
            if target:
                return True
            # En passant
            if en_passant_target and (er, ec) == en_passant_target:
                return True

    # Rook
    elif name == 'r':
        if (sr == er or sc == ec) and (sr != er or sc != ec):
            return is_clear_path(board, start, end)

    # Knight
    elif name == 'h':
        return (abs_dr, abs_dc) in [(1, 2), (2, 1)]

    # Bishop
    elif name == 'b':
        if abs_dr == abs_dc and abs_dr > 0:
            return is_clear_path(board, start, end)

    # Queen
    elif name == 'q':
        if (sr == er or sc == ec or abs_dr == abs_dc) and (sr != er or sc != ec):
            return is_clear_path(board, start, end)

    # King
    elif name == 'k':
        if max(abs_dr, abs_dc) == 1:
            return True
        
        # Castling
        if abs(dc) == 2 and dr == 0:
            # Kingside castling
            if dc > 0:
                if castling_rights and castling_rights.get(f'{turn}_kingside', False):
                    if is_clear_path(board, start, (sr, sc+2)):
                        for col in [sc, sc+1, sc+2]:
                            if is_square_under_attack(board, (sr, col), 'black' if turn == 'white' else 'white'):
                                return False
                        return True
            # Queenside castling
            else:
                if castling_rights and castling_rights.get(f'{turn}_queenside', False):
                    if is_clear_path(board, start, (sr, sc-2)):
                        for col in [sc, sc-1, sc-2]:
                            if is_square_under_attack(board, (sr, col), 'black' if turn == 'white' else 'white'):
                                return False
                        return True

    return False

def is_clear_path(board, start, end):
    sr, sc = start
    er, ec = end
    dr = er - sr
    dc = ec - sc
    step_r = 1 if dr > 0 else (-1 if dr < 0 else 0)
    step_c = 1 if dc > 0 else (-1 if dc < 0 else 0)

    r, c = sr + step_r, sc + step_c
    while (r, c) != (er, ec):
        if board[r][c]:
            return False
        r += step_r
        c += step_c
    return True

def is_square_under_attack(board, pos, by_color):
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.startswith(by_color):
                if is_valid_move(board, (r, c), pos, by_color):
                    return True
    return False

def get_all_valid_moves(board, pos, turn, en_passant_target=None, castling_rights=None):
    moves = []
    for r in range(8):
        for c in range(8):
            if is_valid_move(board, pos, (r, c), turn, en_passant_target, castling_rights):
                # Check if move would leave king in check
                temp_board = [row[:] for row in board]
                make_move(temp_board, pos, (r, c), turn, en_passant_target, castling_rights)
                if not is_king_in_check(temp_board, turn):
                    moves.append((r, c))
    return moves

def get_all_player_moves(board, player, en_passant_target=None, castling_rights=None):
    moves = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.startswith(player):
                pos_moves = get_all_valid_moves(board, (r, c), player, en_passant_target, castling_rights)
                for dest in pos_moves:
                    moves.append({'from': (r, c), 'to': dest})
    return moves

def make_move(board, start, end, turn, en_passant_target=None, castling_rights=None):
    sr, sc = start
    er, ec = end
    piece = board[sr][sc]
    name = piece[piece.index('(')+1]
    
    # Handle en passant
    if name == 'p' and abs(sc - ec) == 1 and not board[er][ec] and (er, ec) == en_passant_target:
        captured_row = er + 1 if turn == 'white' else er - 1
        board[captured_row][ec] = None
    
    # Handle castling
    if name == 'k' and abs(sc - ec) == 2:
        if ec > sc:
            board[er][ec-1] = board[er][7]
            board[er][7] = None
        else:
            board[er][ec+1] = board[er][0]
            board[er][0] = None
    
    # Handle pawn promotion
    if name == 'p' and er in [0, 7]:
        piece = f"{turn}(q)"
    
    board[er][ec] = piece
    board[sr][sc] = None

def is_king_in_check(board, color):
    king_pos = None
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.startswith(color) and piece[piece.index('(')+1] == 'k':
                king_pos = (r, c)
                break
        if king_pos:
            break
    
    if not king_pos:
        return False
    
    return is_square_under_attack(board, king_pos, 'black' if color == 'white' else 'white')

def update_castling_rights(castling_rights, piece, start_pos):
    if piece.endswith('k)'):
        castling_rights[f"{piece.split('(')[0]}_kingside"] = False
        castling_rights[f"{piece.split('(')[0]}_queenside"] = False
    elif piece.endswith('r)'):
        _, sc = start_pos
        color = piece.split('(')[0]
        if sc == 0:
            castling_rights[f"{color}_queenside"] = False
        elif sc == 7:
            castling_rights[f"{color}_kingside"] = False
    return castling_rights
