import winreg
import os
import time
import subprocess
import ctypes
import sys
import logging
from threading import Timer
from datetime import datetime

# Configuração de logging melhorada
def setup_logging():
    logging.basicConfig(
        filename=r'C:\Windows\Temp\bak_account_monitor.log',
        level=logging.DEBUG,  # Alterado para DEBUG para mais detalhes
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )
    logging.info("Iniciando monitor de contas .bak (Versão Aprimorada)")

# Verificação de admin com log detalhado
def is_admin():
    try:
        admin = ctypes.windll.shell32.IsUserAnAdmin()
        logging.debug(f"Verificação de admin: {admin}")
        return admin
    except Exception as e:
        logging.error(f"Erro ao verificar privilégios: {e}")
        return False

if not is_admin():
    logging.critical("FALHA: Execute como Administrador!")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

setup_logging()

def check_bak_accounts():
    """Verificação aprimorada de contas .bak"""
    try:
        logging.debug("Acessando chave do registro...")
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY
        )

        bak_users = []
        key_count = winreg.QueryInfoKey(registry_key)[0]
        logging.debug(f"Total de subchaves encontradas: {key_count}")

        for i in range(key_count):
            try:
                subkey_name = winreg.EnumKey(registry_key, i)
                subkey = winreg.OpenKey(registry_key, subkey_name)
                
                try:
                    profile_image_path, _ = winreg.QueryValueEx(subkey, "ProfileImagePath")
                    logging.debug(f"Verificando: {profile_image_path}")
                    
                    # Verificação mais abrangente (case insensitive e caminhos alternativos)
                    if any(ext in profile_image_path.lower() for ext in ['.bak', '.temp', '.tmp']):
                        username = os.path.basename(profile_image_path)
                        username = username.split('.')[0]  # Remove todas as extensões
                        bak_users.append(username)
                        logging.warning(f"CONTA TEMPORÁRIA DETECTADA: {username} (Caminho: {profile_image_path})")
                except WindowsError as e:
                    logging.debug(f"Subchave {subkey_name} sem ProfileImagePath: {e}")
                finally:
                    subkey.Close()
            except Exception as e:
                logging.error(f"Erro ao processar subchave {i}: {e}")
        
        registry_key.Close()
        return bak_users
        
    except Exception as e:
        logging.critical(f"ERRO NO REGISTRO: {e}")
        return []

# ... (mantenha as outras funções notify_user, fix_bak_account, logout_user como no script anterior)

def process_bak_users():
    """Processamento com logs detalhados"""
    logging.info("--- INÍCIO DA VERIFICAÇÃO ---")
    bak_users = check_bak_accounts()
    
    if not bak_users:
        logging.warning("Nenhuma conta temporária encontrada! Verificando configuração...")
        
        # Verificação extra para debug
        try:
            test_path = r"C:\Users\UsuarioTeste.bak"
            if os.path.exists(test_path):
                logging.error(f"ERRO: O script não detectou {test_path} mas o caminho existe!")
            else:
                logging.info("Sistema de arquivos verificado - nenhum .bak encontrado")
        except Exception as e:
            logging.error(f"Teste de verificação falhou: {e}")
    
    # ... (restante do processamento)

def main():
    logging.info("==== SISTEMA ATIVADO ====")
    logging.info(f"Python {sys.version}")
    logging.info(f"Executando em: {os.getcwd()}")
    
    while True:
        process_bak_users()
        time.sleep(300)  # Verifica a cada 5 minutos para testes

if __name__ == "__main__":
    main()