Run this in Delta after entering a Search For The Needle round:

```lua
loadstring(game:HttpGet("https://raw.githubusercontent.com/ainesys/rblxscripts/master/search%20for%20needle/AineNeedle.txt"))()
```

Objective mode starts automatically. AUTO pauses it, SELL NOW sells early, BUY toggles automatic purchases, and OBJECTIVES toggles candle/boss progression. Drag the title bar with a finger or mouse to move the panel. The panel stays within the screen when dragged or rotated, with larger touch buttons. Hide collapses it; X stops and cleans up. F6 also toggles automation.

The farm collects hay and gems, uses the fastest owned hand/pitchfork/vacuum option based on its replicated stats, and deploys an owned drone. Upgraded hand collection sends nearby extra hay IDs in the same request. It caches nearby targets, bounds hay scans, and tracks character collisions through events. Server cooldowns still determine accepted collection speed.

Selling uses the map's SellPart objects, with scarecrow/cow fallbacks. The script sells when the bag fills or after 15 seconds, then waits for HayHeld to reach zero before returning.

Automatic purchases use round Cash and the current game's upgrade configuration, including cost multipliers. The farm buys Grasp, Speed, and Capacity; after the initial upgrades it saves for the shop's cash pitchfork option. After developing the pitchfork, it saves for the cash vacuum option. It upgrades the owned tool and capacity; owned drones also get upgrades. Purchases wait for a replicated level/ownership change before buying again. CashReserve, AutoBuyPitchfork, and AutoBuyVacuum are configurable at the top. Gems and Robux purchases are excluded.

In Graveyard, the priority is the top-left objectives. Revealed loose candles are highlighted, collected, and carried to an available holder. The script waits for the server's match-puzzle event before requesting lighting completion, then checks the holder's Lit attribute. If lighting remains unconfirmed, complete the match minigame manually. Farming resumes after confirmation. Hidden candles remain at a shared placeholder position until the game reveals them; the script farms to uncover them.

Skeletons and imps interrupt farming when nearby. With an owned pitchfork, the script moves out of melee reach, aims using the game's combat helper, and fights before resuming the farm. Once all four candles are lit, it waits for the Pumpkin Golem to awaken, then fights it. Boss grab/pull events trigger escape attempts. Movement stops during cutscenes and the ending; the script reports completion only when NeedleRoundComplete is confirmed. AutoDefend, AutoBoss, and AutoSkipEnding are configurable, with ending skips off by default.

The general and MM2 scripts supplied the UI and cleanup conventions. The initial game calls came from this [public source](https://pastebin.com/raw/SFuQwVQU). The Halloween changes use on-device inspection of the Graveyard clients and combat helpers, including NeedleHaystack.Config, CandleClient, CandleMatchClient, BossFight.BossAim, and PumpkinBoss.Config. Captured client sources and device diagnostics are kept outside this repository.

Validation includes Lua parsing and simulated checks for collection, multi-grab, request timing, both sell layouts, confirmed sales/purchases, affordability, candle progression, combat priority, objective transitions, touch dragging, and cleanup. Run `python "search for needle/tests/verify_farm.py"` with `lupa` and `luaparser` installed. On-device testing confirmed hay collection, scarecrow sales, cash tool/upgrade purchases, skeleton defense, all four candles found and lit, and damage to the awakened Pumpkin Golem. See the script's status panel for unconfirmed actions.

TNT automation and other maps' puzzle/needle hand-in sequences are outside this script. Entering another place unloads client scripts, so run it again after teleporting.
