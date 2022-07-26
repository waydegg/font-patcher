import json
import os
from pathlib import Path
from urllib import request

font_file_extentions = ["ttf", "otf", "sfd"]

base_url = "https://api.github.com/repos/ryanoasis/nerd-fonts/contents"
headers = {"Accept": "application/vnd.github.v3.raw"}


def download_font_patcher():
    print("Downloading script: font-patcher")
    request.urlretrieve(
        "https://raw.githubusercontent.com/ryanoasis/nerd-fonts/master/font-patcher",
        "font-patcher",
    )


def download_glyphs(*, local_path: str | Path, remote_path: str | Path):
    local_path = Path(local_path) if isinstance(local_path, str) else local_path
    remote_path = Path(remote_path) if isinstance(remote_path, str) else remote_path

    local_path.mkdir(exist_ok=True)

    glyphs_url = f"{base_url}/{remote_path}"
    glyphs_req = request.Request(glyphs_url, headers=headers)
    glyphs_res = request.urlopen(glyphs_req)
    glyphs_res_data = json.loads(glyphs_res.read())

    for obj in glyphs_res_data:
        file_full_name = obj["name"]
        file_type = obj["type"]
        file_remote_path = Path(obj["path"])

        if file_type == "dir":
            next_local_path = os.path.join(local_path, file_remote_path.parts[-1])
            next_remote_path = file_remote_path
            download_glyphs(local_path=next_local_path, remote_path=next_remote_path)

        if file_type == "file":
            _, file_extention = os.path.splitext(file_full_name)
            if file_extention[1:] not in font_file_extentions:
                continue
            print(f"Downloading glyphs: {file_full_name}")
            download_path = str(file_remote_path).split("/", 1)[1]
            request.urlretrieve(obj["download_url"], download_path)


def patch_font(raw_font_path: str | Path):
    raw_font_path = Path(raw_font_path)
    raw_font_name = raw_font_path.name.split(".")[0]

    fonts_path = Path("fonts")
    font_path = os.path.join(fonts_path, raw_font_name)
    unpatched_fonts_path = Path(os.path.join(font_path, "unpatched"))
    patched_font_path = Path(os.path.join(font_path, "patched"))

    unpatched_fonts_path.mkdir(parents=True, exist_ok=True)
    patched_font_path.mkdir(exist_ok=True)

    font_weights = ["regular", "bold", "italic", "bold-italic"]
    for idx, font_weight in enumerate(font_weights):
        font_weight_msg = f"{font_weight.capitalize()} {raw_font_name}"

        print(f"Extracting {font_weight_msg}")
        unpatched_ttx_fp = os.path.join(unpatched_fonts_path, font_weight) + ".ttx"
        os.system(f"ttx -y {idx} -q -o {unpatched_ttx_fp} {raw_font_path}")

        print(f"Compiling {font_weight_msg}")
        unpatched_ttf_fp = os.path.join(unpatched_fonts_path, font_weight) + ".ttf"
        os.system(f"ttx -q -o {unpatched_ttf_fp} {unpatched_ttx_fp} ")

        print(f"Patching {font_weight_msg}")
        patching_args = [
            "fontforge",
            "-script",
            "./font-patcher",
            unpatched_ttf_fp,
            "--complete",
            "--glyphdir",
            "./glyphs/",
            "--outputdir",
            str(patched_font_path),
            ">/dev/null 2>&1",
        ]
        patching_command = " ".join(patching_args)
        os.system(patching_command)


if __name__ == "__main__":
    # Download font patcher script
    download_font_patcher()

    # Download glyphs
    download_glyphs(local_path="glyphs", remote_path="src/glyphs")

    patch_font("/System/Library/Fonts/Menlo.ttc")
    # patch_font("/System/Library/Fonts/Avenir.ttc")
    # patch_font("/System/Library/Fonts/Noteworthy.ttc")
