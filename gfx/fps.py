import sdl2 as sdl
from gfx.text import TextRenderer


class Fps:
    target_fps = 60.0
    desired_frame_time = 1000.0 / target_fps

    def __init__(self) -> None:
        self.start_tick = 0.0
        self.delta = 0.0
        self.avg_fps = 0.0

    def draw(self, rend: sdl.SDL_Renderer, x: int, y: int):
        txtRend = TextRenderer(0)
        txtRend.draw(rend, f"FPS: {round(self.avg_fps, 0)}", x, y)

    def start(self) -> None:
        self.start_tick = sdl.SDL_GetTicks()

    def tick(self) -> None:
        # time spent so far in this frame (ms)
        elapsed = sdl.SDL_GetTicks() - self.start_tick
        frame_delay = self.desired_frame_time - elapsed
        # sleep if we finished early so the total frame time ~= desired_frame_time
        if frame_delay > 0:
            sdl.SDL_Delay(int(frame_delay))
        # recompute total frame time including any delay and update fps
        self.delta = sdl.SDL_GetTicks() - self.start_tick
        if self.delta > 0:
            self.avg_fps = 1000.0 / self.delta

    def tick_old(self) -> None:
        self.delta = sdl.SDL_GetTicks() - self.start_tick
        frame_delay = self.desired_frame_time - self.delta
        if frame_delay > 0:
            sdl.SDL_Delay(int(frame_delay))
        if self.delta > 0:
            self.avg_fps = 1000.0 / self.delta

