#!/usr/bin/env python

import argparse
import json
import logging
import os
from pathlib import Path
import subprocess
import sys

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(os.environ.get("LOGLEVEL", "WARNING").upper())


def parseargs(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mod-folders",
        nargs="+",
        type=Path,
        default=[os.environ["FACTORIO_CHECK_mod_folders"]]
        if os.environ.get("FACTORIO_CHECK_mod_folders", "")
        else [],
        help="A list of mod folders that you would like to package",
    )
    parser.add_argument(
        "--factorio-folder", required=True, type=Path, help="The base factorio folder"
    )
    return parser.parse_args(args)


def delete_previously_existing_zips(zip_name: str, factorio_folder: Path) -> None:
    previously_existing_zips = list(factorio_folder.glob(f"{zip_name}_*.zip"))
    for previously_existing_zip in previously_existing_zips:
        previously_existing_zip.unlink()


def zip_dir_and_move_zip_to_folder(
    addon_folder: Path, factorio_final_folder: Path
) -> None:
    """
    Final folder may be the mods or scenarios folder
    """
    log.debug(f"working on {addon_folder}")
    print(f"working on {addon_folder}")
    print(log)
    og_dir = os.getcwd()
    info_file = addon_folder / "info.json"
    with open(info_file) as fh:
        info_file_data = json.load(fh)
    mod_name = info_file_data["name"]
    mod_version = info_file_data["version"]
    delete_previously_existing_zips(mod_name, factorio_final_folder)
    os.chdir(addon_folder.parent)
    log.debug(f"In directory {os.getcwd()}")
    zipfile_to_save = Path(f"{mod_name}_{mod_version}.zip")
    command = ["zip", "-r", str(zipfile_to_save), str(addon_folder.name)]
    r = subprocess.run(command)
    if r.returncode:
        raise RuntimeError(f"Failure to run command: {' '.join(command)}")

    command = [
        "mv",
        str(zipfile_to_save),
        str(factorio_final_folder / str(zipfile_to_save)),
    ]
    r = subprocess.run(command)
    if r.returncode:
        raise RuntimeError(f"Failure to run command: {' '.join(command)}")

    os.chdir(og_dir)
    log.debug(f"Finished {addon_folder}")


def main(
    mod_folders: list[Path], scenario_folders: list[Path], factorio_folder: Path
) -> None:
    for mod_folder in mod_folders:
        zip_dir_and_move_zip_to_folder(
            mod_folder.resolve(), (factorio_folder / "mods").resolve()
        )
    for scenario_folder in scenario_folders:
        zip_dir_and_move_zip_to_folder(
            scenario_folder.resolve(), (factorio_folder / "scenario").resolve()
        )


def main_cli() -> None:
    args = parseargs(sys.argv[1:])
    main(args.mod_folders, [], args.factorio_folder)
