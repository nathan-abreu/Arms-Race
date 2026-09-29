"""Ponto de entrada do ARMS RACE (Python 3.12)."""
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description="ARMS RACE — Ringue Neon")
    parser.add_argument("--headless", action="store_true", help="Executa sem janela e áudio")
    parser.add_argument("--frames", type=int, default=0, help="Encerra após N quadros (0: ilimitado)")
    parser.add_argument("--scene", choices=("menu", "ringue"), default="menu")
    parser.add_argument("--no-audio", action="store_true", help="Desativa o mixer de áudio")
    args = parser.parse_args()
    if args.frames < 0:
        parser.error("--frames deve ser maior ou igual a zero")
    if args.headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
    from scripts.game import Game
    Game(args.scene,audio_enabled=not args.no_audio).run(args.frames)


if __name__ == "__main__":
    main()
