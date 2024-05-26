import socket

# Configuration
HOST = 'localhost'
PORT = 12345

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        
        while True:
            response = client_socket.recv(1024).decode()
            if response:
                print(response, end='')

            if 'Goodbye!' in response:
                break

            message = input()
            client_socket.sendall(message.encode())

if __name__ == '__main__':
    main()
