const express = require("express");
const rulesRouter = require("./routes/rules");

const app = express();
app.use(express.json());
app.use("/api/v1/rules", rulesRouter);

// Malformed JSON in the request body throws inside express.json() before
// any route runs — without this it would surface as an unhandled 500.
app.use((err, req, res, next) => {
  if (err.type === "entity.parse.failed") {
    return res.status(400).json({
      error: {
        code: "INVALID_JSON",
        message: "Request body must be valid JSON.",
      },
    });
  }
  return next(err);
});

const PORT = process.env.PORT || 3000;
if (require.main === module) {
  app.listen(PORT, () => console.log(`Listening on port ${PORT}`));
}

module.exports = app;
