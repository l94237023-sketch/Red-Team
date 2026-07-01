import os
import requests
import json
import random
from openai import OpenAI

class APIIntegration:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None
        self.deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')

    def query_openai(self, prompt):
        if not self.openai_client:
            return None
        try:
            resp = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are a Gold Level Cybersecurity AI."}, {"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            return resp.choices[0].message.content
        except:
            return None

    def query_deepseek(self, prompt):
        if not self.deepseek_key:
            return None
        try:
            headers = {"Authorization": f"Bearer {self.deepseek_key}", "Content-Type": "application/json"}
            payload = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
            resp = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload, timeout=10)
            return resp.json()['choices'][0]['message']['content']
        except:
            return None

    def query_openrouter(self, prompt):
        if not self.openrouter_key:
            return None
        try:
            headers = {"Authorization": f"Bearer {self.openrouter_key}", "Content-Type": "application/json"}
            payload = {"model": "meta-llama/llama-3.2-3b-instruct:free", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=10)
            return resp.json()['choices'][0]['message']['content']
        except:
            return None

    def multi_ai_consensus(self, prompt):
        results = []
        for func in [self.query_openai, self.query_deepseek, self.query_openrouter]:
            try:
                res = func(prompt)
                if res:
                    results.append(res)
            except:
                continue
        if not results:
            return None
        return max(set(results), key=results.count) if results else results[0]
