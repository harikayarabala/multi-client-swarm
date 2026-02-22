const express = require("express");
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 3000;

function readSecret(path, fallback) {
  try {
    return fs.readFileSync(path, "utf8").trim();
  } catch (e) {
    return fallback;
  }
}

const CLIENT_NAME =
  process.env.CLIENT_NAME || readSecret("/run/secrets/client_a_name", "Client-A");

const DB_CONNECTION =
  process.env.DB_CONNECTION || readSecret("/run/secrets/client_a_db", "Not Provided");

app.get("/", (req, res) => {
  res.json({
    message: `Hello from ${CLIENT_NAME}`,
    database: DB_CONNECTION,
  });
});

app.listen(PORT, () => {
  console.log(`${CLIENT_NAME} running on port ${PORT}`);
});
