import socket
import threading
import random
import json

# Configuration
HOST = 'localhost'
PORT = 12345
DATA_FILE = 'leaderboard.json'

# Load or initialize leaderboard
def load_leaderboard():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_leaderboard(leaderboard):
    with open(DATA_FILE, 'w') as file:
        json.dump(leaderboard, file, indent=4)

# Initialize leaderboard
leaderboard = load_leaderboard()

# Handle client connections
def handle_client(client_socket):
    client_name = None
    client_socket.sendall(b'Welcome to the Guessing Game!\n')
    
    while True:
        # Choose difficulty
        client_socket.sendall(b'Choose difficulty: easy (1-50), medium (1-100), hard (1-500)\n')
        client_socket.sendall(b'Enter easy/medium/hard: ')
        difficulty_choice = client_socket.recv(1024).decode().strip().lower()
        if difficulty_choice == 'medium':
            difficulty = 100
        elif difficulty_choice == 'hard':
            difficulty = 500
        else:
            difficulty = 50
        
        # Set the random number to guess
        number_to_guess = random.randint(1, difficulty)
        client_socket.sendall(f'Guess the number between 1 and {difficulty}:\n'.encode())

        # Game logic
        tries = 0
        while True:
            try:
                guess = int(client_socket.recv(1024).decode().strip())
                tries += 1
                if guess < number_to_guess:
                    client_socket.sendall(b'Higher!\n')
                elif guess > number_to_guess:
                    client_socket.sendall(b'Lower!\n')
                else:
                    client_socket.sendall(b'Congratulations! You guessed it!\n')
                    break
            except ValueError:
                client_socket.sendall(b'Invalid input. Please enter a number.\n')

        # Handle scoring and leaderboard
        if not client_name:
            client_socket.sendall(b'Enter your name: ')
            client_name = client_socket.recv(1024).decode().strip()
        
        leaderboard.append({'name': client_name, 'score': tries, 'difficulty': difficulty_choice})
        save_leaderboard(leaderboard)
        
        client_socket.sendall(b'Do you want to play again? (yes/no): ')
        if client_socket.recv(1024).decode().strip().lower() != 'yes':
            break

    # Send leaderboard
    sorted_leaderboard = sorted(leaderboard, key=lambda x: x['score'])
    client_socket.sendall(b'Leaderboard:\n')
    for entry in sorted_leaderboard:
        client_socket.sendall(f"{entry['name']} - {entry['score']} tries ({entry['difficulty']})\n".encode())
    
    client_socket.sendall(b'Goodbye!\n')
    client_socket.close()

# Main server loop
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f'Server listening on {HOST}:{PORT}')
    
    while True:
        client_socket, addr = server.accept()
        print(f'Connection from {addr}')
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()
