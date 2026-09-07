import math
import webbrowser

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

# Configurar color de fondo general (#1a1a1a)
Window.clearcolor = (0.1, 0.1, 0.1, 1)

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

# Definición de Afinaciones Estándar
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

class TunerTransposerApp(App):
    def build(self):
        self.title = "Afinia"
        self.is_listening = False
        self.tuning_mode = "auto"
        self.active_string_idx = 0
        self.current_strings = INSTRUMENTS['Guitarra (6 cuerdas)']
        
        # Simulación para demo
        self.sim_freq = 82.41
        self.sim_counter = 0

        root = BoxLayout(orientation='vertical', padding=12, spacing=10)

        # Navegación Superior (Tabs)
        nav = BoxLayout(size_hint_y=None, height=48, spacing=5)
        self.btn_tuner_tab = Button(text="Afinador", background_normal='', background_color=(0.23, 0.23, 0.23, 1), bold=True, font_size='16sp')
        self.btn_trans_tab = Button(text="Transpositor", background_normal='', background_color=(0.14, 0.14, 0.14, 1), bold=True, font_size='16sp')
        
        self.btn_tuner_tab.bind(on_press=self.show_tuner)
        self.btn_trans_tab.bind(on_press=self.show_transposer)
        nav.add_widget(self.btn_tuner_tab)
        nav.add_widget(self.btn_trans_tab)
        root.add_widget(nav)

        # Contenedores de Vistas
        self.tuner_view = BoxLayout(orientation='vertical', spacing=12)
        self.trans_view = BoxLayout(orientation='vertical', spacing=12)

        self.build_tuner_ui()
        self.build_transposer_ui()

        root.add_widget(self.tuner_view)
        return root

    def show_tuner(self, instance):
        if self.tuner_view.parent is None:
            self.root.remove_widget(self.trans_view)
            self.root.add_widget(self.tuner_view)
            self.btn_tuner_tab.background_color = (0.23, 0.23, 0.23, 1)
            self.btn_trans_tab.background_color = (0.14, 0.14, 0.14, 1)

    def show_transposer(self, instance):
        if self.trans_view.parent is None:
            self.root.remove_widget(self.tuner_view)
            self.root.add_widget(self.trans_view)
            self.btn_trans_tab.background_color = (0.23, 0.23, 0.23, 1)
            self.btn_tuner_tab.background_color = (0.14, 0.14, 0.14, 1)

    # --- AFINADOR ---
    def build_tuner_ui(self):
        # Encabezado con Donación y Selector
        header = BoxLayout(size_hint_y=None, height=45)
        title_btn = Button(text="Afinia", color=(0.82, 0.69, 0.82, 1), background_normal='', background_color=(0,0,0,0), font_size='22sp', bold=True, halign='left')
        title_btn.bind(on_press=lambda x: webbrowser.open('https://www.paypal.me/tuusuario'))
        
        self.inst_spinner = Spinner(
            text='Guitarra (6 cuerdas)',
            values=tuple(INSTRUMENTS.keys()),
            size_hint=(None, None),
            size=(190, 42),
            background_normal='',
            background_color=(0.16, 0.16, 0.16, 1),
            font_size='14sp'
        )
        self.inst_spinner.bind(text=self.on_instrument_change)

        header.add_widget(title_btn)
        header.add_widget(self.inst_spinner)
        self.tuner_view.add_widget(header)

        # Fila de Controles
        controls = BoxLayout(size_hint_y=None, height=48, spacing=8)
        self.mic_btn = Button(text="Activar micrófono", background_normal='', background_color=(0.23, 0.23, 0.23, 1), bold=True, font_size='15sp')
        self.mic_btn.bind(on_press=self.toggle_microphone)
        
        mode_box = BoxLayout(spacing=2)
        self.btn_auto = Button(text="Auto", background_normal='', background_color=(0.23, 0.23, 0.23, 1), bold=True)
        self.btn_manual = Button(text="Manual", background_normal='', background_color=(0.16, 0.16, 0.16, 1), bold=True)
        self.btn_auto.bind(on_press=lambda x: self.set_mode("auto"))
        self.btn_manual.bind(on_press=lambda x: self.set_mode("manual"))
        mode_box.add_widget(self.btn_auto)
        mode_box.add_widget(self.btn_manual)

        controls.add_widget(self.mic_btn)
        controls.add_widget(mode_box)
        self.tuner_view.add_widget(controls)

        # Display Central (Nota y Hz)
        display = BoxLayout(size_hint_y=None, height=90, padding=10)
        self.lbl_note = Label(text="–", font_size='56sp', bold=True, color=(1, 1, 1, 1))
        self.lbl_freq = Label(text="0.0 Hz", font_size='18sp', color=(0.7, 0.7, 0.7, 1))
        display.add_widget(self.lbl_note)
        display.add_widget(self.lbl_freq)
        self.tuner_view.add_widget(display)

        # Barra de Afinación Visual (-50 a +50 Cents)
        self.cent_bar = ProgressBar(max=100, value=50, size_hint_y=None, height=20)
        self.lbl_cents = Label(text="––", font_size='22sp', bold=True, size_hint_y=None, height=35, color=(1, 1, 1, 1))
        self.tuner_view.add_widget(self.cent_bar)
        self.tuner_view.add_widget(self.lbl_cents)

        # Botones de Cuerdas
        self.strings_grid = GridLayout(cols=3, spacing=8, size_hint_y=1)
        self.render_strings()
        self.tuner_view.add_widget(self.strings_grid)

    def render_strings(self):
        self.strings_grid.clear_widgets()
        self.string_buttons = []
        for idx, s in enumerate(self.current_strings):
            btn = Button(
                text=f"[size=18sp][b]{s['note']}[/b][/size]\n[size=12sp][color=8a8a8a]{s['label']} {s['freq']}Hz[/color][/size]",
                markup=True,
                halign='center',
                background_normal='',
                background_color=(0.16, 0.16, 0.16, 1)
            )
            btn.bind(on_press=lambda b, i=idx: self.select_string(i))
            self.string_buttons.append(btn)
            self.strings_grid.add_widget(btn)

    def set_mode(self, mode):
        self.tuning_mode = mode
        if mode == "auto":
            self.btn_auto.background_color = (0.23, 0.23, 0.23, 1)
            self.btn_manual.background_color = (0.16, 0.16, 0.16, 1)
        else:
            self.btn_manual.background_color = (0.23, 0.23, 0.23, 1)
            self.btn_auto.background_color = (0.16, 0.16, 0.16, 1)

    def select_string(self, idx):
        if self.tuning_mode == "manual":
            self.active_string_idx = idx
            for i, btn in enumerate(self.string_buttons):
                btn.background_color = (0.29, 0.29, 0.41, 1) if i == idx else (0.16, 0.16, 0.16, 1)

    def on_instrument_change(self, spinner, text):
        self.current_strings = INSTRUMENTS[text]
        self.render_strings()

    def toggle_microphone(self, instance):
        if not self.is_listening:
            self.is_listening = True
            self.mic_btn.text = "Detener"
            self.mic_btn.background_color = (0.35, 0.23, 0.23, 1)
            Clock.schedule_interval(self.process_audio, 0.1)
        else:
            self.is_listening = False
            self.mic_btn.text = "Activar micrófono"
            self.mic_btn.background_color = (0.23, 0.23, 0.23, 1)
            Clock.unschedule(self.process_audio)
            self.reset_tuner_display()

    def reset_tuner_display(self):
        self.lbl_note.text = "–"
        self.lbl_freq.text = "0.0 Hz"
        self.cent_bar.value = 50
        self.lbl_cents.text = "––"
        self.lbl_cents.color = (1, 1, 1, 1)

    def process_audio(self, dt):
        # Simulación simple para demo
        self.sim_counter += 1
        if self.sim_counter % 10 == 0:
            self.sim_freq = self.current_strings[self.sim_counter // 10 % len(self.current_strings)]['freq']
        
        detected_freq = self.sim_freq
        
        if detected_freq > 30:
            target = min(self.current_strings, key=lambda x: abs(x['freq'] - detected_freq))
            cents = int(1200 * math.log2(detected_freq / target['freq']))
            cents_clamped = max(-50, min(50, cents))

            self.lbl_note.text = target['note']
            self.lbl_freq.text = f"{detected_freq:.1f} Hz"
            self.cent_bar.value = 50 + cents_clamped
            self.lbl_cents.text = f"{'+' if cents > 0 else ''}{cents}"

            if abs(cents) <= 5:
                self.lbl_cents.color = (0.54, 0.72, 0.48, 1)  # Verde
            else:
                self.lbl_cents.color = (1, 1, 1, 1)

    # --- TRANSPOSITOR ---
    def build_transposer_ui(self):
        self.trans_view.add_widget(Label(text="Transpositor", font_size='22sp', bold=True, size_hint_y=None, height=35))

        self.input_chords = TextInput(
            text="Sol  Mim  Lam  Re7",
            multiline=True,
            size_hint_y=None,
            height=90,
            background_normal='',
            background_color=(0.16, 0.16, 0.16, 1),
            foreground_color=(1, 1, 1, 1),
            padding=(10, 10),
            font_size='16sp'
        )
        self.trans_view.add_widget(self.input_chords)

        keys_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=45)
        self.spin_from = Spinner(text='Sol (G)', values=[f"{es} ({en})" for es, en in zip(NOTES_ES, NOTES_EN)], background_normal='', background_color=(0.16, 0.16, 0.16, 1))
        self.spin_to = Spinner(text='Do (C)', values=[f"{es} ({en})" for es, en in zip(NOTES_ES, NOTES_EN)], background_normal='', background_color=(0.16, 0.16, 0.16, 1))
        keys_grid.add_widget(self.spin_from)
        keys_grid.add_widget(self.spin_to)
        self.trans_view.add_widget(keys_grid)

        self.spin_format = Spinner(text='Español (Do, Re, Mi...)', values=('Español (Do, Re, Mi...)', 'Anglo (C, D, E...)'), size_hint_y=None, height=45, background_normal='', background_color=(0.16, 0.16, 0.16, 1))
        self.trans_view.add_widget(self.spin_format)

        btn_transpose = Button(text="Transponer", size_hint_y=None, height=50, background_normal='', background_color=(0.23, 0.23, 0.23, 1), bold=True, font_size='16sp')
        btn_transpose.bind(on_press=self.process_transpose)
        self.trans_view.add_widget(btn_transpose)

        self.lbl_output = Label(text="Do  Lam  Rem  Sol7", color=(0.54, 0.72, 0.48, 1), font_size='20sp', bold=True, size_hint_y=1)
        self.trans_view.add_widget(self.lbl_output)

    def parse_chord(self, chord):
        chord = chord.strip()
        for length in [2, 1]:
            if length <= len(chord):
                potential = chord[:length].upper()
                if potential in NOTE_MAP:
                    return NOTE_MAP[potential], chord[length:]
        return None, chord

    def process_transpose(self, instance):
        from_text = self.spin_from.text.split(' ')[0]
        to_text = self.spin_to.text.split(' ')[0]
        
        from_idx = NOTE_MAP.get(from_text.upper())
        to_idx = NOTE_MAP.get(to_text.upper())
        if from_idx is None or to_idx is None:
            return
        
        shift = (to_idx - from_idx + 12) % 12
        target_arr = NOTES_ES if "Español" in self.spin_format.text else NOTES_EN

        tokens = self.input_chords.text.split(' ')
        res = []
        for t in tokens:
            if not t.strip():
                res.append(t)
                continue
            idx_note, suffix = self.parse_chord(t)
            if idx_note is not None:
                res.append(target_arr[(idx_note + shift) % 12] + suffix)
            else:
                res.append(t)

        self.lbl_output.text = "  ".join(res)

if __name__ == '__main__':
    TunerTransposerApp().run()
