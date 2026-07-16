def print_board(board):
    """
    Affiche le plateau de jeu actuel.
    Les positions sont numérotées de 1 à 9 pour faciliter l'entrée utilisateur.
    """
    print(f"\n {board[0] if board[0] != ' ' else '1'} | {board[1] if board[1] != ' ' else '2'} | {board[2] if board[2] != ' ' else '3'}")
    print("---+---+---")
    print(f" {board[3] if board[3] != ' ' else '4'} | {board[4] if board[4] != ' ' else '5'} | {board[5] if board[5] != ' ' else '6'}")
    print("---+---+---")
    print(f" {board[6] if board[6] != ' ' else '7'} | {board[7] if board[7] != ' ' else '8'} | {board[8] if board[8] != ' ' else '9'}\n")

def get_player_move(player, board):
    """
    Demande au joueur actuel de choisir une case et valide l'entrée.
    Retourne l'indice (0-8) de la case choisie.
    """
    while True:
        try:
            prompt = f"Joueur {player}, choisissez votre case (1-9) : "
            move = input(prompt)
            position = int(move) - 1  # Convertir l'entrée 1-9 en indice 0-8

            if not (0 <= position < 9):
                print("Entrée invalide. Veuillez entrer un nombre entre 1 et 9.")
            elif board[position] != ' ':
                print("Cette case est déjà occupée ! Choisissez une autre.")
            else:
                return position
        except ValueError:
            print("Entrée invalide. Veuillez entrer un nombre.")

def check_win(board, player):
    """
    Vérifie si le joueur actuel a gagné.
    """
    winning_combinations = [
        # Lignes
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        # Colonnes
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        # Diagonales
        [0, 4, 8], [2, 4, 6]
    ]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] == player:
            return True
    return False

def check_draw(board):
    """
    Vérifie si toutes les cases sont remplies (match nul).
    """
    return ' ' not in board

def play_game():
    """
    Fonction principale pour gérer le déroulement du jeu de morpion.
    """
    board = [' '] * 9  # Initialise un plateau vide
    current_player = 'X'
    game_over = False

    print("Bienvenue au Morpion !")
    print("Joueur X commence, puis Joueur O.")
    print("Entrez un nombre de 1 à 9 pour placer votre marqueur.")
    
    while not game_over:
        print_board(board)
        
        position = get_player_move(current_player, board)
        board[position] = current_player

        if check_win(board, current_player):
            print_board(board)
            print(f"Félicitations ! Le joueur {current_player} a gagné !")
            game_over = True
        elif check_draw(board):
            print_board(board)
            print("Match nul ! Personne n'a gagné.")
            game_over = True
        else:
            # Changer de joueur
            current_player = 'O' if current_player == 'X' else 'X'
    
    print("Fin de la partie.")

if __name__ == "__main__":
    play_game()