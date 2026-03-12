---
name: browse
description: |
  Fast web browsing via persistent headless Chromium daemon. Navigate to any URL,
  read page content, click elements, fill forms, run JavaScript, take screenshots,
  inspect CSS/DOM, capture console/network logs, and more. ~100ms per command after
  first call. Use when asked to browse a website, check a page, verify a deployment,
  test the UI, do QA, read web docs, or interact with any web page.
  Trigger with /browse.
---

# rstack: Persistent Browser for Copilot

Persistent headless Chromium daemon. First call auto-starts (~3s). Every subsequent call: ~100-200ms. Auto-shuts down after 30 min idle.

## SETUP (check BEFORE any browse command)

Before using any browse command, find the binary using `bash`:

```bash
# Check project-level first, then personal
if test -x .github/skills/rstack/browse/dist/browse; then
  B=.github/skills/rstack/browse/dist/browse
elif test -x ~/.copilot/skills/rstack/browse/dist/browse; then
  B=~/.copilot/skills/rstack/browse/dist/browse
else
  echo "NEEDS_SETUP"
fi
```

Set `B` to whichever path is found. Prefer project-level if multiple exist.

If `NEEDS_SETUP`:
1. Tell user: "rstack browse needs a one-time build (~10 seconds). OK to proceed?" Use `ask_user`.
2. If approved, find the rstack directory and run: `cd <RSTACK_DIR> && ./setup`
3. If `bun` not installed: `curl -fsSL https://bun.sh/install | bash`

## IMPORTANT
- Use compiled binary via `bash` tool: `$B <command> <args>`
- Browser persists between calls — cookies, tabs, state carry over
- Server auto-starts on first command

## Quick Reference

All commands run via `bash` tool:

```bash
B=~/.copilot/skills/rstack/browse/dist/browse  # or detected path

# Navigate
$B goto https://example.com

# Read page text
$B text

# Screenshot (then use view tool to see the image)
$B screenshot /tmp/page.png

# Snapshot: accessibility tree with refs
$B snapshot -i

# Click/fill by ref (after snapshot)
$B click @e3
$B fill @e4 "test@test.com"

# Run JavaScript
$B js "document.title"

# Get all links
$B links

# By CSS selector
$B click "button.submit"
$B fill "#email" "test@test.com"

# HTML/CSS inspection
$B html "main"
$B css "body" "font-family"
$B attrs "nav"

# Wait for element
$B wait ".loaded"

# Viewport
$B viewport 375x812

# Cookies/headers
$B cookie "session=abc123"
$B header "Authorization:Bearer token123"
```

## Command Reference

### Navigation
```
browse goto <url>         Navigate current tab
browse back               Go back
browse forward            Go forward
browse reload             Reload page
browse url                Print current URL
```

### Content Extraction
```
browse text               Cleaned page text
browse html [selector]    innerHTML or full page
browse links              All links as "text → href"
browse forms              All forms + fields as JSON
browse accessibility      Accessibility tree
```

### Snapshot (ref-based selection)
```
browse snapshot           Full accessibility tree with @refs
browse snapshot -i        Interactive elements only
browse snapshot -c        Compact (no empty structural elements)
browse snapshot -d <N>    Limit depth
browse snapshot -s <sel>  Scope to CSS selector
```

After snapshot, use @refs:
```
browse click @e3
browse fill @e4 "value"
browse hover @e1
browse html @e2
browse css @e5 "color"
browse attrs @e6
```

Refs invalidated on navigation — run `snapshot` again after `goto`.

### Interaction
```
browse click <selector>        Click element
browse fill <selector> <value> Fill input
browse select <selector> <val> Select dropdown
browse hover <selector>        Hover
browse type <text>             Type into focused element
browse press <key>             Press key (Enter, Tab, Escape, etc.)
browse scroll [selector]       Scroll into view or page bottom
browse wait <selector>         Wait for element (max 10s)
browse viewport <WxH>          Set viewport
```

### Inspection
```
browse js <expression>         Run JS
browse eval <js-file>          Run JS file
browse css <selector> <prop>   Computed CSS property
browse attrs <selector>        Element attributes as JSON
browse console                 Console messages
browse console --clear         Clear console buffer
browse network                 Network requests
browse network --clear         Clear network buffer
browse cookies                 All cookies as JSON
browse storage                 localStorage + sessionStorage
browse storage set <key> <val> Set localStorage
browse perf                    Page load timings
```

### Visual
```
browse screenshot [path]       Screenshot (default: /tmp/browse-screenshot.png)
browse pdf [path]              Save as PDF
browse responsive [prefix]     Screenshots at mobile/tablet/desktop
```

### Compare
```
browse diff <url1> <url2>      Text diff between two pages
```

### Multi-step (chain)
```
echo '[["goto","https://example.com"],["snapshot","-i"],["click","@e1"]]' | browse chain
```

### Tabs
```
browse tabs                    List tabs
browse tab <id>                Switch tab
browse newtab [url]            Open new tab
browse closetab [id]           Close tab
```

### Server Management
```
browse status                  Health, uptime, tab count
browse stop                    Shutdown
browse restart                 Kill + restart
```

## Speed Rules

1. Navigate once, query many times
2. Use `snapshot -i` for interaction (get refs, then click/fill)
3. Use `js` for precision extraction
4. Use `links` to survey page structure
5. Use `chain` for multi-step flows
6. Use `responsive` for layout checks

## When to Use What

| Task | Commands |
|------|----------|
| Read a page | `goto <url>` then `text` |
| Interact | `snapshot -i` then `click @e3` |
| Check element exists | `js "!!document.querySelector('.thing')"` |
| Extract data | `js "document.querySelector('.price').textContent"` |
| Visual check | `screenshot /tmp/x.png` then use `view` tool on the image |
| Fill form | `snapshot -i` → `fill @e4 "val"` → `click @e5` → `screenshot` |
| Debug console | `console` |
| Check network | `network` |
| Compare pages | `diff <url1> <url2>` |
| Mobile check | `responsive /tmp/prefix` |

## Architecture
- Persistent Chromium daemon on localhost (port 9400-9410)
- Bearer token auth per session
- State file: `/tmp/browse-server.json`
- Auto-shutdown after 30 min idle
- Crash → auto-restart on next command

**Security note:** This is a real browser with persistent state. Cookies, localStorage, and sessions carry over. Be cautious with sensitive production environments.
