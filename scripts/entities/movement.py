"""Motor cinemático compartilhado, plataformas unidirecionais e paredes sólidas."""
import pygame
from scripts.balance import MOVEMENT as T


def approach(value, target, amount):
    return value + max(-amount, min(amount, target - value))


class Movement:
    def init_movement(self):
        self.coyote_time = self.jump_buffer = 0.0
        self.jump_held = False
        self.jump_consumed = False
        self.was_grounded = False
        self.braking = False
        self.start_run = 0.0
        self.movement_state = "parado"

    def jump(self):
        if (self.grounded or self.coyote_time > 0) and not self.jump_consumed and self.stun <= 0 and self.alive:
            self.velocity.y = -T.jump_speed
            self.grounded = False
            self.coyote_time = self.jump_buffer = 0
            self.jump_consumed = True
            self.jump_held = True
            self.events.append("jump")
            return True
        return False

    def request_jump(self):
        self.jump_held = True
        self.jump_buffer = T.buffer
        return self.jump()

    def release_jump(self):
        self.jump_held = False
        if self.velocity.y < -T.jump_cut_speed:
            self.velocity.y = -T.jump_cut_speed

    def move_step(self, dt, platforms, walls=()):
        self.landed_speed = 0
        self.was_grounded = self.grounded
        if self.grounded:
            self.coyote_time = T.coyote
            self.jump_consumed = False
        else:
            self.coyote_time = max(0, self.coyote_time-dt)
        if self.jump_buffer > 0:
            self.jump()
            self.jump_buffer = max(0, self.jump_buffer-dt)
        self.braking = self.grounded and abs(self.velocity.x)>140 and self.axis*self.velocity.x<=0
        self.start_run = max(0, self.start_run-dt)
        if self.stun <= 0:
            axis = max(-1, min(1, self.axis))
            if axis and self.grounded and abs(self.velocity.x)<20:
                self.start_run = .10
            acceleration = T.acceleration if self.grounded else T.air_acceleration
            if axis*self.velocity.x<0 and self.grounded:
                acceleration = T.reversal
            if not axis:
                acceleration = T.friction if self.grounded else T.air_drag
            self.velocity.x = approach(self.velocity.x, axis*T.speed, acceleration*dt)
            if axis and not self.aim_locked:
                self.facing = 1 if axis>0 else -1
        old = self.rect
        self.pos.x += self.velocity.x*dt
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.velocity.x>0:
                    self.pos.x = wall.left-self.WIDTH/2
                elif self.velocity.x<0:
                    self.pos.x = wall.right+self.WIDTH/2
                self.velocity.x = 0
        gravity = T.gravity * (T.fall_multiplier if self.velocity.y>0 else 1)
        self.velocity.y = min(T.terminal_speed, self.velocity.y+gravity*dt)
        self.pos.y += self.velocity.y*dt
        self.grounded = False
        if self.velocity.y>=0:
            for platform in sorted((*platforms, *walls), key=lambda p:p.top):
                if self.rect.right>platform.left+1 and self.rect.left<platform.right-1 and old.bottom<=platform.top+1 and self.pos.y>=platform.top:
                    self.landed_speed = self.velocity.y if self.velocity.y>180 else 0
                    if self.landed_speed:
                        self.landing_time = .12
                        self.events.append("landing")
                    self.pos.y = platform.top
                    self.velocity.y = 0
                    self.grounded = True
                    self.jump_consumed = False
                    self.coyote_time = T.coyote
                    if self.jump_buffer>0:
                        held = self.jump_held
                        self.jump()
                        if not held:
                            self.release_jump()
                    break
        else:
            for wall in walls:
                if self.rect.colliderect(wall) and old.top>=wall.bottom-1:
                    self.pos.y = wall.bottom+self.HEIGHT
                    self.velocity.y = 0
        self.movement_state = ("derrotado" if not self.alive else "dano" if self.stun>0 else
                               "pousando" if self.landing_time>0 else
                               "pulando" if self.velocity.y<-10 else "caindo" if not self.grounded else
                               "freando" if self.braking else "correndo" if abs(self.velocity.x)>30 else "parado")
