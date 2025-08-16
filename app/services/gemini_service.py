import google.generativeai as genai
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator

try:
    from app.config import settings
    from app.models import ChatMessage, UsageInfo
except ImportError:
    from config import settings
    from models import ChatMessage, UsageInfo

import asyncio
import json


logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.base_model = settings.gemini_model
        
        
    def _convert_messages_to_gemini_format(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        gemini_messages = []
        
        for message in messages:
            role = message.role

            if role == "assistant":
                role = "model"
            elif role == "system":
                role = "user"
                content = f"System instructions: {message.content}"
            else:
                content = message.content
            

            gemini_message = {
                "role": role,
                "parts": [{"text": content}]
            }

            gemini_messages.append(gemini_message)
        

        
        return gemini_messages


    async def simple_chat(self, message: str, model: Optional[str] = None, temperature: Optional[float] = 0.7, max_tokens: Optional[int] = 150) -> Dict[str, Any]:
        try:
            generation_config = genai.GenerationConfig(
                temperature=temperature or 0.7,
                max_output_tokens=max_tokens or 150,
                top_p=0.8,
                top_k=40
            )
            
            model_name = model if model and model.startswith("gemini") else self.base_model
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )
            
            response = await asyncio.to_thread(model.generate_content, message)
            response_text = response.text if response.text else "No response generated"
            input_tokens = len(message.split()) * 1.3
            output_tokens = len(response_text.split()) * 1.3
            
            
            response_payload = {
                "response": response_text,
                "usage": UsageInfo(
                    prompt_tokens=int(input_tokens),
                    output_tokens=int(output_tokens),
                    total_tokens=int(input_tokens + output_tokens)
                ),
                "model": model_name,
                "finish_reason": "stop"
            }

            return response_payload
            
        except Exception as e:
            logger.error(f"Gemini API error in simple_chat: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")


    async def create_chat_completion(self, messages: List[ChatMessage], model: Optional[str] = None, temperature: Optional[float] = 0.7, max_tokens: Optional[int] = 150) -> Dict[str, Any]:
        try:
            generation_config = genai.GenerationConfig(
                temperature=temperature or 0.7,
                max_output_tokens=max_tokens or 150,
                top_p=0.8,
                top_k=40
            )
            
            model_name = model if model and model.startswith("gemini") else self.model_name
            gemini_model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )
            
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini_format(messages)
            
            # Start chat session
            chat = gemini_model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
            
            # Get the last message (current user input)
            last_message = gemini_messages[-1]["parts"][0]["text"]
            
            # Send message and wait for response
            response = await asyncio.to_thread(chat.send_message, last_message)
            response_text = response.text if response.text else "No response generated"
            
            total_input = sum(len(msg.content.split()) for msg in messages) * 1.3
            output_tokens = len(response_text.split()) * 1.3
            

            response_payload = {
                "response": response_text,
                "usage": UsageInfo(
                    prompt_tokens=int(total_input),
                    output_tokens=int(output_tokens),
                    total_tokens=int(total_input + output_tokens)
                ),
                "model": model_name,
                "finish_reason": "stop"
            }
            return response_payload
            
        except Exception as e:
            logger.error(f"Gemini API error in create_chat_completion: {str(e)}")
            raise Exception(f"Gemini API error: {str(e)}")


    async def streaming_chat_completion(self, messages: List[ChatMessage], model: Optional[str] = None, temperature: Optional[float] = 0.7, max_tokens: Optional[int] = 150) -> AsyncGenerator[str, None]:
        
        try:
            generation_config = genai.GenerationConfig(
                temperature=temperature or 0.7,
                max_output_tokens=max_tokens or 150,
                top_p=0.8,
                top_k=40
            )
            
            model_name = model if model and model.startswith("gemini") else self.model_name
            gemini_model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )
            
            gemini_messages = self._convert_messages_to_gemini_format(messages)
            chat = gemini_model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
            last_message = gemini_messages[-1]["parts"][0]["text"]
            response = await asyncio.to_thread(chat.send_message, last_message, stream=True)
            
            # Yield chunks as they come, a generator function that returns chunks over time
            for chunk in response:
                if chunk.text:
                    yield chunk.text 
                    
        except Exception as e:
            logger.error(f"Gemini API error in streaming_chat_completion: {str(e)}")
            yield f"Error: {str(e)}"
