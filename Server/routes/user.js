const express = require("express");
const { User, Sleep } = require("../database");
const userRouter = express.Router();

//
async function sendExpoPushNotification(
  targetExpoToken,
  title,
  body,
  data = {}
) {
  const expoPushEndpoint = "https://exp.host/--/api/v2/push/send";
  const message = {
    to: targetExpoToken,
    sound: "default",
    title: title,
    body: body,
    data: data, // Optional: Send extra data to your app
  };

  try {
    console.log(`Sending notification to Expo token: ${targetExpoToken}`);
    const response = await fetch(expoPushEndpoint, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Accept-encoding": "gzip, deflate",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(message),
    });

    const responseData = await response.json(); // Expo returns receipt details or errors
    console.log("Expo Push API Response:", responseData);

    // Check for errors in the response from Expo
    if (responseData.data?.status === "error") {
      console.error(
        `Error sending push via Expo: ${responseData.data.message}`
      );
      if (responseData.data.details?.error === "DeviceNotRegistered") {
        // This token is invalid, remove it from your DB
        console.log(
          `Expo token ${targetExpoToken} is invalid. Removing from DB.`
        );
        // await removeExpoTokenFromDB(userId, targetExpoToken);
      }
      return false;
    }
    return true; // Indicate success
  } catch (error) {
    console.error("Error calling Expo Push API:", error);
    return false;
  }
}

/**
 * @route   POST /api/users
 * @desc    Create a new user
 * @access  Public (adjust access control as needed)
 */
router.post("/", async (req, res) => {
  console.log("Received request to create user:", req.body);
  const { name, gender, age, expoNotificationToken } = req.body;

  // Basic validation (Mongoose schema validation is more robust)
  if (!name || !gender || !age || !expoNotificationToken) {
    return res.status(400).json({
      message:
        "Missing required fields: name, gender, age, expoNotificationToken",
    });
  }

  // Validate gender enum (optional, Mongoose does this too)
  if (!["Male", "Female", "Other"].includes(gender)) {
    return res.status(400).json({ message: "Invalid gender specified." });
  }
  if (typeof age !== "number" || age < 0) {
    return res.status(400).json({ message: "Invalid age specified." });
  }

  try {
    // Check if user with this token already exists (optional, depends on your logic)
    let existingUser = await User.findOne({ expoNotificationToken });
    if (existingUser) {
      console.warn(
        `User creation attempt failed: Token already exists for user ${existingUser._id}`
      );
      // Decide how to handle: return error, or maybe update existing user?
      // For now, returning an error as creating a *new* user with same token seems wrong.
      return res
        .status(409)
        .json({ message: "User with this notification token already exists" });
    }

    // Create new user instance
    const newUser = new User({
      name,
      gender,
      age,
      expoNotificationToken,
      sleepArray: [], // Initialize sleepArray as empty
    });

    // Save user to database
    const savedUser = await newUser.save();
    console.log("User created successfully:", savedUser._id);

    // Return the created user (excluding sensitive data if needed in future)
    res.status(201).json(savedUser);
  } catch (error) {
    console.error("Error creating user:", error);
    if (error.code === 11000) {
      // Duplicate key error (likely expoNotificationToken if unique index)
      return res.status(409).json({
        message:
          "Error: A user with this notification token might already exist.",
        details: error.message,
      });
    }
    if (error.name === "ValidationError") {
      return res
        .status(400)
        .json({ message: "Validation Error", details: error.message });
    }
    res
      .status(500)
      .json({ message: "Server error creating user", details: error.message });
  }
});

/**
 * @route   PATCH /api/users/:userId/token
 * @desc    Update the expoNotificationToken for a specific user
 * @access  Protected (User should likely only update their own token)
 */
