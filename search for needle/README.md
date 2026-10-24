Run `AineNeedle.txt` as a client script after entering a Search For The Needle round. Farming starts automatically. Tap FARM ON to pause, SELL NOW to sell early, Hide to collapse the panel, or X to stop and clean up. F6 also toggles farming.

The script collects hay and gems, uses an owned pitchfork or vacuum, deploys an owned drone, and moves to the cow when the bag fills or every five seconds. It waits for HayHeld to reach zero before returning. Settings at the top control request intervals, scan size, tools, and selling frequency. Server cooldowns and distance checks still determine accepted collection speed.

The general script supplied the mobile panel and cleanup conventions; the MM2 script supplied the farming session, temporary collision changes, and pickup retry pattern. Game-specific remote names, argument shapes, player attributes, and workspace paths come from inspection of this [public source](https://pastebin.com/raw/SFuQwVQU). That source was read as text, never executed. No external loaders are included.

Validation: Lua syntax passed. A simulated Roblox environment passed checks for bounded collection requests, moving to the cow, sale delay and retry timing, waiting for sale confirmation, returning after selling, vacuum start/tick, collision restoration, removing hover, disconnecting on close, rerun replacement, and character removal. These checks do not establish server acceptance or live collection speed.

Live execution has not been verified. The panel reports missing round objects, attributes, and unconfirmed sales. TNT and needle hand-in are omitted because their complete working sequences were not established. Entering another place unloads client scripts, so run it again after teleporting.
