import winreg
import os
import time
import subprocess
from threading import Timer

def check_bak_accounts():
    try:
        # Acessar a chave do registro onde as contas de usuário estão armazenadas
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList",
            0,
            winreg.KEY_READ
        )

        bak_users = []
        
        # Iterar pelas subchaves para encontrar contas .bak
        for i in range(winreg.QueryInfoKey(registry_key)[0]):
            subkey_name = winreg.EnumKey(registry_key, i)
            subkey = winreg.OpenKey(registry_key, subkey_name)
            
            try:
                profile_image_path = winreg.QueryValueEx(subkey, "ProfileImagePath")[0]
                if profile_image_path.endswith('.bak'):
                    # Extrair o nome de usuário do caminho
                    username = os.path.basename(profile_image_path).replace('.bak', '')
                    bak_users.append(username)
            except WindowsError:
                continue
            finally:
                subkey.Close()
        
        registry_key.Close()
        
        return bak_users
        
    except WindowsError as e:
        print(f"Erro ao acessar o registro: {e}")
        return []

def notify_user(username):
    try:
        # Enviar mensagem via cmd usando msg.exe
        message = (f"ATENÇÃO {username}: Foi identificado que você está usando uma conta temporária (.bak). "
                  "Salve todo o seu trabalho imediatamente. Sua sessão nesta máquina virtual "
                  "será finalizada em 120 segundos. Você poderá fazer login novamente após 5 minutos.")
        
        subprocess.run(
            ['msg', '/server:127.0.0.1', username, message],
            check=True
        )
        print(f"Notificação enviada para {username}")
    except subprocess.CalledProcessError as e:
        print(f"Falha ao enviar notificação para {username}: {e}")

def logout_user(username):
    try:
        # Desconectar o usuário usando logoff remoto
        subprocess.run(
            ['logoff', f'/server:127.0.0.1', username],
            check=True
        )
        print(f"Usuário {username} desconectado com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"Falha ao desconectar {username}: {e}")

def process_bak_users():
    print("Iniciando verificação de contas .bak...")
    bak_users = check_bak_accounts()
    
    if not bak_users:
        print("Nenhuma conta .bak encontrada.")
        return
    
    print(f"Contas .bak encontradas: {', '.join(bak_users)}")
    
    for user in bak_users:
        # Notificar o usuário
        notify_user(user)
        
        # Agendar logout após 120 segundos
        t = Timer(120.0, logout_user, args=[user])
        t.start()

def main():
    while True:
        process_bak_users()
        # Esperar 20 minutos antes da próxima verificação
        time.sleep(60)  # 1200 segundos = 20 minutos

if __name__ == "__main__":
    main()