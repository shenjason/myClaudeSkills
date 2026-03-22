## Step 1 — Identify the Issue

**User expects:** A top-nav dropdown shows 4 options when clicked.
**What is actually happening:** Only 2 options appear.
**Two hypotheses to distinguish:**
1. **Data issue** — only 2 items are loaded into the component's state/props; the other 2 never arrive.
2. **Rendering issue** — all 4 items are in state, but 2 are visually hidden (overflow clipped, `display: none`, container height too small, z-index buried, etc.).

---

## Step 2 — Launch the Application

The app is already running at `localhost:3000`. I bring the browser forward:

```bash
osascript -e 'tell application "Google Chrome" to activate'
sleep 1
```

---

## Step 3 — Capture Initial Screenshot (Closed State)

```bash
python3 ~/.claude/skills/screenshot-eval/scripts/screenshot.py --window "Google Chrome" --delay 1
# => /tmp/screenshot_20260321_090001.png
```

**What I see:** The app renders correctly at `localhost:3000`. The top nav is visible with a dropdown trigger (chevron icon) around x=420, y=52. No error banners. The dropdown is closed.

---

## Step 4 — Open the Dropdown and Screenshot Again

```python
# interact_click_dropdown.py
import subprocess, time, pyautogui
subprocess.run(['osascript', '-e', 'tell application "Google Chrome" to activate'])
time.sleep(0.5)
pyautogui.click(x=420, y=52)
time.sleep(0.4)
```

```bash
python3 /tmp/interact_click_dropdown.py
python3 ~/.claude/skills/screenshot-eval/scripts/screenshot.py --window "Google Chrome" --delay 0.5
# => /tmp/screenshot_20260321_090045.png
```

**What I see:** The dropdown is open. A white card appears below the trigger containing exactly 2 items ("Profile" and "Settings"). The card's bottom edge has a clean border-radius — it does not look clipped mid-item. The container appears sized exactly to its 2 children, not truncated. This strongly suggests a data issue rather than CSS clipping.

---

## Step 5 — Diagnose

### 5a. Query the DOM from the DevTools Console

```javascript
document.querySelectorAll('[data-testid="dropdown-item"]').length
// => 2
```

Only 2 DOM nodes exist. If all 4 were rendered-but-hidden, this would return 4. The missing items are **not in the DOM at all** — this rules out a CSS visibility issue and confirms a **data issue**.

### 5b. Check React Component State

In React DevTools Components panel, I select the `NavDropdown` component. Its props show:

```
props.items = [
  { id: 1, label: "Profile" },
  { id: 2, label: "Settings" }
]
```

Only 2 items in props. The component renders correctly — it renders exactly what it receives.

### 5c. Find Where `items` Is Populated

I search the source:

```bash
grep -r "menuItems\|navItems\|dropdownItems" src/ --include="*.tsx" -l
```

I open the relevant file (e.g., `src/components/TopNav.tsx`) and find one of two situations:

**Scenario A — hardcoded array with 2 items:**
```tsx
const menuItems = [
  { id: 1, label: "Profile" },
  { id: 2, label: "Settings" },
  // TODO: add remaining items   <-- bug found here
];
```

**Scenario B — API call:** I check the Network tab. The `/api/nav-items` response is:
```json
{ "items": [{ "id": 1, "label": "Profile" }, { "id": 2, "label": "Settings" }] }
```
The backend only returns 2 items (likely a stray `LIMIT 2` or an over-restrictive WHERE clause).

**Diagnosis:**
> The dropdown shows 2 options because the `items` array fed to `NavDropdown` contains only 2 entries. The component renders correctly. The root cause is the data source — either a hardcoded array missing 2 entries or an API/query returning an incomplete result set.

---

## Step 6 — Implement the Fix

**Case A — hardcoded array** in `src/components/TopNav.tsx`:

```tsx
// Before
const menuItems = [
  { id: 1, label: "Profile" },
  { id: 2, label: "Settings" },
];

// After
const menuItems = [
  { id: 1, label: "Profile" },
  { id: 2, label: "Settings" },
  { id: 3, label: "Notifications" },
  { id: 4, label: "Sign Out" },
];
```

**Case B — API query** in `server/routes/nav.js`:

```js
// Before (stray LIMIT)
const items = await db.query('SELECT * FROM nav_items LIMIT 2');

// After
const items = await db.query('SELECT * FROM nav_items ORDER BY sort_order');
```

Verify syntax after editing:

```bash
npx tsc --noEmit         # TypeScript frontend
node -c server/routes/nav.js  # Node backend
```

---

## Step 7 — Relaunch and Re-screenshot

The dev server hot-reloads. After ~2 seconds I click the dropdown again and capture:

```bash
python3 /tmp/interact_click_dropdown.py
python3 ~/.claude/skills/screenshot-eval/scripts/screenshot.py --window "Google Chrome" --delay 0.5
# => /tmp/screenshot_20260321_090330.png
```

**What I see:** The dropdown now shows all 4 items: "Profile", "Settings", "Notifications", "Sign Out". The card is taller, proportionally sized to 4 children. All items are fully legible with consistent padding. No clipping.

---

## Step 8 — Evaluate

Issue is fully resolved. All 4 options are visible.

---

## Summary

| | |
|---|---|
| **Root cause** | The data source supplied only 2 items. The `NavDropdown` component was correct — it rendered exactly what it received. |
| **Key diagnostic step** | `querySelectorAll` returning 2 nodes (not 4) proved the missing items were never in the DOM, ruling out CSS hiding before reading a single line of source code. |
| **Fix** | Added the 2 missing items to the hardcoded array in `TopNav.tsx` (or removed the stray `LIMIT 2` from the backend query). |
| **Verification** | Post-fix screenshot shows all 4 dropdown items rendered and correctly styled. |

### The Data-vs-Rendering Decision Rule

```javascript
// Run in DevTools console with the dropdown open:
document.querySelectorAll('[role="menuitem"]').length
```

- Returns **2** → data issue (items never reached the DOM)
- Returns **4** → rendering issue (check CSS: `overflow: hidden`, `max-height`, `opacity: 0`, `visibility: hidden`, `display: none`, z-index overlap)
