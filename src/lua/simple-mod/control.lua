-- local ModSRC = require("modsrc.main")

script.on_event(defines.events.on_player_changed_position, function(event)
	local player = game.get_player(event.player_index) -- get the player that moved
	-- if they're wearing our armor
	if
		player.character
		and player.get_inventory(defines.inventory.character_armor).get_item_count("fire-armor") >= 1
	then
		-- create the fire where they're standing
		player.surface.create_entity({ name = "fire-flame", position = player.position, force = "neutral" })
	end
end)


if script.active_mods["factorio-check"] then
	local tests = require("tests.main")
	script.on_event(defines.events.on_tick, function()
		if game.tick == 60 * 5 then
			tests.tests_entrypoint()
		end
	end)
end
