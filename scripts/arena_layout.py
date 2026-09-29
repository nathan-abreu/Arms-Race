"""Marcos normalizados da imagem v2; posição física representa a sola dos pés."""
from scripts.config import WIDTH, HEIGHT, ROOT

BACKGROUND_PATH = ROOT / "assets" / "imagens" / "ringue_neon_background_v2.png"
GROUND_Y = .714
LEFT_EDGE = .105
RIGHT_EDGE = .895
SPAWNS = (.29, .71)
DROP_POINTS = (.40, .50, .60)
FIGHTER_HEIGHT = 164
FIGHTER_WIDTH = 56
SHOULDER_HEIGHT = 108


def apply_layout(data):
    """O JSON continua fornecendo as regras; esta imagem define a geometria."""
    data = dict(data)
    from scripts.balance import DELIVERY
    data['weapon_warning']=DELIVERY.warning
    floor = round(HEIGHT * GROUND_Y)
    left, right = round(WIDTH * LEFT_EDGE), round(WIDTH * RIGHT_EDGE)
    data["platforms"] = [[left, floor, right-left, 24]]
    data["player_spawn"], data["enemy_spawn"] = ([round(x*WIDTH), floor] for x in SPAWNS)
    data["weapon_drop_points"] = [round(x*WIDTH) for x in DROP_POINTS]
    return data
