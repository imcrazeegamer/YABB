from pathlib import Path
from gui import widgets, ping, pong, restart_script
from logic.game import Game


FPS = 60
DEFAULT_AUTOPLAY = 2
PLAYER_TOKEN_SPRITE = str(Path.cwd() / 'gui' / 'token.png')
TOKEN_ALIGNMENT = [
    ('left', 'top'),
    ('right', 'top'),
    ('right', 'bottom'),
    ('left', 'bottom'),
]

COLORS = [
    (0.6,0.6,0.6,1),  # Grey
    (0.93,0.64,0.16,1),  # Orange
    (0.40, 0.92, 0.18, 1), # Green
    (0.92, 0.24, 0.078, 1),  # Red
    (0.18, 0.56, 0.92, 1),  # Blue
    (0.92, 0.08, 0.85, 1),  # Magenta
]


class App(widgets.App):
    def __init__(self):
        super().__init__()
        self.title = 'Yet Another Bot Battler'
        self.detailed_mode = True
        self.auto_play = False
        self.auto_play_interval = 1000/DEFAULT_AUTOPLAY
        self.game = Game()
        self.im = widgets.InputManager(app_control_defaults=True)
        self.last_turn = ping()
        self.im.register('Toggle details', '^ d', self.toggle_detailed_mode)
        self.im.register('Toggle play', 'spacebar', self.toggle_auto_play)
        self.hook_mainloop(FPS)
        self.make_widgets()

    def new_game(self, *a):
        self.auto_play = False
        self.game = Game()
        self.make_widgets()

    @property
    def tps(self):
        return 1000/self.auto_play_interval

    @tps.setter
    def tps(self, x):
        self.auto_play_interval = 1000/x

    @property
    def player_count(self):
        return len(self.game.players_bots)

    def toggle_detailed_mode(self, *a):
        self.detailed_mode = not self.detailed_mode

    def toggle_auto_play(self, *a):
        self.auto_play = not self.auto_play
        self.last_turn = ping()

    def do_turn(self, *a):
        self.game.do_turn()

    def mainloop_hook(self, dt):
        if self.game.is_game_over:
            self.auto_play = False
        delta = pong(self.last_turn)
        if self.auto_play and delta > self.auto_play_interval:
            for i in range(round(delta / self.auto_play_interval)):
                self.do_turn()
            self.last_turn = ping()
        self.refresh_gui()

    def make_widgets(self):
        self.root.clear_widgets()
        main_frame = self.root.add(widgets.BoxLayout(orientation='vertical'))
        self.menu_bar = main_frame.add(MenuBar())
        self.menu_bar.set_size(y=35)
        bottom_frame = main_frame.add(widgets.BoxLayout())
        self.score_frame = ScoreFrame().set_size(x=250)
        bottom_frame.add(self.score_frame)
        cy, cx = self.game.board.shape
        main_grid = widgets.GridLayout(cols=cx, rows=cy)
        bottom_frame.add(main_grid)
        self.cells = []
        for iy in range(cy):
            self.cells.append([])
            for ix in range(cx):
                w = MapCell()
                w.set_color(COLORS[0])
                main_grid.add(w)
                self.cells[-1].append(w)
        self.player_tokens = []
        for player in range(self.player_count):
            token = PlayerToken(
                color=COLORS[player+1],
                anchor_x=TOKEN_ALIGNMENT[player][0],
                anchor_y=TOKEN_ALIGNMENT[player][1],
            )
            self.cells[0][0].add(token)
            self.player_tokens.append(token)

    def refresh_gui(self):
        self.menu_bar.refresh()
        self.score_frame.set_scores(self.game.scores)
        self.refresh_grid()

    def refresh_grid(self):
        for y, row in enumerate(self.cells):
            for x, cell in enumerate(row):
                cindex = self.game.board[y, x]
                cell.set_color(COLORS[cindex])
                cell.label.text = f'{x}, {y}' if self.detailed_mode else ''
        for pindex, (x, y) in enumerate(self.game.players_loc):
            cell = self.cells[x][y]
            token = self.player_tokens[pindex]
            token.parent.remove_widget(token)
            cell.add(token)


class MapCell(widgets.AnchorLayout):
    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.padding = 5
        self.label = self.add(widgets.MLabel(text=text, color=(0,0,0,1)))

    def set_color(self, color):
        self.label.make_bg(color)


class PlayerToken(widgets.AnchorLayout):
    def __init__(self, color, **kwargs):
        super().__init__(**kwargs)
        self.im = widgets.Image(source=PLAYER_TOKEN_SPRITE, color=color)
        self.im.set_size(x=50, y=50)
        self.add(self.im)


class ScoreFrame(widgets.AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_frame = widgets.BoxLayout(orientation='vertical')
        self.add(self.main_frame)
        self.details_label = widgets.MLabel(color=(0,0,0,1))
        self.details_label.make_bg(COLORS[0])
        self.main_frame.add(self.details_label)
        self.score_labels = []
        for p in range(self.app.player_count):
            lbl = widgets.MLabel(color=(0,0,0,1))
            lbl.make_bg(COLORS[p+1])
            self.score_labels.append(lbl)
            self.main_frame.add(lbl)

    def set_scores(self, scores):
        unclaimed = scores[0]
        scores = scores[1:]
        in_progress_str = '[b][u]Game over![/u][/b]' if self.app.game.is_game_over else 'Game in progress...'
        self.details_label.text = '\n'.join([
            in_progress_str,
            f'[b]Turn {self.app.game.turn}[/b] / {self.app.game.max_turns}',
            f'Unclaimed: [b]{unclaimed} cells[/b]',
        ])
        sorted_scores = sorted(enumerate(scores), key=lambda x: -x[1])
        for sorted_index, (player_index, score) in enumerate(sorted_scores):
            self.score_labels[sorted_index].text=f'[u]Player {player_index+1}[/u]: [b]{score} cells[/b]'
            self.score_labels[sorted_index].make_bg(COLORS[player_index+1])


class MenuBar(widgets.BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add(widgets.Button(text='Autoplay /s:', on_release=self.focus_tps))
        self.tps_entry = self.add(widgets.Entry(on_text=self.set_tps_text))
        self.tps_entry.set_size(x=60)
        self.play_button = widgets.Button(on_release=self.toggle_auto_play)
        self.add(self.play_button)
        for text, callback in [
            ('Single turn', self.do_single),
            ('New game', self.do_new),
            ('Debug', self.do_debug),
            ('Restart', self.do_restart),
            ('Quit', self.do_quit),
        ]:
            btn = widgets.Button(text=text, on_release=callback)
            self.add(btn)

    def focus_tps(self, *a):
        self.tps_entry.set_focus()

    def set_tps_text(self, tps_text):
        try:
            tps = int(tps_text)
        except ValueError:
            self.tps_entry.text = str(round(self.app.tps))
            return
        tps = max(1, min(tps, FPS*10))
        self.app.tps = tps
        self.tps_entry.text = str(round(self.app.tps))

    def toggle_auto_play(self, *a):
        self.app.toggle_auto_play()

    def do_single(self, *a):
        self.app.game.do_turn()

    def do_new(self, *a):
        self.app.new_game()

    def do_debug(self, *a):
        self.app.game.toggle_debug()

    def do_restart(self, *a):
        restart_script()

    def do_quit(self, *a):
        self.app.stop()

    def refresh(self):
        self.play_button.text = 'Pause' if self.app.auto_play else 'Play'