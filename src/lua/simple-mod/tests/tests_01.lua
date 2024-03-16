local FC = require("__factorio-check__/main")
local ModSRC = require("modsrc.main")

local Public = {}

function Public.add_tests()
	FC.register_test("test is 22", function()
		local ret = ModSRC.ret_22()
		FC.assert_equal(22, ret)
		FC.assert_not_equal(11, ret)
	end)

	FC.register_test("test is 22", function()
		local ret = ModSRC.ret_22()
		FC.assert_equal(22, ret)
		FC.assert_not_equal(11, ret)
	end)
end

return Public
