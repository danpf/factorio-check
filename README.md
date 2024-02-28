
# Factorio Testing Mod: factorio-check

## Description
This is a mod that enables unit testing for Factorio mods and scenarios.


This repository contains 3 main tools that you may want to use:

* factorio-check python library
* factorio-check factorio mod
* factorio-check Dockerfile

---
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
    --factorio_scenario simple-scenario \
    --factorio_scenario_dir /opt/factorio/scenarios
    --factorio_scenario_copy_dirs /opt/factorio-check-examples/simple-scenario

# Alternative invocation for mods
run-factorio-test \
    --factorio_executable /opt/factorio/bin/x64/factorio \
    --factorio_mods_dir /opt/factorio/mods
    --factorio_mods_copy_dirs /opt/factorio-check-examples/simple-mod
```

The library looks to manage scenarios and mods even when they are in different directories
by copying them to the factorio scenario/mods directory before the executable is started.  Multiple mods
and scenarios can be provided to the arguments with suffix '_dirs' so you can copy more than
1 mod/scenario if you want to.  Unless otherwise specified via `--factorio_scenario`, the `base/freeplay`
scenario is used.

For more information, you can find the code [HERE](src/python/factorio_check).

**The library is a modification of the python code from [Angels Mods Unit-test script](https://github.com/Arch666Angel/mods/blob/master/angelsdev-unit-test/python/factorio_controller.py)**
**Thank you to Angel for the open-source library**

---
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

---
#### Factorio Docker Image

This image is the core of this CI toolkit.  It integrates all of the aforementioned tools, and provides a modular interface
that can be used to evaluate your mods or scenarios.


The image also, very importantly, has the [vscode-factoriomod-debug](https://github.com/justarandomgeek/vscode-factoriomod-debug)
lua-language-server addon installed.  This lua-language-server addon enables you to quickly evaluate your library for potential bugs and,
if integrated with CI, can provide insight into areas where your code might be missing edge-case handling, as well as 


---
#### Factorio Docker Image: Static Analysis
To run static analysis on the local scenario, or mod you are developing, simply run:
```bash
$ docker run --rm \
    -v "$(pwd)":"$(pwd):ro" \
    --entrypoint /usr/local/bin/lint-entrypoint.sh \
    -t danpfuw/factorio-check:${{ matrix.version_and_sha.version }} \
    "$(pwd)"
> Diagnosis completed, no problems found

# or with errors:
$ docker run --rm \
    -v "$(pwd)":"$(pwd):ro" \
    --entrypoint lint-entrypoint.sh \
    -t danpfuw/factorio-check:latest \
    "$(pwd)"
> Diagnosis complete, 1 problems found, see /opt/luals/lua-language-server/log/check.json
> {
>     "file:///Users/martha/git/factorio-docker/src/lua/simple-scenario/./control.lua": [
>         {
>             "code": "undefined-field",
>             "message": "Undefined field `player_indexx`.",
>             "range": {
>                 "end": {
>                     "character": 51,
>                     "line": 6
>                 },
>                 "start": {
>                     "character": 38,
>                     "line": 6
>                 }
>             },
>             "severity": 2,
>             "source": "Lua Diagnostics."
>         }
>     ]
> }
```

The formatting isn't great, and sometimes there may be duplicates, but it
should at least provide some insight into where you might be able to improve
your work.

**This is heavily based on the work at [factoriotools/factorio-docker](https://github.com/factoriotools/factorio-docker)**
**Thank you to the factoriotools team for their creation and maintenance of this open source library**
**Thank you to justarandomgeek for their [vscode-factoriomod-debug](https://github.com/justarandomgeek/vscode-factoriomod-debug) library**


## Contributing
Guidelines for contributing to the mod.

## License
MIT License. See the LICENSE file for details.
