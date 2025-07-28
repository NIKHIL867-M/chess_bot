# custalgo_mcts.py
import random
import math
import chess
import chess.syzygy

# Optional: Set to your Syzygy tablebase path or None if unavailable
TABLEBASE_PATH = None  
try:
    tablebase = chess.syzygy.open_tablebase(TABLEBASE_PATH) if TABLEBASE_PATH else None
except Exception:
    tablebase = None

def to_pythonchess_board(board_array, turn="white"):
    """
    Convert your custom 8x8 board array to python-chess Board object.
    Your board: (0,0) = top-left, python-chess expects rank 8 at top.
    """
    piece_map = {'p': 'p', 'r': 'r', 'h': 'n', 'n': 'n', 'b': 'b', 'q': 'q', 'k': 'k'}
    rows_fen = []
    
    # Process rows from top to bottom (rank 8 to rank 1 in chess notation)
    for row in board_array:
        fen_row = ""
        empty_count = 0
        for piece in row:
            if piece is None:
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                try:
                    color, descr = piece.split("(")
                    name = descr[0].lower()
                    fen_piece = piece_map.get(name, '?')
                    fen_row += fen_piece.upper() if color == "white" else fen_piece.lower()
                except Exception:
                    fen_row += '?'
        if empty_count > 0:
            fen_row += str(empty_count)
        rows_fen.append(fen_row)
    
    fen_position = "/".join(rows_fen)
    fen_turn = 'w' if turn == 'white' else 'b'
    fen = f"{fen_position} {fen_turn} - - 0 1"
    
    try:
        board = chess.Board(fen)
        return board
    except ValueError:
        return chess.Board()  # fallback to default position

def to_move_tuple(move):
    """
    Convert python-chess Move to your internal move dict format.
    
    Python-chess: square 0 = a1 (bottom-left), square 63 = h8 (top-right)
    Your board: (0,0) = top-left, (7,7) = bottom-right
    
    Need to flip the rank (row) coordinate.
    """
    from_rank, from_file = divmod(move.from_square, 8)
    to_rank, to_file = divmod(move.to_square, 8)
    
    # Convert python-chess ranks (0=bottom) to your array rows (0=top)
    from_row = 7 - from_rank
    to_row = 7 - to_rank
    
    return {'from': (from_row, from_file), 'to': (to_row, to_file)}

class Node:
    def __init__(self, board, parent=None, move=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0

    def is_fully_expanded(self):
        return len(self.children) == len(list(self.board.legal_moves))

    def best_child(self, c_param=1.4):
        def uct(child):
            if child.visits == 0:
                return float('inf')
            exploitation = child.wins / child.visits
            exploration = c_param * math.sqrt(math.log(self.visits) / child.visits)
            return exploitation + exploration
        if not self.children:
            return None
        return max(self.children, key=uct)

def syzygy_score(board):
    if not tablebase or not board.is_valid() or board.is_game_over():
        return 0
    try:
        return tablebase.probe_wdl(board)
    except Exception:
        return 0

def select_promising_node(node):
    while node.children:
        node = node.best_child()
        if node is None:
            break
    return node

def expand_node(node):
    tried_moves = {child.move for child in node.children}
    for move in node.board.legal_moves:
        if move not in tried_moves:
            new_board = node.board.copy()
            new_board.push(move)
            child_node = Node(new_board, node, move)
            node.children.append(child_node)
            return child_node
    return node

def simulate_random_playout(node):
    board = node.board.copy()
    while not board.is_game_over():
        moves = list(board.legal_moves)
        if not moves:
            break
        best_move = None
        best_score = -float('inf')
        for move in moves:
            board.push(move)
            score = syzygy_score(board)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move
        board.push(best_move if best_move else random.choice(moves))
    return board.result()

def backpropagate(node, result):
    while node:
        node.visits += 1
        if (result == "1-0" and node.board.turn == chess.BLACK) or (result == "0-1" and node.board.turn == chess.WHITE):
            node.wins += 1
        elif result == "1/2-1/2":
            node.wins += 0.5
        node = node.parent

def hybrid_mcts(board_array, player_color, iterations=75):
    turn = "white" if player_color == "white" else "black"
    board = to_pythonchess_board(board_array, turn=turn)
    if board.is_game_over():
        return None
    
    root = Node(board)
    for _ in range(iterations):
        promising_node = select_promising_node(root)
        if promising_node is None or promising_node.board.is_game_over():
            continue
        node = expand_node(promising_node)
        result = simulate_random_playout(node)
        backpropagate(node, result)
    
    if not root.children:
        return None
    best_move = max(root.children, key=lambda c: c.visits).move
    return best_move

def get_mcts_ai_move(board, player, depth, generate_all_moves, is_valid_move, make_move, undo_move):
    """
    Main API function for MCTS AI with proper coordinate conversion.
    """
    if not board or not player or depth < 1:
        return None
    
    iterations = max(25, depth * 15)
    mcts_move = hybrid_mcts(board, player, iterations=iterations)
    
    if mcts_move is None:
        return None
    
    move_dict = to_move_tuple(mcts_move)
    
    # Additional validation using your rules (optional but recommended)
    try:
        if not is_valid_move(board, move_dict['from'], move_dict['to'], player):
            return None  # Return None if move is invalid per your rules
    except Exception:
        pass  # If validation fails, let game.py handle it
    
    return move_dict
