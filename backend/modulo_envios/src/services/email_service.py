import smtplib
import email.message
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

class EmailService:
    def __init__(self):
        load_dotenv()
        
        self.email_remetente = os.getenv("EMAIL")
        self.password = os.getenv("EMAIL_APP_PASSWORD")
        print(f"EMAIL: {self.email_remetente}, EMAIL_APP_PASSWORD: {self.password}")
        if not self.email_remetente or not self.password:
            error_msg = "Variáveis de ambiente EMAIL e/ou EMAIL_APP_PASSWORD não definidas ou não configuradas no arquivo .env!"
            print(f"ERRO [EmailService]: {error_msg}", file=sys.stderr)
            raise ValueError(error_msg)
        
    def send_bulk(self, usuarios, conteudo):
        destinatarios = [u.get("email") for u in usuarios if u.get("email")]

        if not destinatarios:
            print("Nenhum usuário com email válido para enviar.")
            return False

        return self.send(destinatarios, corpo_email=conteudo)


        
    def send(self, destinatarios, corpo_email=None, assunto="Alerta Meteorológico"):
        """
        Envia um email para uma lista de destinatários.
        
        Args:
            destinatarios (list): Lista de emails dos destinatários.
            corpo_email (str, optional): Corpo do email em HTML.
            assunto (str, optional): Assunto do email.
            
        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário.
        """
        if not destinatarios:
            print("AVISO: Nenhum destinatário fornecido.", file=sys.stderr)
            return False

        msg = email.message.Message()
        msg['Subject'] = assunto
        msg['From'] = self.email_remetente
        msg['To'] = ", ".join(destinatarios)

        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(corpo_email)

        try:
            # Usando 'with' para garantir que a conexão seja fechada automaticamente
            with smtplib.SMTP('smtp.gmail.com', 587) as s:
                s.starttls()
                s.login(msg['From'], self.password)
                s.sendmail(msg['From'], destinatarios, msg.as_string().encode('utf-8'))
            return True
        except smtplib.SMTPException as e:
            print(f"ERRO ao enviar email: {e}", file=sys.stderr)
            return False