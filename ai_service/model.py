from google import genai
import json
import time
import os


class GeminiModel:
    def __init__(self, api_key=None):
        self.api_key = (
            api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
        )
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-1.5-flash-002"

        # Define prompts for different movement types
        self.movement_prompts = {
            "cpr": """
            You are a medical AI trained to evaluate first aid technique performance in videos.
            Your task is to analyze a user's Adult CPR demonstration video step-by-step using Chain of Thought reasoning, compare each aspect against international first aid guidelines, and score each criterion accordingly.
            Evaluate the following categories in sequence, and assign a score (with reasoning) to each sub-criterion based on the video.
            Focus on chest compressions, rescue breaths, and cycle coordination.
            Then output ONLY a valid JSON object — no explanation, no commentary. Make sure the output is strictly valid JSON format that can be parsed by any JSON parser.

            Categories and sub-criteria:

            1. Chest Compressions (Total – 60 points)
              (CoT 1a) Rescuer Positioning – Kneels beside the casualty's chest. (0–5 points)
              (CoT 1b) Hand Placement – Places the heel of one hand on the center of the chest (lower half of the sternum), with the heel of the other hand on top. (0–15 points)
              (CoT 1c) Finger Interlocking & Position – Interlocks fingers and ensures they are kept off the casualty's chest/ribs. (0–5 points)
              (CoT 1d) Body Mechanics & Arm Position – Leans directly over the casualty's chest with arms straight (elbows locked), using body weight for compressions. (0–10 points)
              (CoT 1e) Compression Depth – Compresses the chest to a depth of 5 to 6 cm. (0–15 points)
              (CoT 1f) Chest Recoil – Allows the chest to fully recoil between compressions without losing hand contact. (0–5 points)
              (CoT 1g) Compression Rate – Delivers compressions at a rate of 100–120 per minute. (0–5 points)

            2. Rescue Breaths (Total – 30 points)
              *Note: Score 0 if not performed; section may be marked N/A for compression-only CPR.*
              (CoT 2a) Open Airway – Performs the head-tilt/chin-lift maneuver after 30 compressions. (0–10 points)
              (CoT 2b) Nose Pinch – Pinches the casualty's nose closed before delivering breaths. (0–5 points)
              (CoT 2c) Mouth Seal – Creates a proper seal over the casualty's mouth. (0–5 points)
              (CoT 2d) Breath Delivery & Chest Rise – Delivers breaths resulting in visible chest rise. (0–10 points)

            3. Cycle Coordination & Efficiency (Total – 10 points)
              (CoT 3a) Correct Cycle Ratio – Performs 30 compressions followed by 2 breaths (if applicable). (0–5 points)
              (CoT 3b) Minimize Interruptions – Keeps transitions quick and efficient. (0–5 points)

            Output ONLY this format as valid JSON:
            {{
              "total_point": <total_score>,
              "detailed_summary": {{
                "score_breakdown": {{
                  "Chest Compressions": "<x>/60",
                  "Rescue Breaths": "<x>/30",
                  "Cycle Coordination & Efficiency": "<x>/10"
                }},
                "strengths": [
                  // list of well-performed areas with reasoning
                ],
                "areas_for_improvement": [
                  // list of specific feedback points or missing/incorrect actions
                ]
              }}
            }}
            """,
            "heimlich": """
            You are a medical AI trained to evaluate Heimlich maneuver performance in videos.
            Your task is to analyze a user's Heimlich technique demonstration video step-by-step using Chain of Thought reasoning, compare each aspect against international first aid guidelines for choking response, and score each criterion accordingly.
            Evaluate the following categories in sequence, and assign a score (with reasoning) to each sub-criterion based on the video.
            Focus on the practical technique of the Heimlich maneuver — including back blows, abdominal thrusts, and correct cycle management.
            Then output ONLY a valid JSON object — no explanation, no commentary. Make sure the output is strictly valid JSON format that can be parsed by any JSON parser.

            Categories and sub-criteria:

            1. Back Blow Technique ("Slap it out") (Total: 45 points)
              (CoT 1a) Casualty Positioning — Rescuer supports the casualty's chest with one hand and leans the casualty sufficiently forward. (0–15 points)
              (CoT 1b) Rescuer Stance — Stands to the side and slightly behind the casualty. (0–5 points)
              (CoT 1c) Hand Placement & Target Area — Uses the heel of the hand to strike the area between the casualty's shoulder blades. (0–15 points)
              (CoT 1d) Blow Delivery — Delivers sharp, distinct back blows (up to 5). (0–10 points)

            2. Abdominal Thrust Technique ("Squeeze it out") (Total: 45 points)
              (CoT 2a) Rescuer Stance — Stands behind the casualty. (0–5 points)
              (CoT 2b) Arm Placement — Places both arms around the casualty's upper abdomen/waist. (0–10 points)
              (CoT 2c) Hand Placement & Grip — Clenches one fist and places it between the navel (belly button) and the bottom of the sternum (breastbone). Grasps the fist firmly with the other hand. (0–15 points)
              (CoT 2d) Thrust Action & Direction — Pulls sharply inwards and upwards with distinct thrusts (up to 5 times). (0–15 points)

            3. Cycle Management & Technique Transition (Total: 10 points)
              (CoT 3a) Correct Cycle Execution — Continuously alternates between up to 5 back blows and up to 5 abdominal thrusts until the obstruction is cleared (or as per scenario). (0–5 points)
              (CoT 3b) Brief Mouth Check — Performs a quick visual check inside the casualty's mouth after each set of back blows AND each set of abdominal thrusts to look for the obstruction. (0–5 points)

            Output ONLY this format as valid JSON:
            {{
              "total_point": <total_score>,
              "detailed_summary": {{
                "score_breakdown": {{
                  "Back Blow Technique": "<x>/45",
                  "Abdominal Thrust Technique": "<x>/45",
                  "Cycle Management & Technique Transition": "<x>/10"
                }},
                "strengths": [
                  // list of well-performed areas with reasoning
                ],
                "areas_for_improvement": [
                  // list of specific feedback points or missing/incorrect actions
                ]
              }}
            }}
            """,
            "recovery": """
            You are a medical AI trained to evaluate Recovery Position technique performance in videos.
            Your task is to analyze a user's demonstration of the Recovery Position step-by-step using Chain of Thought reasoning, compare each aspect against international first aid guidelines, and score each criterion accordingly.
            Evaluate the following categories in sequence, and assign a score (with reasoning) to each sub-criterion based on the video.
            Focus on the practical technique of the Recovery Position — including initial limb setup, rolling motion, and airway maintenance.
            Then output ONLY a valid JSON object — no explanation, no commentary. Make sure the output is strictly valid JSON format that can be parsed by any JSON parser.

            Categories and sub-criteria:

            1. Initial Setup & Limb Positioning (Total - 40 points)
              (CoT 1a) Rescuer Position - Kneels correctly beside the casualty. (0–5 points)
              (CoT 1b) Casualty Leg Check - Ensures both casualty's legs are initially straight. (0–5 points)
              (CoT 1c) Near Arm Placement - Places the casualty's near arm at a right angle, elbow bent, palm up. (0–15 points)
              (CoT 1d) Far Arm Placement - Brings far arm across chest, back of hand against cheek, holds in place. (0–15 points)

            2. Rolling the Casualty (Total - 35 points)
              (CoT 2a) Far Leg Preparation - Bends the casualty's far knee, foot flat on the floor. (0–10 points)
              (CoT 2b) Rolling Technique - Maintains hand against cheek while pulling on knee to roll casualty smoothly. (0–25 points)

            3. Final Adjustments & Airway Maintenance (Total - 25 points)
              (CoT 3a) Top Leg Position - Adjusts top leg to rest in a stable L-shape. (0–10 points)
              (CoT 3b) Head Tilt & Airway - Performs slight head tilt to ensure airway is open. (0–10 points)
              (CoT 3c) Final Hand/Cheek Check - Confirms hand position supports head and airway. (0–5 points)

            Output ONLY this format as valid JSON:
            {{
              "total_point": <total_score>,
              "detailed_summary": {{
                "score_breakdown": {{
                  "Initial Setup & Limb Positioning": "<x>/40",
                  "Rolling the Casualty": "<x>/35",
                  "Final Adjustments & Airway Maintenance": "<x>/25"
                }},
                "strengths": [
                  // list of well-performed areas with reasoning
                ],
                "areas_for_improvement": [
                  // list of specific feedback points or missing/incorrect actions
                ]
              }}
            }}
            """,
            "nosebleed": """
            You are a medical AI trained to evaluate first aid technique performance in videos.
            Your task is to analyze a user's Nosebleed First Aid demonstration video step-by-step using Chain of Thought reasoning, compare each aspect against international first aid guidelines, and score each criterion accordingly.
            Evaluate the following categories in sequence, and assign a score (with reasoning) to each sub-criterion based on the video.
            Focus on casualty positioning, bleeding control, and follow-up management. 
            Then output ONLY a valid JSON object — no explanation, no commentary. Make sure the output is strictly valid JSON format that can be parsed by any JSON parser.

            Categories and sub-criteria:

            1. Casualty Positioning & Airway Management (Total - 45 points)
              (CoT 1a) Initial Positioning - Sitting - Ensures the casualty is sitting down, not lying down. (0–15 points)
              (CoT 1b) Correct Posture - Leaning Forward - Ensures the casualty leans their head and upper body forward. (0–20 points)
              (CoT 1c) Breathing Instruction - Instructs the casualty to breathe through their mouth. (0–10 points)

            2. Bleeding Control Technique (Total - 40 points)
              (CoT 2a) Hand Placement - Pinching Soft Part - Correctly identifies and pinches the soft part of the nose. (0–25 points)
              (CoT 2b) Application of Pressure - Continuous - Maintains firm and continuous pressure without releasing. (0–15 points)

            3. Management, Duration & Assessment (Total - 15 points)
              (CoT 3a) Duration - Initial Hold - Maintains pressure for 10 minutes. (0–5 points)
              (CoT 3b) Assessment - Releasing Pressure - Releases after 10 minutes to assess bleeding. (0–5 points)
              (CoT 3c) Reapplication If Necessary - Reapplies correct technique if bleeding continues. (0–5 points)

            Output ONLY this format as valid JSON:
            {{
              "total_point": <total_score>,
              "detailed_summary": {{
                "score_breakdown": {{
                  "Casualty Positioning & Airway Management": "<x>/45",
                  "Bleeding Control Technique": "<x>/40",
                  "Management, Duration & Assessment": "<x>/15"
                }},
                "strengths": [
                  // list of well-executed actions with reasoning
                ],
                "areas_for_improvement": [
                  // list of specific feedback points or missing/incorrect actions
                ]
              }}
            }}
            """,
            "shock": """
            You are a medical AI trained to evaluate first aid technique performance in videos.
            Your task is to analyze a user's Shock First Aid demonstration video step-by-step using Chain of Thought reasoning, compare each aspect against international first aid guidelines, and score each criterion accordingly.
            Evaluate the following categories in sequence, and assign a score (with reasoning) to each sub-criterion based on the video.
            Focus on casualty positioning, limb elevation, clothing adjustment, and warmth provision.
            Then output ONLY a valid JSON object — no explanation, no commentary. Make sure the output is strictly valid JSON format that can be parsed by any JSON parser.

            Categories and sub-criteria:

            1. Casualty Positioning (Total - 65 points)
              (CoT 1a) Lie Casualty Down - Assists casualty into a flat, supine position. (0–20 points)
              (CoT 1b) Use Underlying Insulation - Ensures casualty is on an insulating layer (blanket, mat, etc). (0–5 points)
              (CoT 1c) Elevate Legs Correctly - Raises both legs above heart level using stable support. (0–40 points)

            2. Casualty Care (Demonstrated Actions) (Total - 35 points)
              (CoT 2a) Loosen Tight Clothing - Loosens clothing at neck, chest, and waist. (0–15 points)
              (CoT 2b) Provide Warmth (Covering) - Covers casualty with blanket/coat to preserve body heat. (0–20 points)

            Output ONLY this format as valid JSON:
            {{
              "total_point": <total_score>,
              "detailed_summary": {{
                "score_breakdown": {{
                  "Casualty Positioning": "<x>/65",
                  "Casualty Care": "<x>/35"
                }},
                "strengths": [
                  // list of well-executed actions with reasoning
                ],
                "areas_for_improvement": [
                  // list of specific feedback points or missing/incorrect actions
                ]
              }}
            }}
            """,
            # Default prompt for other movements
            "default": """
            You are a medical AI trained to evaluate first aid technique performance in videos.
            Your task is to analyze the demonstrated {movement_name} technique in this video against best practice standards.

            Evaluate the movement critically, considering:
            - Correct body positioning and alignment
            - Proper technique execution
            - Effectiveness of the movement
            - Safety considerations

            Score the performance on a scale of 0-100, where 100 represents perfect execution according to first aid guidelines.

            IMPORTANT: Respond ONLY in JSON format like this example:
            {{
                "total_point": 85,
                "detailed_summary": {{
                    "comment": "The movement was generally well-executed",
                    "strengths": ["Good body positioning", "Proper hand placement", "Effective pressure application"],
                    "areas_for_improvement": ["Could improve timing", "Ensure consistent technique throughout"]
                }}
            }}
            """,
        }

    def _get_movement_type(self, movement_name):
        """
        Identify movement type from the movement name.
        """
        movement_name = movement_name.lower()
        if "cpr" in movement_name:
            return "cpr"
        elif "heimlich" in movement_name:
            return "heimlich"
        elif "recovery" in movement_name:
            return "recovery"
        elif "nosebleed" in movement_name:
            return "nosebleed"
        elif "shock" in movement_name:
            return "shock"
        else:
            return "default"

    def predict(self, video_file, movement_name="exercise"):
        """
        Process video with Gemini API and return assessment based on movement type
        """
        try:
            # Get the prompt template based on movement type
            movement_type = self._get_movement_type(movement_name)
            prompt_template = self.movement_prompts.get(
                movement_type, self.movement_prompts["default"]
            )

            # Format the prompt with movement name
            prompt = prompt_template.format(movement_name=movement_name)

            # Check if we're using a URI path or a file
            if isinstance(video_file, str) and os.path.exists(video_file):
                # Process file upload path
                print(f"Uploading file: {video_file}")
                with open(video_file, "rb") as f:
                    uploaded_file = self.client.files.upload(
                        file=f, config={"mime_type": "video/mp4"}
                    )
            else:
                # Handle case where video_file is already a file object
                uploaded_file = self.client.files.upload(
                    file=video_file, config={"mime_type": "video/mp4"}
                )

            # Wait for processing
            gemini_file = self.client.files.get(name=uploaded_file.name)

            print("Processing video...", end="")
            while gemini_file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(1)
                gemini_file = self.client.files.get(name=gemini_file.name)
            print(" Done!")

            if gemini_file.state.name == "FAILED":
                return {
                    "error": "Video processing failed",
                    "details": gemini_file.state.name,
                }

            # Generate content with Gemini
            model = (
                "gemini-1.5-flash-002"
                if movement_type == "default"
                else "gemini-1.5-flash-002"
            )
            response = self.client.models.generate_content(
                model=model,
                contents=[gemini_file, prompt],
            )

            # Parse the response
            json_text = response.text.strip()

            # Extract JSON from the response
            json_start_index = -1
            json_end_index = -1

            code_block_start = json_text.find("```json")
            if code_block_start != -1:
                json_start_index = code_block_start + 7
                code_block_end = json_text.find("```", json_start_index)
                if code_block_end != -1:
                    json_end_index = code_block_end
            else:
                json_start_index = json_text.find("{")
                if json_start_index != -1:
                    json_end_index = json_text.rfind("}") + 1

            if (
                json_start_index != -1
                and json_end_index != -1
                and json_start_index < json_end_index
            ):
                json_data = json.loads(
                    json_text[json_start_index:json_end_index].strip()
                )
                return json_data
            else:
                return {
                    "error": "Could not parse JSON response",
                    "raw_response": json_text,
                }

        except Exception as e:
            return {"error": str(e)}

    def save_video_uri(self, video_path, uri_file_path=None):
        """
        Upload video and save URI to a file
        """
        try:
            if uri_file_path is None:
                uri_file_path = os.path.splitext(video_path)[0] + ".txt"

            # Check if URI file exists
            if os.path.exists(uri_file_path):
                with open(uri_file_path, "r") as f:
                    video_uri = f.read().strip()
                print(f"Using existing video URI: {video_uri}")
                return self.client.files.get(name=video_uri)

            # Upload new file
            print(f"Uploading file: {video_path}")
            with open(video_path, "rb") as f:
                video_file = self.client.files.upload(file=f)

            print(f"Completed upload: {video_file.uri}")

            # Save URI to file
            with open(uri_file_path, "w") as f:
                f.write(video_file.uri)

            print(f"URI saved to {uri_file_path}")
            return video_file

        except Exception as e:
            print(f"Error saving video URI: {str(e)}")
            return None


# Initialize model
model = GeminiModel()
