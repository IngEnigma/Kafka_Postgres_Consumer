import psycopg2
import os
import json
import requests

# Configuración de la conexión a la base de datos obtenida de variables de entorno
DB_PARAMS = {
    'dbname': os.getenv('PGDATABASE', 'crimes'),
    'user': os.getenv('PGUSER', 'crimes_owner'),
    'password': os.getenv('PGPASSWORD', 'npg_QUkH7TfKZlF8'),
    'host': os.getenv('PGHOST', 'ep-curly-recipe-a50hnh5z-pooler.us-east-2.aws.neon.tech'),
    'port': os.getenv('PGPORT', '5432')
}

JSONL_URL = "https://raw.githubusercontent.com/IngEnigma/StreamlitSpark/refs/heads/master/results/male_crimes/data.jsonl"

def get_db_connection():
    """Establece una conexión con la base de datos."""
    return psycopg2.connect(**DB_PARAMS)

def insert_crime(data):
    """Inserta un registro en la tabla crimes."""
    required_fields = ['dr_no', 'report_date', 'victim_age', 'victim_sex', 'crm_cd_desc']
    if not all(field in data for field in required_fields):
        print(f"Faltan campos requeridos en el registro: {data}")
        return

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        insert_query = """
            INSERT INTO crimes (dr_no, report_date, victim_age, victim_sex, crm_cd_desc)
            VALUES (%s, %s, %s, %s, %s);
        """
        cur.execute(insert_query, (
            data['dr_no'],
            data['report_date'],
            data['victim_age'],
            data['victim_sex'],
            data['crm_cd_desc']
        ))
        conn.commit()
        cur.close()
        conn.close()
        print(f"Registro insertado exitosamente: {data}")
    except Exception as e:
        print(f"Error al insertar el registro: {e}")

def main():
    try:
        response = requests.get(JSONL_URL)
        response.raise_for_status()
        for line in response.text.strip().splitlines():
            crime_data = json.loads(line)
            insert_crime(crime_data)
    except Exception as e:
        print(f"Error al obtener o procesar los datos: {e}")

if __name__ == '__main__':
    main()
