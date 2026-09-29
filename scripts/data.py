"""Carregamento independente das cenas; caminhos relativos ao projeto."""
import json
from scripts.config import ROOT


def load_level(name="ringue_neon"):
    path = ROOT / "dados" / "levels" / f"{name}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data["name"], str)
        assert len(data["platforms"]) >= 1
        for rect in data["platforms"]:
            assert len(rect) == 4 and all(isinstance(v, (int, float)) for v in rect)
            assert rect[2] > 0 and rect[3] > 0
        assert len(data["player_spawn"]) == len(data["enemy_spawn"]) == 2
        assert data["weapon_interval"] > 0 and data["weapon_warning"] > 0
        if name == "ringue_neon":
            from scripts.arena_layout import apply_layout
            data = apply_layout(data)
        return data
    except (OSError, ValueError, KeyError, TypeError, AssertionError) as exc:
        raise ValueError("Não foi possível carregar os dados do Ringue Neon.") from exc
