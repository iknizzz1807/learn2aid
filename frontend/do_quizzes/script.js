// Import Firebase modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import {
  getAuth,
  signInWithPopup,
  GoogleAuthProvider,
  onAuthStateChanged,
  signOut,
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
import {
  getFirestore,
  collection,
  doc,
  getDoc,
  getDocs,
  addDoc,
  query,
  where,
  orderBy,
  serverTimestamp,
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

// Firebase configuration
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
const db = getFirestore(app);
const provider = new GoogleAuthProvider();

// DOM Elements
const loginInfo = document.getElementById("login-info");
const mainContent = document.getElementById("main-content");
const loginButton = document.getElementById("login-button");
const logoutButton = document.getElementById("logout-button");
const quizList = document.getElementById("quiz-list");
const quizSelection = document.getElementById("quiz-selection");
const quizTaking = document.getElementById("quiz-taking");
const quizTitle = document.getElementById("quiz-title");
const quizDescription = document.getElementById("quiz-description");
const questionsContainer = document.getElementById("questions-container");
const prevQuestion = document.getElementById("prev-question");
const nextQuestion = document.getElementById("next-question");
const questionCounter = document.getElementById("question-counter");
const submitQuiz = document.getElementById("submit-quiz");
const timer = document.getElementById("timer");
const resultsContainer = document.getElementById("results-container");
const resultScore = document.getElementById("result-score");
const resultPercentage = document.getElementById("result-percentage");
const resultTime = document.getElementById("result-time");
const resultsFeedback = document.getElementById("results-feedback");
const backToQuizzes = document.getElementById("back-to-quizzes");

// Global state
let currentUser = null;
let currentQuiz = null;
let currentQuestions = [];
let currentQuestionIndex = 0;
let userAnswers = [];
let quizStartTime = null;
let quizTimerInterval = null;
let quizTimeLimit = 0;
let quizAttemptId = null;

// Login with Google
loginButton.addEventListener("click", async () => {
  try {
    await signInWithPopup(auth, provider);
  } catch (error) {
    console.error("Login error:", error);
    alert(`Login failed: ${error.message}`);
  }
});

// Logout
logoutButton.addEventListener("click", async () => {
  try {
    await signOut(auth);
    clearQuizState();
  } catch (error) {
    console.error("Logout error:", error);
  }
});

// Back to quizzes
backToQuizzes.addEventListener("click", () => {
  resultsContainer.classList.add("hidden");
  quizSelection.classList.remove("hidden");
  clearQuizState();
});

// Monitor auth state changes
onAuthStateChanged(auth, async (user) => {
  if (user) {
    // User is signed in
    currentUser = user;
    loginInfo.innerHTML = `
    <p>Signed in as: <strong>${user.displayName}</strong> (${user.email})</p>
  `;
    mainContent.style.display = "block";
    loadQuizzes();
  } else {
    // User is signed out
    currentUser = null;
    loginInfo.innerHTML = `
    <button id="login-button" class="btn btn-primary">Login with Google</button>
  `;
    document
      .getElementById("login-button")
      .addEventListener("click", async () => {
        try {
          await signInWithPopup(auth, provider);
        } catch (error) {
          console.error("Login error:", error);
          alert(`Login failed: ${error.message}`);
        }
      });
    mainContent.style.display = "none";
    quizSelection.classList.remove("hidden");
    quizTaking.classList.add("hidden");
    resultsContainer.classList.add("hidden");
  }
});

// Load all quizzes
async function loadQuizzes() {
  try {
    quizList.innerHTML = `
    <div class="d-flex justify-content-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  `;

    // Get all quizzes or filter by category if needed
    const q = query(collection(db, "quizzes"), orderBy("created", "desc"));
    const querySnapshot = await getDocs(q);

    if (querySnapshot.empty) {
      quizList.innerHTML = `
      <p class="text-center my-4">No quizzes found. Please check back later.</p>
    `;
      return;
    }

    let listHTML = "";
    querySnapshot.forEach((doc) => {
      const quiz = doc.data();
      quiz.id = doc.id;

      listHTML += `
      <a href="#" class="list-group-item list-group-item-action quiz-list-item" data-id="${
        quiz.id
      }">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h5 class="mb-1">${quiz.title}</h5>
            <small class="text-muted">${quiz.category}</small>
          </div>
          <span class="badge bg-primary rounded-pill">${
            quiz.questionCount || 0
          } Questions</span>
        </div>
        <p class="mb-1">${quiz.description}</p>
        <small class="text-muted">${
          quiz.timeLimit
            ? `Time limit: ${formatTime(quiz.timeLimit)}`
            : "No time limit"
        }</small>
      </a>`;
    });

    quizList.innerHTML = listHTML;

    // Add click handlers
    document.querySelectorAll(".quiz-list-item").forEach((item) => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        startQuiz(item.dataset.id);
      });
    });
  } catch (error) {
    console.error("Error loading quizzes:", error);
    quizList.innerHTML = `
    <div class="alert alert-danger">Error loading quizzes. Please try again later.</div>
  `;
  }
}

