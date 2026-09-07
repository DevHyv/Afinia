import math
import webbrowser

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.uix.button import Button
from kivy.metrics import dp

# Permisos en tiempo de ejecución para Android
from kivy.utils import platform
if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.RECORD_AUDIO, Permission.INTERNET])

# Configurar color de fondo general
Window.clearcolor = get_color_from_hex('#121212')

# Tablas para el Transpositor
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
        self.sim_counter = 0
        self.sim_freq = 82.41
        self.string_buttons = []

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
        if not self.is_listening:
            self.is_listening = True
            self.ids.mic_btn.text = "Detener"
            self.ids.mic_btn.background_color = get_color_from_hex('#E53935')
            Clock.schedule_interval(self.process_audio, 0.1)
        else:
            self.is_listening = False
            self.ids.mic_btn.text = "Activar micrófono"
            self.ids.mic_btn.background_color = get_color_from_hex('#3D3D5C')
            Clock.unschedule(self.process_audio)
            self.reset_display()

    def reset_display(self):
        self.ids.lbl_note.text = "–"
        self.ids.lbl_freq.text = "0.0 Hz"
        self.ids.cent_bar.value = 50
        self.ids.lbl_cents.text = "––"
        self.ids.lbl_cents.color = get_color_from_hex('#FFFFFF')

    def process_audio(self, dt):
        if not self.is_listening:
            return
        
        # NOTA: Esto es una simulación visual. Aquí iría el código real de Pyaudio/Audiostream
        self.sim_counter += 1
        if self.sim_counter % 10 == 0:
            idx = (self.sim_counter // 10) % len(self.current_strings)
            self.sim_freq = self.current_strings[idx]['freq']
        detected_freq = self.sim_freq

        if detected_freq > 30:
            target = min(self.current_strings, key=lambda x: abs(x['freq'] - detected_freq))
            cents = int(1200 * math.log2(detected_freq / target['freq']))
            cents_clamped = max(-50, min(50, cents))
            
            self.ids.lbl_note.text = target['note']
            self.ids.lbl_freq.text = f"{detected_freq:.1f} Hz"
            self.ids.cent_bar.value = 50 + cents_clamped
            self.ids.lbl_cents.text = f"{'+' if cents > 0 else ''}{cents}"
            self.ids.lbl_cents.color = get_color_from_hex('#8BC34A') if abs(cents) <= 5 else get_color_from_hex('#FFFFFF')

class TransposerScreen(Screen):
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
                
        # Unir respetando saltos de línea
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
        # Carga el diseño que contiene el ScreenManager y la Barra de Navegación
        return Builder.load_file('afinia.kv')

if __name__ == '__main__':
    AfiniaApp().run()
