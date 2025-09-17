import socket
import os
import struct
import cryptography.fernet as fernet

key = 'keys/key.key'
host = '148.220.209.122'
port = 8080

def get_key(key_path):
    if not os.path.exists(key_path):
        key = fernet.Fernet.generate_key()
        with open(key_path, 'wb') as key_file:
            key_file.write(key)
        print("Nueva clave generada")
    with open(key_path, 'rb') as key_file:
        return key_file.read()

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def recibir_bytes_encriptada(client_socket):
    header = recvall(client_socket, 8)
    if not header:
        return None
    (length,) = struct.unpack('!Q', header)
    return recvall(client_socket, length)

def enviar_bytes_encriptados(imagen_bytes, client_socket):
    header = struct.pack('!Q', len(imagen_bytes))
    client_socket.sendall(header + imagen_bytes)
    print("Imagen enviada al cliente")
    client_socket.close()

def main():
    key_value = get_key(key)
    f = fernet.Fernet(key_value)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor escuchando en {host}:{port}")
    print("Esperando conexión de cliente...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Conexión desde {addr}")
        try:
            imagen_bytes = recibir_bytes_encriptada(client_socket)
            if not imagen_bytes:
                print("No se recibió imagen o conexión cerrada.")
                client_socket.close()
                continue
            try:
                imagen_bytes = f.decrypt(imagen_bytes)
            except Exception as e:
                print(f"Error al desencriptar la imagen: {e}")
                client_socket.close()
                continue
            
            with open('imagen_recibida.jpg', 'wb') as img_f:
                img_f.write(imagen_bytes)
            print("Imagen recibida y guardada como 'imagen_recibida.jpg'")

            encrypt_back = f.encrypt(imagen_bytes)
            print("Enviando imagen de regreso...")
            enviar_bytes_encriptados(encrypt_back, client_socket)
        finally:
            client_socket.close()
            print("Conexión cerrada")
            
if __name__ == "__main__":
    main()