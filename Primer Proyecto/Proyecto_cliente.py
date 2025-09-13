import socket
import struct
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim

def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def enviar_imagen(imagen_path, sock):
    with open(imagen_path, 'rb') as file:
        imagen_data = file.read()
    header = struct.pack('!Q', len(imagen_data))
    sock.sendall(header + imagen_data)
    print("Imagen enviada al servidor")

def comparar_imagenes(imagen1_path, imagen2_path):
    imagen1 = cv2.imread(imagen1_path)
    nparr = np.frombuffer(imagen2_path, np.uint8)
    imagen2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if imagen1 is None or imagen2 is None:
        print("Error al cargar las imágenes para comparación")
        return

    grayA = cv2.cvtColor(imagen1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imagen2, cv2.COLOR_BGR2GRAY)

    s = ssim(grayA, grayB)
    m = mse(grayA, grayB)

    print(f"SSIM: {s}")
    print(f"MSE: {m}")

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


imagen = 'imagenes/f-35b-lightning.jpg'
host = '192.168.1.90'
port = 8080
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
if client_socket:
    print("Conexión exitosa al servidor")
    enviar_imagen(imagen, client_socket)
    print("Esperando imagen de regreso...")

    header = recvall(client_socket, 8)
    if not header:
        print("No se recibió respuesta del servidor")
    else:
        (length,) = struct.unpack('!Q', header)
        data = recvall(client_socket, length)
        if not data:
            print("Respuesta incompleta del servidor")
        else:
            comparar_imagenes(imagen, data)
    client_socket.close()
else:
    print("Error al conectar con el servidor")