router.patch("/:userId/token", async (req, res) => {
  const { userId } = req.params;
  const { expoNotificationToken } = req.body;
  console.log(`Received request to update token for user ${userId}`);

  if (!expoNotificationToken) {
    return res
      .status(400)
      .json({ message: "Missing required field: expoNotificationToken" });
  }

  // Optional: Validate if the provided userId is a valid MongoDB ObjectId format
  if (!mongoose.Types.ObjectId.isValid(userId)) {
    return res.status(400).json({ message: "Invalid user ID format" });
  }

  try {
    // Find the user by ID and update their token
    // { new: true } returns the updated document
    const updatedUser = await User.findByIdAndUpdate(
      userId,
      { $set: { expoNotificationToken: expoNotificationToken } }, // Use $set to update specific field
      { new: true, runValidators: true } // runValidators ensures schema rules (like required) are checked on update
    );

    // Check if a user was found and updated
    if (!updatedUser) {
      console.warn(`Token update failed: User not found with ID: ${userId}`);
      return res.status(404).json({ message: "User not found" });
    }

    console.log(`Token updated successfully for user ${userId}`);
    // Return the updated user (consider excluding sensitive fields)
    res.status(200).json(updatedUser);
  } catch (error) {
    console.error(`Error updating token for user ${userId}:`, error);
    if (error.code === 11000) {
      // Duplicate key error
      return res.status(409).json({
        message:
          "Error: This notification token might already be in use by another user.",
        details: error.message,
      });
    }
    if (error.name === "ValidationError") {
      return res
        .status(400)
        .json({ message: "Validation Error", details: error.message });
    }
    res
      .status(500)
      .json({ message: "Server error updating token", details: error.message });
  }
});

/**
 * @route   POST /api/users/alert  <-- Or maybe just /api/alert if in separate file
 * @desc    Trigger a drowsiness alert for a specific user
 * @access  Protected/Internal (Should only be called by trusted sources like Pi/Arduino)
 */
router.post("/alert", async (req, res) => {
  const { userId, source = "unknown", confidence } = req.body; // Expect userId from trigger source
  console.log(
    `Received alert trigger for userId: ${userId} from source: ${source}`
  );

  // 1. Validate Input
  if (!userId) {
    return res.status(400).json({ message: "Missing required field: userId" });
  }
  if (!mongoose.Types.ObjectId.isValid(userId)) {
    return res.status(400).json({ message: "Invalid user ID format" });
  }

  try {
    // 2. Find the User and their Token
    const user = await User.findById(userId).select(
      "expoNotificationToken name"
    ); // Select only needed fields

    if (!user) {
      console.warn(`Alert trigger failed: User not found with ID: ${userId}`);
      return res.status(404).json({ message: "User not found" });
    }

    if (!user.expoNotificationToken) {
      console.warn(
        `Alert trigger failed: User ${userId} has no Expo notification token stored.`
      );
      // Still return success to the caller, as the user exists but can't be notified
      return res.status(200).json({
        message: "User found but has no notification token.",
        notification_sent: false,
      });
    }

    // 3. Send the Notification using the function
    const title = "Drowsiness Alert!";
    const body = `Possible drowsiness detected${
      user.name ? " for " + user.name : ""
    }. Please consider taking a break.`;
    const dataPayload = {
      // Example extra data
      alertType: "drowsiness",
      triggerSource: source,
      confidenceScore: confidence,
      userId: userId, // Send userId back to app if useful
    };

    const notificationSent = await sendExpoPushNotification(
      user.expoNotificationToken,
      title,
      body,
      dataPayload
    );

    // 4. Respond to the Trigger Source (Pi/Arduino)
    if (notificationSent) {
      console.log(`Successfully sent alert notification to user ${userId}`);
      res.status(200).json({
        message: "Alert processed, notification sent.",
        notification_sent: true,
      });
    } else {
      console.log(
        `Processed alert for user ${userId}, but notification failed to send (check Expo API logs/token validity).`
      );
      // Still send 200 OK to the Pi, maybe indicate failure in payload
      res.status(200).json({
        message: "Alert processed, but notification failed to send.",
        notification_sent: false,
      });
    }

    // 5. (Optional) Log the alert event to a separate collection or update user stats
  } catch (error) {
    console.error(`Server error processing alert for user ${userId}:`, error);
    res.status(500).json({
      message: "Server error processing alert",
      details: error.message,
    });
  }
});

module.exports = userRouter;
