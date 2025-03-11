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
  query,
  where,
  orderBy,
  serverTimestamp,
  deleteDoc,
  doc,
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";
import {
  getStorage,
  ref,
  uploadBytesResumable,
  getDownloadURL,
  deleteObject,
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-storage.js";

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
const storage = getStorage(app);
const provider = new GoogleAuthProvider();

// DOM Elements
const loginInfo = document.getElementById("login-info");
const mainContent = document.getElementById("main-content");
const loginButton = document.getElementById("login-button");
const logoutButton = document.getElementById("logout-button");
const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("file-input");
const selectFileButton = document.getElementById("select-file");
const uploadProgress = document.getElementById("upload-progress");
const progressBar = uploadProgress.querySelector(".progress-bar");
const videoForm = document.getElementById("video-form");
const videoTitle = document.getElementById("video-title");
const videoDescription = document.getElementById("video-description");
const videoCategory = document.getElementById("video-category");
const videoDuration = document.getElementById("video-duration");
const thumbnailUrl = document.getElementById("thumbnail-url");
const agreeTerms = document.getElementById("agree-terms");
const uploadButton = document.getElementById("upload-button");
const videosContainer = document.getElementById("videos-container");
const refreshVideosButton = document.getElementById("refresh-videos");
const categoryButtons = document.querySelectorAll(".category-btn");

// Global state
let currentUser = null;
let selectedFile = null;
let currentCategory = "all";

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
    currentUser = user;
    loginInfo.innerHTML = `
    <p>Signed in as: <strong>${user.displayName}</strong> (${user.email})</p>
  `;
    mainContent.style.display = "block";
    loadVideos(currentCategory);
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
  }
});

// Setup category filter buttons
categoryButtons.forEach((button) => {
  button.addEventListener("click", () => {
    // Remove active class from all buttons
    categoryButtons.forEach((btn) => btn.classList.remove("active"));
    // Add active class to clicked button
    button.classList.add("active");

    // Set current category and reload videos
    currentCategory = button.dataset.category;
    console.log(currentCategory);
    loadVideos(currentCategory);
  });
});

// Drag and drop functionality
["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
  dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

["dragenter", "dragover"].forEach((eventName) => {
  dropArea.addEventListener(eventName, highlight, false);
});

["dragleave", "drop"].forEach((eventName) => {
  dropArea.addEventListener(eventName, unhighlight, false);
});

function highlight() {
  dropArea.classList.add("highlight");
}

function unhighlight() {
  dropArea.classList.remove("highlight");
}

dropArea.addEventListener("drop", handleDrop, false);

function handleDrop(e) {
  const dt = e.dataTransfer;
  const files = dt.files;

  if (files.length > 0 && files[0].type.startsWith("video/")) {
    handleFile(files[0]);
  } else {
    alert("Please drop a video file");
  }
}

// Select file button
selectFileButton.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    handleFile(e.target.files[0]);
  }
});

// Handle selected file
function handleFile(file) {
  if (!file.type.startsWith("video/")) {
    alert("Please select a video file");
    return;
  }

  selectedFile = file;
  dropArea.innerHTML = `
  <p>Selected file: <strong>${file.name}</strong> (${formatFileSize(
    file.size
  )})</p>
  <button id="change-file" class="btn btn-outline-secondary">Change File</button>
`;

  document.getElementById("change-file").addEventListener("click", () => {
    selectedFile = null;
    dropArea.innerHTML = `
    <p>Drag and drop video files here or click to select files</p>
    <button id="select-file" class="btn btn-outline-primary">Select Video File</button>
  `;
    document.getElementById("select-file").addEventListener("click", () => {
      fileInput.click();
    });
    uploadButton.disabled = true;
  });

  // Try to get video duration
  const videoEl = document.createElement("video");
  videoEl.preload = "metadata";
  videoEl.onloadedmetadata = () => {
    videoDuration.value = Math.round(videoEl.duration);
  };
  videoEl.src = URL.createObjectURL(file);

  // Enable upload button if terms are agreed
  checkUploadButtonState();
}

// Format file size
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " bytes";
  else if (bytes < 1048576) return (bytes / 1024).toFixed(2) + " KB";
  else if (bytes < 1073741824) return (bytes / 1048576).toFixed(2) + " MB";
  else return (bytes / 1073741824).toFixed(2) + " GB";
}

// Check terms agreement to enable upload button
agreeTerms.addEventListener("change", checkUploadButtonState);

function checkUploadButtonState() {
  uploadButton.disabled = !(selectedFile && agreeTerms.checked);
}

