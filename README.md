# chatbot-ingenieria-sistema
# Chatbot de Ingeniería de Sistemas

Un asistente virtual inteligente especializado en proporcionar información sobre la carrera de Ingeniería de Sistemas, desarrollado con Python, TensorFlow y una interfaz gráfica moderna.

![Vista previa del chatbot](avatar.png)

## 📋 Características

- **Interfaz gráfica amigable**: Diseñada con CustomTkinter para una experiencia visual moderna
- **Reconocimiento de intenciones**: Utiliza procesamiento de lenguaje natural para entender las preguntas
- **Contexto de conversación**: Mantiene el contexto de la carrera sobre la que se está consultando
- **Sistema de feedback**: Permite a los usuarios calificar las respuestas recibidas
- **Sugerencias inteligentes**: Ofrece preguntas relacionadas basadas en la conversación
- **Historial de chat**: Guarda y permite exportar las conversaciones
- **Síntesis de voz**: Reproduce las respuestas en audio (si está disponible pyttsx3)

## 🚀 Tecnologías utilizadas

- **Python**: Lenguaje base del proyecto
- **TensorFlow/Keras**: Para el modelo de procesamiento de lenguaje natural
- **NLTK**: Procesamiento de texto y tokenización
- **CustomTkinter**: Interfaz gráfica moderna
- **Pickle**: Serialización de datos del modelo

## 🛠️ Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/tu-usuario/chatbot-ingenieria-sistemas.git
cd chatbot-ingenieria-sistemas
Crea y activa un entorno virtual:
bash
Run
python -m venv venvvenv\Scripts\activate
Instala las dependencias:
bash
Run
pip install -r requirements.txt
Ejecuta la aplicación:
bash
Run
python main.py
📊 Estructura del proyecto
gui.py: Interfaz gráfica del chatbot
predict.py: Módulo de predicción y manejo de contexto
data.json: Base de conocimiento con intenciones y respuestas
model.h5: Modelo entrenado de red neuronal
data.pickle: Datos procesados para el modelo
chat_history.txt: Historial de conversaciones
feedback.txt: Registro de feedback de los usuarios
💡 Cómo funciona
El chatbot utiliza un modelo de red neuronal entrenado con TensorFlow para clasificar las preguntas del usuario en diferentes categorías o "intenciones". Cada intención tiene un conjunto de patrones de preguntas y posibles respuestas.

El flujo de funcionamiento es:

El usuario ingresa una pregunta
El texto se procesa (tokenización, stemming) y se convierte en un vector
El modelo predice la intención más probable
Se selecciona una respuesta aleatoria de las disponibles para esa intención
Se mantiene el contexto de la conversación para preguntas subsecuentes
🔧 Personalización
Puedes personalizar el chatbot modificando el archivo data.json:

Añade nuevas intenciones con sus patrones y respuestas
Modifica las respuestas existentes
Agrega sugerencias para cada intención
Define categorías para organizar el conocimiento
📝 Licencia
Este proyecto está bajo la Licencia MIT - mira el archivo LICENSE para detalles

👨‍💻 Autor
Tu Nombre -    ELIAS BALLESTERO
¡Gracias por usar este chatbot! Si tienes sugerencias o encuentras algún problema, no dudes en abrir un issue.