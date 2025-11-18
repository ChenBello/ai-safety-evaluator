from PIL import Image
import torch
from transformers import AutoFeatureExtractor, AutoModelForImageClassification, CLIPProcessor, CLIPModel

# --- Emotion Detection Model ---
model_name = "tahayf/vit-base-patch16-224_ferplus"
extractor = AutoFeatureExtractor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)

# Map raw model labels to real emotion names
labels_mapping = {
    "LABEL_0": "neutral",
    "LABEL_1": "happy",
    "LABEL_2": "surprised",
    "LABEL_3": "sad",
    "LABEL_4": "angry",
    "LABEL_5": "disgust",
    "LABEL_6": "fear",
    "LABEL_7": "contempt"
}

descriptions = {
    "neutral": "Neutral, without strong emotions.",
    "happy": "Positive emotions, joy or comfort.",
    "surprised": "Surprise or unexpectedness.",
    "sad": "Sadness or a somber mood.",
    "angry": "Anger or frustration.",
    "disgust": "Disgust or dislike.",
    "fear": "Fear or concern.",
    "contempt": "Feeling of disdain or disrespect."
}

def analyze_emotion(image: Image.Image):
    inputs = extractor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    raw_labels = model.config.id2label
    result = {labels_mapping.get(raw_labels[i], raw_labels[i]): float(probs[0][i]) for i in range(len(raw_labels))}

    top_label, top_prob = max(result.items(), key=lambda x: x[1])
    explanation = descriptions.get(top_label, "Emotion not recognized.")
    return result, top_label, top_prob, explanation

# --- Safety / Content Risk Detection (CLIP zero-shot) ---
clip_model_name = "openai/clip-vit-base-patch32"
clip_model = CLIPModel.from_pretrained(clip_model_name)
clip_processor = CLIPProcessor.from_pretrained(clip_model_name)
risk_labels = ["safe", "violent", "sexual", "graphic", "neutral"]

def analyze_risk(image: Image.Image):
    inputs = clip_processor(text=risk_labels, images=image, return_tensors="pt", padding=True)
    outputs = clip_model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits_per_image, dim=1)
    result = {label: float(prob) for label, prob in zip(risk_labels, probs[0])}

    top_label, top_prob = max(result.items(), key=lambda x: x[1])
    explanations = {
        "safe": "The image appears safe for general viewing.",
        "violent": "The image may contain violent content.",
        "sexual": "The image may contain sexual content.",
        "graphic": "The image may contain graphic or disturbing content.",
        "neutral": "No significant risk detected."
    }
    explanation = explanations.get(top_label, "Risk not recognized.")
    return result, top_label, top_prob, explanation

# --- Combined Analysis ---
def analyze_image_combined(image: Image.Image):
    emotion_result, emotion_label, emotion_prob, emotion_desc = analyze_emotion(image)
    risk_result, risk_label, risk_prob, risk_desc = analyze_risk(image)

    return {
        "emotion": {
            "result": emotion_result,
            "top_label": emotion_label,
            "top_prob": emotion_prob,
            "description": emotion_desc
        },
        "risk": {
            "result": risk_result,
            "top_label": risk_label,
            "top_prob": risk_prob,
            "description": risk_desc
        }
    }

# from openai import OpenAI
#
# client = OpenAI(api_key="OPENAI_API_KEY")
#
# def analyze_image_for_risk(image_b64):
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "input_image", "image": image_b64},
#                     {"type": "text", "text": "Analyze the emotional and safety risk in this image"}
#                 ]
#             }
#         ]
#     )
#
#     return response.choices[0].message["content"]
