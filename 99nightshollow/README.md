Run `AineHollow.txt` on the client after entering a 99 Nights round.

```lua
loadstring(game:HttpGet("https://raw.githubusercontent.com/ainesys/rblxscripts/master/99nightshollow/AineHollow.txt"))()
```

The connected phone has a saved Delta entry named **99 Nights Hollow**. Its local loader is:

```lua
loadstring(readfile("AineHollow.lua"))()
```

The script fuels the fire, chops nearby small trees when fuel runs out, finds the marked void entrance, and collects the 20 red Hollow flowers. It waits for replicated fuel and flower progress, loads unexplored flower locations, and stops quest actions when the server sets `HollowBeaten`. Map progress alone does not count as a win.

The mobile panel provides QUEST, ENTER VOID, SAFE LANTERN, and FUEL controls. Drag its title to move it; Hide collapses it, and X stops the script and removes its hover objects. F6 toggles quest actions. Hover protection stays active while quest actions are paused and after completion. Game cutscenes temporarily control the character.

Safety includes hovering between interactions, retreating from mobs or damage, avoiding unsafe flower locations, eating suitable food, and using owned bandages or medkits below 85% health. Defense aims an owned gun at nearby NPCs, checks line of sight, and uses the gun's normal firing and reload methods. It excludes players and requires ammunition. Available free Hollow upgrades favor health, damage, and stuns.

Before entering, the script searches accessible supply chests and collects guns, medicine, and flashlights. `RequireSafetySupplies` defaults to true: if necessary, it continues fueling through fire level 5 to unlock supplies. The ENTER VOID button allows manual entry once the fire reaches level 3. Settings are at the top of the script. Supplies and hover reduce risk; they do not prevent every source of damage.

On-device validation completed the quest: 20/20 flowers, `HollowBeaten = true`, and 100 HP after returning from the void. The protected run also confirmed fire progression to level 3, flower pickup, and automatic completion detection. Gun firing and medicine were not needed for that completion; their selection, aiming, reload, and healing behavior were checked with mocks.

Run `python 99nightshollow/tests/verify_hollow.py` with `lupa` and `luaparser` installed. The tests reuse the repository's game-object fixture and cover hover, pause protection, mob/damage retreat, server transitions, death handling, progress/completion, cleanup, medicine selection, aimed fire, player exclusion, line of sight, reload, and absent weapons. The full script also passes Luau bytecode compilation.

The script uses the live client's interaction conventions and the replicated `HollowPlant`/`HollowLantern` tags. Captured client sources, phone screenshots, and device diagnostics stay outside this repository. Entering another place unloads the script; run the saved entry again after loading a new round.
