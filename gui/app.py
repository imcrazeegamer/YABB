from pathlib import Path

from gui import widgets, ping, pong, restart_script
from logic.game import Game, DEFAULT_MAP_SIZE, DEFAULT_MAX_TURNS, MINIMUM_MAP_SIZE
from bots import BOT_CLASSES


TITLE = 'Yet Another Bot Battler'
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

BOT_NAMES = list(BOT_CLASSES.keys())
DEFAULT_BOT_NAME = 'Default'
assert DEFAULT_BOT_NAME in BOT_CLASSES


class App(widgets.App):
    def __init__(self):
        super().__init__()
        self.title = TITLE
        self.detailed_mode = False
        self.auto_play = False
        self.auto_play_interval = 1000/DEFAULT_AUTOPLAY
        self.game = self.get_game()
        self.new_game_popup = NewGamePopup()
        self.im = widgets.InputManager(app_control_defaults=True)
        self.last_turn = ping()
        self.im.register('Toggle play', 'spacebar', self.toggle_auto_play)
        self.im.register('New game', '^ n', self.new_game)
        self.hook_mainloop(FPS)
        self.make_widgets()

    def new_game(self, *a):
        self.new_game_popup.open()

    def do_new_game(self, *args, **kwargs):
        print(f'starting new game with args: {args} kwargs {kwargs}')
        self.auto_play = False
        self.game = self.get_game(*args, **kwargs)
        self.make_widgets()
        self.new_game_popup.dismiss()

    def get_game(self, *args, bots=None, **kwargs):
        if bots is None:
            bots = [BOT_CLASSES[DEFAULT_BOT_NAME] for _ in range(4)]
        return Game(*args, bots=bots, **kwargs)

    @property
    def tps(self):
        return 1000/self.auto_play_interval

    @tps.setter
    def tps(self, x):
        self.auto_play_interval = 1000/x

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
        self.game_frame = main_frame.add(GameGUI())

    def refresh_gui(self):
        debug_str = f' -- DEBUG MODE' if self.game.is_debug else ''
        self.title = f'{TITLE}{debug_str}'
        self.menu_bar.refresh()
        self.game_frame.refresh()


