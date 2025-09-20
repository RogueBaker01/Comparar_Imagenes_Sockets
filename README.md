# Comparar Imágenes con Sockets

## Descripción

Este proyecto implementa un sistema **cliente-servidor en Python** que permite enviar imágenes a través de **sockets TCP/IP** y compararlas con imágenes de referencia almacenadas en el servidor.  

La comparación se realiza utilizando métricas de visión por computadora como:  

- **MSE (Mean Squared Error)** → mide la diferencia promedio entre píxeles.  
- **SSIM (Structural Similarity Index)** → evalúa similitud estructural, brillo y contraste.  

Además, se incorpora **cifrado simétrico con Fernet** para asegurar la transmisión de las imágenes.

---

## 📂 Estructura del proyecto

Comparar_Imagenes_Sockets/
├── imagenes/ # Carpeta con imágenes de referencia
├── keys/ # Carpeta donde se guardan las llaves de cifrado
├── Proyecto_Servidor.py # Código del servidor
├── Proyecto_cliente.py # Cliente principal
├── Proyecto_cliente_st.py # Cliente alternativo / pruebas
├── imagen_recibida.jpg # Imagen recibida (temporal)
└── requirements.txt # Dependencias del proyecto

---

## ⚙️ Instalación

Clonar este repositorio:

```bash
git clone https://github.com/RogueBaker01/Comparar_Imagenes_Sockets.git
cd Comparar_Imagenes_Sockets

```
Instalar dependecias pip install numpy opencv matplotlib scikit-image cryptography

