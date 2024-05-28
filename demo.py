from flask import request, jsonify, send_file, render_template, Flask
from utils.text_processing import replace_numbers_with_words
from utils.data_extraction import *
from utils.audio_generation import generate_audio_2
import json
import os
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, util
from collections import deque
from flask_cors import CORS
import base64



app = Flask(__name__)
cors = CORS(app, origins="*")

client = MongoClient(
    "mongodb+srv://nisujadhav657:bc5adVc5Btc5qfz4@hostinguser.kc0uvjw.mongodb.net/"
)
db = client["Health_Insurance"]

empty_responses = deque(maxlen=3)

model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

USER_FOLDER = os.path.join(os.path.dirname(__file__), "User_Json")
WAV_FOLDER = os.path.join(os.path.dirname(__file__), "wavFiles")
Call_Recording_FOLDER = os.path.join(os.path.dirname(__file__), "CallRecord_Json")


@app.route("/health-insurance", methods=["POST"])
def health_insurance():
    data = request.json
    action = data.get("action")

    if action == "send_audio":
        text = "Hello What is your name?"
        responsefilename = "response.wav"
        wav_path = os.path.join(WAV_FOLDER, responsefilename)
        generate_audio_2(text, wav_path)

        with open(wav_path, "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")

        return jsonify({"filename": responsefilename, "audio_data": audio_data})
    
    elif action == "receive_response":
        response = data.get("response")

        print("Response", response)

        text = f"Hello {response} nice to meet you"
        responsefilename = "second.wav"
        wav_path = os.path.join(WAV_FOLDER, responsefilename)
        generate_audio_2(text, wav_path)

        with open(wav_path, "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")

        return jsonify({"filename": responsefilename, "audio_data": audio_data})

    else:
        # Return a response for invalid action
        return jsonify({"error": "Invalid action."}), 400


