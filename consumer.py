import psycopg2
import os
import json
import threading
from confluent_kafka import Consumer, KafkaException
from flask import Flask

app = Flask(__name__)

# Configuración de Redpanda
KAFKA_CONFIG = {
    'bootstrap.servers': 'cvq4abs3mareak309q80.any.us-west-2.mpx.prd.cloud.redpanda.com:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'SCRAM-SHA-256',
    'sasl.username': 'IngEnigma',
    'sasl.password': 'BrARBOxX98VI4f2LIuIT1911NYGrXu',
    'group.id': 'crimes-consumer-group',
    'auto.offset.reset': 'earliest'
}

# Configuración de PostgreSQL
DB_PARAMS = {
    'dbname': os.getenv('PGDATABASE', 'crimes'),
    'user': os.getenv('PGUSER', 'crimes_owner'),
    'password': os.getenv('PGPASSWORD', 'npg_QUkH7TfKZlF8'),
    'host': os.getenv('PGHOST', 'ep-curly-recipe-a50hnh5z-pooler.us-east-2.aws.neon.tech'),
    'port': os.getenv('PGPORT', '5432')
}

TOPIC = "crimes"

def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)

def insert_crime(data):
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
        print(f"Registro insertado exitosamente: DR No {data['dr_no']}")
    except Exception as e:
        print(f"Error al insertar el registro: {e}")

def kafka_consumer_loop():
    consumer = Consumer(KAFKA_CONFIG)
    consumer.subscribe([TOPIC])
    print("Consumer iniciado y suscrito al tópico", TOPIC)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                print("No hay nuevos mensajes...")
                continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    print("Fin de partición alcanzado")
                    continue
                else:
                    print(f"Error al consumir: {msg.error()}")
                    break

            try:
                print(f"Mensaje recibido: {msg.value().decode('utf-8')}")
                crime_data = json.loads(msg.value().decode('utf-8'))
                print("Datos parseados:", crime_data)
                insert_crime(crime_data)
            except json.JSONDecodeError as e:
                print(f"Error decodificando mensaje JSON: {e}")
                print("Mensaje problemático:", msg.value())
            except Exception as e:
                print(f"Error procesando mensaje: {e}")

    except KeyboardInterrupt:
        print("Deteniendo consumer...")
    except Exception as e:
        print(f"Error inesperado en el consumer: {e}")
    finally:
        consumer.close()

# Endpoint simple para monitoreo
@app.route("/health")
def health():
    return "ok", 200

if __name__ == '__main__':
    # Ejecutar el consumer en segundo plano
    consumer_thread = threading.Thread(target=kafka_consumer_loop, daemon=True)
    consumer_thread.start()

    # Lanzar Flask
    app.run(host="0.0.0.0", port=8080)
