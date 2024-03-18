# Factorio Testing Mod: factorio-check
______________________________________________________________________

[![Docker Pulls](https://flat.badgen.net/docker/pulls/danpfuw/factorio-check?icon=docker&label=pulls)](https://hub.docker.com/r/danpfuw/factorio-check/)
[![PyPi Downloads](https://flat.badgen.net/pypi/dm/factorio-check)](https://pypi.org/project/factorio-check/)
______________________________________________________________________

## Description

This is a mod that enables unit testing for Factorio mods and scenarios.

This repository contains 3 main tools that you may want to use:

- factorio-check python library
- factorio-check factorio mod
- factorio-check Dockerfile

______________________________________________________________________

#### Python library

The python library is essentially a factorio executable wrapper that watches,
and parses the output of the factorio executable.

Its invocation looks like this:

```python
    fc.launch_game()
    fc.execute_unit_tests()
    fc.terminate_game()
    tests_pass = fc.analyze_unit_test_results()
    if not tests_pass:
        raise RuntimeError("Tests failed")
```

Upon installation, the python library provides access to the `run-factorio-test` command.
Up to date examples can be found in the .github directory, but it is run typically via something like this:

```bash
run-factorio-test \
    --factorio_executable /opt/factorio/bin/x64/factorio \
    --scenario simple-scenario \
    --scenario_copy_dirs /opt/factorio-check-examples/simple-scenario \
    --factorio_scenario_dir /opt/factorio/scenarios

# Alternative invocation for mods
run-factorio-test \
    --factorio_executable /opt/factorio/bin/x64/factorio \
    --factorio_mods_dir /opt/factorio/mods \
    --mods_copy_dirs /opt/factorio-check-examples/simple-mod

```

**Note**
The above can also be modified to run using environment variables, by prepending `FACTORIO_CHECK_` to any of the arguments.
lists become comma separated values.  use_box64 is unique in that the value is not checked, only the existence
of the environment variable is.

The library looks to manage scenarios and mods even when they are in different directories
by copying them to the factorio scenario/mods directory before the executable is started.  Multiple mods
and scenarios can be provided to the arguments with suffix '\_dirs' so you can copy more than
1 mod/scenario if you want to.  Unless otherwise specified via `--scenario`, the `base/freeplay`
scenario is used.

For more information, you can find the code [HERE](src/python/factorio_check).

**The library is inspired by the python code from [Angels Mods Unit-test script](https://github.com/Arch666Angel/mods/blob/master/angelsdev-unit-test/python/factorio_controller.py)**
**Thank you to Angel for the open-source library**

______________________________________________________________________

#### Factorio mod

This Lua script provides a basic lua test framework, designed to facilitate the creation and execution
of unit tests in a Lua environment. It offers a simple set of functions that are all self explanatory,
please view the script [HERE](src/lua/factorio-check/main.lua).

The core of the script is `Public.run_tests` which iterates through all registered tests, executes
them, and logs their pass or fail status.

brief excerpt of implemented testing for a module:

```lua
local FC = require("__factorio-check__/main")
local scenario_scripts = require("scenario_scripts.thing")

local Public = {}

local function add_tests()
	FC.register_test("check is foo", function()
		FC.assert_equal("foo", scenario_scripts.foo())
	end)
	FC.register_test("check is bar", function()
		FC.assert_equal("bar", scenario_scripts.bar())
	end)
	FC.register_test("check is foobar", function()
		FC.assert_equal("foobar", scenario_scripts.foobar())
	end)
end

```

See the [scenario](src/lua/simple-scenario) and [mod](src/lua/simple-mod) for more in depth examples of how the testing
framework could be integrated with existing codebases.

Very briefly, it is simple to create a tests/main.lua file, and add the following code to control.lua

```lua
if script.active_mods["factorio-check"] then
	local tests = require("tests.main")
	script.on_event(defines.events.on_tick, function()
		if game.tick == 60 * 10 then
			tests.tests_entrypoint()
		end
	end)
end
```

You may want to consider adding the tests to the bottom of your files to have access to local functions.

```lua
local function foo()
    return "foo"
end


if script.active_mods["factorio-check"] then
    local FC = require("__factorio-check__/main")
	FC.register_test("check is foo", function()
		FC.assert_equal("foo", foo())
	end)
end
```

______________________________________________________________________

#### Factorio Docker Image

This image is the core of this CI toolkit.  It integrates all of the aforementioned tools, and provides a modular interface
that can be used to evaluate your mods or scenarios.

The image also, very importantly, has the [vscode-factoriomod-debug](https://github.com/justarandomgeek/vscode-factoriomod-debug)
lua-language-server addon installed.  This lua-language-server addon enables you to quickly evaluate your library for potential bugs and,
if integrated with CI, can provide insight into areas where your code might be missing edge-case handling, as well as if your formatting
has deviated from whatever is desired.


The image is tagged based on both this library's version, as well as the factorio version. This manifests as:
```
danpfuw/factorio-check:{ this library version }_{ factorio release version }

ex.
danpfuw/factorio-check:0.0.10_1.1.104
```
______________________________________________________________________

#### Factorio Docker Image: Static Analysis

To run static analysis on the local scenario, or mod you are developing, simply run:

```bash
$ docker run --rm \
    -v "$(pwd)":"$(pwd):ro" \
    -e MODE=LINT \
    -e TARGET_PATH="$(pwd)"
    -t danpfuw/factorio-check:0.0.10_1.1.104
> Diagnosis completed, no problems found

# Errors manifest as:

> Diagnosis complete, 1 problems found, see /opt/luals/lua-language-server/log/check.json
> Linting complete: Errors found!
> file:///.../src/lua/simple-scenario/control.lua code: undefined-field, message: Undefined field `player_indexxx`., severity: 2, source: Lua Diagnostics., line:char-range: 6:38-6:52
```


You can also lint the formatting of the project by adding the environment variable `LINT_FORMATTING=ON`. Keep in mind that you must follow this
[documentation](https://luals.github.io/wiki/formatter/) and add a `.editorconfig` file to your project to enable this feature.

#### Factorio Docker Image: Testing

To run static analysis on the local scenario, or mod you are developing, simply run:

```bash
$ docker run --rm \
    -v "$(pwd)":"$(pwd)":ro \
    -e MODE=TEST \
    -e FACTORIO_CHECK_scenario=my-fun-scenario \
    -e FACTORIO_CHECK_scenario_copy_dirs="$(pwd)" \
    -t danpfuw/factorio-check:0.0.10_1.1.104
> Diagnosis completed, no problems found

# Errors manifest as:

> Diagnosis complete, 1 problems found, see /opt/luals/lua-language-server/log/check.json
> Linting complete: Errors found!
> file:///.../src/lua/simple-scenario/control.lua code: undefined-field, message: Undefined field `player_indexxx`., severity: 2, source: Lua Diagnostics., line:char-range: 6:38-6:52
```

You can also lint the formatting of the project by adding the environment variable `LINT_FORMATTING=ON`. Keep in mind that you must follow this
[documentation](https://luals.github.io/wiki/formatter/) and add a `.editorconfig` file to your project to enable this feature.


#### Factorio Docker Image: Github Actions Static Analysis and Testing

To run this static analysis and testing you can easily incorporate this image into the github actions folder of your mod or scenario.

Example:
```yaml
---
name: Test My Mod
on:
  push:
    branches:
      - master
  pull_request:
    branches:
      - master
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      FACTORIO_VERSION: 1.1.104
      # Consider pinning to whatever most recent tagged version is.
      FACTORIO_CHECK_VERSION: master
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Lint
        run: |
          docker run --rm \
            -v "$(pwd)":"$(pwd)":ro \
            -e MODE=LINT \
            -e TARGET_PATH="$(pwd)" \
            -t danpfuw/factorio-check:${FACTORIO_CHECK_VERSION}_${FACTORIO_VERSION}
      - name: Test
        run: |
          docker run --rm \
          -v "$(pwd)":"$(pwd)":ro \
          -e MODE=TEST \
          -e FACTORIO_CHECK_scenario=my-fun-scenario \
          -e FACTORIO_CHECK_scenario_copy_dirs="$(pwd)" \
            -t danpfuw/factorio-check:${FACTORIO_CHECK_VERSION}_${FACTORIO_VERSION}
```


**Note:** sometimes lua-language-server may report duplicates, but it should at least provide some insight into where you might be able to improve your work.

**This is heavily based on the work at [factoriotools/factorio-docker](https://github.com/factoriotools/factorio-docker)**
**Thank you to the factoriotools team for their creation and maintenance of this open source library**
**Thank you to justarandomgeek for their [vscode-factoriomod-debug](https://github.com/justarandomgeek/vscode-factoriomod-debug) library**

## License

MIT License. See the LICENSE file for details.
