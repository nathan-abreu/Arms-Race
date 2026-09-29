"""Balanceamento em px, segundos e px/s; sem dependência de renderização."""
from dataclasses import dataclass


@dataclass(frozen=True)
class MovementTuning:
    speed: float = 380
    acceleration: float = 2800
    reversal: float = 5400
    friction: float = 3400
    air_control: float = .65
    air_acceleration: float = 2800 * .65
    air_drag: float = 260
    gravity: float = 1900
    fall_multiplier: float = 2700 / 1900
    terminal_speed: float = 1100
    jump_speed: float = 720
    jump_cut_speed: float = 270
    coyote: float = .12
    buffer: float = .12
    hitstun: float = .13
    invulnerability: float = .22


@dataclass(frozen=True)
class CombatTuning:
    preparation: float = .045
    recovery: float = .12
    strong_stop: float = .065
    light_stop: float = .040
    combo_window: float = .400
    combo_buffer: float = .100
    combo_durations: tuple = (.230, .250, .340)
    combo_active: tuple = (.080, .090, .115)
    combo_damage: tuple = (7, 8, 13)
    combo_knockback: tuple = (255, 285, 440)
    aim_deadzone: float = 12
    pan_arc: float = 65
    pan_stop: float = .080
    hit_flash: float = .050
    body_spacing: float = 84


@dataclass(frozen=True)
class DeliveryTuning:
    warning: float = .9
    opening: float = .12
    acceleration: float = 2150
    pickup_flight: float = .18
    impact_compression: float = .12


DELIVERY = DeliveryTuning()


@dataclass(frozen=True)
class AITuning:
    reaction_min: float = .14
    reaction_max: float = .24
    mistake_chance: float = .10
    edge_margin: float = 55
    danger_radius: float = 100
    low_health: int = 28


MOVEMENT = MovementTuning()
COMBAT = CombatTuning()
AI = AITuning()
