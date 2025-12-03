import requests
import os

def get_chatbot_response(messages):
    """
    Send system + user messages to RunPod endpoint and return raw output.
    Works for structured JSON tasks.
    """
    # Concatenate all messages (system + user)
    prompt = ""
    for message in messages:
        prompt += message.get("content", "") + "\n"
    
    payload = {"input": {"prompt": prompt}}
    
    RUNPOD_ENDPOINT = os.getenv("RUNPOD_ENDPOINT")
    TOKEN = os.getenv("RUNPOD_TOKEN")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    
    url = f"{RUNPOD_ENDPOINT}/runsync"
    
    response = requests.post(url, json=payload, headers=headers, timeout=180)
    
    try:
        # Return raw text — do NOT post-process
        output_text = response.json()["output"][0]["choices"][0]["tokens"][0].strip()
    except (KeyError, IndexError):
        output_text = str(response.json())
    
    return output_text


def get_embedding(embedding_client,model_name,text_input):
    output = embedding_client.embeddings.create(input = text_input,model=model_name)
    
    embedings = []
    for embedding_object in output.data:
        embedings.append(embedding_object.embedding)

    return embedings