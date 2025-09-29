import os
import uuid
import subprocess
import requests
import shutil
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


class PromptRequest(BaseModel):
    prompt: str

# Set OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

app.mount("/media", StaticFiles(directory="media"), name="media")

@app.post("/api/generate-animation")
async def generate_animation(data: PromptRequest):
    prompt = data.prompt

    try:
        print("OPENROUTER_API_KEY:", OPENROUTER_API_KEY[:8] + "..." if OPENROUTER_API_KEY else "MISSING")

        # Step 1: Generate Python code using OpenRouter
        system_prompt = (
            "You are a Python expert specialized in Manim animation. Given a user prompt, "
            "return valid Manim Community v0.18.0 code that creates an animation as described. "
            "Do not include markdown or explanations—only the Python code."
        )

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "x-ai/grok-4-fast:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        try:
            response.raise_for_status()
            json_response = response.json()
            print("OpenRouter response:", json_response)
            manim_code = json_response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print("OpenRouter API error:", e)
            return JSONResponse({"error": f"OpenRouter API error: {str(e)}"}, status_code=500)

        # Remove markdown or any unwanted characters
        if manim_code.startswith("```python"):
            manim_code = manim_code.replace("```python", "").replace("```", "").strip()


        # Step 2: Write code to file
        unique_id = str(uuid.uuid4())
        script_path = f"temp_{unique_id}.py"
        with open(script_path, "w") as f:
            f.write(manim_code)

        # Step 3: Run Manim to render the animation
        output_file = f"{unique_id}.mp4"
        

        subprocess.run([
            "manim", "-ql", script_path, "-o", output_file
        ], check=True)

        videoURL = f"/media/videos/temp_{unique_id}/480p15/{output_file}"
        
        # Step 5: Cleanup script
        os.remove(script_path)

        # Return the URL to access the video
        return JSONResponse({"videoUrl": videoURL})


    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