class GameGUI(widgets.AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.make_widgets()

    def make_widgets(self):
        main_frame = self.add(widgets.BoxLayout())
        self.score_frame = ScoreFrame(padding=10).set_size(x=250)
        self.score_frame.make_bg((0.05, 0.15, 0.25, 1))
        main_frame.add(self.score_frame)
        cy, cx = self.game.board.shape
        main_grid = widgets.GridLayout(cols=cx, rows=cy)
        main_frame.add(main_grid)
        self.cells = []
        for iy in range(cy):
            self.cells.append([])
            for ix in range(cx):
                w = MapCell()
                w.set_color(COLORS[0])
                main_grid.add(w)
                self.cells[-1].append(w)
        self.player_tokens = []
        for player in range(self.game.player_count):
            token = PlayerToken(
                color=COLORS[player+1],
                anchor_x=TOKEN_ALIGNMENT[player][0],
                anchor_y=TOKEN_ALIGNMENT[player][1],
            )
            self.cells[0][0].add(token)
            self.player_tokens.append(token)

    def refresh(self):
        self.score_frame.set_scores(self.game.scores)
        self.refresh_grid()

    def refresh_grid(self):
        for y, row in enumerate(self.cells):
            for x, cell in enumerate(row):
                cindex = self.game.board[y, x]
                cell.set_color(COLORS[cindex])
                cell.label.text = f'{x}, {y}' if self.app.detailed_mode else ''
        for pindex, (x, y) in enumerate(self.game.players_loc):
            cell = self.cells[x][y]
            token = self.player_tokens[pindex]
            token.parent.remove_widget(token)
            cell.add(token)

    @property
    def game(self):
        return self.app.game


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
        for p in range(self.app.game.player_count):
            lbl = widgets.MLabel(color=(0,0,0,1))
            lbl.make_bg(COLORS[p+1])
            self.score_labels.append(lbl)
            self.main_frame.add(lbl)

    def set_scores(self, scores):
        unclaimed = scores[0]
        scores = scores[1:]

        if self.app.game.is_game_over:
            winner_index = self.app.game.get_winner()
            winner = self.app.game.players_bots[winner_index]
            in_progress_str = '\n'.join([
                f'[b][u]Game over![/u][/b]',
                f'Winner: #{winner_index+1} [b]{winner.name}[/b]',
                '',
            ])
        else:
            in_progress_str = 'Game in progress...'
        self.details_label.text = '\n'.join([
            in_progress_str,
            f'[b]Turn {self.app.game.turn}[/b] / {self.app.game.max_turns}',
            f'Unclaimed: [b]{unclaimed} cells[/b]',
        ])
        sorted_scores = sorted(enumerate(scores), key=lambda x: -x[1])
        for sorted_index, (player_index, score) in enumerate(sorted_scores):
            bot = self.app.game.players_bots[player_index]
            name_str = f'#{player_index+1} - {bot.name}' if self.app.detailed_mode else bot.name
            self.score_labels[sorted_index].text = '\n'.join([
                f'[u]{name_str}[/u]: [b]{score} cells[/b]',
                f'',
                f'[i]{bot.say}[/i]',
            ])
            self.score_labels[sorted_index].make_bg(COLORS[player_index+1])


class MenuBar(widgets.BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.play_button = widgets.Button(on_release=self.toggle_auto_play)
        self.add(self.play_button)
        self.add(widgets.Button(text='Autoplay /s:', on_release=self.focus_tps))
        self.tps_entry = self.add(widgets.Entry(on_text=self.set_tps_text))
        self.tps_entry.set_size(x=40)
        self.detailed = self.add(widgets.CheckBox(active=self.app.detailed_mode))
        self.detailed.bind(active=self.set_detailed)
        self.detailed.set_size(x=20)
        self.detailed_label = self.add(widgets.Label(text='Detailed')).set_size(x=60)
        self.detailed_label.bind(on_touch_down=self.toggle_checkbox)
        for text, callback in [
            ('Single turn', self.do_single),
            ('Debug', self.do_debug),
            ('New game', self.do_new),
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
        self.app.auto_play = False
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

    def set_detailed(self, *a):
        self.app.detailed_mode = self.detailed.active

    def toggle_checkbox(self, w, m):
        if not self.detailed_label.collide_point(*m.pos):
            return
        self.detailed.active = not self.detailed.active


class NewGamePopup(widgets.Popup):
    def __init__(self, title='New game configuration', **kwargs):
        self.config_frame = NewGameConfig()
        super().__init__(
            title=title,
            content=self.config_frame,
            **kwargs
        )
        self.set_size(x=400, y=500)


class NewGameConfig(widgets.AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_frame = self.add(widgets.BoxLayout(orientation='vertical'))
        main_frame.add(widgets.Label(text='Max turns:')).set_size(y=35)
        self.max_turns = main_frame.add(widgets.Entry(text=str(DEFAULT_MAX_TURNS)))
        self.bot_selector = main_frame.add(BotSelector())
        self.mapsize_selector = main_frame.add(MapSizeSelector())
        start_btn = widgets.Button(text='Start new game', on_release=self.do_new_game)
        start_btn.set_size(y=50)
        main_frame.add(start_btn)

    def do_new_game(self, *a):
        try:
            max_turns = int(self.max_turns.text)
        except ValueError:
            max_turns = DEFAULT_MAX_TURNS
        max_turns = max(1, max_turns)
        self.app.do_new_game(
            bots=self.bot_selector.selected_bots,
            map_size=self.mapsize_selector.selected_size,
            game_length=max_turns,
        )


class BotSelector(widgets.GridLayout):
    def __init__(self, **kwargs):
        super().__init__(cols=2, **kwargs)
        self.selection_widgets = []
        for i in range(4):
            lbl = widgets.Label(text=f'Bot #{i+1}:')
            lbl.set_size(x=80, y=60)
            self.add(lbl)

            btn = self.add(widgets.DropDownSelect())
            btn.set_options(BOT_NAMES)
            btn.background_color = 0.5, 0.5, 0.2, 1
            btn.text = DEFAULT_BOT_NAME
            btn.set_size(y=60)
            self.selection_widgets.append(btn)

    @property
    def selected_bots(self):
        return [BOT_CLASSES[w.text] for w in self.selection_widgets]


class MapSizeSelector(widgets.BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_size(y=35)
        self.add(widgets.Label(text='Map size:'))
        self.config_y = self.add(widgets.Entry(text=str(DEFAULT_MAP_SIZE[0])))
        self.config_y.set_size(x=40)
        self.add(widgets.Label(text=f'×')).set_size(x=40)
        self.config_x = self.add(widgets.Entry(text=str(DEFAULT_MAP_SIZE[1])))
        self.config_x.set_size(x=40)

    @property
    def selected_size(self):
        x = self.config_x.text
        try:
            x = int(x)
        except ValueError:
            x = DEFAULT_MAP_SIZE[0]
        y = self.config_y.text
        try:
            y = int(y)
        except ValueError:
            y = DEFAULT_MAP_SIZE[1]
        return max(x, MINIMUM_MAP_SIZE[0]), max(y, MINIMUM_MAP_SIZE[1])
