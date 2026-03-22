# Debugging: Dropdown Menu Showing 2 of 4 Options

## Problem Statement

An Electron app has a top-nav dropdown that should display 4 options but only renders 2. The goal is to determine whether this is a **data issue** (options not loaded into the component's state/props) or a **rendering issue** (options exist in data but aren't visible due to CSS or DOM logic).

---

## Step 1: Distinguish Data vs. Render — The Core Question

These two failure modes have different root causes and different fixes:

| Category | What it means | Example causes |
|---|---|---|
| Data issue | The component only receives or holds 2 items | API returns 2, filter trims to 2, state update drops items |
| Render issue | Component has 4 items but only shows 2 | CSS overflow/height, conditional render logic, z-index clipping |

The fastest way to answer this is to **inspect the component's data at runtime** before looking at CSS.

---

## Step 2: Open DevTools and Inspect the DOM

Since this is an Electron app with a Chromium renderer, open DevTools with `Ctrl+Shift+I` (or `Cmd+Option+I` on Mac), or via the app menu if exposed.

Navigate to the **Elements** panel. Find the dropdown container (likely a `<ul>`, `<div>`, or `<select>` element). Count the child `<li>` or `<option>` nodes.

- If there are **only 2 child nodes**: this is a **data issue**. The component was never given 4 items to render.
- If there are **4 child nodes but 2 are hidden**: this is a **rendering issue**.

To check visibility on hidden nodes, look for:
- `display: none`
- `visibility: hidden`
- `opacity: 0`
- `overflow: hidden` on the parent container with a fixed `max-height` or `height` that clips content
- `clip` or `clip-path` rules

---

## Step 3: Inspect React/Vue/Angular Component State (if applicable)

If the app uses React, install or use the **React DevTools** extension (available for Electron via manual injection or if already bundled). In the Components panel, select the dropdown component and inspect its `props` and `state`.

Look for the array that feeds the dropdown options (e.g., `items`, `options`, `menuItems`). Count the items:

- Array has 2 items -> **data issue**
- Array has 4 items -> **rendering issue**

If React DevTools aren't available, use the **Console** panel. If the component attaches data to a DOM node via a `__reactFiber` or `__reactInternalInstance` key, you can inspect it:

```js
// In the console, select the dropdown element first, then:
let el = document.querySelector('.nav-dropdown'); // adjust selector
let fiberKey = Object.keys(el).find(k => k.startsWith('__reactFiber'));
let fiber = el[fiberKey];
// Traverse fiber to find memoizedProps or memoizedState
console.log(fiber.memoizedProps);
```

---

## Step 4: Check the Network Tab for Data Issues

If the options are loaded from an API:

1. Open the **Network** tab in DevTools.
2. Filter by XHR/Fetch.
3. Trigger the dropdown to open (or reload the page) and look for the relevant API call.
4. Inspect the response payload — does it return 4 items or 2?

- Response has 2 items -> the backend or the fetch call is the source of truth; data issue starts upstream.
- Response has 4 items but state has 2 -> something in the data transformation pipeline (mapping, filtering, slicing) is trimming the array.

---

## Step 5: Trace the Data Pipeline in the Console

If the response has 4 items but the UI shows 2, add temporary `console.log` statements (or use the Sources panel to set breakpoints) at each transformation step:

```js
// Example: where options are set
setMenuItems(data.options); // log data.options here
// or
this.setState({ items: processedItems }); // log processedItems
```

Common culprits:
- A `.slice(0, 2)` or `.filter()` call unintentionally limiting the array
- A hardcoded `limit` or `maxItems` prop set to 2
- A feature flag or permissions check hiding certain options

---

## Step 6: Diagnose Rendering Issues

If the data is confirmed to have 4 items but only 2 are visible:

### CSS Overflow Clipping

```css
/* Common culprit */
.dropdown-menu {
  max-height: 80px; /* only tall enough for 2 items */
  overflow: hidden;
}
```

In the Elements panel, select the dropdown container and check its **Computed** styles. If `overflow` is `hidden` and the `height` or `max-height` is too small, increase it or switch to `overflow: auto`.

### Z-Index / Stacking Context

If the dropdown is inside a container with `overflow: hidden` or `position: relative` with clipping, the bottom items may be cut off. Check parent elements for `overflow: hidden`.

### Conditional Rendering Logic

Search the source for conditional rendering on menu items:

```jsx
// React example
{items.map((item, i) => (
  // Bug: only renders first 2
  i < 2 && <DropdownItem key={item.id} {...item} />
))}
```

Or a `v-if` / `*ngIf` condition gated on an index.

---

## Proposed Fix (Based on Most Likely Cause)

Without seeing the code, the most common scenario for "4 expected, 2 shown" is one of:

1. **A CSS `max-height` too small**: Fix by increasing `max-height` or setting `overflow: auto` on the dropdown container.
2. **An accidental `.slice(0, 2)`** or `maxItems = 2` prop: Remove or correct the limit.
3. **An API or state management bug**: Ensure the full array is passed through without being trimmed.

---

## Verification Steps

After applying a fix:

1. Open DevTools Elements panel — confirm the dropdown container now has 4 child nodes.
2. Open the Components/State panel — confirm the options array has 4 items.
3. Click the dropdown in the UI — visually confirm all 4 options appear.
4. If options are permission-gated, test with an account that should have access to all 4 and confirm they render.
5. Run any existing unit or integration tests for the dropdown component to ensure no regression.

---

## Summary

The structured approach is: **DOM node count first** (data vs. render split), then **component state inspection** (where in the pipeline data is lost), then **CSS computed styles** (if data is present but clipped). This sequence minimizes guesswork and quickly isolates whether to fix the data layer or the presentation layer.
