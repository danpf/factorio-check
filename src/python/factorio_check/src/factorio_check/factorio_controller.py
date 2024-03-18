import argparse
from dataclasses import dataclass, field
import logging
import os
import shutil
from pathlib import Path
import time
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
    factorio_scenario_dir: Path | None
    scenario: str
    scenario_copy_dirs: list[Path]
    mods_copy_dirs: list[Path]
    factorio_process: subprocess.Popen | None = None
    testing_logs: list[str] = field(default_factory=list)
    use_box64: bool = False
    max_seconds: int = 300
    start_time: int = 0
    tests_ran: bool = False

    def launch_game(self) -> None:
        self.pre_copy_dirs()
        self.tests_ran = False
        args = self.build_args(self.factorio_executable, self.factorio_mods_dir)
        self.start_time = int(time.time())
        if self.use_box64:
            args.insert(0, "box64")
        self.factorio_process = subprocess.Popen(
            args,
            cwd=self.factorio_executable.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        log.info(f"Started factorio process {' '.join(args)}")

    def pre_copy_dirs(self) -> None:
        if self.factorio_scenario_dir:
            for pth in self.scenario_copy_dirs:
                copy_path = self.factorio_scenario_dir / pth.name
                if copy_path.is_dir():
                    shutil.rmtree(copy_path)
                copy_to_path = f"cp {pth} {copy_path}"
                log.info(copy_to_path)
                shutil.copytree(pth, copy_path)
        if self.factorio_mods_dir:
            for pth in self.mods_copy_dirs:
                copy_path = self.factorio_mods_dir / pth.name
                if copy_path.is_dir():
                    shutil.rmtree(copy_path)
                copy_to_path = f"cp {pth} {copy_path}"
                log.info(copy_to_path)
                shutil.copytree(pth, copy_path)

    def terminate_game(self) -> None:
        if self.factorio_process is not None:
            if self.factorio_process.poll() is None:
                timeout_seconds = 20
                try:
                    log.info(f"Closing {self.factorio_process}")
                    try:
                        self.factorio_process.wait(timeout=timeout_seconds)
                    except subprocess.TimeoutExpired:
                        log.warning(
                            f"Process did not terminate in {timeout_seconds} seconds, forcefully killing."
                        )
                        self.factorio_process.kill()
                except Exception as e:
                    log.error(f"Error while terminating the process: {e}")
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
        log.info("Executing unit tests...")
        unit_tests_start = False
        self.testing_logs = []
        for line in self.get_game_output():
            if line is False:
                log.warning("Game output is false, process may have terminated...")
                break
            c_time = time.time()
            if int(c_time - self.start_time) > self.max_seconds:
                log.warning("Max seconds exceeded, terminating...")
                break
            if isinstance(line, str):
                if "UNIT TESTS START" in line:
                    unit_tests_start = True
                    log.debug(f"Add: {line}")
                    self.testing_logs.append(line)
                elif "UNIT TESTS DONE" in line:
                    log.debug(f"Add: {line}")
                    self.testing_logs.append(line)
                    log.info("Unit tests end found, terminating gracefully...")
                    self.terminate_game()
                    log.info("Terminated...")
                    self.tests_ran = True
                    break
                elif unit_tests_start:
                    log.debug(f"Unit tests start Add: {line}")
                    self.testing_logs.append(line)
                else:
                    log.debug(f"Pre/Post test line: {line}")


    def analyze_unit_test_results(self) -> bool:
        failed_tests = False
        log.info("analyzing...")
        if not self.tests_ran:
            log.error("Tests did not run")
            return False
        for line in self.testing_logs:
            log.info(line)
        failed_tests = False
        for line in self.testing_logs:
            if "Total tests failed" in line:
                split_line = line.split()
                if int(split_line[-1]) == 0:
                    failed_tests = True
        return failed_tests

    def build_args(
        self, factorio_executable: Path, factorio_mods_dir: Path | None
    ) -> list[str]:
        args = [
            str(factorio_executable),
            "--start-server-load-scenario",
            self.scenario if self.scenario else "base/freeplay",
        ]
        if factorio_mods_dir is not None:
            args.append("--mod-directory")
            args.append(str(factorio_mods_dir))

        return args


def parse_args(args: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--factorio_executable",
        type=Path,
        help="Path to the factorio executable",
        required=False,
        default=Path(os.environ["FACTORIO_CHECK_factorio_executable"])
        if os.environ.get("FACTORIO_CHECK_factorio_executable")
        else Path("/opt/factorio/bin/x64/factorio"),
    )
    parser.add_argument(
        "--use_box64",
        help="Use box64 to run factorio",
        default=True
        if os.environ.get("FACTORIO_CHECK_use_box64")
        else False,
        action="store_true",
    )
    parser.add_argument(
        "--factorio_mods_dir",
        type=Path,
        help="Path to the factorio mods directory",
        default=Path(os.environ["FACTORIO_CHECK_factorio_mods_dir"])
        if os.environ.get("FACTORIO_CHECK_factorio_mods_dir")
        else Path("/opt/factorio/mods"),
    )
    parser.add_argument(
        "--factorio_scenario_dir",
        type=Path,
        help="Path to the factorio scenario directory",
        default=Path(os.environ["FACTORIO_CHECK_factorio_scenario_dir"])
        if os.environ.get("FACTORIO_CHECK_factorio_scenario_dir")
        else Path("/opt/factorio/scenarios"),
    )
    parser.add_argument(
        "--scenario",
        type=str,
        help="Your factorio scenario to run",
        default=os.environ.get("FACTORIO_CHECK_scenario", ""),
    )
    parser.add_argument(
        "--scenario_copy_dirs",
        type=Path,
        nargs="+",
        default=[
            Path(x) for x in os.environ["FACTORIO_CHECK_scenario_copy_dirs"].split(",")
        ]
        if os.environ.get("FACTORIO_CHECK_scenario_copy_dirs")
        else [],
        help="Path(s) to copy to the factorio scenario directory",
    )
    parser.add_argument(
        "--mods_copy_dirs",
        default=[
            Path(x) for x in os.environ["FACTORIO_CHECK_mods_copy_dirs"].split(",")
        ]
        if os.environ.get("FACTORIO_CHECK_mods_copy_dirs")
        else [],
        type=Path,
        nargs="+",
        help="Path(s) to copy to the factorio mods directory",
    )
    parser.add_argument(
        "--max_test_seconds",
        type=int,
        help="Maximum number of seconds to allow tests to take",
        default=int(os.environ.get("FACTORIO_CHECK_max_test_seconds", 300)),
    )
    return parser.parse_args(args)


def main_cli() -> None:
    args = parse_args(sys.argv[1:])
    fc = FactorioController(
        factorio_executable=args.factorio_executable,
        factorio_mods_dir=args.factorio_mods_dir,
        factorio_scenario_dir=args.factorio_scenario_dir,
        scenario_copy_dirs=args.scenario_copy_dirs,
        mods_copy_dirs=args.mods_copy_dirs,
        scenario=args.scenario,
        max_seconds=args.max_test_seconds,
        use_box64=args.use_box64,
    )
    fc.launch_game()
    fc.execute_unit_tests()
    fc.terminate_game()
    tests_pass = fc.analyze_unit_test_results()
    if not tests_pass:
        raise RuntimeError("Tests failed")
