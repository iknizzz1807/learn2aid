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
  addDoc,
  getDocs,
  getDoc,
  doc,
  updateDoc,
  deleteDoc,
  serverTimestamp,
  query,
  orderBy,
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
const newQuizButton = document.getElementById("new-quiz-button");
const quizEditor = document.getElementById("quiz-editor");
const welcomePanel = document.getElementById("welcome-panel");
const editorTitle = document.getElementById("editor-title");
const quizForm = document.getElementById("quiz-form");
const quizId = document.getElementById("quiz-id");
const quizTitle = document.getElementById("quiz-title");
const quizDescription = document.getElementById("quiz-description");
const quizCategory = document.getElementById("quiz-category");
const quizTimeLimit = document.getElementById("quiz-time-limit");
const questionsContainer = document.getElementById("questions-container");
const addQuestionButton = document.getElementById("add-question-button");
const cancelButton = document.getElementById("cancel-button");
const deleteQuizButton = document.getElementById("delete-quiz-button");
const questionTemplate = document.getElementById("question-template");

// Global state
let questionCounter = 0;

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
  } catch (error) {
    console.error("Logout error:", error);
  }
});

// Monitor auth state changes
onAuthStateChanged(auth, async (user) => {
  if (user) {
    // User is signed in
    loginInfo.innerHTML = `
    <p>Signed in as: <strong>${user.displayName}</strong> (${user.email})</p>
  `;
    mainContent.style.display = "block";
    loadQuizzes();
  } else {
    // User is signed out
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
  }
});

// Load all quizzes
async function loadQuizzes() {
  try {
    quizList.innerHTML =
      '<li class="list-group-item text-center">Loading quizzes...</li>';

    const q = query(collection(db, "quizzes"), orderBy("created", "desc"));
    const querySnapshot = await getDocs(q);

    if (querySnapshot.empty) {
      quizList.innerHTML =
        '<li class="list-group-item text-center">No quizzes found</li>';
      return;
    }

    let listHTML = "";
    querySnapshot.forEach((doc) => {
      const quiz = doc.data();
      quiz.id = doc.id;

      listHTML += `
      <li class="list-group-item quiz-list-item" data-id="${quiz.id}">
        <div class="d-flex justify-content-between">
          <div>
            <strong>${quiz.title}</strong>
            <div><small class="text-muted">${quiz.category}</small></div>
          </div>
          <span class="badge bg-primary rounded-pill">${
            quiz.questionCount || 0
          } Q</span>
        </div>
      </li>`;
    });

    quizList.innerHTML = listHTML;

    // Add click handlers
    document.querySelectorAll(".quiz-list-item").forEach((item) => {
      item.addEventListener("click", () => loadQuizForEditing(item.dataset.id));
    });
  } catch (error) {
    console.error("Error loading quizzes:", error);
    quizList.innerHTML = `<li class="list-group-item text-danger">Error loading quizzes</li>`;
  }
}

// Create a new question element
function createQuestionElement(index, questionData = null) {
  const clone = document.importNode(questionTemplate.content, true);
  const questionCard = clone.querySelector(".question-card");

  // Set question index and number
  questionCard.dataset.questionIndex = index;
  questionCard.querySelector(".question-number").textContent = index + 1;

  // Set radio names
  const radioButtons = questionCard.querySelectorAll(".option-radio");
  radioButtons.forEach((radio) => {
    radio.name = `correct-${index}`;
  });

  // Fill in data if provided
  if (questionData) {
    questionCard.querySelector(".question-text").value =
      questionData.text || "";
    questionCard.querySelector(".question-image-url").value =
      questionData.imageURL || "";

    // Fill options
    const optionInputs = questionCard.querySelectorAll(".option-text");
    for (
      let i = 0;
      i < Math.min(optionInputs.length, questionData.options.length);
      i++
    ) {
      optionInputs[i].value = questionData.options[i] || "";
    }

    // Select correct answer
    if (
      typeof questionData.answer === "number" &&
      questionData.answer >= 0 &&
      questionData.answer < 4
    ) {
      radioButtons[questionData.answer].checked = true;
    }
  }

  // Add remove handler
  questionCard
    .querySelector(".remove-question")
    .addEventListener("click", function () {
      if (confirm("Are you sure you want to remove this question?")) {
        questionCard.remove();
        updateQuestionNumbers();
      }
    });

  return questionCard;
}

// Update question numbering
function updateQuestionNumbers() {
  const questions = questionsContainer.querySelectorAll(".question-card");
  questions.forEach((question, index) => {
    question.dataset.questionIndex = index;
    question.querySelector(".question-number").textContent = index + 1;

    // Update radio button names
    const radioButtons = question.querySelectorAll(".option-radio");
    radioButtons.forEach((radio) => {
      radio.name = `correct-${index}`;
    });
  });
}

// Add question button handler
addQuestionButton.addEventListener("click", () => {
  const newQuestion = createQuestionElement(questionCounter++);
  questionsContainer.appendChild(newQuestion);
});

// New quiz button handler
newQuizButton.addEventListener("click", () => {
  resetQuizForm();
  quizEditor.classList.remove("d-none");
  welcomePanel.classList.add("d-none");
  editorTitle.textContent = "Create New Quiz";
  deleteQuizButton.classList.add("d-none");
});

// Cancel button handler
cancelButton.addEventListener("click", () => {
  quizEditor.classList.add("d-none");
  welcomePanel.classList.remove("d-none");
});

