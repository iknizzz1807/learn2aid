from google import genai

client = genai.Client(api_key="AIzaSyAn09nmpcku6PUyhRx8rXNU8YMscYYp1vY")

# Step 1: upload video and get the uri link
video_name = "cpr"

print("Uploading file...")
video_file = client.files.upload(file=video_name + ".mp4")
print(f"Completed upload: {video_file.uri}")

# Step 2: verify the API has successfully received the files by calling the files.get method
import time

# Check whether the file is ready to be used.
while video_file.state.name == "PROCESSING":
    print(".", end="")
    time.sleep(1)
    video_file = client.files.get(name=video_file.name)

if video_file.state.name == "FAILED":
    raise ValueError(video_file.state.name)

print("Done")

# Step 3: start prompting
from IPython.display import Markdown

# Pass the video file reference like any other media part.
response = client.models.generate_content(
    model="gemini-1.5-pro",
    contents=[
        video_file,
        "Rate this video's movement based on standard best CPR movement: how much point out of 100?"
        "Give some comments on the person' CPR movement.",
    ],
)

print(response.text)
