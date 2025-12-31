import psycopg2
from config import DATABASE_URL

def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Conexão estabelecida com sucesso!")
        return conn
    except Exception as e:
        print(f"Erro ao conectar: {e}")

if __name__ == "__main__":
    get_connection()
