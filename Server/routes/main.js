const express = require("express");
const bodyParser = require("body-parser");

// const authRouter = require("./authorization");
const userRouter = require("./user");

const router = express.Router();

router.use(bodyParser.json());

// router.use("/auth", authRouter);
router.use("/user", userRouter);

module.exports = router;
