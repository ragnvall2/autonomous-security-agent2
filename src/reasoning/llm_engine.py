# src/reasoning/llm_engine.py
import os
import sys
from llama_cpp import Llama

class LLMEngine:
    """LLM Reasoning Engine using llama-cpp-python"""
    
    def __init__(self, model_path, context_window=4096, temperature=0.1, max_tokens=1024):
        """Initialize the LLM engine with the specified model"""
        self.model_path = model_path
        self.context_window = context_window
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize the model
        self.model = Llama(
            model_path=model_path,
            n_ctx=context_window,
            verbose=False
        )
    
    def generate(self, prompt, temperature=None, max_tokens=None):
        """Generate a response for the given prompt"""
        if temperature is None:
            temperature = self.temperature
        if max_tokens is None:
            max_tokens = self.max_tokens
            
        # Create a system prompt for security analysis
        system_prompt = """You are an expert security analyst specializing in web application security. 
Your task is to identify security vulnerabilities, explain why they are issues, 
and provide clear recommendations to fix them."""
        
        # Format the prompt for instruction-tuned models
        formatted_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_prompt}
<|eot_id|><|start_header_id|>user<|end_header_id|>
{prompt.strip()}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        # Generate the response
        response = self.model(
            formatted_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=["<|eot_id|>"]
        )
        
        # Extract the generated text
        return response["choices"][0]["text"]
    
    def analyze_security(self, page_context):
        """Analyze a web page for security vulnerabilities"""
        prompt = f"""
        Analyze the following web page content for security vulnerabilities:
        
        {page_context}
        
        Identify any potential security issues and explain how to fix them.
        """
        return self.generate(prompt)