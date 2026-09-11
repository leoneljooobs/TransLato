"""
Script de pruebas unitarias para el traductor y la base de datos.
"""
import os
import unittest
from database import (
    init_db,
    register_user,
    add_word,
    get_weekly_words,
    get_total_words_count,
    get_all_users,
)
from translator import translator


class TestChatbotCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_translation(self):
        """Prueba que el traductor convierta palabras básicas de inglés a español."""
        translations = {
            "hello": "hola",
            "world": "mundo",
            "water": "agua",
        }
        for english, expected_spanish in translations.items():
            result = translator.translate(english)
            print(f"[TEST] Traduciendo '{english}' -> '{result}'")
            self.assertIn(expected_spanish.lower(), result.lower())

    def test_database_operations(self):
        """Prueba la inserción de usuario, palabras y consulta semanal."""
        test_user_id = 999999
        test_chat_id = 999999
        username = "test_user"

        # Registrar usuario y agregar palabras
        register_user(test_user_id, test_chat_id, username)
        add_word(test_user_id, test_chat_id, "cat", "gato", username)
        add_word(test_user_id, test_chat_id, "dog", "perro", username)

        # Verificar conteo total
        total = get_total_words_count(test_user_id)
        self.assertGreaterEqual(total, 2)

        # Verificar palabras semanales
        weekly_words = get_weekly_words(test_user_id, days=7)
        words_en = [w["original_text"] for w in weekly_words]
        self.assertIn("cat", words_en)
        self.assertIn("dog", words_en)

        # Verificar lista de usuarios
        users = get_all_users()
        user_ids = [u["user_id"] for u in users]
        self.assertIn(test_user_id, user_ids)
        print("[TEST] Base de datos verificada correctamente.")


if __name__ == "__main__":
    unittest.main()

