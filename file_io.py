from pathlib import Path


def get_recusrive(
    directory: str, ext_dict: dict[str, int], size_dict: dict[str, int]
) -> None:
    path = Path(directory)
    for dirpath, dirnames, filenames in path.walk():
        for filename in filenames:
            p = Path(dirpath)
            ext = get_ext(filename, p)
            if ext == "":
                continue
            ext_dict[ext] += 1
            handle_size(ext, p, size_dict)


def handle_size(ext: str, file_path: Path, size_dict: dict[str, int]) -> None:
    byte_size = file_path.stat().st_size
    size_dict[ext] += (int)(byte_size / 1024)  # store size in KB
    pass


def get_ext(filename: str, path: Path) -> str:
    # if no suffixes, try to parse manually
    if len(path.suffixes) == 0:
        if filename.find(".") > -1:
            return filename.rsplit(".", 1)[-1]
        # else:
        #     print("NO SUFFIX:", filename, p.suffixes)

    # normal suffix counting
    return path.suffix
    # ext_dict[path.suffix] += 1


def get_dirs(directory: str) -> list[str]:
    dirs = [entry for entry in Path(directory).iterdir() if entry.is_dir()]
    return [d.name for d in dirs]


def count_file_extensions(directory: str, ext_dict: dict):
    files = Path(directory).iterdir()
    for entry in files:
        if not entry.is_file():
            continue
        ext_dict[entry.suffix] += 1
