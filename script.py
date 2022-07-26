import argparse
import json
import os
import subprocess
import tempfile
from itertools import count
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


def _extract_ttx_font(*, unpatched_ttc_fp: str, unpatched_ttx_fp: str, ttc_idx: int):
    try:
        subprocess.run(
            [
                "ttx",
                "-y",
                str(ttc_idx),
                "-o",
                unpatched_ttx_fp,
                unpatched_ttc_fp,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _compile_ttx_font(*, unpatched_ttx_fp, unpatched_ttf_fp):
    subprocess.run(
        ["ttx", "-o", unpatched_ttf_fp, unpatched_ttx_fp],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


def _patch_ttf_font(*, unpatched_ttf_fp, output_dir):
    subprocess.run(
        [
            "fontforge",
            "-script",
            "./font-patcher",
            unpatched_ttf_fp,
            "--complete",
            "--glyphdir",
            "./glyphs/",
            "--outputdir",
            output_dir,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


def patch_font(unpatched_font_fp: str | Path):
    unpatched_font_fp = Path(unpatched_font_fp)
    unpatched_font_fn, unpatched_font_ext = os.path.splitext(unpatched_font_fp.name)

    patched_fonts_dir = Path(f"fonts/{unpatched_font_fn}")
    patched_fonts_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        if unpatched_font_ext == ".ttc":
            for idx in count(0):
                # Extract a .ttx file
                unpatched_ttx_fp = f"{temp_dir}/{idx}.ttx"
                ok = _extract_ttx_font(
                    unpatched_ttc_fp=str(unpatched_font_fp),
                    unpatched_ttx_fp=unpatched_ttx_fp,
                    ttc_idx=idx,
                )
                if not ok:
                    break

                # Compile the .ttx file into a .ttf file
                print(f"[{idx}/x] Compiling .ttf ")
                unpatched_ttf_fp = f"{temp_dir}/{idx}.ttf"
                _compile_ttx_font(
                    unpatched_ttx_fp=unpatched_ttx_fp, unpatched_ttf_fp=unpatched_ttf_fp
                )

                # Patch the .ttf file
                print(f"[{idx}/x] Patching .ttf")
                _patch_ttf_font(
                    unpatched_ttf_fp=unpatched_ttf_fp, output_dir=patched_fonts_dir
                )

        elif unpatched_font_ext == ".ttf":
            print(f"Patching {unpatched_font_fp}")
            _patch_ttf_font(
                unpatched_ttf_fp=unpatched_font_fp, output_dir=patched_fonts_dir
            )
        else:
            print(f"File extension '{unpatched_font_ext}' not supported")
            return

    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch a .ttc or .ttf font file")
    parser.add_argument(
        "unpatched_font_fp", type=str, help="path to a .ttc or .ttf file"
    )
    parser.add_argument(
        "--skip-downloads",
        help="skip downloading the helper script and any glyphs",
        action="store_true",
    )
    args = parser.parse_args()

    if not args.skip_downloads:
        download_font_patcher()
        download_glyphs(local_path="glyphs", remote_path="src/glyphs")

    patch_font(args.unpatched_font_fp)
