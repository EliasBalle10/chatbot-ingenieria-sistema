# predict.py - Módulo mejorado con control de contexto para el chatbot

import random
import json
import pickle
import numpy as np
import os
import nltk
from nltk.stem.lancaster import LancasterStemmer
from tensorflow.keras.models import load_model

stemmer = LancasterStemmer()

# Rutas
base_dir = os.path.dirname(__file__)
model_path = os.path.join(base_dir, 'model.h5')
data_path = os.path.join(base_dir, 'data.json')
pickle_path = os.path.join(base_dir, 'data.pickle')

# Cargar archivos
model = load_model(model_path)
with open(data_path, encoding='utf-8') as f:
    intents = json.load(f)
with open(pickle_path, 'rb') as f:
    words, tags, training, output = pickle.load(f)

# Contexto global
contexto_actual = {
    "carrera": None
}

# Utilidades

def bag_of_words(sentence, words):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    bag = [1 if w in sentence_words else 0 for w in words]
    return np.array(bag)


# Predicción

def get_response(user_input):
    global contexto_actual


    # Construir bolsa de palabras
    input_bow = bag_of_words(user_input, words)
    resultado = model.predict(np.array([input_bow]))[0]
    umbral = 0.7

    resultados = [(i, r) for i, r in enumerate(resultado) if r > umbral]
    resultados.sort(key=lambda x: x[1], reverse=True)

    # Si no se detecta intención clara
    if not resultados:
        return "No entendí bien eso 🤔. ¿Podrías reformularlo o especificar la carrera sobre la que quieres información?"

    # Buscar intent
    for i, _ in resultados:
        tag = tags[i]
        for intent in intents['intents']:
            if intent['tag'] == tag:
                categoria = intent.get('categoria_general', None)

                # Validar contexto si está activo
                if contexto_actual["carrera"] and categoria and categoria != contexto_actual["carrera"]:
                    continue

                return random.choice(intent['responses'])

    return "Hmm... no encontré una respuesta adecuada. Intenta con otra pregunta."

# Opción para resetear contexto

def reset_context():
    contexto_actual["carrera"] = None
    return "Contexto reiniciado. ¿que informacion quieres sobre la carrera o prefieres hablar tranquilamente?"
