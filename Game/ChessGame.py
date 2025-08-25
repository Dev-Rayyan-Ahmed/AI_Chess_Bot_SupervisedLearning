import pygame
import chess
from ChessBot import ChessBot,Stock

chess_bot = ChessBot()
stockfish = Stock()

pygame.init()
WIDTH, HEIGHT = 600, 600
SQ_SIZE = WIDTH // 8
WHITE = (238, 238, 210) #Color COde
BLACK = (118, 150, 86)
HIGHLIGHT_COLOR = (186, 202, 68)

# Load chess pieces
PIECE_IMAGES = {}
# small for Black; Capital for White
PIECE_NAMES = {
    "p": "black_pawn", "r": "black_rook", "n": "black_knight", "b": "black_bishop",
    "q": "black_queen", "k": "black_king",
    "P": "white_pawn", "R": "white_rook", "N": "white_knight", "B": "white_bishop",
    "Q": "white_queen", "K": "white_king"
}

for piece, filename in PIECE_NAMES.items():
    PIECE_IMAGES[piece] = pygame.transform.scale(
        pygame.image.load(f"images/{filename}.png"), (SQ_SIZE, SQ_SIZE)
    )


# Initialize game
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
board = chess.Board()
selected_square = None  # Stores selected piece square
possible_moves = []  # Stores legal moves for the selected piece

def draw_board():
    """Draw the chessboard"""
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces():
    """Draw chess pieces on the board"""
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)  # Convert (row, col) to chess library index
            piece = board.piece_at(square)
            if piece:
                screen.blit(PIECE_IMAGES[piece.symbol()], (col * SQ_SIZE, row * SQ_SIZE))

def highlight_moves():
    for move in possible_moves:
        to_square = move.to_square
        row, col = 7 - (to_square // 8), to_square % 8
        pygame.draw.circle(screen, HIGHLIGHT_COLOR, (col * SQ_SIZE + SQ_SIZE // 2, row * SQ_SIZE + SQ_SIZE // 2), 10)

def get_legal_moves(square):
    return [move for move in board.legal_moves if move.from_square == square]

def handle_click(pos):
    """Handle user mouse clicks for selecting and moving pieces, including pawn promotion"""
    global selected_square, possible_moves

    col, row = pos[0] // SQ_SIZE, pos[1] // SQ_SIZE
    clicked_square = chess.square(col, 7 - row)

    if selected_square is None:
        # Select piece if it's the player's turn
        piece = board.piece_at(clicked_square)
        if piece and (piece.color == board.turn):
            selected_square = clicked_square
            possible_moves = get_legal_moves(selected_square)
    else:
        # Check if the selected piece is a pawn reaching the last rank for promotion
        piece = board.piece_at(selected_square)
        if piece and piece.piece_type == chess.PAWN and (chess.square_rank(clicked_square) in [0, 7]):
            move = chess.Move(selected_square, clicked_square, promotion=chess.QUEEN)  # Promote to a queen
        else:
            move = chess.Move(selected_square, clicked_square)

        if move in board.legal_moves:
            board.push(move)

        selected_square, possible_moves = None, []  # Reset selection

def show_game_over_screen(result):
    """Display game over message and freeze game until restarted."""
    font = pygame.font.SysFont('Arial', 50)

    if result == "checkmate":
        font.set_bold(True)
        statement_ = font.render(f"{('White Won' if outcome.winner == chess.WHITE else 'Black Won' if outcome.winner == chess.BLACK else 'Draw')}", True, (255, 0, 0))
        text = font.render(f"{str(board.outcome().termination).strip("Termination.")}", True, (255, 0, 0))
    elif result == "stalemate":
        text = font.render("STALEMATE!", True, (200, 200, 0))
    else:
        text = font.render("GAME OVER", True, (255, 255, 255))

    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

    # StateMent Rect
    StateMent_Rect = statement_.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70))
    screen.blit(statement_, StateMent_Rect)

    # Restart Prompt
    small_font = pygame.font.SysFont('Arial', 30)
    small_font.set_bold(True)
    restart_text = small_font.render("Press R to restart", True, (200, 200, 200))
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
    screen.blit(restart_text, restart_rect)

    pygame.display.flip()

    # **Freeze game until user presses "R" to restart**
    game_over = True
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Press 'R' to restart
                    board.reset()
                    return  # Exit the function and continue the main loop

# Main loop
running = True
while running:
    draw_board()
    draw_pieces()
    highlight_moves()
    pygame.display.flip()

    if board.turn == chess.BLACK:
        # Ai_move = AI_makesMove(board)
        Ai_move = chess_bot.predict(board)

        if Ai_move is None:
            outcome = board.outcome()
            print(f"GAME OVER: {('White' if outcome.winner == chess.WHITE else 'Black' if outcome.winner == chess.BLACK else 'Draw')} WON, Reason: {outcome.termination}")
            show_game_over_screen("checkmate")
        else:
            print(Ai_move)
            board.push(Ai_move)

    # Change it to True to Do AI Vs AI
    Bot_vs_Stock = True
    if Bot_vs_Stock:
        if board.turn == chess.WHITE:

            Ai_move = stockfish.predict(board)

            if Ai_move is None:
                outcome = board.outcome()
                print(f"GAME OVER: {('White' if outcome.winner == chess.WHITE else 'Black' if outcome.winner == chess.BLACK else 'Draw')} WON, Reason: {outcome.termination}")
                show_game_over_screen("checkmate")
            else:
                Ai_move = chess.Move.from_uci(Ai_move)
                board.push(Ai_move)

    ###################################

    if board.is_game_over():
        outcome = board.outcome()
        if outcome.termination == chess.Termination.CHECKMATE:
            show_game_over_screen("checkmate")
        elif outcome.termination == chess.Termination.STALEMATE:
            show_game_over_screen("stalemate")
        else:
            show_game_over_screen("gameover")
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_click(event.pos)

pygame.quit()
