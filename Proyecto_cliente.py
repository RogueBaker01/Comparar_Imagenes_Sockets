import socket
import struct
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
from cryptography.fernet import Fernet   

key_file = 'keys/key.key'
imagen = 'imagenes/gato.jpeg'
host = '148.220.215.19'
port = 8080

def get_key(key_path):
    if not os.path.exists(key_path):
        key = Fernet.generate_key()   
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        with open(key_path, 'wb') as f:
            f.write(key)
        print("Nueva clave generada")
    with open(key_path, 'rb') as f:
        return f.read()

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def enviar_imagen_cifrada(imagen_path, sock, key):
    with open(imagen_path, 'rb') as file:
        imagen_data = file.read()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(imagen_data)
    header = struct.pack('!Q', len(encrypted))
    sock.sendall(header + encrypted)
    print("Imagen cifrada enviada al servidor")

def recibir_respuesta(sock):
    header = recvall(sock, 8)
    if not header:
        print("No se recibió respuesta del servidor")
        return None
    (length,) = struct.unpack('!Q', header)
    data = recvall(sock, length)
    return data

def comparar_imagenes(imagen1_path, imagen2_bytes):
    imagen1 = cv2.imread(imagen1_path)
    nparr = np.frombuffer(imagen2_bytes, np.uint8)
    imagen2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if imagen1 is None or imagen2 is None:
        print("Error al cargar las imágenes para comparación")
        return

    grayA = cv2.cvtColor(imagen1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imagen2, cv2.COLOR_BGR2GRAY)

    s = ssim(grayA, grayB)
    m = mse(grayA, grayB)
    msg = ""
    
    if isinstance(s, tuple):
        s = s[0]

    if s == 1.0:
        msg = "Las imágenes son idénticas"
    elif s > 0.8:
        msg = "Las imágenes son muy similares"
    elif s > 0.5:
        msg = "Las imágenes son parecidas"
    else:
        msg = "Las imágenes son diferentes"

    if m == 0.0:
        msg += " y no hay diferencia de error (MSE=0)"
    elif m < 100:
        msg += f" con un error mínimo (MSE={m:.2f})"
    elif m < 1000:
        msg += f" con un error moderado (MSE={m:.2f})"
    else:
        msg += f" con un error alto (MSE={m:.2f})"

    print(msg)

    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    axs[0].imshow(cv2.cvtColor(imagen1, cv2.COLOR_BGR2RGB))
    axs[0].set_title("Imagen Original")
    axs[0].axis("off")

    axs[1].imshow(cv2.cvtColor(imagen2, cv2.COLOR_BGR2RGB))
    axs[1].set_title("Imagen Recibida")
    axs[1].axis("off")

    fig.suptitle(f"SSIM: {s:.4f} | MSE: {m:.2f}", fontsize=14)
    fig.text(0.5, 0.02, f"SSIM: {s:.4f}    MSE: {m:.2f}", ha='center', fontsize=12)
    plt.show()

def mse(imagenA, imagenB):
    err = np.sum((imagenA.astype("float") - imagenB.astype("float")) ** 2)
    err /= float(imagenA.shape[0] * imagenA.shape[1])
    return err

def main():
    key = get_key(key_file)
    f = Fernet(key)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    if client_socket:
        print("Conexión exitosa al servidor")
        enviar_imagen_cifrada(imagen, client_socket, key)
        print("Esperando imagen de regreso...")
        
        respuesta = recibir_respuesta(client_socket)
        if not respuesta:
            print("No se recibió respuesta del servidor")
        else:
            decrypted = f.decrypt(respuesta)
            comparar_imagenes(imagen, decrypted)
            
    else:
        print("Error al conectar con el servidor")
        client_socket.close()

if __name__ == "__main__":
    main()
