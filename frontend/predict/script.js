// Import Firebase modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getAuth,
  signInWithPopup,
  GoogleAuthProvider,
  onAuthStateChanged,
  signOut,
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// Your Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyB9Cl_caDnMbkDdtRd7oGlFB11C0wFh7FE",
  authDomain: "learn2aid.firebaseapp.com",
  projectId: "learn2aid",
  storageBucket: "learn2aid.appspot.com",
  messagingSenderId: "720302589716",
  appId: "1:720302589716:web:bcd5400adc8d41aa73e401",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

// DOM Elements
const loginGoogleBtn = document.getElementById("login-google");
const logoutBtn = document.getElementById("logout");
const userInfo = document.getElementById("user-info");
const userPhoto = document.getElementById("user-photo");
const userName = document.getElementById("user-name");
const userEmail = document.getElementById("user-email");
const predictionForm = document.getElementById("prediction-form");
const inputValue = document.getElementById("input-value");
const predictBtn = document.getElementById("predict-btn");
const apiResponse = document.getElementById("api-response");

// Backend API URL
const API_BASE_URL = "http://localhost:8080";

// Login with Google
loginGoogleBtn.addEventListener("click", async () => {
  try {
    console.log("Starting Google sign-in process...");
    const result = await signInWithPopup(auth, provider);
    console.log("Sign-in successful", result);
  } catch (error) {
    console.error("Error signing in:", error);
    apiResponse.textContent = JSON.stringify(
      {
        code: error.code,
        message: error.message,
        additionalData: error.customData ? error.customData.toJSON() : null,
      },
      null,
      2
    );
  }
});

// Logout
logoutBtn.addEventListener("click", async () => {
  try {
    await signOut(auth);
    apiResponse.textContent = "Enter a value and click Predict";
  } catch (error) {
    console.error("Error signing out:", error);
  }
});

// Make prediction
predictBtn.addEventListener("click", async () => {
  try {
    const value = parseFloat(inputValue.value);

    if (isNaN(value)) {
      apiResponse.textContent = "Please enter a valid number";
      return;
    }

    apiResponse.textContent = "Loading...";

    const token = await auth.currentUser.getIdToken();
    const response = await fetch(`${API_BASE_URL}/api/v1/predict`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ x: value }),
    });

    // Check if we need to refresh the token
    if (response.headers.get("X-Refresh-Token") === "true") {
      console.log("Token is about to expire, refreshing...");
      await auth.currentUser.getIdToken(true);
    }

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    apiResponse.textContent = `Prediction result: ${
      data.prediction
    }\n\nFull response:\n${JSON.stringify(data, null, 2)}`;
  } catch (error) {
    apiResponse.textContent = `Error: ${error.message}`;
    console.error("Prediction error:", error);
  }
});

// Monitor auth state changes
onAuthStateChanged(auth, (user) => {
  if (user) {
    // User is signed in
    console.log("User is signed in:", user);
    loginGoogleBtn.classList.add("hidden");
    logoutBtn.classList.remove("hidden");
    predictionForm.classList.remove("hidden");
    userInfo.style.display = "block";

    // Display user info
    userName.textContent = user.displayName;
    userEmail.textContent = user.email;
    if (user.photoURL) {
      userPhoto.src = user.photoURL;
    } else {
      userPhoto.src = "https://via.placeholder.com/50";
    }
  } else {
    // User is signed out
    console.log("User is signed out");
    loginGoogleBtn.classList.remove("hidden");
    logoutBtn.classList.add("hidden");
    predictionForm.classList.add("hidden");
    userInfo.style.display = "none";
  }
});
