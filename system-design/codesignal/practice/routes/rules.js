const express = require("express");
const rulesStore = require("../data/rulesStore");

const router = express.Router();

const REQUIRED_STRING_FIELDS = ["name", "trigger", "condition", "action"];
const MAX_FIELD_LENGTH = 500;

function validateCreatePayload(body) {
  const errors = [];

  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    return { valid: false, errors: ["Request body must be a JSON object."] };
  }

  for (const field of REQUIRED_STRING_FIELDS) {
    const value = body[field];
    if (typeof value !== "string" || value.trim().length === 0) {
      errors.push(`"${field}" is required and must be a non-empty string.`);
    } else if (value.length > MAX_FIELD_LENGTH) {
      errors.push(`"${field}" must be ${MAX_FIELD_LENGTH} characters or fewer.`);
    }
  }

  if (body.enabled !== undefined && typeof body.enabled !== "boolean") {
    errors.push('"enabled" must be a boolean if provided.');
  }

  return { valid: errors.length === 0, errors };
}

function validateTogglePayload(body) {
  if (typeof body !== "object" || body === null || Array.isArray(body)) {
    return { valid: false, error: "Request body must be a JSON object." };
  }

  if (!Number.isInteger(body.version) || body.version < 1) {
    return {
      valid: false,
      error:
        '"version" is required and must be a positive integer matching the rule\'s current version.',
    };
  }

  return { valid: true };
}

function notFoundResponse(res, id) {
  return res.status(404).json({
    error: {
      code: "NOT_FOUND",
      message: `No rule found with id "${id}".`,
    },
  });
}

router.get("/", (req, res) => {
  return res.status(200).json(rulesStore.findAll());
});

router.get("/:id", (req, res) => {
  const rule = rulesStore.findById(req.params.id);
  if (!rule) {
    return notFoundResponse(res, req.params.id);
  }
  return res.status(200).json(rule);
});

router.post("/", (req, res) => {
  const { valid, errors } = validateCreatePayload(req.body);

  if (!valid) {
    return res.status(400).json({
      error: {
        code: "VALIDATION_ERROR",
        message: "One or more fields failed validation.",
        details: errors,
      },
    });
  }

  const payload = {
    name: req.body.name.trim(),
    trigger: req.body.trigger.trim(),
    condition: req.body.condition.trim(),
    action: req.body.action.trim(),
    enabled: req.body.enabled === undefined ? true : req.body.enabled,
  };

  let created;
  try {
    created = rulesStore.create(payload);
  } catch (err) {
    return res.status(500).json({
      error: {
        code: "INTERNAL_ERROR",
        message: "Failed to create rule.",
      },
    });
  }

  return res
    .status(201)
    .set("Location", `/api/v1/rules/${created.id}`)
    .json(created);
});

router.patch("/:id/toggle", (req, res) => {
  const { valid, error } = validateTogglePayload(req.body);
  if (!valid) {
    return res.status(400).json({
      error: { code: "VALIDATION_ERROR", message: error },
    });
  }

  const result = rulesStore.toggleEnabled(req.params.id, req.body.version);

  if (result.outcome === "not_found") {
    return notFoundResponse(res, req.params.id);
  }

  if (result.outcome === "conflict") {
    return res.status(409).json({
      error: {
        code: "VERSION_CONFLICT",
        message:
          "The rule has changed since you last read it. Refetch and retry with the current version.",
        current: result.current,
      },
    });
  }

  return res.status(200).json(result.rule);
});

router.delete("/:id", (req, res) => {
  const deleted = rulesStore.remove(req.params.id);
  if (!deleted) {
    return notFoundResponse(res, req.params.id);
  }
  return res.status(204).send();
});

module.exports = router;
