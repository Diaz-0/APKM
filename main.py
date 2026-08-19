from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
import socket
import time

# Fondo general de la ventana en gris muy oscuro (Estilo App moderna)
Window.clearcolor = (0.07, 0.07, 0.09, 1)

class TarjetaRedonda(BoxLayout):
    """Un contenedor personalizado con esquinas redondeadas y fondo oscuro"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            # Color de tarjeta (Gris oscuro elegante)
            self.bg_color = Color(0.12, 0.12, 0.16, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])
        self.bind(pos=self.actualizar_rect, size=self.actualizar_rect)

    def actualizar_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MonitorMobileApp(App):
    def build(self):
        self.title = "Monitor de Red Starlink"
        self.monitoreando = False

        # Layout Principal General con márgenes (Padding)
        root = BoxLayout(orientation='vertical', padding=25, spacing=20)

        # --- TÍTULO SUPERIOR ---
        lbl_titulo = Label(
            text="MONITOR DE RED", 
            font_size=18, 
            bold=True, 
            color=(0.6, 0.6, 0.7, 1),
            size_hint=(1, 0.1)
        )
        root.add_widget(lbl_titulo)

        # --- TARJETA CENTRAL DE INDICADORES ---
        self.tarjeta = TarjetaRedonda(orientation='vertical', padding=20, spacing=10, size_hint=(1, 0.6))
        
        # Etiqueta de Ping Título
        self.tarjeta.add_widget(Label(
            text="LATENCIA PING", 
            font_size=12, 
            color=(0.5, 0.5, 0.6, 1),
            bold=True
        ))

        # Valor Grande del Ping
        self.lbl_ping = Label(
            text="-- ms", 
            font_size=42, 
            bold=True, 
            color=(1, 1, 1, 1)
        )
        self.tarjeta.add_widget(self.lbl_ping)

        # Subtítulo de estado dentro de la tarjeta
        self.lbl_estado_red = Label(
            text="Desconectado", 
            font_size=14, 
            color=(0.4, 0.8, 0.6, 1)
        )
        self.tarjeta.add_widget(self.lbl_estado_red)

        root.add_widget(self.tarjeta)

        # --- CONTENEDOR PARA EL BOTÓN INFERIOR ---
        btn_layout = AnchorLayout(size_hint=(1, 0.25), padding=[0, 10, 0, 0])
        
        self.btn_control = Button(
            text="INICIO", 
            font_size=20, 
            bold=True,
            size_hint=(0.8, 0.8),
            color=(1, 1, 1, 1),
            background_color=(0, 0, 0, 0), # Limpiamos el fondo feo por defecto
        )
        
        # Dibujamos un botón moderno redondeado con canvas
        with self.btn_control.canvas.before:
            self.color_boton = Color(0.15, 0.65, 0.35, 1) # Verde moderno inicial
            self.btn_rect = RoundedRectangle(pos=self.btn_control.pos, size=self.btn_control.size, radius=[25])
        
        self.btn_control.bind(pos=self.actualizar_btn, size=self.actualizar_btn)
        self.btn_control.bind(on_press=self.toggle_monitoreo)
        
        btn_layout.add_widget(self.btn_control)
        root.add_widget(btn_layout)

        return root

    def actualizar_btn(self, *args):
        self.btn_rect.pos = self.btn_control.pos
        self.btn_rect.size = self.btn_control.size

    def toggle_monitoreo(self, instance):
        if not self.monitoreando:
            self.monitoreando = True
            self.btn_control.text = "DETENER"
            self.color_boton.rgba = (0.85, 0.2, 0.2, 1) # Rojo elegante para detener
            self.lbl_estado_red.text = "Monitoreando en tiempo real..."
            
            Clock.schedule_interval(self.actualizar_ping, 1.0)
        else:
            self.monitoreando = False
            self.btn_control.text = "INICIO"
            self.color_boton.rgba = (0.15, 0.65, 0.35, 1) # Verde de vuelta
            self.lbl_estado_red.text = "Pausado"
            
            Clock.unschedule(self.actualizar_ping)
            self.lbl_ping.text = "-- ms"
            self.lbl_ping.color = (1, 1, 1, 1)

    def actualizar_ping(self, dt):
        if not self.monitoreando:
            return False
            
        try:
            inicio = time.time()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            s.connect(("8.8.8.8", 53))
            s.close()
            ms = int((time.time() - inicio) * 1000)
            
            self.lbl_ping.text = f"{ms} ms"

            # Semáforo de colores adaptado al estilo juego
            if ms < 100:
                self.lbl_ping.color = (1, 1, 1, 1) # Blanco
                self.lbl_estado_red.text = "Conexión Estable"
                self.lbl_estado_red.color = (0.4, 0.8, 0.6, 1)
            elif ms < 250:
                self.lbl_ping.color = (1, 0.85, 0.2, 1) # Amarillo
                self.lbl_estado_red.text = "Latencia Moderada"
                self.lbl_estado_red.color = (1, 0.85, 0.2, 1)
            else:
                self.lbl_ping.color = (0.9, 0.3, 0.3, 1) # Rojo
                self.lbl_estado_red.text = "Lag Alto / Pico de red"
                self.lbl_estado_red.color = (0.9, 0.3, 0.3, 1)
        except:
            self.lbl_ping.text = "999 ms"
            self.lbl_ping.color = (0.9, 0.3, 0.3, 1)
            self.lbl_estado_red.text = "Sin Conexión (Micro-corte)"
            self.lbl_estado_red.color = (0.9, 0.3, 0.3, 1)

if __name__ == '__main__':
    MonitorMobileApp().run()