// Start a quiz
async function startQuiz(quizId) {
  try {
    // Get quiz data
    const quizDoc = await getDoc(doc(db, "quizzes", quizId));

    if (!quizDoc.exists()) {
      alert("Quiz not found!");
      return;
    }

    // Set current quiz data
    currentQuiz = quizDoc.data();
    currentQuiz.id = quizId;
    quizTitle.textContent = currentQuiz.title;
    quizDescription.textContent = currentQuiz.description;

    // Get questions
    const questionsSnapshot = await getDocs(
      collection(db, "quizzes", quizId, "questions")
    );

    if (questionsSnapshot.empty) {
      alert("This quiz has no questions!");
      return;
    }

    // Build questions array
    currentQuestions = [];
    questionsSnapshot.forEach((questionDoc) => {
      const questionData = questionDoc.data();
      questionData.id = questionDoc.id;
      currentQuestions.push(questionData);
    });

    // Initialize user answers
    userAnswers = new Array(currentQuestions.length).fill(-1);

    // Reset current question index
    currentQuestionIndex = 0;

    // Create quiz attempt record
    const attemptData = {
      userId: currentUser.uid,
      quizId: quizId,
      startTime: serverTimestamp(),
      isCompleted: false,
      answers: userAnswers.slice(),
    };

    const attemptRef = await addDoc(
      collection(db, "quiz_attempts"),
      attemptData
    );
    quizAttemptId = attemptRef.id;

    // Setup timer if needed
    quizTimeLimit = currentQuiz.timeLimit;
    if (quizTimeLimit > 0) {
      timer.classList.remove("hidden");
      quizStartTime = new Date();
      startTimer(quizTimeLimit);
    } else {
      timer.classList.add("hidden");
    }

    // Display first question
    displayCurrentQuestion();

    // Show quiz taking section
    quizSelection.classList.add("hidden");
    quizTaking.classList.remove("hidden");
    resultsContainer.classList.add("hidden");

    // Update navigation buttons state
    updateNavigationButtons();
  } catch (error) {
    console.error("Error starting quiz:", error);
    alert(`Error starting quiz: ${error.message}`);
  }
}

// Display current question
function displayCurrentQuestion() {
  const question = currentQuestions[currentQuestionIndex];
  questionCounter.textContent = `Question ${currentQuestionIndex + 1} of ${
    currentQuestions.length
  }`;

  let html = `
  <div class="question-card">
    <h5 class="mb-3">${question.text}</h5>
    ${
      question.imageURL
        ? `<img src="${question.imageURL}" alt="Question image" class="img-fluid mb-3">`
        : ""
    }
    <div class="options-container">
`;

  question.options.forEach((option, index) => {
    const isSelected = userAnswers[currentQuestionIndex] === index;
    html += `
    <label class="option-label ${
      isSelected ? "selected" : ""
    }" data-index="${index}">
      <input type="radio" name="question${currentQuestionIndex}" value="${index}" ${
      isSelected ? "checked" : ""
    } style="display: none;">
      ${option}
    </label>
  `;
  });

  html += `
    </div>
  </div>
`;

  questionsContainer.innerHTML = html;

  // Add click handlers for options
  document.querySelectorAll(".option-label").forEach((label) => {
    label.addEventListener("click", () => {
      const index = parseInt(label.dataset.index);
      selectAnswer(index);
    });
  });
}

// Select answer
function selectAnswer(index) {
  // Save the answer
  userAnswers[currentQuestionIndex] = index;

  // Update visual selection
  const options = document.querySelectorAll(".option-label");
  options.forEach((option, i) => {
    if (i === index) {
      option.classList.add("selected");
      option.querySelector("input").checked = true;
    } else {
      option.classList.remove("selected");
      option.querySelector("input").checked = false;
    }
  });
}

// Navigate to previous question
prevQuestion.addEventListener("click", () => {
  if (currentQuestionIndex > 0) {
    currentQuestionIndex--;
    displayCurrentQuestion();
    updateNavigationButtons();
  }
});

// Navigate to next question
nextQuestion.addEventListener("click", () => {
  if (currentQuestionIndex < currentQuestions.length - 1) {
    currentQuestionIndex++;
    displayCurrentQuestion();
    updateNavigationButtons();
  }
});

// Update navigation buttons state
function updateNavigationButtons() {
  prevQuestion.disabled = currentQuestionIndex === 0;
  nextQuestion.disabled = currentQuestionIndex === currentQuestions.length - 1;
}

// Start timer
function startTimer(seconds) {
  let timeLeft = seconds;
  updateTimerDisplay(timeLeft);

  clearInterval(quizTimerInterval);
  quizTimerInterval = setInterval(() => {
    timeLeft--;
    updateTimerDisplay(timeLeft);

    if (timeLeft <= 0) {
      clearInterval(quizTimerInterval);
      alert("Time's up! Your quiz will be submitted.");
      submitQuizHandler();
    }
  }, 1000);
}

