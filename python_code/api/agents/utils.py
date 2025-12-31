import requests
import os
import time
import threading
from queue import Queue, Empty
from dotenv import load_dotenv

load_dotenv()

def get_chatbot_response(messages, max_retries=3, timeout=180):
    """
    Send system + user messages to RunPod endpoint and return raw output.
    """
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
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting API call (attempt {attempt + 1}/{max_retries})...")
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            
            # Debug: print status code and raw response
            print(f"Response status: {response.status_code}")
            
            # Check if response is valid
            if response.status_code != 200:
                print(f"❌ Bad status code: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
                raise requests.exceptions.RequestException(f"Status {response.status_code}")
            
            # Try to parse JSON
            try:
                response_json = response.json()
                print(f"Response JSON keys: {response_json.keys()}")
            except Exception as e:
                print(f"❌ Failed to parse JSON: {e}")
                print(f"Raw response text: {response.text[:500]}")
                raise
            
            # Try multiple possible response formats
            try:
                # Original format
                output_text = response_json["output"][0]["choices"][0]["tokens"][0].strip()
                return output_text
            except (KeyError, IndexError, TypeError):
                pass
            
            try:
                # Alternative format 1: output.text
                output_text = response_json["output"]["text"]
                return output_text.strip()
            except (KeyError, TypeError):
                pass
            
            try:
                # Alternative format 2: output as string
                output_text = response_json["output"]
                if isinstance(output_text, str):
                    return output_text.strip()
            except (KeyError, TypeError):
                pass
            
            try:
                # Alternative format 3: choices format (OpenAI style)
                output_text = response_json["choices"][0]["message"]["content"]
                return output_text.strip()
            except (KeyError, IndexError, TypeError):
                pass
            
            try:
                # Alternative format 4: direct output list
                if isinstance(response_json["output"], list):
                    output_text = response_json["output"][0]
                    if isinstance(output_text, str):
                        return output_text.strip()
            except (KeyError, IndexError, TypeError):
                pass
            
            # If we got here, none of the formats worked
            print(f"⚠️ Unknown response format. Full response: {response_json}")
            return "Sorry, I received an unexpected response format."
            
        except requests.exceptions.ReadTimeout:
            print(f"⏱️ Request timed out after {timeout} seconds")
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return "I apologize, but I'm experiencing technical difficulties right now."
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {e}")
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return "I apologize, but I'm having trouble connecting to the service."
    
    return "I apologize, but I'm experiencing technical difficulties."


def run_with_timeout(func, args=(), kwargs=None, timeout=30):
    """
    Run a function with a timeout using threading (works on Windows).
    Returns (success, result) tuple.
    """
    if kwargs is None:
        kwargs = {}
    
    result_queue = Queue()
    exception_queue = Queue()
    
    def worker():
        try:
            result = func(*args, **kwargs)
            result_queue.put(result)
        except Exception as e:
            exception_queue.put(e)
    
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        print(f"[run_with_timeout] Function timed out after {timeout}s")
        return (False, None)
    
    if not exception_queue.empty():
        exception = exception_queue.get()
        print(f"[run_with_timeout] Function raised exception: {exception}")
        return (False, exception)
    
    if not result_queue.empty():
        result = result_queue.get()
        return (True, result)
    
    return (False, None)


def get_embedding(embedding_client, model_name, text_input, max_retries=3, timeout=30):
    """
    Get embeddings with timeout and retry logic (Windows-compatible).
    """
    if isinstance(text_input, str):
        text_input = [text_input]
    elif not isinstance(text_input, list):
        text_input = [str(text_input)]
    
    for attempt in range(max_retries):
        try:
            print(f"[get_embedding] Attempt {attempt + 1}/{max_retries}, timeout={timeout}s")
            print(f"[get_embedding] Text length: {len(text_input[0])} chars")
            
            def call_embedding():
                return embedding_client.embeddings.create(
                    input=text_input, 
                    model=model_name
                )
            
            success, result = run_with_timeout(call_embedding, timeout=timeout)
            
            if not success:
                raise TimeoutError(f"Embedding call timed out after {timeout}s")
            
            output = result
            embeddings = []
            for embedding_object in output.data:
                embeddings.append(embedding_object.embedding)
            
            print(f"[get_embedding] Successfully got {len(embeddings)} embedding(s)")
            return embeddings
        
        except Exception as e:
            print(f"[get_embedding] ❌ Error (attempt {attempt + 1}): {e}")
            
            if attempt < max_retries - 1:
                wait_time = 3 * (attempt + 1)
                print(f"[get_embedding] Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[get_embedding] Max retries reached, returning zero vector")
                return [[0.0] * 384]
    
    return [[0.0] * 384]


def double_check_json_output(json_string):
    """Check and correct JSON string."""
    prompt = f"""You will check this json string and correct any mistakes. Return only the corrected json.

{json_string}
"""
    messages = [{"role": "user", "content": prompt}]
    response = get_chatbot_response(messages)
    return response