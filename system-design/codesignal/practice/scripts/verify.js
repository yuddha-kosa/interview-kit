// Small end-to-end client for the rules API. Exercises create -> get ->
// update -> delete against a running server (npm start in another terminal).
// Requires Node 18+ for the built-in `fetch`.
//
// Usage: node scripts/verify.js  (optionally BASE_URL=http://localhost:4000/api/v1/rules)

const BASE_URL = process.env.BASE_URL || "http://localhost:3000/api/v1/rules";

function assertStatus(res, expected, label) {
  if (res.status !== expected) {
    throw new Error(`${label}: expected status ${expected}, got ${res.status}`);
  }
}

async function main() {
  console.log("1. POST create rule");
  const createRes = await fetch(BASE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: "verify-script-rule",
      trigger: "ticket.tagged",
      condition: "tag == urgent",
      action: "notify:#oncall",
    }),
  });
  assertStatus(createRes, 201, "create");
  const created = await createRes.json();
  if (!created.id || created.version !== 1 || created.enabled !== true) {
    throw new Error(`create response missing expected fields: ${JSON.stringify(created)}`);
  }
  console.log("   OK ->", created);

  console.log("2. GET by id");
  const getRes = await fetch(`${BASE_URL}/${created.id}`);
  assertStatus(getRes, 200, "get by id");
  const fetched = await getRes.json();
  if (fetched.id !== created.id) throw new Error("fetched id does not match created id");
  console.log("   OK ->", fetched);

  console.log("3. PATCH toggle (enabled true -> false)");
  const toggleRes = await fetch(`${BASE_URL}/${created.id}/toggle`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ version: fetched.version }),
  });
  assertStatus(toggleRes, 200, "toggle");
  const toggled = await toggleRes.json();
  if (toggled.enabled !== false || toggled.version !== fetched.version + 1) {
    throw new Error(`toggle did not flip enabled/bump version: ${JSON.stringify(toggled)}`);
  }
  console.log("   OK ->", toggled);

  // Bonus check (beyond the plain CRUD walkthrough): retrying the toggle
  // with the now-stale version should be rejected, since this is the whole
  // point of the version field we added. Delete me if you just want the
  // plain create/get/update/delete path.
  console.log("3b. PATCH toggle again with a stale version (expect 409)");
  const staleRes = await fetch(`${BASE_URL}/${created.id}/toggle`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ version: fetched.version }), // old version now
  });
  assertStatus(staleRes, 409, "stale toggle");
  console.log("   OK -> correctly rejected with 409");

  console.log("4. DELETE rule");
  const deleteRes = await fetch(`${BASE_URL}/${created.id}`, { method: "DELETE" });
  assertStatus(deleteRes, 204, "delete");
  console.log("   OK -> 204 No Content");

  console.log("5. GET after delete (expect 404)");
  const afterDeleteRes = await fetch(`${BASE_URL}/${created.id}`);
  assertStatus(afterDeleteRes, 404, "get after delete");
  console.log("   OK -> 404");

  console.log("\nAll checks passed.");
}

main().catch((err) => {
  console.error("VERIFY FAILED:", err.message);
  process.exit(1);
});
