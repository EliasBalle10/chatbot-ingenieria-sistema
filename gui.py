import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, filedialog
from PIL import Image, ImageTk, ImageDraw
import pyttsx3
import threading
import datetime
import os
import sys
import json

# Añadir el directorio actual al path para importar predict
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from predict import get_response, reset_context

# Configurar voz con pyttsx3
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
except Exception as e:
    print(f"Advertencia: No se pudo inicializar el motor de voz - {e}")
    engine = None

# Crear historial si no existe
history_file = os.path.join(os.path.dirname(__file__), "chat_history.txt")
if not os.path.exists(history_file):
    with open(history_file, "w", encoding="utf-8") as f:
        f.write("")

# Aplicar modo oscuro
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot de Ingeniería de Sistemas")
        self.root.geometry("800x700")
        self.root.resizable(True, True)

        self.font = ("JetBrains Mono", 12)
        self.user_color = "#D1F7C4"
        self.bot_color = "#EAEAEA"
        
        # Cargar sugerencias desde data.json
        self.sugerencias_por_tag = self.cargar_sugerencias()
        self.ultima_pregunta = ""
        self.botones_sugerencia = []

        avatar_path = os.path.join(os.path.dirname(__file__), "avatar.png")
        self.avatar = self.make_circle(avatar_path) if os.path.exists(avatar_path) else None

        # Frame principal
        self.frame = ctk.CTkFrame(master=root)
        self.frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para categorías
        self.categorias_frame = ctk.CTkFrame(master=self.frame)
        self.categorias_frame.pack(fill=ctk.X, pady=5)
        
        # Botones de categorías
        categorias = [
            "Plan de estudios", 
            "Salidas laborales", 
            "Tecnologías", 
            "Perfil del egresado"
        ]
        
        for categoria in categorias:
            btn = ctk.CTkButton(
                master=self.categorias_frame, 
                text=categoria,
                command=lambda cat=categoria: self.mostrar_preguntas_categoria(cat)
            )
            btn.pack(side=ctk.LEFT, padx=5, pady=5)
        
        # Frame para preguntas de categoría (inicialmente oculto)
        self.preguntas_categoria_frame = ctk.CTkFrame(master=self.frame)
        self.botones_preguntas = []
        
        # Área de chat
        self.chat_area = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD,
                                                 font=self.font, bg="#1f1f1f", fg="white",
                                                 state="disabled")
        self.chat_area.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))

        # Frame para entrada
        self.input_frame = ctk.CTkFrame(master=self.frame)
        self.input_frame.pack(fill=ctk.X, pady=5)

        self.input_field = ctk.CTkEntry(master=self.input_frame, font=self.font)
        self.input_field.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=(0, 5))
        self.input_field.bind("<Return>", self.send_message)

        self.send_button = ctk.CTkButton(master=self.input_frame, text="Enviar", command=self.send_message)
        self.send_button.pack(side=ctk.RIGHT)
        
        # Frame para botones de control
        self.control_frame = ctk.CTkFrame(master=self.frame)
        self.control_frame.pack(fill=ctk.X, pady=5)
        
        # Botón para reiniciar contexto
        self.reset_button = ctk.CTkButton(
            master=self.control_frame, 
            text="Reiniciar contexto", 
            command=self.reset_context_and_ask
        )
        self.reset_button.pack(side=ctk.LEFT, padx=5)
        
        # Botón para ver historial
        self.history_button = ctk.CTkButton(
            master=self.control_frame, 
            text="Ver historial", 
            command=self.show_history
        )
        self.history_button.pack(side=ctk.LEFT, padx=5)
        
        # Frame para opciones comunes
        self.options_frame = ctk.CTkFrame(master=self.frame)
        self.options_frame.pack(fill=ctk.X, pady=5)
        
        # Botones de opciones comunes
        option_buttons = [
            "¿Qué es la ingeniería de sistemas?",
            "¿Qué lenguajes de programación se aprenden?",
            "¿Dónde puede trabajar un egresado?",
            "¿Qué herramientas debo aprender?"
        ]
        
        for option in option_buttons:
            btn = ctk.CTkButton(
                master=self.options_frame, 
                text=option, 
                command=lambda opt=option: self.select_option(opt)
            )
            btn.pack(side=ctk.LEFT, padx=5, pady=5)
        
        # Frame para sugerencias (inicialmente vacío)
        self.sugerencias_frame = ctk.CTkFrame(master=self.frame)
        self.sugerencias_frame.pack(fill=ctk.X, pady=5)
        
        # Frame para feedback
        self.feedback_frame = ctk.CTkFrame(master=self.frame)
        
        # Mensaje de bienvenida
        self.add_bot_message("¡Hola! Soy el asistente virtual especializado en Ingeniería de Sistemas. Puedo ayudarte con información sobre esta carrera. ¿Qué te gustaría saber?")
        
        # Enfocar el campo de entrada
        self.input_field.focus()

    def cargar_sugerencias(self):
        """Carga las sugerencias desde el archivo data.json"""
        sugerencias = {}
        try:
            data_path = os.path.join(os.path.dirname(__file__), 'data.json')
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for intent in data['intents']:
                if 'tag' in intent and 'sugerencias' in intent:
                    sugerencias[intent['tag']] = intent['sugerencias']
                    
            return sugerencias
        except Exception as e:
            print(f"Error al cargar sugerencias: {e}")
            return {}
    
    def mostrar_preguntas_categoria(self, categoria):
        """Muestra preguntas relacionadas con una categoría específica"""
        # Limpiar botones anteriores
        for btn in self.botones_preguntas:
            btn.destroy()
        self.botones_preguntas = []
        
        # Mapeo de categorías a etiquetas
        mapeo_categorias = {
            "Plan de estudios": ["plan_estudios", "asignaturas", "duración"],
            "Salidas laborales": ["salidas_laborales", "mercado_laboral", "salario"],
            "Tecnologías": ["tecnologías", "programación", "herramientas"],
            "Perfil del egresado": ["perfil_egresado", "habilidades", "especialización"]
        }
        
        # Cargar preguntas relacionadas con la categoría
        preguntas = []
        try:
            data_path = os.path.join(os.path.dirname(__file__), 'data.json')
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            etiquetas_categoria = mapeo_categorias.get(categoria, [])
            
            for intent in data['intents']:
                if 'etiquetas' in intent and 'patterns' in intent and len(intent['patterns']) > 0:
                    # Verificar si alguna etiqueta coincide con la categoría
                    if any(etiqueta in etiquetas_categoria for etiqueta in intent['etiquetas']):
                        preguntas.append(intent['patterns'][0])
        except Exception as e:
            print(f"Error al cargar preguntas por categoría: {e}")
        
        # Mostrar hasta 5 preguntas
        preguntas = list(set(preguntas))[:5]
        
        if preguntas:
            self.preguntas_categoria_frame.pack(fill=ctk.X, pady=5)
            
            for pregunta in preguntas:
                btn = ctk.CTkButton(
                    master=self.preguntas_categoria_frame,
                    text=pregunta,
                    command=lambda p=pregunta: self.select_option(p)
                )
                btn.pack(fill=ctk.X, padx=5, pady=2)
                self.botones_preguntas.append(btn)
        else:
            # Si no hay preguntas, ocultar el frame
            self.preguntas_categoria_frame.pack_forget()

    def make_circle(self, img_path, size=(40, 40)):
        try:
            img = Image.open(img_path).resize(size).convert("RGBA")
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            img.putalpha(mask)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error al cargar avatar: {e}")
            return None

    def save_to_history(self, sender, message):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        try:
            with open(history_file, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} {sender}: {message}\n")
        except Exception as e:
            print(f"Error al guardar historial: {e}")

    def speak(self, text):
        if engine:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"Error al reproducir voz: {e}")

    def add_user_message(self, message):
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, f"Tú: {message}\n", "user")
        self.chat_area.tag_config("user", foreground="lightgreen")
        self.chat_area.configure(state="disabled")
        self.chat_area.see(tk.END)
        self.save_to_history("Tú", message)
        self.ultima_pregunta = message

    def add_bot_message(self, message):
        self.chat_area.configure(state="normal")
        if self.avatar:
            self.chat_area.image_create(tk.END, image=self.avatar)
        self.chat_area.insert(tk.END, f" Bot: {message}\n", "bot")
        self.chat_area.tag_config("bot", foreground="lightblue")
        self.chat_area.configure(state="disabled")
        self.chat_area.see(tk.END)
        self.save_to_history("Bot", message)
        self.speak(message)
        
        # Mostrar botones de feedback
        self.mostrar_feedback()
        
        # Buscar sugerencias relacionadas con la respuesta
        self.mostrar_sugerencias()

    def mostrar_feedback(self):
        """Muestra botones de feedback para la última respuesta"""
        # Limpiar frame de feedback anterior
        for widget in self.feedback_frame.winfo_children():
            widget.destroy()
        
        # Mostrar el frame de feedback
        self.feedback_frame.pack(fill=ctk.X, pady=5)
        
        # Etiqueta de feedback
        feedback_label = ctk.CTkLabel(
            master=self.feedback_frame,
            text="¿Te fue útil esta respuesta?"
        )
        feedback_label.pack(side=ctk.LEFT, padx=5)
        
        # Botón de feedback positivo
        btn_util = ctk.CTkButton(
            master=self.feedback_frame,
            text="👍 Sí",
            command=lambda: self.registrar_feedback(True)
        )
        btn_util.pack(side=ctk.LEFT, padx=5)
        
        # Botón de feedback negativo
        btn_no_util = ctk.CTkButton(
            master=self.feedback_frame,
            text="👎 No",
            command=lambda: self.registrar_feedback(False)
        )
        btn_no_util.pack(side=ctk.LEFT, padx=5)

    def registrar_feedback(self, util):
        """Registra el feedback del usuario"""
        feedback_msg = "¡Gracias por tu feedback!" if util else "Lamento que la respuesta no haya sido útil. ¿Puedes ser más específico con tu pregunta?"
        self.add_bot_message(feedback_msg)
        
        # Ocultar frame de feedback después de usarlo
        self.feedback_frame.pack_forget()
        
        # Guardar feedback en archivo
        try:
            feedback_file = os.path.join(os.path.dirname(__file__), "feedback.txt")
            with open(feedback_file, "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                f.write(f"{timestamp} Pregunta: {self.ultima_pregunta} | Útil: {'Sí' if util else 'No'}\n")
        except Exception as e:
            print(f"Error al guardar feedback: {e}")

    def mostrar_sugerencias(self):
        """Muestra sugerencias relacionadas con la última pregunta"""
        # Limpiar sugerencias anteriores
        for btn in self.botones_sugerencia:
            btn.destroy()
        self.botones_sugerencia = []
        
        # Buscar sugerencias relacionadas
        sugerencias = []
        
        # Intentar encontrar sugerencias basadas en la última respuesta
        try:
            data_path = os.path.join(os.path.dirname(__file__), 'data.json')
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for intent in data['intents']:
                if 'patterns' in intent and 'sugerencias' in intent:
                    for pattern in intent['patterns']:
                        if self.ultima_pregunta.lower() in pattern.lower() or pattern.lower() in self.ultima_pregunta.lower():
                            sugerencias = intent['sugerencias']
                            break
                    if sugerencias:
                        break
        except Exception as e:
            print(f"Error al buscar sugerencias: {e}")
        
        # Si no se encontraron sugerencias específicas, usar algunas genéricas
        if not sugerencias:
            sugerencias = [
                "¿Qué es la ingeniería de sistemas?",
                "¿Qué salidas laborales tiene esta carrera?",
                "¿Qué tecnologías se aprenden?"
            ]
        
        # Mostrar sugerencias
        if sugerencias:
            # Título de sugerencias
            titulo = ctk.CTkLabel(
                master=self.sugerencias_frame,
                text="También podrías preguntar:"
            )
            titulo.pack(fill=ctk.X, padx=5, pady=2)
            self.botones_sugerencia.append(titulo)
            
            # Botones de sugerencias
            for sugerencia in sugerencias:
                btn = ctk.CTkButton(
                    master=self.sugerencias_frame,
                    text=sugerencia,
                    command=lambda s=sugerencia: self.select_option(s)
                )
                btn.pack(fill=ctk.X, padx=5, pady=2)
                self.botones_sugerencia.append(btn)

    def send_message(self, event=None):
        message = self.input_field.get().strip()
        if message:
            self.add_user_message(message)
            self.input_field.delete(0, tk.END)
            threading.Thread(target=self.process_response, args=(message,), daemon=True).start()

    def process_response(self, message):
        try:
            response = get_response(message)
            self.root.after(0, lambda: self.add_bot_message(response))
        except Exception as e:
            error_msg = f"Lo siento, ocurrió un error al procesar tu mensaje. ({e})"
            self.root.after(0, lambda: self.add_bot_message(error_msg))

    def reset_context_and_ask(self):
        response = reset_context()
        self.add_bot_message(response)
        
    def select_option(self, option):
        """Maneja la selección de una opción predefinida"""
        self.add_user_message(option)
        self.input_field.delete(0, tk.END)
        
        # Procesar respuesta en un hilo separado
        threading.Thread(target=self.process_response, args=(option,), daemon=True).start()
    
    def show_history(self):
        """Muestra el historial de conversación"""
        try:
            # Verificar si existe el archivo de historial
            if not os.path.exists(history_file) or os.path.getsize(history_file) == 0:
                self.add_bot_message("No hay historial de conversación disponible.")
                return
                
            # Crear ventana para mostrar historial
            history_window = ctk.CTkToplevel(self.root)
            history_window.title("Historial de Conversación")
            history_window.geometry("600x400")
            
            # Área de texto para mostrar historial
            history_text = scrolledtext.ScrolledText(
                history_window, 
                wrap=tk.WORD,
                font=self.font, 
                bg="#1f1f1f", 
                fg="white"
            )
            history_text.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
            
            # Cargar historial
            with open(history_file, "r", encoding="utf-8") as f:
                history_content = f.read()
                
            # Mostrar historial
            history_text.insert(tk.END, history_content)
            
            # Frame para botones
            btn_frame = ctk.CTkFrame(master=history_window)
            btn_frame.pack(fill=ctk.X, padx=10, pady=5)
            
            # Botón para exportar historial
            export_btn = ctk.CTkButton(
                master=btn_frame,
                text="Exportar Historial",
                command=lambda: self.export_history()
            )
            export_btn.pack(side=ctk.LEFT, padx=5)
            
            # Botón para cerrar ventana
            close_btn = ctk.CTkButton(
                master=btn_frame,
                text="Cerrar",
                command=history_window.destroy
            )
            close_btn.pack(side=ctk.RIGHT, padx=5)
            
        except Exception as e:
            self.add_bot_message(f"Error al mostrar historial: {e}")
    
    def export_history(self):
        """Exporta el historial a un archivo seleccionado por el usuario"""
        try:
            # Solicitar ubicación para guardar
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                title="Guardar historial como"
            )
            
            if file_path:
                # Copiar el archivo de historial
                with open(history_file, "r", encoding="utf-8") as src:
                    with open(file_path, "w", encoding="utf-8") as dst:
                        dst.write(src.read())
                
                self.add_bot_message(f"Historial exportado correctamente a {file_path}")
        except Exception as e:
            self.add_bot_message(f"Error al exportar historial: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = ChatbotGUI(root)
    root.mainloop()
