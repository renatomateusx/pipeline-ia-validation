from abc import ABC, abstractmethod
from typing import Dict, Any
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class AIService(ABC):
    @abstractmethod
    async def analyze(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

class OpenAIService(AIService):
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def analyze(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Prepara o prompt para análise
        prompt = self._prepare_prompt(payload)
        
        # Faz a chamada para a API do OpenAI
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um especialista em segurança de CI/CD. Analise o payload fornecido e identifique potenciais problemas de segurança."},
                {"role": "user", "content": prompt}
            ]
        )

        # Processa a resposta
        analysis = response.choices[0].message.content
        
        # Classifica o resultado
        status = self._classify_result(analysis)
        
        return {
            "status": status,
            "analysis": analysis,
            "details": self._extract_details(analysis)
        }

    def _prepare_prompt(self, payload: Dict[str, Any]) -> str:
        # Converte o payload em um prompt estruturado
        prompt = "Analise o seguinte payload de pipeline CI/CD:\n\n"
        for key, value in payload.items():
            prompt += f"{key}:\n{value}\n\n"
        return prompt

    def _classify_result(self, analysis: str) -> str:
        # Lógica simples de classificação baseada em palavras-chave
        if "CREDENCIAIS" in analysis.upper() or "SECRET" in analysis.upper():
            return "FALHA"
        elif "PERMISSÃO" in analysis.upper() or "RISCO" in analysis.upper():
            return "RISCO"
        return "OK"

    def _extract_details(self, analysis: str) -> Dict[str, Any]:
        # Extrai detalhes relevantes da análise
        return {
            "summary": analysis[:200],  # Primeiros 200 caracteres como resumo
            "full_analysis": analysis
        }

# Factory para criar instâncias do serviço de IA
class AIServiceFactory:
    @staticmethod
    def create_service(provider: str = "openai") -> AIService:
        if provider == "openai":
            return OpenAIService()
        # Adicione outros provedores aqui no futuro
        raise ValueError(f"Provedor de IA não suportado: {provider}") 