// Update timer display
function updateTimerDisplay(seconds) {
  timer.textContent = `Time: ${formatTime(seconds)}`;
}

// Format time
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes.toString().padStart(2, "0")}:${secs
    .toString()
    .padStart(2, "0")}`;
}

// Submit quiz handler
submitQuiz.addEventListener("click", submitQuizHandler);

async function submitQuizHandler() {
  // Confirm submission
  if (!confirm("Are you sure you want to submit your quiz?")) {
    return;
  }

  try {
    // Stop timer
    clearInterval(quizTimerInterval);

    // Calculate time taken
    const endTime = new Date();
    const timeTaken =
      quizTimeLimit > 0
        ? quizTimeLimit - Math.floor((endTime - quizStartTime) / 1000)
        : Math.floor((endTime - quizStartTime) / 1000);

    // Calculate score
    let correctAnswers = 0;
    for (let i = 0; i < currentQuestions.length; i++) {
      if (userAnswers[i] === currentQuestions[i].answer) {
        correctAnswers++;
      }
    }

    const score = correctAnswers;
    const maxScore = currentQuestions.length;
    const percentage = Math.round((score / maxScore) * 100);

    // Submit quiz attempt
    const attemptData = {
      userId: currentUser.uid,
      quizId: currentQuiz.id,
      endTime: serverTimestamp(),
      score: score,
      maxScore: maxScore,
      percentage: percentage,
      answers: userAnswers.slice(),
      timeTaken: timeTaken,
      isCompleted: true,
    };

    // Update the quiz attempt in Firestore
    if (quizAttemptId) {
      await updateQuizAttempt(quizAttemptId, attemptData);
    }

    // Show results
    displayResults(score, maxScore, percentage, timeTaken);

    // Hide quiz taking section
    quizTaking.classList.add("hidden");
    resultsContainer.classList.remove("hidden");
  } catch (error) {
    console.error("Error submitting quiz:", error);
    alert(`Error submitting quiz: ${error.message}`);
  }
}

// Update quiz attempt in Firestore
async function updateQuizAttempt(attemptId, data) {
  try {
    const attemptRef = doc(db, "quiz_attempts", attemptId);
    await updateDoc(attemptRef, data);
  } catch (error) {
    console.error("Error updating quiz attempt:", error);
  }
}

// Display results
function displayResults(score, maxScore, percentage, timeTaken) {
  resultScore.textContent = `Score: ${score}/${maxScore}`;
  resultPercentage.textContent = `Percentage: ${percentage}%`;
  resultTime.textContent = `Time taken: ${formatTime(timeTaken)}`;

  // Generate feedback
  let feedbackHtml = '<h4 class="mt-4 mb-3">Question Review:</h4>';

  currentQuestions.forEach((question, index) => {
    const userAnswer = userAnswers[index];
    const correctAnswer = question.answer;
    const isCorrect = userAnswer === correctAnswer;

    feedbackHtml += `
    <div class="card mb-3 ${isCorrect ? "border-success" : "border-danger"}">
      <div class="card-header ${
        isCorrect ? "bg-success text-white" : "bg-danger text-white"
      }">
        <div class="d-flex justify-content-between">
          <span>Question ${index + 1}</span>
          <span>${isCorrect ? "Correct" : "Incorrect"}</span>
        </div>
      </div>
      <div class="card-body">
        <p class="card-text">${question.text}</p>
        <div class="mt-3">
          ${question.options
            .map(
              (option, i) => `
            <div class="mb-2 option-display ${
              i === correctAnswer ? "correct" : ""
            } ${i === userAnswer && i !== correctAnswer ? "incorrect" : ""}">
              <span class="badge ${
                i === correctAnswer
                  ? "bg-success"
                  : i === userAnswer
                  ? "bg-danger"
                  : "bg-secondary"
              } me-2">${["A", "B", "C", "D"][i]}</span>
              ${option}
              ${
                i === correctAnswer
                  ? ' <small class="text-success">(Correct Answer)</small>'
                  : ""
              }
              ${
                i === userAnswer && i !== correctAnswer
                  ? ' <small class="text-danger">(Your Answer)</small>'
                  : ""
              }
            </div>
          `
            )
            .join("")}
        </div>
      </div>
    </div>
  `;
  });

  resultsFeedback.innerHTML = feedbackHtml;
}

// Clear quiz state
function clearQuizState() {
  currentQuiz = null;
  currentQuestions = [];
  currentQuestionIndex = 0;
  userAnswers = [];
  quizStartTime = null;
  clearInterval(quizTimerInterval);
  quizTimerInterval = null;
  quizTimeLimit = 0;
  quizAttemptId = null;
}
