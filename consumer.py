from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Configuración de la conexión a la base de datos obtenida de variables de entorno
DB_PARAMS = {
    'dbname': os.getenv('PGDATABASE', 'crimes'),
    'user': os.getenv('PGUSER', 'crimes_owner'),
    'password': os.getenv('PGPASSWORD', 'npg_QUkH7TfKZlF8'),
    'host': os.getenv('PGHOST', 'ep-curly-recipe-a50hnh5z-pooler.us-east-2.aws.neon.tech'),
    'port': os.getenv('PGPORT', '5432')
}

def get_db_connection():
    """Establece una conexión con la base de datos."""
    return psycopg2.connect(**DB_PARAMS)

@app.route('/insert-crime', methods=['POST'])
def insert_crime():
    data = request.get_json()

    required_fields = ['dr_no', 'report_date', 'victim_age', 'victim_sex', 'crm_cd_desc']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos en la solicitud'}), 400

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
        return jsonify({'message': 'Registro insertado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
