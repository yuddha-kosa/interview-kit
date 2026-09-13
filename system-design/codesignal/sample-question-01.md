# CodeSignal Practice — AI-Assisted Full-Stack Assessment

**Format notes (read once, then ignore while solving):**
- Simulated time box: 75 minutes.
- Stack: Node.js/Express backend, a simple in-memory or SQLite-style data store, minimal HTML/JS or React frontend — pick whichever you'd actually reach for.
- You're expected to work *with* an AI assistant: narrate what you ask it, review what it gives you, and fix anything wrong before accepting it. When you're ready, tell me what to build and I'll play the role of the AI assistant you're directing — give me scoped prompts rather than "just do the whole thing."

---

## Scenario

You're on the Automations team at a mid-size company. Internally, teams create **"Automation Rules"** — simple `when X happens, do Y` triggers (e.g., "when a ticket is tagged `urgent`, notify `#oncall`"). Product wants a minimal internal tool so non-engineers can view and manage these rules without filing a ticket to your team.

You've been handed a half-built repo. Your job is to finish it into a working slice.

## What already exists (assume this is scaffolded for you)

- An Express server with an empty `routes/rules.js`.
- A `rules` table/collection with this shape:

```json
{
  "id": "string (uuid)",
  "name": "string",
  "trigger": "string (e.g. 'ticket.tagged')",
  "condition": "string (e.g. 'tag == urgent')",
  "action": "string (e.g. 'notify:#oncall')",
  "enabled": "boolean",
  "createdAt": "ISO timestamp"
}
```

- A bare React (or plain JS) page with an empty `<div id="rules-root">` and no logic wired up.

## Requirements

1. **Backend API** — implement REST endpoints on `/api/rules`:
   - `GET /api/rules` — list all rules, newest first.
   - `POST /api/rules` — create a rule. Validate `name`, `trigger`, `condition`, `action` are non-empty strings; `enabled` defaults to `true` if omitted.
   - `PATCH /api/rules/:id/toggle` — flip `enabled` for one rule.
   - `DELETE /api/rules/:id` — remove a rule.
   - Return proper status codes (400 for bad input, 404 for missing id).

2. **Frontend** — a single page that:
   - Lists rules in a table (name, trigger → condition → action, enabled state).
   - Has a form to create a new rule.
   - Lets you toggle enabled/disabled and delete a rule, with the UI reflecting the change without a full page reload.

3. **Data layer** — your choice of in-memory array or lightweight persistence, but structure it so swapping in a real DB later wouldn't require rewriting the route handlers (i.e., keep data access behind a small module, not inlined in routes).

## Constraints / things graders reportedly look for

- Don't over-engineer: no auth, no framework migration, no test suite required — this is about shipping a correct, clean vertical slice fast.
- Edge cases worth handling: creating a rule with missing fields, toggling/deleting a rule that doesn't exist, double-submitting the create form.
- Keep the AI-collaboration visible: scope your asks (e.g., "write the POST handler with validation, return 400 with a message on missing fields" rather than "build the backend"), and explicitly check/correct anything an AI-style suggestion gets wrong (e.g., wrong status code, missing validation, mutating state unsafely).

## Stretch (only if time remains)

- Simple client-side filter/search box over the rules list by trigger or name.
- Sort toggle (newest/oldest).

---

*When you're ready, tell me which piece to start with and give me a scoped prompt — I'll respond the way an assistant embedded in the assessment IDE would.*