// Upload video form submit
videoForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!selectedFile) {
    alert("Please select a video file");
    return;
  }

  if (!agreeTerms.checked) {
    alert("Please agree to the terms");
    return;
  }

  try {
    // Disable form
    uploadButton.disabled = true;
    uploadButton.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';

    // Show progress bar
    uploadProgress.classList.remove("hidden");

    // Upload video to Firebase Storage
    const storageRef = ref(
      storage,
      `first_aid_videos/${Date.now()}_${selectedFile.name}`
    );
    const uploadTask = uploadBytesResumable(storageRef, selectedFile);

    // Monitor upload progress
    uploadTask.on(
      "state_changed",
      (snapshot) => {
        const progress =
          (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
        progressBar.style.width = progress + "%";
        progressBar.textContent = Math.round(progress) + "%";
      },
      (error) => {
        console.error("Upload error:", error);
        alert(`Upload failed: ${error.message}`);
        uploadButton.disabled = false;
        uploadButton.innerHTML = "Upload Video";
      },
      async () => {
        // Upload completed successfully
        try {
          // Get download URL
          const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);

          // Generate thumbnail if not provided
          let finalThumbnailUrl = thumbnailUrl.value;
          if (!finalThumbnailUrl) {
            // We'll just use a placeholder image based on the category
            const category = videoCategory.value;
            finalThumbnailUrl = `https://via.placeholder.com/320x180.png?text=${
              category.charAt(0).toUpperCase() + category.slice(1)
            }`;
          }

          // Save video metadata to Firestore
          const videoData = {
            title: videoTitle.value,
            description: videoDescription.value,
            videoUrl: downloadURL,
            thumbnailUrl: finalThumbnailUrl,
            category: videoCategory.value,
            duration: parseInt(videoDuration.value),
            created: serverTimestamp(),
            uploadedBy: currentUser.uid,
            uploaderName: currentUser.displayName,
          };

          await addDoc(collection(db, "aid_videos"), videoData);

          // Reset form
          videoForm.reset();
          selectedFile = null;
          dropArea.innerHTML = `
          <p>Drag and drop video files here or click to select files</p>
          <button id="select-file" class="btn btn-outline-primary">Select Video File</button>
        `;
          document
            .getElementById("select-file")
            .addEventListener("click", () => {
              fileInput.click();
            });

          // Hide progress bar
          uploadProgress.classList.add("hidden");

          // Enable upload button
          uploadButton.disabled = true;
          uploadButton.innerHTML = "Upload Video";

          // Show success message
          alert("Video uploaded successfully!");

          // Reload videos
          loadVideos(currentCategory);
        } catch (error) {
          console.error("Error saving video metadata:", error);
          alert(`Error saving video metadata: ${error.message}`);
          uploadButton.disabled = false;
          uploadButton.innerHTML = "Upload Video";
        }
      }
    );
  } catch (error) {
    console.error("Error uploading video:", error);
    alert(`Error uploading video: ${error.message}`);
    uploadButton.disabled = false;
    uploadButton.innerHTML = "Upload Video";
  }
});

// Load videos
async function loadVideos(category = "all") {
  try {
    videosContainer.innerHTML = `
    <div class="col-12 text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  `;

    // Get all videos or filter by category
    let q;
    if (category === "all") {
      q = query(collection(db, "aid_videos"), orderBy("created", "desc"));
    } else {
      q = query(
        collection(db, "aid_videos"),
        where("category", "==", category)
      );
    }

    const querySnapshot = await getDocs(q);

    if (querySnapshot.empty) {
      videosContainer.innerHTML = `
      <div class="col-12 text-center">
        <p class="text-muted">No videos found. Be the first to upload!</p>
      </div>
    `;
      return;
    }

    let videosHTML = "";
    querySnapshot.forEach((doc) => {
      const video = doc.data();
      video.id = doc.id;

      videosHTML += `
      <div class="col-md-4 mb-4">
        <div class="video-card">
          <img src="${video.thumbnailUrl}" alt="${
        video.title
      }" class="video-thumbnail">
          <h5>${video.title}</h5>
          <p class="text-muted small">${video.category} • ${formatDuration(
        video.duration
      )}</p>
          <div class="d-flex justify-content-between">
            <button class="btn btn-sm btn-primary view-video" data-url="${
              video.videoUrl
            }">
              <i class="bi bi-play-fill"></i> Play
            </button>
            <button class="btn btn-sm btn-danger delete-video" data-id="${
              video.id
            }" data-url="${video.videoUrl}">
              <i class="bi bi-trash"></i> Delete
            </button>
          </div>
        </div>
      </div>
    `;
    });

    videosContainer.innerHTML = videosHTML;

    // Add event listeners
    document.querySelectorAll(".view-video").forEach((button) => {
      button.addEventListener("click", () => {
        window.open(button.dataset.url, "_blank");
      });
    });

    document.querySelectorAll(".delete-video").forEach((button) => {
      button.addEventListener("click", () => {
        deleteVideo(button.dataset.id, button.dataset.url);
      });
    });
  } catch (error) {
    console.error("Error loading videos:", error);
    videosContainer.innerHTML = `
    <div class="col-12">
      <div class="alert alert-danger">Error loading videos. Please try again.</div>
    </div>
  `;
  }
}

// Format duration
function formatDuration(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
}

// Delete video
async function deleteVideo(id, url) {
  if (
    !confirm(
      "Are you sure you want to delete this video? This action cannot be undone."
    )
  ) {
    return;
  }

  try {
    // Delete from Firestore
    await deleteDoc(doc(db, "aid_videos", id));

    // Delete from Storage
    const fileRef = ref(storage, url);
    await deleteObject(fileRef).catch((error) => {
      console.warn("Could not delete file from storage:", error);
      // Continue even if file delete fails
    });

    // Reload videos
    loadVideos(currentCategory);

    alert("Video deleted successfully!");
  } catch (error) {
    console.error("Error deleting video:", error);
    alert(`Error deleting video: ${error.message}`);
  }
}

// Refresh videos button
refreshVideosButton.addEventListener("click", () => {
  loadVideos(currentCategory);
});
