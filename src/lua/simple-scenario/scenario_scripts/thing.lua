local Public = {}

function Public.foo()
	return "foo"
end

function Public.bar()
	return "bar"
end

function Public.foobar()
	return Public.foo() .. Public.bar()
end

local function barfoo()
	return Public.bar() .. Public.foo()
end

if script.active_mods["factorio-check"] then
	local FC = require("__factorio-check__/main")
	FC.register_test("check is barfoo", function()
		FC.assert_equal("barfoo", barfoo())
	end)
end

return Public
