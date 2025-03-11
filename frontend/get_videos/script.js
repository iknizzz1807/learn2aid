// Fetch videos from backend API
async function fetchVideos() {
  try {
    const response = await fetch("http://localhost:8080/api/v1/videos");
    const videos = await response.json();
    displayVideos(videos);
  } catch (error) {
    console.error("Error fetching videos:", error);
  }
}

// Display videos in grid
function displayVideos(videos) {
  const grid = document.getElementById("video-grid");
  grid.innerHTML = "";

  videos.forEach((video) => {
    const card = document.createElement("div");
    card.className = "video-card";
    card.innerHTML = `
      <img src="${video.thumbnailUrl}" alt="${
      video.title
    }" class="video-thumbnail">
      <div class="video-info">
        <h3 class="video-title">${video.title}</h3>
        <p class="video-description">${video.description.slice(0, 60)}...</p>
      </div>
    `;

    card.addEventListener("click", () => playVideo(video));
    grid.appendChild(card);
  });
}

// Play selected video
function playVideo(video) {
  const player = document.getElementById("video-player");
  const videoElement = document.getElementById("video-element");
  const videoTitle = document.getElementById("current-video-title");
  const videoDescription = document.getElementById("current-video-description");

  videoTitle.textContent = video.title;
  videoDescription.textContent = video.description;
  videoElement.src = video.videoUrl;

  player.style.display = "block";
  videoElement.play();
}

// Initialize
fetchVideos();
