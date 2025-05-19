# =============================================================================
# CONFIGURACIÓN INICIAL PARA CHATBOT - VERSIÓN CON JSON LOCAL
# =============================================================================

import nltk
import numpy as np
import tensorflow as tf
import json
import pickle
import os
from nltk.stem.lancaster import LancasterStemmer
from tensorflow.keras import layers, models

# Descargar recursos de NLTK
nltk.download("punkt")
stemmer = LancasterStemmer()

# ---- Configuración de rutas ----
# Obtener el directorio actual del script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Ruta al archivo JSON local (en el mismo directorio que el script)
json_file_path = os.path.join(script_dir, 'data.json')

# Rutas para los archivos generados
pickle_file_path = os.path.join(script_dir, 'data.pickle')
model_file_path = os.path.join(script_dir, 'model.h5')

# ---- Cargar datos desde el archivo JSON local ----
try:
    with open(json_file_path, 'r', encoding='utf-8') as file:
        database = json.load(file)
    print("Datos cargados correctamente desde:", json_file_path)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo JSON en {json_file_path}")
    print("Por favor, asegúrate de que existe un archivo 'data.json' en el mismo directorio que este script.")
    exit(1)
except json.JSONDecodeError:
    print("Error: El archivo JSON no tiene un formato válido.")
    exit(1)

# ---- Procesamiento de datos ----
words = []
all_words = []
tags = []
pattern_to_tag = {}

for content in database['intents']:
    tag = content['tag']
    for pattern in content['patterns']:
        # Tokenizar cada palabra en el patrón
        w = nltk.word_tokenize(pattern)
        words.append(w)
        all_words.extend(w)
        pattern_to_tag[tuple(w)] = tag
        
        if tag not in tags:
            tags.append(tag)

# Stemming y limpieza
all_words = [stemmer.stem(w.lower()) for w in all_words if w != "?"]
all_words = sorted(list(set(all_words)))
tags = sorted(tags)

# ---- Preparación de datos de entrenamiento ----
training = []
output = []
output_empty = [0] * len(tags)

for doc in words:
    bag = []
    wrds = [stemmer.stem(w.lower()) for w in doc]
    
    for w in all_words:
        if w in wrds:
            bag.append(1)
        else:
            bag.append(0)
    
    # Obtener el tag correspondiente
    tag = pattern_to_tag[tuple(doc)]
    output_row = list(output_empty)
    output_row[tags.index(tag)] = 1
    
    training.append(bag)
    output.append(output_row)

training = np.array(training)
output = np.array(output)

# ---- Guardar datos procesados ----
try:
    with open(pickle_file_path, 'wb') as f:
        pickle.dump((all_words, tags, training, output), f)
    print("Datos de entrenamiento guardados en:", pickle_file_path)
except Exception as e:
    print(f"Error al guardar archivo pickle: {e}")
    exit(1)

# ---- Construcción y entrenamiento del modelo ----
model = models.Sequential([
    layers.Dense(8, input_shape=(len(all_words),), activation='relu'),
    layers.Dense(8, activation='relu'),
    layers.Dense(len(tags), activation='softmax')
])

model.compile(optimizer='adam',
             loss='categorical_crossentropy',
             metrics=['accuracy'])

print("Iniciando entrenamiento...")
model.fit(training, output, epochs=1000, batch_size=8, verbose=1)

# ---- Guardar modelo entrenado ----
try:
    model.save(model_file_path)
    print(f"Modelo guardado en: {model_file_path}")
    print("¡Chatbot entrenado exitosamente!")
except Exception as e:
    print(f"Error al guardar el modelo: {e}")