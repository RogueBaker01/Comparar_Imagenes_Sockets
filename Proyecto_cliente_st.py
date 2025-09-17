import streamlit as st
import socket
import struct
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from cryptography.fernet import Fernet
from PIL import Image

KEY_FILE = 'keys/key.key'

def get_key(key_path):
    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, 'wb') as f:
            f.write(key)
        st.toast("Nueva clave de encriptación generada.")
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

def mse(imagenA, imagenB):
    err = np.sum((imagenA.astype("float") - imagenB.astype("float")) ** 2)
    err /= float(imagenA.shape[0] * imagenA.shape[1])
    return err

def comparar_imagenes(imagen_original_bytes, imagen_recibida_bytes):
    
    original_np = np.frombuffer(imagen_original_bytes, np.uint8)
    recibida_np = np.frombuffer(imagen_recibida_bytes, np.uint8)
    
    img_original = cv2.imdecode(original_np, cv2.IMREAD_COLOR)
    img_recibida = cv2.imdecode(recibida_np, cv2.IMREAD_COLOR)

    if img_original is None or img_recibida is None:
        st.error("Error al decodificar las imágenes para la comparación.")
        return

    grayA = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(img_recibida, cv2.COLOR_BGR2GRAY)

    s = ssim(grayA, grayB)
    m = mse(grayA, grayB)

    if isinstance(s, tuple):
        s = s[0]

    if s == 1.0 and m == 0.0:
        msg = "Las imágenes son idénticas."
    elif s > 0.9:
        msg = "Las imágenes son muy similares."
    elif s > 0.6:
        msg = "Las imágenes son parecidas, con algunas diferencias."
    else:
        msg = "Las imágenes son diferentes."

    st.subheader("📊 Resultados de la Comparación")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Índice de Similitud Estructural (SSIM)", value=f"{s:.4f}")
    with col2:
        st.metric(label="Error Cuadrático Medio (MSE)", value=f"{m:.2f}")

    st.info(msg)

    st.subheader("Comparativa Visual")
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        st.image(cv2.cvtColor(img_original, cv2.COLOR_BGR2RGB), caption="Imagen Original Enviada", use_column_width=True)
    with col_img2:
        st.image(cv2.cvtColor(img_recibida, cv2.COLOR_BGR2RGB), caption="Imagen Recibida del Servidor", use_column_width=True)



st.set_page_config(page_title="Cliente de Transferencia Segura", layout="wide")

st.title("Cliente para Transferencia Segura de Imágenes")
st.markdown("Esta aplicación permite enviar una imagen de forma segura a un servidor, recibirla de vuelta y verificar si ha sido alterada en el proceso.")

st.sidebar.header("Configuración del Servidor")
host = st.sidebar.text_input("Dirección IP del Servidor", "192.168.1.90")
port = st.sidebar.number_input("Puerto del Servidor", 1, 65535, 8080)

st.header("1. Sube una imagen")
uploaded_file = st.file_uploader("Elige una imagen (JPG, PNG) para enviar al servidor.", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen a enviar", width=300)

    if st.button("Enviar y Verificar Imagen", type="primary"):
        try:
            key = get_key(KEY_FILE)
            cipher_suite = Fernet(key)

            image_bytes = uploaded_file.getvalue()

            with st.spinner("Conectando con el servidor..."):
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((host, port))
            st.success(f"Conexión exitosa al servidor en {host}:{port}")

            with st.spinner("Encriptando y enviando imagen..."):
                encrypted_data = cipher_suite.encrypt(image_bytes)
                header = struct.pack('!Q', len(encrypted_data))
                client_socket.sendall(header + encrypted_data)
            st.info("Imagen encriptada enviada al servidor.")

            with st.spinner("Esperando respuesta del servidor..."):
                header = recvall(client_socket, 8)
                if not header:
                    st.error("No se recibió una respuesta válida del servidor.")
                else:
                    (length,) = struct.unpack('!Q', header)
                    encrypted_response = recvall(client_socket, length)
            
            st.info("Desencriptando imagen recibida...")
            decrypted_response = cipher_suite.decrypt(encrypted_response)
            
            st.success("Imagen recibida y desencriptada con éxito")

            comparar_imagenes(image_bytes, decrypted_response)

        except ConnectionRefusedError:
            st.error(f"Error de conexión: El servidor en {host}:{port} no está disponible. ¿Está el script del servidor en ejecución?")
        except Exception as e:
            st.error(f"Ha ocurrido un error inesperado: {e}")
        finally:
            if 'client_socket' in locals():
                client_socket.close()