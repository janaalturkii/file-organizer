# Week 3 Learning Notes — Claude 101 & Claude Code 101

**Trainer:** [add name]
**Date completed:** July 2026
**Courses completed:** Claude 101 (Anthropic Academy), Claude Code 101 (Anthropic Academy)

---

## Claude 101

### Chat & Cowork
- **Projects** — Self-contained workspaces with their own memory, chat histories, knowledge bases, and customized instructions. Useful for keeping context isolated per initiative instead of mixing everything into one long chat history.
- **Artifacts** — Standalone, interactive outputs Claude creates in a dedicated window alongside the conversation (e.g. code, documents, diagrams) rather than inline in the chat.
- **Cowork** — Built for work that takes real effort: pulling information from many sources, making sense of it, and producing something finished. Goes beyond a single back-and-forth chat exchange.

### Skills
- Folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. Lets Claude apply the right procedure automatically instead of re-explaining it every time.

### Connectors
- Give Claude access to the same tools, data, and context a person uses every day, turning it from a general assistant into an informed collaborator that can work with real information instead of starting from scratch each conversation.
- Depending on permissions granted, Connectors let Claude read information *and* perform actions: search files, retrieve documents, analyze data, create content, update records, and execute tasks across connected apps.
- Powered by the **Model Context Protocol (MCP)** — described as "USB-C for AI": a universal standard so Claude can connect to many different applications through one consistent interface. Open standard, so developers can build connectors for any tool and they work seamlessly with Claude.
- Two types:
  - **Web connectors** — link Claude to cloud services (Google Drive, Notion, Slack, Asana, etc.)
  - **Desktop extensions** — run locally via the Claude Desktop app, giving access to local files and native applications.

### Enterprise Search
- Designed specifically for finding and synthesizing knowledge buried across a company's tools and data sources.

### Research Mode
- Transforms Claude from a conversational assistant into a systematic investigator. Instead of just answering a question, Claude explores it from multiple angles and synthesizes information from across the web and connected integrations.

### Code (module within Claude 101)
Use cases for Claude in a coding context:
- Build features by describing what's needed in plain English — Claude writes the code, runs tests, and creates commits.
- Debug by pasting error messages and letting Claude analyze the codebase to identify and fix problems.
- Ask questions to navigate an unfamiliar codebase and understand how different parts connect.
- Automate tedious tasks: fixing lint errors, resolving merge conflicts, writing release notes.
- Work from the terminal alongside existing IDE/dev tools rather than switching to a separate interface.

---

## Claude Code 101

### Installation
- Claude Code can be installed and used in the terminal, on the web, or inside an IDE.
- **VS Code:** Open the Extensions panel → search "Claude Code" → install the Anthropic extension (blue verification check) → restart VS Code → open via Command Palette (`Ctrl/Cmd + Shift + P` → "Claude Code: Open in New Tab") or the Claude logo in the sidebar.

### Core workflow: Explore, Plan, Code, Commit
- The single most important habit from the course: **Explore → Plan → Code → Commit**, rather than jumping straight to "write me this code."
- Skipping straight to code generation without exploring/planning first leads to more course-correction later.

### The CLAUDE.md File
- Gives Claude Code **persistent memory** about a project.
- **Problem it solves:** without it, Claude Code starts fresh every session — it has to re-explore the codebase, re-figure out dependencies, and re-learn what's already implemented. This can lead to wrong assumptions and makes it harder to steer Claude correctly.
- Solution: CLAUDE.md acts as standing project context so Claude doesn't have to rediscover the same things every time.

---

## Reflection / Application to `file-organizer`
- The `file-organizer` project doesn't currently have a `CLAUDE.md` — adding one is the direct next step (Task 2 for this week) so Claude Code has persistent context on the project structure, conventions, and known issues (e.g. the PowerShell UTF-16LE encoding gap).
- The Explore → Plan → Code → Commit workflow maps well onto how the project has already been built (feature branches, one PR per day) — going forward, optimization work should follow this same discipline rather than jumping straight into edits.