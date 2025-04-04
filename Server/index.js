const express = require("express");
const bodyParser = require("body-parser");

const mainRouter = require("./routes/main");

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.json());
app.use("/", mainRouter);

// Start server
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
