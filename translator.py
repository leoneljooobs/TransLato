"""
Módulo de traducción de texto utilizando deep-translator.
"""
import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

class TranslatorService:
    def __init__(self, default_source: str = "en", default_target: str = "es"):
        self.default_source = default_source
        self.default_target = default_target
        self.en_to_es = GoogleTranslator(source="en", target="es")
        self.auto_to_es = GoogleTranslator(source="auto", target="es")
        self.auto_to_en = GoogleTranslator(source="auto", target="en")

    def translate(self, text: str) -> str:
        """
        Traduce el texto dado. Si está en inglés, lo traduce a español.
        Si ya está en español o no está seguro, intenta la mejor traducción posible.
        """
        cleaned = text.strip()
        if not cleaned:
            return ""

        try:
            # Primero intentamos traducción inglés -> español
            result = self.en_to_es.translate(cleaned)
            # Si el resultado es exactamente el mismo (y no son números/puntuación)
            # intentamos auto-detectar por si el usuario escribió en español
            if result.strip().lower() == cleaned.lower() and len(cleaned) > 2 and cleaned.isalpha():
                fallback = self.auto_to_en.translate(cleaned)
                if fallback.strip().lower() != cleaned.lower():
                    return f"{fallback} (ES ➡️ EN)"
            return result
        except Exception as e:
            logger.error(f"Error al traducir '{text}': {e}")
            try:
                # Intento de respaldo con auto-detección
                return self.auto_to_es.translate(cleaned)
            except Exception as e2:
                logger.error(f"Error de respaldo en traducción: {e2}")
                raise RuntimeError("No se pudo traducir la palabra en este momento. Inténtalo de nuevo.")

# Instancia singleton para reutilizar en el bot
translator = TranslatorService()

if __name__ == "__main__":
    test_words = ["apple", "run", "serendipity", "how are you today?"]
    for w in test_words:
        print(f"{w} -> {translator.translate(w)}")

