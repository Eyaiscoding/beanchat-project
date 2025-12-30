from dotenv import load_dotenv
import os
from .utils import get_chatbot_response, get_embedding
from openai import OpenAI
from copy import deepcopy
from pinecone import Pinecone

load_dotenv()

class DetailsAgent():
    def __init__(self):
        print("[DetailsAgent] Initializing...")
        
        self.embedding_client = OpenAI(
            api_key=os.getenv("RUNPOD_TOKEN"), 
            base_url=os.getenv("RUNPOD_EMBEDDING_URL")
        )
        
        self.embedding_model_name = "BAAI/bge-small-en-v1.5"
        
        try:
            self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            self.index_name = os.getenv("PINECONE_INDEX_NAME")
            print(f"[DetailsAgent] Pinecone initialized with index: {self.index_name}")
        except Exception as e:
            print(f"[DetailsAgent] Warning: Could not initialize Pinecone: {e}")
            self.pc = None
            self.index_name = None
        
        # Fallback menu information
        self.menu_fallback = """
MERRY'S WAY COFFEE SHOP MENU:

DRINKS:
- Cappuccino: $4.50
- Latte: $4.75
- Espresso shot: $2.00
- Dark chocolate (Drinking Chocolate): $5.00

PASTRIES:
- Chocolate Croissant: $3.75
- Croissant: $3.25
- Almond Croissant: $4.00
- Jumbo Savory Scone: $3.25
- Cranberry Scone: $3.50
- Oatmeal Scone: $3.25
- Ginger Scone: $3.50

BISCOTTI:
- Chocolate Chip Biscotti: $2.50
- Hazelnut Biscotti: $2.75
- Ginger Biscotti: $2.50

SYRUPS:
- Chocolate syrup: $1.50
- Hazelnut syrup: $1.50
- Caramel syrup: $1.50
- Sugar Free Vanilla syrup: $1.50

PACKAGED:
- Dark chocolate (Packaged Chocolate): $3.00
"""
    
    def get_closest_results(self, index_name, input_embeddings, top_k=2):
        """Query Pinecone with timeout protection"""
        try:
            print(f"[DetailsAgent] Querying Pinecone...")
            
            if self.pc is None:
                print("[DetailsAgent] Pinecone not available, using fallback")
                return None
            
            index = self.pc.Index(index_name)
            
            results = index.query(
                namespace="ns1",
                vector=input_embeddings,
                top_k=top_k,
                include_values=False,
                include_metadata=True
            )
            
            print(f"[DetailsAgent] Got {len(results.get('matches', []))} results from Pinecone")
            return results
            
        except Exception as e:
            print(f"[DetailsAgent] Error querying Pinecone: {e}")
            return None

    def get_response(self, messages):
        try:
            print("[DetailsAgent] Starting get_response...")
            messages = deepcopy(messages)
            user_message = messages[-1]['content']
            print(f"[DetailsAgent] User message: {user_message[:100]}...")
            
            source_knowledge = None
            
            # Try to get embedding and query Pinecone
            if self.pc is not None:
                try:
                    print("[DetailsAgent] Getting embedding...")
                    embedding = get_embedding(
                        self.embedding_client, 
                        self.embedding_model_name, 
                        user_message,
                        timeout=15  # Shorter timeout
                    )
                    
                    if embedding and len(embedding) > 0:
                        embedding_vector = embedding[0]
                        print(f"[DetailsAgent] Embedding obtained, querying Pinecone...")
                        
                        result = self.get_closest_results(self.index_name, embedding_vector)
                        
                        if result and 'matches' in result and len(result['matches']) > 0:
                            source_knowledge = "\n".join([
                                x['metadata']['text'].strip() + '\n' 
                                for x in result['matches']
                            ])
                            print(f"[DetailsAgent] Retrieved {len(result['matches'])} contexts from Pinecone")
                        else:
                            print("[DetailsAgent] No matches from Pinecone, using fallback")
                    
                except Exception as e:
                    print(f"[DetailsAgent] Error in embedding/Pinecone pipeline: {e}")
            
            # Use fallback if Pinecone failed or unavailable
            if source_knowledge is None:
                print("[DetailsAgent] Using fallback menu information")
                source_knowledge = self.menu_fallback

            prompt = f"""Menu: {source_knowledge}

Question: {user_message}

Answer the question in one short sentence. Do not ask follow-up questions."""

            system_prompt = """You are a helpful assistant for Merry's Way coffee shop. Answer questions briefly in one sentence. Do not ask questions."""
            
            messages[-1]['content'] = prompt
            input_messages = [{"role": "system", "content": system_prompt}] + messages[-3:]

            print("[DetailsAgent] Calling LLM for response...")
            chatbot_output = get_chatbot_response(input_messages, timeout=60)
            print("[DetailsAgent] Got LLM response")
            
            output = self.postprocess(chatbot_output)
            print("[DetailsAgent] Response processed successfully")
            
            return output
            
        except Exception as e:
            print(f"[DetailsAgent] CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            # Emergency fallback
            return {
                "role": "assistant",
                "content": "I apologize for the technical difficulty. Please ask me about our menu items, and I'll do my best to help!",
                "memory": {"agent": "details_agent", "error": str(e)}
            }

    def postprocess(self, output):
        return {
            "role": "assistant",
            "content": output,
            "memory": {"agent": "details_agent"}
        }