@app.route("/callUser", methods=["POST"])
def callUser():
    data = request.json
    dataset_collection = db["calling_questions"]
    dataset = list(dataset_collection.find())
    voice = data.get("voice")
    action = data.get("action")
    conversation = []
    guid = request.headers.get("X-GUID")
    fileName = f"user_enquiry_{guid}.json"
    username = "thanos"
    tag = data.get("tag")
    global consecutive_negative_responses
    
    print('tag',tag)

    if action == "send_call_audio":
        text = f"Hello {username}.my name is titan, and I'm calling from Health Insurance system. How are you today?"

        newText = replace_numbers_with_words(text)

        responsefilename = "response.wav"
        wav_path = os.path.join(WAV_FOLDER, responsefilename)

        generate_audio_2(newText, wav_path)

        with open(wav_path, "rb") as f:
            audio_data = base64.b64encode(f.read()).decode("utf-8")

        return jsonify({"filename": responsefilename, "audio_data": audio_data})

    elif action == "recieve_call_response":
        user_response = data.get("response")

        negative_keywords = [
            "not interested",
            "don't want",
            "don't have time",
            "don't need",
            "don't",
        ]

        print("User Response", user_response)
        if any(keyword in user_response for keyword in negative_keywords):
            consecutive_negative_responses += 1
        else:
            consecutive_negative_responses = 0

        print("Negative Count", consecutive_negative_responses)
        print("Negative Count Condition ", consecutive_negative_responses >= 4)

        if not user_response.strip():
            empty_responses.append(user_response)

            if len(empty_responses) == 3 and all(
                not response.strip() for response in empty_responses
            ):
                text = "It seems we're having trouble with the connection.I will call you latter. Goodbye!"

                newText = replace_numbers_with_words(text)

                terminate_filename = "terminate.wav"

                wav_path = os.path.join(WAV_FOLDER, terminate_filename)

                generate_audio_2(newText, wav_path)

                with open(wav_path, "rb") as f:
                    audio_data = base64.b64encode(f.read()).decode("utf-8")

                return jsonify(
                    {"filename": terminate_filename, "audio_data": audio_data}
                )

            else:
                text = f"I couldn't hear you. Are you there {username}?"

                newText = replace_numbers_with_words(text)

                responsefilename = "response.wav"
                wav_path = os.path.join(WAV_FOLDER, responsefilename)

                generate_audio_2(newText, wav_path)

                with open(wav_path, "rb") as f:
                    audio_data = base64.b64encode(f.read()).decode("utf-8")

                return jsonify({"filename": responsefilename, "audio_data": audio_data})

        elif consecutive_negative_responses >= 4:

            text = f"Okay {username}. Thank you for your time. Have a great day!"

            newText = replace_numbers_with_words(text)

            terminate_filename = "terminate.wav"

            wav_path = os.path.join(WAV_FOLDER, terminate_filename)

            generate_audio_2(newText, wav_path)

            with open(wav_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")

            return jsonify({"filename": terminate_filename, "audio_data": audio_data})

        elif "schedule my call" in user_response and tag == None:
            text = "Of course, I'd be happy to schedule the call for you. Could you please let me know what time works best for you?"

            newText = replace_numbers_with_words(text)

            responsefilename = "response.wav"

            wav_path = os.path.join(WAV_FOLDER, responsefilename)

            generate_audio_2(newText, wav_path)

            with open(wav_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")

            return jsonify(
                {
                    "filename": responsefilename,
                    "audio_data": audio_data,
                    "tag": "schedule",
                }
            )
        elif tag == "schedule":
            schedule_time = extract_date_time(user_response)
            if schedule_time:
                text = f"Excellent! I've scheduled the call for {schedule_time} to discuss your health insurance plan. Thank you for your time. Have a great day {username}."
                responsefilename = "schedule.wav"

                wav_path = os.path.join(WAV_FOLDER, responsefilename)
                
                newText = replace_numbers_with_words(text)

                generate_audio_2(newText, wav_path)

                with open(wav_path, "rb") as f:
                    audio_data = base64.b64encode(f.read()).decode("utf-8")

                return jsonify({"filename": responsefilename, "audio_data": audio_data})
            else:
                text = "Can you please provide me valid date and time so i can easily schedule your call."

                newText = replace_numbers_with_words(text)

                responsefilename = "response.wav"

                wav_path = os.path.join(WAV_FOLDER, responsefilename)

                generate_audio_2(newText, wav_path)

                with open(wav_path, "rb") as f:
                    audio_data = base64.b64encode(f.read()).decode("utf-8")

                return jsonify({"filename": responsefilename, "audio_data": audio_data})

        else:
            empty_responses.clear()

            conversation.append({"user": user_response})

            user_question_embeding = model.encode(user_response, convert_to_tensor=True)
            similarities = []

            for data in dataset:
                dataset_question_embedding = model.encode(
                    data["user"], convert_to_tensor=True
                )
                similarity_score = util.pytorch_cos_sim(
                    user_question_embeding, dataset_question_embedding
                )
                similarities.append(similarity_score)
            most_similar_index = similarities.index(max(similarities))

            if similarities[most_similar_index] < 0.3:
                text = "I couldn't hear you properly. Can you please say that again?"

            else:
                answer = dataset[most_similar_index]["ai"]
                if user_response.lower() != dataset[most_similar_index]["user"].lower():
                    newdata = {"user": user_response, "ai": answer}
                    dataset_collection.insert_one(newdata)
                text = answer

            conversation.append({"AI": text})

            with open(os.path.join(Call_Recording_FOLDER, fileName), "w") as f:
                json.dump(conversation, f)

            newText = replace_numbers_with_words(text)

            responsefilename = "response.wav"

            wav_path = os.path.join(WAV_FOLDER, responsefilename)

            generate_audio_2(newText, wav_path)

            with open(wav_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")

            return jsonify({"filename": responsefilename, "audio_data": audio_data})


if __name__ == "__main__":
    app.run(debug=True)
