import sdl2 as sdl
import sdl2.sdlttf as sdl_ttf


class TextRenderer:
    def __init__(self, angle: int) -> None:
        self.font = sdl_ttf.TTF_OpenFont(b"PTSans.ttf", 24)
        # self.font = sdl_ttf.TTF_OpenFont(b"/System/Library/Fonts/SFNSMono.ttf", 24)
        if not self.font:
            print("Failed to load font:", sdl_ttf.TTF_GetError())
        self.angle = angle


    def draw(self, rend: sdl.SDL_Renderer, text: str, x: int, y: int):
        color = sdl.SDL_Color(255, 255, 255)
        # surface = sdl_ttf.TTF_RenderText_Solid(font, text.encode('utf-8'), color)
        surface: sdl.SDL_Surface = sdl_ttf.TTF_RenderUTF8_Blended(
            self.font, text.encode("utf-8"), color
        )
        if not surface:
            print("Failed to create surface for text:", sdl_ttf.TTF_GetError())
            return
        texture = sdl.SDL_CreateTextureFromSurface(rend, surface)
        text_rect = sdl.SDL_Rect(x, y, surface.contents.w, surface.contents.h)
        # sdl.SDL_RenderCopy(rend, texture, None, text_rect)
        sdl.SDL_RenderCopyEx(rend, texture, None, text_rect, self.angle, None, sdl.SDL_FLIP_NONE)
        sdl.SDL_FreeSurface(surface)
        sdl.SDL_DestroyTexture(texture)

    def __del__(self):
        sdl_ttf.TTF_CloseFont(self.font)
