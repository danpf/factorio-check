import argparse
from dataclasses import dataclass, field
import logging
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Generator

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(os.environ.get("LOGLEVEL", "WARNING").upper())


@dataclass
class FactorioController:
    factorio_executable: Path
    factorio_mods_dir: Path | None
    factorio_process: subprocess.Popen | None = None
    testing_logs: list[str] = field(default_factory=list)

    def launch_game(self) -> None:
        args = self.build_args(self.factorio_executable, self.factorio_mods_dir)
        self.factorio_process = subprocess.Popen(
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
        if self.factorio_process.stdout is None:
            raise RuntimeError("Can't get output when process.stdout is None")
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

    def execute_unit_tests(self) -> None:
        """
        Runs the unit tests and adds up the testing_logs
        """
        unit_tests_start = False
        self.testing_logs = []
        for line in self.get_game_output():
            if isinstance(line, str):
                if line.startswith("UNIT TESTS START"):
                    unit_tests_start = True
                    self.testing_logs.append(line)
                elif unit_tests_start:
                    self.testing_logs.append(line)
                elif line.startswith("UNIT TESTS DONE"):
                    self.testing_logs.append(line)
                    self.terminate_game()
                    break

    def analyze_unit_test_results(self) -> bool:
        failed_tests = False
        log.info("analyzing...")
        for line in self.testing_logs:
            print(line)
        failed_tests = False
        for line in self.testing_logs:
            if line.startswith("Total tests failed"):
                split_line = line.split()
                if int(split_line[-1]) == 0:
                    failed_tests = True
        return failed_tests

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


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--factorio_executable", type=Path, help="thing1", required=True)
    parser.add_argument("--factorio_mods_dir", type=Path, help="thing2")
    return parser.parse_args(args)


def main_cli() -> None:
    args = parse_args(sys.argv[1:])
    fc = FactorioController(
        factorio_executable=args.factorio_executable,
        factorio_mods_dir=args.factorio_mods_dir,
    )
    fc.launch_game()
    fc.execute_unit_tests()
    fc.terminate_game()
    tests_pass = fc.analyze_unit_test_results()
    if not tests_pass:
        raise RuntimeError("Tests failed")
