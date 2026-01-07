import sdl2 as sdl


class RectRenderer:
    def __init__(self) -> None:
        self.rects = []
        self.colors = []
        # For animation preparation
        self.target_rects = []
        self.animation_speed = 0.2  # Example speed for animation


    def set_rects(self, rects: list[sdl.SDL_Rect], colors: list[sdl.SDL_Color]) -> None:
        # If we don't have rects yet, initialize them at starting positions
        if not self.rects:
            self.rects = [sdl.SDL_Rect(0, 0, 0, 0) for _ in rects]
        # Always set new targets (don't overwrite current positions)
        self.target_rects = [sdl.SDL_Rect(r.x, r.y, r.w, r.h) for r in rects]
        self.colors = colors[:]

    def draw(self, rend: sdl.SDL_Renderer) -> None:
        for rect, color in zip(self.rects, self.colors):
            sdl.SDL_SetRenderDrawColor(rend, color.r, color.g, color.b, 255)
            sdl.SDL_RenderFillRect(rend, rect)

    def update(self) -> None:
        # Placeholder for animation logic
        # For example, move rects towards target positions
        for i, rect in enumerate(self.rects):
            if i < len(self.target_rects):
                target = self.target_rects[i]
                rect.x += int((target.x - rect.x) * self.animation_speed)
                rect.y += int((target.y - rect.y) * self.animation_speed)
                rect.w += int((target.w - rect.w) * self.animation_speed)
                rect.h += int((target.h - rect.h) * self.animation_speed)

