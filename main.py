import ctypes
import random
from file_io import get_recusrive
from concurrent.futures import ThreadPoolExecutor, wait
import pandas as pd
import matplotlib.pyplot as plt
import time
import logging

# import tkinter as tk
import sdl2 as sdl
import sdl2.sdlttf as sdl_ttf

from collections import defaultdict
from gfx.text import TextRenderer
from gfx.fps import Fps
from gfx.rect import RectRenderer

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    # format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S",
)


ext_dict = defaultdict((int))
size_dict = defaultdict((int))
window_x = 1000
window_y = 750
df_files: pd.DataFrame = None # type: ignore
new_data_available = False
cached_boxes: list = []
cached_box_colors: list = []
running: bool = True
window: sdl.SDL_Window


def worker_count_files():
    # get_recusrive("/home/dnb/dev/", ext_dict=ext_dict, size_dict=size_dict)
    get_recusrive("/Users/david/dev/", ext_dict=ext_dict, size_dict=size_dict)
    print(
        f"Done counting files. ext_dict:{len(ext_dict)} size_dict len: {len(size_dict)}"
    )


def worker_prepare_for_render():
    global new_data_available
    global df_files
    while running:
        new_df_files: pd.DataFrame = get_file_stats()
        if df_files is None or df_files.empty or (new_df_files.size != df_files.size):
            df_files = new_df_files
            new_data_available = True
        time.sleep(2)


def get_file_stats() -> pd.DataFrame:
    # os.system("clear")
    print(f"len: {len(ext_dict)}")
    df = pd.DataFrame(ext_dict.items(), columns=["Extension", "Count"])

    # if i use str dtype, pandas converts to object which is not what I want
    df["Extension"] = df["Extension"].astype(pd.StringDtype())
    df.sort_values(by="Count", ascending=False, inplace=True)
    # print(df.shape)
    # print(df.columns)
    # print(df.head(40))
    return df


def draw_plt():
    # check n items
    n = 1
    df = pd.DataFrame()
    while n < 1000:
        n += 1
        df = get_file_stats()
        x = df["Extension"].head(5).values
        y = df["Count"].head(5).values

        # must be rendered in main thread
        plt.close()
        plt.bar(x, y)
        plt.xlabel("Extension")
        plt.ylabel("Count")
        plt.title("Top 5 File Extensions")
        plt.draw()
        plt.pause(0.2)


def divide_area_by_percentages_2(
    total_area,
    percentages,
    canvas_width=1000,
    canvas_height=1000,
    min_ratio=0.5,
    max_ratio=2.0,
    padding=10,
):
    """
    Delar in en area enligt procentandelar utan överlappning.

    Args:
        total_area: Total area att dela
        percentages: Lista med procentandelar
        canvas_width: Bredd på canvas
        canvas_height: Höjd på canvas
        min_ratio: Minsta höjd/bredd-förhållande
        max_ratio: Största höjd/bredd-förhållande
        padding: Mellanrum mellan delarna

    Returns:
        Lista med tupler (x, y, höjd, bredd, area)
    """
    parts = []
    occupied = []  # Håller koll på redan placerade områden

    for percentage in percentages:
        area = total_area * (percentage / 100)

        # Randomisera höjd/bredd-förhållande
        ratio = random.uniform(min_ratio, max_ratio)
        height = (area / ratio) ** 0.5
        width = height * ratio

        # Försök hitta en ledig position
        placed = False
        attempts = 0
        max_attempts = 50

        while not placed and attempts < max_attempts:
            x = random.uniform(0, max(0, canvas_width - width))
            y = random.uniform(0, max(0, canvas_height - height))

            # Kontrollera om denna position överlappar något redan placerat
            if not overlaps(x, y, width, height, occupied, padding):
                parts.append((x, y, height, width, area))
                occupied.append((x, y, width, height))
                placed = True

            attempts += 1

        if not placed:
            print(f"Varning: Del {len(parts)+1} kunde inte placeras utan överlappning")

    return parts


def overlaps(x, y, width, height, occupied, padding=0):
    """Kontrollerar om en rektangel överlappar med någon i occupied-listan."""
    for ox, oy, owidth, oheight in occupied:
        if not (
            x + width + padding < ox
            or x > ox + owidth + padding
            or y + height + padding < oy
            or y > oy + oheight + padding
        ):
            return True
    return False


def divide_area_by_percentages(total_area, percentages, min_ratio=0.5, max_ratio=2.0):
    """
    Delar in en area enligt procentandelar med randomiserad höjd/bredd.

    Args:
        total_area: Total area att dela
        percentages: Lista med procentandelar
        min_ratio: Minsta höjd/bredd-förhållande
        max_ratio: Största höjd/bredd-förhållande

    Returns:
        Lista med tupler (höjd, bredd, area)
    """
    parts = []

    for percentage in percentages:
        area = total_area * (percentage / 100)

        # Randomisera höjd/bredd-förhållande
        ratio = random.uniform(min_ratio, max_ratio)

        # Beräkna höjd och bredd från area och förhållande
        # area = höjd * bredd, bredd = höjd * ratio
        height = (area / ratio) ** 0.5
        width = height * ratio

        parts.append((height, width, area))

    return parts


# Exempel
total = 100
percentages = [50, 30, 20]
result = divide_area_by_percentages(total, percentages)

