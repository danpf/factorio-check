import logging
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Generator
from pathlib import Path

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(os.environ.get("LOGLEVEL", "WARNING").upper())


@dataclass
class FactorioController:
    factorio_executable: Path
    factorio_process: subprocess.Popen | None
    factorio_mods_dir: Path | None

    def launch_game(self) -> None:
        args = self.build_args(self.factorio_executable, self.factorio_mods_dir)
        self.factorioProcess = subprocess.Popen(
            executable=self.factorio_executable,
            args=args,
            cwd=self.factorio_executable.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        log.info(f"Started factorio process {self.factorio_process}")

    def terminate_game(self) -> None:
        if self.factorio_process is not None:
            if self.factorio_process.poll() is None:
                log.info(f"Closing {self.factorio_process}")
                self.factorio_process.terminate()
                self.factorio_process.wait()
            else:
                log.info(f"{self.factorio_executable} terminated unexpectedly...")
        self.factorio_process = None

    def get_game_output(self) -> Generator[bool | str, Any, bool]:
        if self.factorio_process is None:
            raise RuntimeError("Can't get output when process is None")
        for line in iter(self.factorio_process.stdout.readline, ""):
            line_data = line.strip().decode("utf-8")
            if line_data == "":
                yield self.factorio_process.poll() is None
            else:
                yield line_data
        self.factorio_process.stdout.close()
        return_code = self.factorio_process.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, self.factorio_executable)
        return False

    def executeUnitTests(self) -> bool:
        # This does not actually execute anything, it waits till the mod signals the tests are finished while logging all unit test results
        for line in self.getGameOutput():
            if type(line) is str:
                if re.fullmatch(r"angelsdev\-unit\-test: .*", line):
                    self.log(line[21:])
                    if re.fullmatch(r"angelsdev\-unit\-test: Finished testing!.*", line):
                        return True if re.fullmatch(r".* All unit tests passed!", line) else False
                elif re.fullmatch(r" *[0-9]+\.[0-9]{3} Error ModManager\.cpp\:[0-9]+\:.*", line):
                    self.log(line[re.match(r" *[0-9]+\.[0-9]{3} Error ModManager\.cpp\:[0-9]+\: *", line).regs[0][1] :])
                    return False  # Error during launch launch
            elif type(line) is bool and line == False:
                return False  # Terminated factorio
        return False  # unexpected end

    def build_args(self, factorio_executable: Path, factorio_mods_dir: Path | None) -> list[str]:
        args = [
            str(factorio_executable),
            "--load-scenario",
            "base/freeplay",
        ]
        if factorio_mods_dir is not None:
            args.append("--mod-directory")
            args.append(str(factorio_mods_dir))

        return args


# def parseargs(args: List[str]) -> argparse.Namespace:
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--thing1", help="thing1")
#     return parser.parse_args(args)
#
# if __name__ == "__main__":
#     fc = FactorioController()
#     fc.launchGame()
#     fc.executeUnitTests()
#     fc.terminateGame()
#
# #!#!/usr/bin/env python
#
# import argparse
# from typing import List
# import sys
# import logging
#
# log = logging.getLogger(__name__)
#
#
#
def main_cli() -> None:
    return


#
#     pass
#
# if __name__ == "__main__":
#     main(sys.argv[1:])
