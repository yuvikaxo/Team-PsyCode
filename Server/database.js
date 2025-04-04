const mongoose = require("mongoose");

const connectionURL =
  "mongodb+srv://admin:NKvalSPuz4pkffng@cluster0.7ffcbvq.mongodb.net/Zendrive";

mongoose
  .connect(connectionURL)
  .then(() => {
    console.log("Connected to MongoDB Atlas");
  })
  .catch((error) => {
    console.error("Error connecting to MongoDB Atlas:", error);
  });

const UserSchema = new mongoose.Schema({
  expoNotificationToken: { type: String, required: true },
  name: { type: String, required: true },
  gender: { type: String, enum: ["Male", "Female", "Other"], required: true },
  age: { type: Number, required: true },
  sleepArray: [{ type: mongoose.Schema.Types.ObjectId, ref: "Sleep" }],
});

const UserDb = mongoose.model("User", UserSchema);
const SleepSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  remSleepPercentage: { type: Number, required: true },
  deepSleepPercentage: { type: Number, required: true },
  lightSleep: { type: Number, required: true },
  totalSleepDuration: { type: Number, required: true }, // in hours
  timeOfSleep: { type: Date, required: true },
});

const SleepDb = mongoose.model("Sleep", SleepSchema);

module.exports = { UserDb, SleepDb };
