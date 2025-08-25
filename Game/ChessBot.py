import chess
import numpy as np
from tensorflow import keras
import json
from stockfish import Stockfish



class ChessBot:
    def __init__(self):
        self.pred_model = keras.models.load_model(r"C:\Users\PMLS\PycharmProjects\PyCharm_Coding_Env\.PROJECTS\Chess\Model_Training\Move_Predict_models\TF_50EPOCHS_15Limit.keras")
        self.eval_model = keras.models.load_model(r"C:\Users\PMLS\PycharmProjects\PyCharm_Coding_Env\.PROJECTS\Chess\Model_Training\Eval_models\chess_eval_model_on_40000_Epochs2.5Steps.keras")

        path = r"C:\Users\PMLS\PycharmProjects\PyCharm_Coding_Env\.PROJECTS\Chess\Model_Training\move_to_int_files\move_to_int_50_15.json"
        with open(path, "r") as file:
            self.move_to_int = json.load(file)

        ## StockFish
        self.stock = Stock()


    @staticmethod
    def board_to_matrix(board):
        matrix = np.zeros((8, 8, 12))
        piece_map = board.piece_map()

        for square, piece in piece_map.items():
            row, col = divmod(square, 8)

            # for channel selection

            piece_type = piece.piece_type - 1  # using zero-based channels
            piece_color = 0 if piece.color else 1

            channel = piece_type + piece_color

            matrix[row][col][channel] = 1
        return matrix

    def get_model_eval(self, board):
        matrix = self.board_to_matrix(board).reshape(1,8, 8, 12)
        score = self.eval_model.predict(matrix, verbose=0)[0][0]
        return score*100 # normalized while training, so returning back

    def predict(self, board, n_tops=5):

        if board.is_game_over():
            # print("Game Over")
            return None

        print("Prediction Model")
        board_matrix = ChessBot.board_to_matrix(board).reshape(1, 8, 8, 12)
        predictions = self.pred_model.predict(board_matrix)[0]

        legal_moves = list(board.legal_moves)
        legal_moves_uci = [move.uci() for move in legal_moves]

        ## Wrapper For Eval_Model
        print("Eval Model")
        # using get because some key might not be available, so we get None
        move_idx = [self.move_to_int.get(move) for move in legal_moves_uci]
        legal_predicted_moves = [(move, predictions[idx]) for move, idx in
                                 zip(legal_moves, move_idx) if idx is not None]

        legal_predicted_moves.sort(key=lambda x: x[1], reverse=True)
        top_moves = legal_predicted_moves[:n_tops]

        board_scores = []
        for move, prediction in legal_predicted_moves:
            board.push(move)

            stockfish_mode = True
            if stockfish_mode:
                board_scores.append(self.stock.get_stockfish_eval(board))
            else:
                board_scores.append(self.get_model_eval(board))

            board.pop()

        best_move_idx = np.argmin(board_scores)
        best_move, _ = legal_predicted_moves[best_move_idx]
        return best_move

class Stock:
    def __init__(self):
        self.stockfish = Stockfish(
            path=r"C:\Users\PMLS\PycharmProjects\PyCharm_Coding_Env\.PROJECTS\Chess\Model_Training\StockFish\stockfish_win\stockfish-windows-x86-64-avx2.exe",
            parameters={"Skill Level": 1}
        )

    def predict(self, board):
        if board.is_game_over():
            return None
        self.stockfish.set_fen_position(board.fen())
        move = self.stockfish.get_best_move(100)
        return move
    
    def get_stockfish_eval(self, board):
        fen = board.fen()
        self.stockfish.set_fen_position(fen)
        evaluation = self.stockfish.get_evaluation()

        if evaluation["type"] == "cp":
            return evaluation["value"]
        return 2000 if evaluation["value"] > 0 else -2000
    
    



# Simple Driver Code

chess_bot = ChessBot()
stockfish = Stock()

game_board = chess.Board()
eval_model_vals = {}
stock_evals = {}
for i in range(1,5):
    stock_move = stockfish.predict(game_board)
    game_board.push_uci(stock_move)

    print()
    print(game_board)
    print(f"Move: {i}")
    print("StockFish: ",stockfish.get_stockfish_eval(game_board))
    print("Eval_Model: ",chess_bot.get_model_eval(game_board))

    stock_evals[i] = stockfish.get_stockfish_eval(game_board)
    eval_model_vals[i] = chess_bot.get_model_eval(game_board)

print("Eval Model Evaluations per Move: ",eval_model_vals)
print("StockFish Evaluations per Move: ",stock_evals)

