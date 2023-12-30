from flask import Flask, request, jsonify, render_template, send_file
from openai import OpenAI
import os
import uuid
from config import api_key


client = OpenAI(api_key=api_key)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/process_audio", methods=["POST"])
def process_audio():
    # try:
    audio_file = request.files["audio"]
    if audio_file:
        tmp_filename = str(uuid.uuid4().hex)
        audio_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{tmp_filename}.wav")
        audio_file.save(audio_path)

        audio_file = open(audio_path, "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, language="en"
        )
        print(transcript)
        user_input = transcript.text
        print(user_input)
        prompt = f"You are a here to answer all of my questions:{user_input}"

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant.Your name is Jarvis. You are a Montclair State University's newest AI. You know everything about the university. And you are reporting to your professor. And the professor is a male. End every sentence with Professor Jenq.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        response = completion.choices[0].message.content
        print(response)

        tmp_filename = str(uuid.uuid4().hex)
        processed_audio_path = os.path.join(
            app.config["UPLOAD_FOLDER"], f"{tmp_filename}.wav"
        )

        audio_response = client.audio.speech.create(
            model="tts-1", voice="alloy", input=response
        )

        audio_response.stream_to_file(processed_audio_path)

        # Return the processed audio
        return send_file(processed_audio_path, as_attachment=True)


if __name__ == "__main__":
    # app.run(debug=False, host="0.0.0.0")
    app.run(debug=True)
