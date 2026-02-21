const express = require("express");
const app = express();

const PORT = process.env.PORT || 3000;
const CLIENT_NAME = process.env.CLIENT_NAME || "Client-A";
const DB_CONNECTION = process.env.DB_CONNECTION || "Not Provided";

app.get("/", (req, res) => {
  res.json({
    message: `Hello from ${CLIENT_NAME}`,
    database: DB_CONNECTION,
  });
});

app.listen(PORT, () => {
  console.log(`${CLIENT_NAME} running on port ${PORT}`);
});
