import socket
import struct

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def recibir_imagen(client_socket):
    header = recvall(client_socket, 8)
    if not header:
        return None
    (length,) = struct.unpack('!Q', header)
    return recvall(client_socket, length)

def enviar_imagen_bytes(imagen_bytes, client_socket):
    header = struct.pack('!Q', len(imagen_bytes))
    client_socket.sendall(header + imagen_bytes)
    print("Imagen enviada al cliente")
    client_socket.close()

host = '192.168.1.90'
port = 8080
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))
server_socket.listen(5)
print(f"Servidor escuchando en {host}:{port}")
print("Esperando conexión de cliente...")

while True:
    client_socket, addr = server_socket.accept()
    print(f"Conexión desde {addr}")
    imagen_bytes = recibir_imagen(client_socket)
    if not imagen_bytes:
        print("No se recibió imagen o conexión cerrada.")
        client_socket.close()
        continue

    with open('imagen_recibida.jpg', 'wb') as f:
        f.write(imagen_bytes)
    print("Imagen recibida y guardada como 'imagen_recibida.jpg'")

    print("Enviando imagen de regreso...")
    enviar_imagen_bytes(imagen_bytes, client_socket)

