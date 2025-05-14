import sys

from Game_components.game_state import GameState
from Game_components.game_renderer import GameRenderer
from Game_components.game_renderer_core import GameRendererCore
from Game_components.game_render_hud import GameRendererHud
from Game_components.input_handler import InputHandler
from Game_components.game_engine import GameEngine

def main():
    game_state = GameState()

    game_renderer = GameRenderer(game_state)

    input_handler = InputHandler(game_state, game_renderer)

    game_engine = GameEngine(game_state, game_renderer, input_handler)
    game_engine.start()

if __name__ == "__main__":
    main()
