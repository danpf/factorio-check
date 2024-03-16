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

function Public.tests_entrypoint()
	FC.init()
	add_tests()
	FC.run_tests()
	FC.reset_global_state()
	FC.run_tests()
end

return Public
