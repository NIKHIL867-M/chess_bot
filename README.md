Custom Chess AI – Alpha-Beta with Heap-Based Move Ordering
Overview
This is a custom-built chess search algorithm that combines:

Alpha-Beta Pruning – Efficiently searches the move tree and prunes unpromising branches.

Heap-Based Move Ordering – Uses a priority queue to explore the most promising moves first.

MVV-LVA Captures & Promotion Priority – Tactical moves are searched before others for early cutoffs.

Modular Design – Works with your existing game logic (generate_all_moves, is_valid_move, make_move, undo_move).

This algorithm is meant for integration into a larger chess engine or as one component in a multi-algorithm chess bot.

Features
Reliable and Customizable: Core logic is clean, modular, and adaptable.

Efficient: Good move ordering improves alpha-beta pruning effectiveness.

Tactical Strength: Prioritizes captures and promotions.

Clear Structure: Easy to extend with iterative deepening, transposition tables, or better evaluation functions.

How It Works
Move Ordering Score

Uses MVV-LVA (Most Valuable Victim – Least Valuable Attacker) to rank capture moves.

Promotions are given a large bonus.

Heap Storage

Moves are pushed into a max-heap priority queue so the best-scoring moves are explored first.

Alpha-Beta Pruning

Reduces the number of positions evaluated by cutting off branches that cannot influence the final decision.

Material-Based Evaluation

Currently uses a simple material point system, but can be replaced with a more sophisticated evaluation function.

Usage
You need to provide four core functions from your engine logic:

python
generate_all_moves(board, player)
is_valid_move(board, move, player)
make_move(board, move)
undo_move(board, move)
Call the AI like this:

python
best_move = get_ai_move(board, 'white', depth=5,
    generate_all_moves=generate_all_moves,
    is_valid_move=is_valid_move,
    make_move=make_move,
    undo_move=undo_move)
Increasing Depth for Stronger Play
The depth parameter controls how many plies (half-moves) the search explores.

Deeper search = better decision-making (the AI sees further ahead).

For example:

Depth 3 → Fast but tactical strength is low.

Depth 6-8 → Stronger play, more calculation power.

Depth 10+ → Much better but requires optimizations for speed.

Adding iterative deepening, transposition tables, and better evaluation will let you push to depth 20+ efficiently.

Recommended Upgrades
Iterative Deepening – Improves move ordering and allows flexible time control.

Transposition Tables – Store evaluated positions to avoid re-calculations.

Quiescence Search – Avoids the horizon effect by extending tactical sequences.

Better Evaluation – Include factors like pawn structure, king safety, mobility.

License
This is your custom-made implementation and can be reused or modified for your chess bot projects.
