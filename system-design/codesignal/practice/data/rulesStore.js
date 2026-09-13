const { randomUUID } = require("crypto");

// In-memory store. Swapping this for a real DB later should only require
// changing what's inside these functions, not the route handlers that call them.
//
// Map keyed by id — O(1) lookup/update/delete for the toggle and delete
// endpoints instead of scanning an array. Iteration order is insertion
// order (oldest first), so "newest first" listing means reversing at
// read time, not relying on the Map itself.
const rules = new Map();

function create(fields) {
  const now = new Date().toISOString();
  const rule = {
    id: randomUUID(),
    name: fields.name,
    trigger: fields.trigger,
    condition: fields.condition,
    action: fields.action,
    enabled: fields.enabled,
    version: 1,
    createdAt: now,
    updatedAt: now,
  };

  rules.set(rule.id, rule);
  return rule;
}

function findById(id) {
  return rules.get(id);
}

function findAll() {
  // Map iterates in insertion order (oldest first); reverse for newest-first.
  return Array.from(rules.values()).reverse();
}

function remove(id) {
  return rules.delete(id); // true if it existed and was removed, false otherwise
}

// Optimistic locking: caller must supply the version they last read.
// Returns one of:
//   { outcome: "not_found" }
//   { outcome: "conflict", current }   — someone else changed it first
//   { outcome: "ok", rule }
function toggleEnabled(id, expectedVersion) {
  const rule = rules.get(id);
  if (!rule) {
    return { outcome: "not_found" };
  }

  if (rule.version !== expectedVersion) {
    return { outcome: "conflict", current: rule };
  }

  rule.enabled = !rule.enabled;
  rule.version += 1;
  rule.updatedAt = new Date().toISOString();
  return { outcome: "ok", rule };
}

module.exports = {
  create,
  findById,
  findAll,
  remove,
  toggleEnabled,
};
