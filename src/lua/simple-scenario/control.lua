-- If you have tests located in your required files, you must init factorio-check before requiring them.
if script.active_mods["factorio-check"] then
	local FC = require("__factorio-check__/main")
	FC.init()
end

Thing = require("scenario_scripts.thing")

script.on_event(defines.events.on_player_changed_position, function(event)
	local player = game.get_player(event.player_index) -- get the player that moved
	if not player then return end
	-- if they're wearing our armor
	if player.character then
		-- create the fire where they're standing
		player.surface.create_entity({ name = "fire-flame", position = player.position, force = "neutral" })
		if (event.tick % 2 == 0) then
			player.create_local_flying_text({ text = Thing.foo() })
		else
			player.create_local_flying_text({ text = Thing.bar() })
		end
	end
end)

if script.active_mods["factorio-check"] then
	local tests = require("tests.main")
	script.on_event(defines.events.on_tick, function()
		if game.tick == 60 * 10 then
			tests.tests_entrypoint()
		end
	end)
end
