import os
import time
from typing import Optional, Dict
from datetime import datetime, timedelta


class GeminiAPIKeyManager:

    def __init__(self):
        self.api_keys = [
            "AIzaSyAEpFa7bCmg3LelBLBJ2KkBg9VxGrJ-C3I",
            "AIzaSyCSKRwGAI9zFuBOWeWximWDM4ThmLcor6k",
            "AIzaSyCJDoGFYmOA0I1tcwc_HRpEcZLYSeJisFE",
            "AIzaSyAEpFa7bCmg3LelBLBJ2KkBg9VxGrJ-C3I",
        ]

        self.current_key_index = 0
        self.failed_keys: Dict[int, datetime] = {}
        self.cooldown_minutes = 60
        self.request_count = 0

    def get_current_key(self) -> Optional[str]:
        """Retorna a chave API atual, removendo do cooldown chaves que já esperaram tempo suficiente"""
        self._cleanup_cooled_down_keys()
        
        if len(self.failed_keys) >= len(self.api_keys):
            print("⚠️ TODAS as chaves estão em cooldown. Aguardando...")
            return None

        key = self.api_keys[self.current_key_index]

        if key.startswith("SUA_CHAVE_API"):
            env_key = os.environ.get("GEMINI_API_KEY")
            if env_key:
                return env_key

        return key
    
    def _cleanup_cooled_down_keys(self):
        """Remove chaves que já passaram pelo período de cooldown"""
        now = datetime.now()
        keys_to_remove = []
        
        for key_index, failed_time in self.failed_keys.items():
            if now - failed_time > timedelta(minutes=self.cooldown_minutes):
                keys_to_remove.append(key_index)
                print(f"✅ Chave #{key_index + 1} recuperada após cooldown de {self.cooldown_minutes} minutos")
        
        for key_index in keys_to_remove:
            del self.failed_keys[key_index]

    def rotate_key(self) -> bool:
        """
        Rotaciona para a próxima chave disponível
        Retorna True se conseguiu rotacionar, False se todas as chaves falharam
        """
        self.failed_keys[self.current_key_index] = datetime.now()
        print(f"❌ Chave #{self.current_key_index + 1} atingiu o limite. Entrando em cooldown por {self.cooldown_minutes} minutos.")
        
        self._cleanup_cooled_down_keys()

        if len(self.failed_keys) >= len(self.api_keys):
            print("⚠️ ERRO: Todas as chaves API do Gemini estão em cooldown!")
            return False

        attempts = 0
        while attempts < len(self.api_keys):
            self.current_key_index = (self.current_key_index + 1) % len(
                self.api_keys)

            if self.current_key_index not in self.failed_keys:
                print(
                    f"🔄 Rotacionando para chave API #{self.current_key_index + 1}"
                )
                return True

            attempts += 1

        return False

    def mark_key_as_working(self):
        """Marca a chave atual como funcionando (remove das falhas)"""
        if self.current_key_index in self.failed_keys:
            del self.failed_keys[self.current_key_index]
            print(f"✅ Chave #{self.current_key_index + 1} voltou a funcionar!")
        
        self.request_count += 1
        if self.request_count % 10 == 0:
            print(f"📊 Usando chave #{self.current_key_index + 1} - {self.request_count} requisições processadas")

    def reset_failures(self):
        """Reseta o contador de falhas (útil para resetar manualmente)"""
        self.failed_keys.clear()
        self.current_key_index = 0
        print("🔄 Todas as chaves foram resetadas!")
    
    def get_status(self) -> dict:
        """Retorna o status atual do gerenciador de chaves"""
        self._cleanup_cooled_down_keys()
        
        total_keys = len(self.api_keys)
        failed_count = len(self.failed_keys)
        active_count = total_keys - failed_count
        
        return {
            'current_key_index': self.current_key_index + 1,
            'total_keys': total_keys,
            'active_keys': active_count,
            'failed_keys': failed_count,
            'request_count': self.request_count
        }


key_manager = GeminiAPIKeyManager()
