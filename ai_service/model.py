from google import genai
import json
import time
import os


class GeminiModel:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-1.5-pro"

    def predict(self, video_file, movement_name="exercise"):
        """
        Process video with Gemini API and return assessment
        """
        try:
            # Upload file to Gemini
            uploaded_file = self.client.files.upload(file=video_file)

            # Wait for processing
            gemini_file = self.client.files.get(name=uploaded_file.name)
            while gemini_file.state.name == "PROCESSING":
                time.sleep(1)
                gemini_file = self.client.files.get(name=gemini_file.name)

            if gemini_file.state.name == "FAILED":
                return {
                    "error": "Video processing failed",
                    "details": gemini_file.state.name,
                }

            # Generate content with Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    gemini_file,
                    f"""
                    This video is about {movement_name} movement, rate this video point out of 100, ?/100
                    "Comment" on this movement. Comment is in general about the movement,
                    "Detail" is rating in detailed about the good and bad part of the movement things to improve why the score is ?/100 
                    IMPORTANT: Respond ONLY in JSON format like this example:
                    {{
                        "point": 85,
                        "comment": "The movement is very good!",
                        "detail": "Detailed stuffs"
                    }}
                    """,
                ],
            )

            # Parse the response
            json_text = response.text.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]

            json_data = json.loads(json_text.strip())
            return json_data

        except Exception as e:
            return {"error": str(e)}


# Initialize model
model = GeminiModel()
