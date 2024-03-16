require("util")

local Public = {}

function Public.init()
	if global.prev_global_state == nil then
		global.prev_global_state = table.deepcopy(global)
		global.registered_tests = {}
	end
end

function Public.reset_global_state()
	local registered_tests = global.registered_tests
	global = table.deepcopy(global.prev_global_state)
	global.registered_tests = registered_tests
end

function Public.register_test(name, test_function)
	global.registered_tests[name] = test_function
end

function Public.assert_equal(actual, expected, message)
	if actual ~= expected then
		error(message or ("Expected " .. tostring(expected) .. ", got " .. tostring(actual)))
	end
end

function Public.assert_not_equal(actual, expected, message)
	if actual == expected then
		error(message or ("Expected " .. tostring(expected) .. ", got " .. tostring(actual)))
	end
end

function Public.run_tests()
	local passed = 0
	local failed = 0
	log("UNIT TESTS START")

	for name, test_function in pairs(global.registered_tests) do
		local status, err = pcall(test_function)

		if status then
			log("Test '" .. name .. "' passed.")
			passed = passed + 1
		else
			log("Test '" .. name .. "' failed: " .. err)
			failed = failed + 1
		end
	end
	local total = passed + failed

	log("Total tests passed: " .. passed)
	log("Total tests failed: " .. failed)
	log("UNIT TESTS DONE: " .. passed .. "/" .. total)
end

return Public
