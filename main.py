import math
import webbrowser
import numpy as np
import pyaudio

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button
from kivy.metrics import dp

# Permisos para Android
from kivy.utils import platform
if platform == "android":
    from android.permissions import request_permissions, Permission, check_permission
    request_permissions([Permission.RECORD_AUDIO, Permission.INTERNET])

Window.clearcolor = get_color_from_hex('#121212')

NOTES_ES = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]
NOTES_EN = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

NOTE_MAP = {
    'C': 0, 'DO': 0, 'C#': 1, 'DB': 1, 'DO#': 1, 'REB': 1,
    'D': 2, 'RE': 2, 'D#': 3, 'EB': 3, 'RE#': 3, 'MIB': 3,
    'E': 4, 'MI': 4, 'F': 5, 'FA': 5, 'F#': 6, 'GB': 6,
    'FA#': 6, 'SOLB': 6, 'G': 7, 'SOL': 7, 'G#': 8, 'AB': 8,
    'SOL#': 8, 'LAB': 8, 'A': 9, 'LA': 9, 'A#': 10, 'BB': 10,
    'LA#': 10, 'SIB': 10, 'B': 11, 'SI': 11
}

INSTRUMENTS = {
    'Guitarra (6 cuerdas)': [
        {'note': 'E', 'freq': 82.41, 'label': '6ª'},
        {'note': 'A', 'freq': 110.00, 'label': '5ª'},
        {'note': 'D', 'freq': 146.83, 'label': '4ª'},
        {'note': 'G', 'freq': 196.00, 'label': '3ª'},
        {'note': 'B', 'freq': 246.94, 'label': '2ª'},
        {'note': 'E', 'freq': 329.63, 'label': '1ª'}
    ],
    'Bajo': [
        {'note': 'E', 'freq': 41.20, 'label': '4ª'},
        {'note': 'A', 'freq': 55.00, 'label': '3ª'},
        {'note': 'D', 'freq': 73.42, 'label': '2ª'},
        {'note': 'G', 'freq': 98.00, 'label': '1ª'}
    ],
    'Ukelele': [
        {'note': 'G', 'freq': 392.00, 'label': '4ª'},
        {'note': 'C', 'freq': 261.63, 'label': '3ª'},
        {'note': 'E', 'freq': 329.63, 'label': '2ª'},
        {'note': 'A', 'freq': 440.00, 'label': '1ª'}
    ]
}

class TunerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_listening = False
        self.tuning_mode = "auto"
        self.active_string_idx = 0
        self.current_strings = INSTRUMENTS['Guitarra (6 cuerdas)']
        self.string_buttons = []
        
        # Configuraciones de Audio
        self.CHUNK = 4096  # Tamaño grande para detectar bajos (41Hz)
        self.RATE = 44100
        self.last_freq = 0.0

    def on_enter(self):
        self.render_strings()

    def render_strings(self):
        grid = self.ids.strings_grid
        grid.clear_widgets()
        self.string_buttons = []
        for idx, s in enumerate(self.current_strings):
            btn = Button(
                text=f"[size=24sp][b]{s['note']}[/b][/size]\n[size=16sp][color=#999999]{s['label']} {s['freq']}Hz[/color][/size]",
                markup=True,
                background_normal='',
                background_color=get_color_from_hex('#2A2A2A'),
                size_hint_y=None,
                height=dp(90)
            )
            btn.bind(on_release=lambda b, i=idx: self.select_string(i))
            self.string_buttons.append(btn)
            grid.add_widget(btn)

    def select_string(self, idx):
        if self.tuning_mode == "manual":
            self.active_string_idx = idx
            for i, btn in enumerate(self.string_buttons):
                btn.background_color = get_color_from_hex('#3D3D5C') if i == idx else get_color_from_hex('#2A2A2A')

    def set_mode(self, mode):
        self.tuning_mode = mode
        if mode == "auto":
            self.ids.btn_auto.background_color = get_color_from_hex('#3D3D5C')
            self.ids.btn_manual.background_color = get_color_from_hex('#2A2A2A')
        else:
            self.ids.btn_manual.background_color = get_color_from_hex('#3D3D5C')
            self.ids.btn_auto.background_color = get_color_from_hex('#2A2A2A')

    def on_instrument_change(self, text):
        self.current_strings = INSTRUMENTS[text]
        self.render_strings()

    def toggle_microphone(self):
        # Chequeo de seguridad de permisos en Android
        if platform == "android" and not check_permission(Permission.RECORD_AUDIO):
            self.ids.lbl_note.text = "¡Permiso!"
            self.ids.lbl_freq.text = "Acepta el uso del micrófono"
            return

        if not self.is_listening:
            try:
                self.p = pyaudio.PyAudio()
                self.stream = self.p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK
                )
                self.is_listening = True
                self.ids.mic_btn.text = "Detener"
                self.ids.mic_btn.background_color = get_color_from_hex('#E53935')
                Clock.schedule_interval(self.process_audio, 0.1) # Leer cada 100ms
            except Exception as e:
                self.ids.lbl_note.text = "Error Mic"
                print(f"Error al abrir micrófono: {e}")
        else:
            self.is_listening = False
            self.ids.mic_btn.text = "Activar micrófono"
            self.ids.mic_btn.background_color = get_color_from_hex('#3D3D5C')
            Clock.unschedule(self.process_audio)
            
            if hasattr(self, 'stream'):
                self.stream.stop_stream()
                self.stream.close()
            if hasattr(self, 'p'):
                self.p.terminate()
                
            self.reset_display()

    def reset_display(self):
        self.ids.lbl_note.text = "–"
        self.ids.lbl_freq.text = "0.0 Hz"
        self.ids.cent_bar.value = 50
        self.ids.lbl_cents.text = "––"
        self.ids.lbl_cents.color = get_color_from_hex('#FFFFFF')

    def get_pitch(self, signal):
        """Algoritmo de Autocorrelación para detectar tono real"""
        signal = signal - np.mean(signal) # Quitar offset
        volume = np.sqrt(np.mean(signal**2))
        
        # Puerta de ruido (Si está muy callado, ignorar)
        if volume < 400: 
            return 0.0

        # Calcular autocorrelación
        corr = np.correlate(signal, signal, mode='full')
        corr = corr[len(corr)//2:]
        d = np.diff(corr)

        try:
            start = np.nonzero(d > 0)[0][0]
            peak = np.argmax(corr[start:]) + start
            
            if peak == 0 or peak >= len(corr) - 1:
                return 0.0

            # Interpolación Parabólica para exactitud extrema (afinación fina)
            y0, y1, y2 = corr[peak-1], corr[peak], corr[peak+1]
            if 2 * y1 - y0 - y2 == 0:
                true_peak = peak
            else:
                true_peak = peak + (y0 - y2) / (2 * (y0 - 2 * y1 + y2))

            return self.RATE / true_peak
        except Exception:
            return 0.0

    def process_audio(self, dt):
        if not self.is_listening or not self.stream.is_active():
            return

        try:
            # Leer buffer del micrófono real
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            
            # Detectar frecuencia real
            detected_freq = self.get_pitch(samples)

            if detected_freq > 30 and detected_freq < 1500:
                # Suavizar salto de frecuencias para que no titile bruscamente
                if self.last_freq > 0:
                    detected_freq = (detected_freq * 0.4) + (self.last_freq * 0.6)
                self.last_freq = detected_freq

                # Determinar si afinamos en Auto o Manual
                if self.tuning_mode == "auto":
                    target = min(self.current_strings, key=lambda x: abs(x['freq'] - detected_freq))
                else:
                    target = self.current_strings[self.active_string_idx]

                # Calcular centavos (diferencia logarítmica)
                cents = int(1200 * math.log2(detected_freq / target['freq']))
                cents_clamped = max(-50, min(50, cents))
                
                # Actualizar pantalla
                self.ids.lbl_note.text = target['note']
                self.ids.lbl_freq.text = f"{detected_freq:.1f} Hz"
                self.ids.cent_bar.value = 50 + cents_clamped
                self.ids.lbl_cents.text = f"{'+' if cents > 0 else ''}{cents}"
                self.ids.lbl_cents.color = get_color_from_hex('#8BC34A') if abs(cents) <= 5 else get_color_from_hex('#FFFFFF')

        except Exception as e:
            print(f"Error procesando audio: {e}")

class TransposerScreen(Screen):
    # ... (El código de Transposer se queda exactamente igual al de mi respuesta anterior)
    def process_transpose(self):
        from_text = self.ids.spin_from.text.split(' ')[0]
        to_text = self.ids.spin_to.text.split(' ')[0]
        from_idx = NOTE_MAP.get(from_text.upper())
        to_idx = NOTE_MAP.get(to_text.upper())
        
        if from_idx is None or to_idx is None:
            return
            
        shift = (to_idx - from_idx + 12) % 12
        target_arr = NOTES_ES if "Español" in self.ids.spin_format.text else NOTES_EN
        tokens = self.ids.input_chords.text.replace('\n', ' \n ').split(' ')
        res = []
        
        for t in tokens:
            if not t.strip() and t != '\n':
                res.append(t)
                continue
            if t == '\n':
                res.append(t)
                continue
                
            idx_note, suffix = self.parse_chord(t)
            if idx_note is not None:
                res.append(target_arr[(idx_note + shift) % 12] + suffix)
            else:
                res.append(t)
                
        self.ids.lbl_output.text = " ".join(res).replace(" \n ", "\n")

    def parse_chord(self, chord):
        chord = chord.strip()
        for length in [2, 1]:
            if length <= len(chord):
                potential = chord[:length].upper()
                if potential in NOTE_MAP:
                    return NOTE_MAP[potential], chord[length:]
        return None, chord

class AfiniaApp(App):
    def build(self):
        self.title = "Afinia"
        return Builder.load_file('afinia.kv')

if __name__ == '__main__':
    AfiniaApp().run()
