const express = require("express");
const bodyParser = require("body-parser");
const { User, Sleep } = require("../database");
const sleepRouter = express.Router();

/**
 * @route   POST /api/users/:userId/sleep
 * @desc    Add a new sleep data record for a specific user
 * @access  Protected (User should likely only add their own sleep data)
 */
router.post("/:userId/record", async (req, res) => {
  const { userId } = req.params;
  const {
    remSleepPercentage,
    deepSleepPercentage,
    lightSleep,
    totalSleepDuration,
    timeOfSleep, // Expecting ISO 8601 date string e.g., "2023-10-27T22:00:00Z"
  } = req.body;

  console.log(
    `Received request to add sleep data for user ${userId}:`,
    req.body
  );

  // 1. Validate Input
  if (!userId || !mongoose.Types.ObjectId.isValid(userId)) {
    return res.status(400).json({ message: "Invalid or missing user ID" });
  }
  if (
    remSleepPercentage == null ||
    deepSleepPercentage == null ||
    lightSleep == null ||
    totalSleepDuration == null ||
    !timeOfSleep
  ) {
    return res.status(400).json({
      message:
        "Missing required sleep data fields (remSleepPercentage, deepSleepPercentage, lightSleep, totalSleepDuration, timeOfSleep)",
    });
  }
  // Add more specific validation if needed (e.g., numbers are numbers, percentages add up, date is valid)

  try {
    // 2. Check if the user exists
    const userExists = await User.findById(userId).select("_id"); // Only select ID for check
    if (!userExists) {
      console.warn(`Add sleep data failed: User not found with ID: ${userId}`);
      return res.status(404).json({ message: "User not found" });
    }

    // 3. Create new Sleep document instance
    const newSleepData = new Sleep({
      userId: userId, // Link to the user
      remSleepPercentage,
      deepSleepPercentage,
      lightSleep,
      totalSleepDuration,
      timeOfSleep: new Date(timeOfSleep), // Convert ISO string to Date object
    });

    // 4. Save the Sleep document
    const savedSleepData = await newSleepData.save();
    console.log(
      `Sleep data saved successfully with ID: ${savedSleepData._id} for user: ${userId}`
    );

    // 5. Add the new Sleep document's ID to the User's sleepArray
    //    Using findByIdAndUpdate with $push is efficient
    await User.findByIdAndUpdate(
      userId,
      { $push: { sleepArray: savedSleepData._id } } // Add the ObjectId to the array
    );
    console.log(`Updated user ${userId}'s sleepArray.`);

    // 6. Respond with the created sleep data
    res.status(201).json(savedSleepData); // 201 Created status
  } catch (error) {
    console.error(`Error saving sleep data for user ${userId}:`, error);
    if (error.name === "ValidationError") {
      // Mongoose validation error (e.g., required field missing, type mismatch)
      return res.status(400).json({
        message: "Validation Error saving sleep data",
        details: error.message,
      });
    }
    // Handle other potential errors (database connection issues, etc.)
    res.status(500).json({
      message: "Server error saving sleep data",
      details: error.message,
    });
  }
});

module.exports = sleepRouter;