// Delete quiz button handler
deleteQuizButton.addEventListener("click", async () => {
  if (!quizId.value) return;

  if (
    confirm(
      "Are you sure you want to delete this quiz? This action cannot be undone!"
    )
  ) {
    try {
      // Delete questions subcollection
      const questionsSnapshot = await getDocs(
        collection(db, "quizzes", quizId.value, "questions")
      );
      const deletePromises = [];

      questionsSnapshot.forEach((questionDoc) => {
        deletePromises.push(
          deleteDoc(
            doc(db, "quizzes", quizId.value, "questions", questionDoc.id)
          )
        );
      });

      await Promise.all(deletePromises);

      // Delete the main quiz document
      await deleteDoc(doc(db, "quizzes", quizId.value));

      // Refresh the quiz list
      loadQuizzes();

      // Hide editor
      quizEditor.classList.add("d-none");
      welcomePanel.classList.remove("d-none");

      alert("Quiz deleted successfully!");
    } catch (error) {
      console.error("Error deleting quiz:", error);
      alert(`Error deleting quiz: ${error.message}`);
    }
  }
});

// Load quiz for editing
async function loadQuizForEditing(id) {
  try {
    // Get quiz data
    const quizDoc = await getDoc(doc(db, "quizzes", id));

    if (!quizDoc.exists()) {
      alert("Quiz not found!");
      return;
    }

    const quizData = quizDoc.data();

    // Reset form
    resetQuizForm();

    // Fill quiz details
    quizId.value = id;
    quizTitle.value = quizData.title || "";
    quizDescription.value = quizData.description || "";
    quizCategory.value = quizData.category || "";
    quizTimeLimit.value = quizData.timeLimit || 0;

    // Get questions
    const questionsSnapshot = await getDocs(
      collection(db, "quizzes", id, "questions")
    );

    if (!questionsSnapshot.empty) {
      questionCounter = 0;
      questionsSnapshot.forEach((questionDoc) => {
        const questionData = questionDoc.data();
        questionData.id = questionDoc.id;
        const questionElement = createQuestionElement(
          questionCounter++,
          questionData
        );
        questionsContainer.appendChild(questionElement);
      });
    }

    // Show editor
    quizEditor.classList.remove("d-none");
    welcomePanel.classList.add("d-none");
    editorTitle.textContent = "Edit Quiz";
    deleteQuizButton.classList.remove("d-none");
  } catch (error) {
    console.error("Error loading quiz:", error);
    alert(`Error loading quiz: ${error.message}`);
  }
}

// Reset quiz form
function resetQuizForm() {
  quizForm.reset();
  quizId.value = "";
  questionsContainer.innerHTML = "";
  questionCounter = 0;
}

// Save quiz
quizForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  try {
    // Validate form
    if (!validateQuizForm()) {
      return;
    }

    // Collect quiz data
    const quizData = {
      title: quizTitle.value,
      description: quizDescription.value,
      category: quizCategory.value,
      timeLimit: parseInt(quizTimeLimit.value),
      questionCount:
        questionsContainer.querySelectorAll(".question-card").length,
      updated: serverTimestamp(),
    };

    let quizRef;

    // Create or update quiz
    if (quizId.value) {
      // Update existing quiz
      quizRef = doc(db, "quizzes", quizId.value);
      await updateDoc(quizRef, quizData);
    } else {
      // Create new quiz
      quizData.created = serverTimestamp();
      quizRef = await addDoc(collection(db, "quizzes"), quizData);
    }

    // Clear any existing questions if updating
    if (quizId.value) {
      const existingQuestions = await getDocs(
        collection(db, "quizzes", quizId.value, "questions")
      );
      const deletePromises = [];

      existingQuestions.forEach((questionDoc) => {
        deletePromises.push(
          deleteDoc(
            doc(db, "quizzes", quizId.value, "questions", questionDoc.id)
          )
        );
      });

      await Promise.all(deletePromises);
    }

    // Save questions
    const questions = questionsContainer.querySelectorAll(".question-card");
    const questionSavePromises = [];

    questions.forEach((questionEl) => {
      const questionData = {
        text: questionEl.querySelector(".question-text").value,
        imageURL: questionEl.querySelector(".question-image-url").value || "",
        options: Array.from(questionEl.querySelectorAll(".option-text")).map(
          (input) => input.value
        ),
        answer: parseInt(
          questionEl.querySelector(".option-radio:checked").value
        ),
      };

      questionSavePromises.push(
        addDoc(
          collection(db, "quizzes", quizRef.id || quizId.value, "questions"),
          questionData
        )
      );
    });

    await Promise.all(questionSavePromises);

    // Refresh the quiz list
    loadQuizzes();

    // Hide editor
    quizEditor.classList.add("d-none");
    welcomePanel.classList.remove("d-none");

    alert("Quiz saved successfully!");
  } catch (error) {
    console.error("Error saving quiz:", error);
    alert(`Error saving quiz: ${error.message}`);
  }
});

// Validate quiz form
function validateQuizForm() {
  // Check basic quiz info
  if (!quizTitle.value || !quizDescription.value || !quizCategory.value) {
    alert("Please fill in all quiz details");
    return false;
  }

  // Check if there are any questions
  const questions = questionsContainer.querySelectorAll(".question-card");
  if (questions.length === 0) {
    alert("Please add at least one question");
    return false;
  }

  // Check each question
  for (const questionEl of questions) {
    const questionText = questionEl.querySelector(".question-text").value;
    if (!questionText) {
      alert("Please fill in all question texts");
      return false;
    }

    // Check options
    const options = questionEl.querySelectorAll(".option-text");
    for (const option of options) {
      if (!option.value) {
        alert("Please fill in all options");
        return false;
      }
    }

    // Check if an answer is selected
    const selectedAnswer = questionEl.querySelector(".option-radio:checked");
    if (!selectedAnswer) {
      alert("Please select a correct answer for each question");
      return false;
    }
  }

  return true;
}
