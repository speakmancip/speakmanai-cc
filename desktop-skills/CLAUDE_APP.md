# Connecting the local SPEAKMAN.AI exe to the Claude app

For people running `SpeakmanAI.exe` on their own computer. It covers three ways of using Claude with it and says which one to pick. The hosted service is different: it has a public https address, and adding it under Settings, Connectors works as `README.md` describes.

**Tested 2026-10-16** on a standard (non-admin) Windows account with the unsigned v1.5.0 build, one run per route. Anything not listed under "What was observed" is untested.

## Which route do I want?

| You want to use | Do this | Needs |
|---|---|---|
| Claude Code in a terminal, or the Code tab of the Claude app | [Claude Code CLI](#route-1-claude-code-cli-recommended) | Nothing beyond the installer. No admin, no Node |
| The chat side of the Claude app | [The config file](#route-2-the-chat-side-of-the-claude-app) | Node installed for your user, and a hand-edited file |
| Cowork | Not covered | The app's Cowork feature needs admin rights to install |

## Route 1: Claude Code CLI (recommended)

One setup covers the terminal and the app's Code tab.

1. Open PowerShell and run `irm https://claude.ai/install.ps1 | iex`. It prints nothing for about 3 to 5 minutes while it downloads. Leave the window open until it reports that it installed Claude Code.
2. On the SPEAKMAN.AI setup page (`http://localhost:8000/setup`), open the **Claude Code (CLI)** tab and press **Check again**. It should say Claude Code was found. You do not need to run `claude` or sign in to it for this step.
3. Press **Connect Claude Code**. It registers the server and installs the skills.
4. Fully quit the Claude app (including its tray icon) and reopen it. Claude Code will now see the server, and the skills appear as slash commands such as `/generate-sad`.

If the installer puts `claude` somewhere that is not on your PATH, the setup page shows how to add it. Connecting from the setup page works either way.

## Route 2: the chat side of the Claude app

The app's own "Add custom connector" screen cannot take the exe's address. That screen is called from Anthropic's servers, which cannot reach `http://127.0.0.1`, and it asks for an https address. The way in is the app's config file, with a small bridge program in between. The exe speaks HTTP, and the config file launches programs, so the bridge turns one into the other.

1. **Install Node for your user.** The bridge is started through `npx`, which comes with Node. A system-wide install needs admin. A per-user install does not (a zip build from nodejs.org unpacked into your profile with its folder added to your user PATH, or `nvm-windows`). In a new PowerShell window, `node --version` and `npx --version` should both answer.
2. **Open the config file.** In the Claude app open the Developer tab and press **Edit config**, or open `%AppData%\Claude\claude_desktop_config.json` yourself. Create it if it is missing.
3. **Add this entry.** If the file already has an `mcpServers` section, add `speakmanai` inside it rather than replacing the file. Use the port the setup page shows if it is not 8000.

   ```json
   {
     "mcpServers": {
       "speakmanai": {
         "command": "npx",
         "args": ["-y", "mcp-remote", "http://127.0.0.1:8000/mcp"]
       }
     }
   }
   ```
4. **Fully quit and reopen the Claude app**, including the tray icon.
5. **Try it.** Start a new chat and ask for something the skills cover, for example "I need an architecture document for a small app". Or ask it to list the SPEAKMAN.AI workflows.

You do not need to upload the skills plugin. In the test the app fetched the skill from the server by itself.

### If it does not connect

These are suggestions from how the pieces fit together. Only the first was seen, and only as an error message.

- The app says "command wasn't found": Node is not installed for this user, or the app was started before it was added to the PATH. Check `where.exe npx` in a new window, then quit and reopen the app.
- The Developer tab lists the server but chat does not use it: ask for a SPEAKMAN.AI deliverable by name, and check the exe is running.
- If Windows will not launch `npx` directly, change `"command"` to `"cmd"` and `"args"` to `["/c", "npx", "-y", "mcp-remote", "http://127.0.0.1:8000/mcp"]`. This was not needed in the test.

### To remove it

Delete the `speakmanai` entry from `claude_desktop_config.json` and restart the app.

## What was observed

- Installing the Claude app as a standard user asked for admin. When declined, the app said Cowork would not be available and installed everything else.
- The app's built-in Claude Code and the chat side both found the server through the `claude_desktop_config.json` entry. With the entry removed, neither connected.
- Installing the Claude Code CLI, then pressing Check again and Connect on the setup page, made the app's built-in Claude Code find the server after an app restart, with no config file and no Node. The CLI had never been opened or signed in to.
- With the config entry in place and no skills uploaded, both the chat side and the app's Claude Code started a SPEAKMAN.AI session on a plain request and fetched the skill from the server.
- The app's custom connector screen expects an https address and could not take the local one.

## Not tested

- Whether the skills plugin upload (`speakmanai-sdlc.zip`) makes skill triggering more reliable than the connector alone.
- A full run to the end from the chat side, and what the run record shows for it.
- Cowork, which needs admin to install.
- Windows setups with Node already installed system-wide, and macOS.
