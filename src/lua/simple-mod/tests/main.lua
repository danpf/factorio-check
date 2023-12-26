local FC = require("__factorio-check__/main")
local tests_01 = require("tests_01")

local Public = {}

function Public.tests_entrypoint()
	FC.init()
	tests_01.add_tests()
	FC.run_tests()

	FC.reset_global_state()
	FC.run_tests()
end
return Public