for i, (h, w, a) in enumerate(result):
    print(f"Del {i+1}: Höjd={h:.2f}, Bredd={w:.2f}, Area={a:.2f}")


def _render_cached_boxes(rend: sdl.SDL_Renderer, recs: RectRenderer):
    global cached_boxes
    global cached_box_colors
    recs.set_rects(cached_boxes, cached_box_colors)
    # for rect, color in zip(cached_boxes, cached_box_colors):
    #     sdl.SDL_SetRenderDrawColor(rend, color.r, color.g, color.b, 255)
    #     sdl.SDL_RenderFillRect(rend, rect)

def _draw_sdl_files(rend: sdl.SDL_Renderer):
    global new_data_available
    global cached_boxes
    global cached_box_colors
    global window
    if not new_data_available:
        return

    cached_boxes.clear()
    cached_box_colors.clear()
    n_files: int = 10
    window_x = ctypes.c_int()
    window_y = ctypes.c_int()
    sdl.SDL_GetWindowSize(window, window_x, window_y)
    w_area: int = window_x.value * window_y.value
    logging.debug(f"Window size: {window_x.value}x{window_y.value}")
    # den måste renderas varje frame om den inte ska blinka...
    start = time.perf_counter()
    tot_extensions: int = df_files["Count"].sum()
    i: int = 0
    percentages: list[int] = []
    for tuple in df_files.head(n_files).itertuples():
        part: int = tuple.Count / tot_extensions  # type: ignore
        percentages.append(part * 100)

    result = divide_area_by_percentages_2(
        w_area, percentages, canvas_width=window_x.value, canvas_height=window_y.value, padding=10
    )
    for i, (x, y, h, w, a) in enumerate(result):
        rect = sdl.SDL_Rect(int(x), int(y), int(w), int(h))
        color = sdl.SDL_Color(
            random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)
        )
        cached_boxes.append(rect)
        cached_box_colors.append(color)
        # sdl.SDL_SetRenderDrawColor(rend, color.r, color.g, color.b, 255)
        # sdl.SDL_RenderFillRect(rend, rect)
        i += 1
    end = time.perf_counter()
    logging.debug(f"render time: {end - start:.4f} seconds")

    # logging.debug("Rendering file extension counts...")
    _draw_sdl_text(rend, "File Extension Counts:", 50, 20)
    new_data_available = False


def _draw_sdl_text(rend: sdl.SDL_Renderer, text: str, x: int, y: int):
    txtRend = TextRenderer(0)
    txtRend.draw(rend, text, x, y)


def draw_sdl_main():
    global running
    global window
    sdl.SDL_Init(sdl.SDL_INIT_VIDEO)
    if sdl_ttf.TTF_Init() < 0:
        print("Failed to initialize TTF:", sdl_ttf.TTF_GetError())
        return
    window = sdl.SDL_CreateWindow(
        b"File Extension Count",
        sdl.SDL_WINDOWPOS_CENTERED,
        sdl.SDL_WINDOWPOS_CENTERED,
        window_x,
        window_y,
        sdl.SDL_WINDOW_SHOWN,
    )
    # sdl.SDL_SetHint(sdl.SDL_HINT_RENDER_DRIVER, b"direct3d")
    ren = sdl.SDL_CreateRenderer(
        # window, -1, sdl.SDL_RENDERER_SOFTWARE
        window, -1, sdl.SDL_RENDERER_ACCELERATED | sdl.SDL_RENDERER_PRESENTVSYNC
    )
    fps = Fps()
    recs = RectRenderer()
    info = sdl.SDL_RendererInfo()
    sdl.SDL_GetRendererInfo(ren, info)
    if(info.flags & sdl.SDL_RENDERER_ACCELERATED):
        print(f"Using accelerated renderer: {info.name.decode('utf-8')}")
    if(info.flags & sdl.SDL_RENDERER_SOFTWARE):
        print("Using software renderer")
    # --- main loop ---
    while running:
        fps.start()
        event = sdl.SDL_Event()
        while sdl.SDL_PollEvent(event) != 0:
            if event.type == sdl.SDL_QUIT:
                running = False
            if event.type == sdl.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl.SDLK_q:
                    running = False
        # background
        sdl.SDL_SetRenderDrawColor(ren, 0, 0, 0, 0)
        # clear screen with color
        sdl.SDL_RenderClear(ren)

        # --- draw here ---
        # fps
        fps.draw(ren, 10, 10)
        # files
        _draw_sdl_files(ren)
        _render_cached_boxes(ren, recs=recs)
        recs.update()
        recs.draw(ren)
        # --- end draw ---

        fps.tick()
        sdl.SDL_RenderPresent(ren)
    # --- end main loop ---

    # --- cleanup ---
    # sdl.SDL_DestroyTexture(tex)
    sdl.SDL_DestroyRenderer(ren)
    sdl.SDL_DestroyWindow(window)
    sdl.SDL_Quit()
    sdl_ttf.TTF_Quit()


# main
def main():
    # plt.ion()
    # plt.show(block=False)
    print("Starting file extension count...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(worker_count_files),
            executor.submit(worker_prepare_for_render),
        ]
        # futures = [executor.submit(do_work), executor.submit(check_extensions)]
        draw_sdl_main()
        # draw_plt()
        wait(futures)
        # check if any exceptions
        futures[0].result()
        # futures[1].result()


if __name__ == "__main__":
    main()
