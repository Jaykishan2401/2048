import numpy as np
import numpy.random

number_of_cells = 16
cell_distribution = np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 4])

number_of_moves = 4
sample_count = 50
spm_scale_param = 10
sl_scale_param = 4
search_param = 200


def init_2048():
    board = np.zeros(number_of_cells, dtype="int")
    init_loc = numpy.random.default_rng().choice(number_of_cells, 2, replace=False)
    board[init_loc] = 2
    board = board.reshape(4, 4)

    return board


def pushRight(board):
    board_new = np.zeros((4, 4), dtype="int")
    done = False
    for row in range(4):
        count = 3
        for col in range(3, -1, -1):
            if board[row][col] != 0:
                board_new[row][count] = board[row][col]
                if col != count:
                    done = True
                count -= 1

    return board_new, done


def merge(board):
    score = 0
    done = False

    for row in range(4):
        for col in range(3, 0, -1):
            if board[row][col] == board[row][col - 1] and board[row][col] != 0:
                board[row][col] = board[row][col] + board[row][col]
                score += board[row][col]
                board[row][col - 1] = 0
                done = True

    return board, done, score


def get_search_params(move_number):
    searches_per_move = spm_scale_param * (1 + (move_number // search_param))
    search_length = sl_scale_param * (1 + (move_number // search_param))

    return searches_per_move, search_length


def moveUp(board):
    board = np.rot90(board, -1)
    board, push_done = pushRight(board)
    board, merge_done, score = merge(board)
    board, _ = pushRight(board)
    board = np.rot90(board)
    move_made = push_done or merge_done

    return board, move_made, score


def moveDown(board):
    board = np.rot90(board)
    board, push_done = pushRight(board)
    board, merge_done, score = merge(board)
    board, _ = pushRight(board)
    board = np.rot90(board, -1)
    move_made = push_done or merge_done

    return board, move_made, score


def moveRight(board):
    board, push_done = pushRight(board)
    board, merge_done, score = merge(board)
    board, _ = pushRight(board)
    move_made = push_done or merge_done

    return board, move_made, score


def moveLeft(board):
    board = np.rot90(board, 2)
    board, push_done = pushRight(board)
    board, merge_done, score = merge(board)
    board, _ = pushRight(board)
    board = np.rot90(board, -2)
    move_made = push_done or merge_done

    return board, move_made, score


def moveRandom(board):
    move_made = False
    move_order = [moveRight, moveUp, moveDown, moveLeft]
    while not move_made and len(move_order) > 0:
        move_index = np.random.randint(0, len(move_order))
        move = move_order[move_index]
        board, move_made, score = move(board)

        if move_made:
            return board, True, score
        move_order.pop(move_index)

    return board, False, score


def moveAI(board, searches_per_move, search_length):
    possible_moves = [moveLeft, moveUp, moveDown, moveRight]
    move_scores = np.zeros(number_of_moves)

    for move_index in range(number_of_moves):
        move_function = possible_moves[move_index]
        board_new, move_made, score_new = move_function(board)

        if move_made:
            board_new = addNewTile(board_new)
            move_scores += score_new

        else:
            continue

        for _ in range(searches_per_move):
            move_number = 1
            search_board = np.copy(board_new)
            game_valid = True

            while game_valid and move_number < search_length:
                search_board, game_valid, score_node = moveRandom(search_board)
                if game_valid:
                    search_board = addNewTile(search_board)
                    move_scores[move_index] += score_node
                    move_number += 1

    best_move_index = np.argmax(move_scores)
    best_move = possible_moves[best_move_index]
    board, game_valid, score = best_move(board)

    return board, game_valid, score


def addNewTile(board):
    cell_value = cell_distribution[np.random.randint(0, len(cell_distribution))]
    cell_row_options, cell_col_options = np.nonzero(np.logical_not(board))
    cell_loc = np.random.randint(0, len(cell_row_options))
    board[cell_row_options[cell_loc], cell_col_options[cell_loc]] = cell_value
    return board


def check_win(board):
    return 2048 in board


