"""
LLM client wrapper supporting OpenAI, HuggingFace API, and Local Models
"""
from django.conf import settings
from typing import List, Dict, Optional
import time


class LLMClient:
    """Wrapper for LLM client (OpenAI, HuggingFace API, or Local Model)"""
    
    def __init__(self, api_key: str = None, model: str = None, use_huggingface: bool = None, use_local: bool = None):
        """
        Initialize LLM client
        
        Args:
            api_key: API key (OpenAI or HuggingFace)
            model: Model name to use
            use_huggingface: Whether to use HuggingFace instead of OpenAI
            use_local: Whether to use local model instead of API
        """
        self.use_local = use_local if use_local is not None else settings.USE_LOCAL_MODEL
        self.use_huggingface = use_huggingface if use_huggingface is not None else settings.USE_HUGGINGFACE
        self.model = model or settings.LLM_MODEL
        
        if self.use_local:
            print(f"Initializing local model: {self.model}")
            self._init_local_model()
        elif self.use_huggingface:
            self.api_key = api_key or settings.HUGGINGFACE_API_KEY
            if not self.api_key:
                raise ValueError("HuggingFace API key not configured. Please set HUGGINGFACE_API_KEY in .env file")
            self._init_huggingface()
        else:
            self.api_key = api_key or settings.OPENAI_API_KEY
            if not self.api_key:
                raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
            self._init_openai()
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
        self.client_type = "openai"
    
    def _init_huggingface(self):
        """Initialize HuggingFace client using InferenceClient"""
        from huggingface_hub import InferenceClient
        self.client = InferenceClient(token=self.api_key)
        self.client_type = "huggingface"
    
    def _init_local_model(self):
        """Initialize local model using transformers"""
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        import torch
        
        print(f"Loading model {self.model}... This may take a minute on first run.")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model)
        self.local_model = AutoModelForSeq2SeqLM.from_pretrained(self.model)
        
        # Move to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.local_model.to(self.device)
        
        self.client_type = "local"
        print(f"Model loaded successfully on {self.device}!")
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ) -> Dict:
        """
        Generate response from LLM
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        
        Returns:
            Dictionary with response and metadata
        """
        temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        max_tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS
        
        if self.client_type == "openai":
            return self._generate_openai(prompt, system_prompt, temperature, max_tokens)
        elif self.client_type == "local":
            return self._generate_local(prompt, system_prompt, temperature, max_tokens)
        else:
            return self._generate_huggingface(prompt, system_prompt, temperature, max_tokens)
    
    def _generate_openai(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> Dict:
        """Generate response using OpenAI"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            end_time = time.time()
            
            return {
                'response': response.choices[0].message.content,
                'model': self.model,
                'tokens_used': response.usage.total_tokens,
                'response_time': end_time - start_time,
            }
        
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
    
    def _generate_local(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> Dict:
        """Generate response using local model"""
        import torch
        
        try:
            start_time = time.time()
            
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nQuestion: {prompt}\nAnswer:"
            
            # Tokenize input
            inputs = self.tokenizer(full_prompt, return_tensors="pt", max_length=512, truncation=True)
            inputs = inputs.to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.local_model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0,
                    top_p=0.95,
                    num_beams=2,
                )
            
            # Decode response
            response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            end_time = time.time()
            
            return {
                'response': response_text,
                'model': self.model,
                'tokens_used': len(outputs[0]),
                'response_time': end_time - start_time,
            }
        
        except Exception as e:
            raise Exception(f"Error with local model: {str(e)}")
    
    def _generate_huggingface(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> Dict:
        """Generate response using HuggingFace InferenceClient"""
        try:
            start_time = time.time()
            
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\nQuestion: {prompt}\nAnswer:"
            
            # Use text_generation method from InferenceClient
            response = self.client.text_generation(
                full_prompt,
                model=self.model,
                max_new_tokens=max_tokens,
                temperature=temperature,
                return_full_text=False,
            )
            
            end_time = time.time()
            
            return {
                'response': response,
                'model': self.model,
                'tokens_used': 0,
                'response_time': end_time - start_time,
            }
        
        except Exception as e:
            error_msg = str(e)
            
            # Check for common errors
            if 'loading' in error_msg.lower():
                raise Exception("Model is currently loading. Please wait 20-30 seconds and try again.")
            elif 'rate limit' in error_msg.lower():
                raise Exception("Rate limit exceeded. Please wait a moment and try again.")
            elif '404' in error_msg or 'not found' in error_msg.lower():
                raise Exception(f"Model '{self.model}' not found or not accessible.")
            else:
                raise Exception(f"Error calling HuggingFace API: {error_msg}")
    
    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
    ) -> Dict:
        """
        Generate response from chat messages
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        
        Returns:
            Dictionary with response and metadata
        """
        temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        max_tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS
        
        if self.client_type == "openai":
            return self._generate_chat_openai(messages, temperature, max_tokens)
        else:
            # Convert messages to single prompt for HuggingFace/Local
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            if self.client_type == "local":
                return self._generate_local(prompt, None, temperature, max_tokens)
            else:
                return self._generate_huggingface(prompt, None, temperature, max_tokens)
    
    def _generate_chat_openai(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Dict:
        """Generate chat response using OpenAI"""
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            end_time = time.time()
            
            return {
                'response': response.choices[0].message.content,
                'model': self.model,
                'tokens_used': response.usage.total_tokens,
                'response_time': end_time - start_time,
            }
        
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")


# Global instance (singleton pattern)
_llm_client = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
