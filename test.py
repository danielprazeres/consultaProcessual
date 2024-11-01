import os
import unittest
from unittest.mock import patch
from dotenv import load_dotenv
from main import verificar_movimentacoes, enviar_telegram

# Carregar variáveis do arquivo .env
load_dotenv()

class TestMovimentacoes(unittest.TestCase):
    @patch("requests.get")
    def test_verificar_movimentacoes(self, mock_get):
        # Mock do texto completo que seria extraído da página, contendo uma data posterior à ultima_data_registrada
        texto_completo = """
            Detalhe do Processo
            ...
            Movimentações do Processo
            MovimentoDocumento
            25/07/2024 10:00:00 - Nova movimentação registrada
            24/07/2024 09:38:38 - Juntada de Petição de petição
            ...
        """
        
        # Configura o mock do get para retornar o texto fictício
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = texto_completo.encode()  # Transformar em bytes para simular conteúdo HTTP

        # Usar mock para capturar chamadas de print e requests.post
        with patch("builtins.print") as mock_print, patch("requests.post") as mock_post:
            mock_post.return_value.status_code = 200  # Simula sucesso no envio ao Telegram
            
            # Executa a função de verificação
            verificar_movimentacoes()
            
            # Verifica se a função print foi chamada com o texto "Mensagem enviada com sucesso!"
            mock_print.assert_any_call("Mensagem enviada com sucesso!")
    
    @patch("requests.post")
    def test_enviar_telegram(self, mock_post):
        # Simulação do retorno de sucesso no envio ao Telegram
        mock_post.return_value.status_code = 200
        
        # Mensagem para testar
        mensagem = "Teste de mensagem"
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        # Chama a função com os parâmetros
        enviar_telegram(mensagem, bot_token=bot_token, chat_id=chat_id)
        
        # Verifica se a requisição foi feita com os parâmetros corretos
        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={"chat_id": chat_id, "text": mensagem}
        )

if __name__ == "__main__":
    unittest.main()