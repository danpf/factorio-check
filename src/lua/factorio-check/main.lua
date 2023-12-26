
-- Entry point for the 'factorio-check' testing framework
-- This script initializes the testing framework and provides core functionalities.
require("util")

-- Table to hold registered test cases
local Public = {}

-- Function to register a new test
function Public.init()
	global.prev_global_state = table.deepcopy(global)
	global.registered_tests = {}
end

function Public.reset_global_state()
	local registered_tests = global.registered_tests
	global = table.deepcopy(global.prev_global_state)
	global.registered_tests = registered_tests
end

-- Function to register a new test
function Public.register_test(name, test_function)
    global.registered_tests[name] = test_function
end

-- Assertion utility for equality check
function Public.assert_equal(actual, expected, message)
    if actual ~= expected then
        error(message or ("Expected " .. tostring(expected) .. ", got " .. tostring(actual)))
        log(message or ("Error: Expected " .. tostring(expected) .. ", got " .. tostring(actual)))
    end
end

-- Assertion utility for equality check
function Public.assert_not_equal(actual, expected, message)
    if actual == expected then
        error(message or ("Expected " .. tostring(expected) .. ", got " .. tostring(actual)))
        log(message or ("Error: Expected " .. tostring(expected) .. ", got " .. tostring(actual)))
    end
end

-- Function to run and report test results
function Public.run_tests()
    local passed = 0
    local failed = 0
    print("UNIT TESTS START")
    log("UNIT TESTS START")

    for name, test_function in pairs(global.registered_tests) do
        local status, err = pcall(test_function)

        if status then
            print("Test '" .. name .. "' passed.")
            log("Test '" .. name .. "' passed.")
            passed = passed + 1
        else
            print("Test '" .. name .. "' failed: " .. err)
            log("Test '" .. name .. "' failed: " .. err)
            failed = failed + 1
        end
    end
	local total = passed + failed

    print("Total tests passed: " .. passed)
    log("Total tests passed: " .. passed)
    print("Total tests failed: " .. failed)
    log("Total tests failed: " .. failed)
    print("UNIT TESTS DONE: " .. passed .. "/" .. total)
    log("UNIT TESTS DONE: " .. passed .. "/" .. total)
end

-- -- Sample tests
-- register_test("test_equal_numbers", function()
--     assert_equal(1, 1, "Numbers should be equal")
-- end)
--
-- register_test("test_unequal_numbers", function()
--     assert_equal(1, 2, "Numbers should not be equal")
-- end)

return Public
