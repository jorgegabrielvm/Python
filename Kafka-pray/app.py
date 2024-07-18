from flask import Flask, render_template, request, jsonify
from confluent_kafka import Producer, Consumer, KafkaException, KafkaError
import json
import threading
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import os
from datetime import datetime

app = Flask(__name__)

# Kafka broker address
broker = '13.60.162.175:9092'
# Kafka topic
topic = 'kafkapray'

# Producer configuration
producer_conf = {
    'bootstrap.servers': broker,
    'batch.size': 32768,  # 32KB
    'linger.ms': 100,  # 100 milliseconds
    'retries': 5,  # Number of retries
}

# Consumer configuration
consumer_conf = {
    'bootstrap.servers': broker,
    'group.id': 'prayer-group',
    'auto.offset.reset': 'earliest',
    'session.timeout.ms': 30000,  # 30 seconds
    'fetch.max.bytes': 52428800,  # 50MB
}

# S3 configuration
s3_bucket_name = 'kafka-kafkapray'
s3_client = boto3.client('s3',
                         aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                         aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

# Create instance of Producer
producer = Producer(producer_conf)

# Called once for each message produced to indicate delivery result.
def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def produce_message(name, prayer_request):
    # Create dictionary payload with timestamp
    payload = {
        'name': name,
        'prayer_request': prayer_request,
        'timestamp': datetime.now().isoformat()
    }
    
    # Convert payload to JSON string
    json_payload = json.dumps(payload)

    try:
        # Produce message to Kafka
        producer.produce(topic, json_payload.encode('utf-8'), callback=delivery_report)
        producer.poll(0)  # Trigger delivery report callback
        return True
    except KafkaException as e:
        print(f'Failed to produce message: {e}')
        return False

def upload_to_s3(message):
    try:
        # Generate a unique key for each message, using timestamp
        s3_key = f"message_{message['timestamp']}.json"

        # Convert the message to JSON string
        json_data = json.dumps(message)

        # Upload the JSON data to S3
        s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=json_data)

        print(f"Uploaded {s3_key} to S3")
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Credentials error: {e}")
    except Exception as e:
        print(f"Failed to upload to S3: {e}")

def consume_messages():
    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])
    
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            if msg.value() is None:
                print("Received empty message")
                continue

            try:
                message = json.loads(msg.value().decode('utf-8'))
                print(f"Consumed message: {message}")

                # Upload the message to S3
                upload_to_s3(message)

            except json.JSONDecodeError as e:
                print(f"Failed to decode message: {e}")
                continue

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        prayer_request = request.form['prayer_request']

        # Produce message to Kafka
        if produce_message(name, prayer_request):
            return render_template('success.html', name=name, prayer_request=prayer_request)
        else:
            return render_template('error.html')
    
    return render_template('index.html')

@app.route('/api/requests')
def get_requests():
    try:
        # List objects in S3 bucket
        response = s3_client.list_objects_v2(Bucket=s3_bucket_name)
        
        # Initialize an empty list for requests
        requests = []

        # Iterate through objects and fetch their contents
        for obj in response.get('Contents', []):
            s3_object = s3_client.get_object(Bucket=s3_bucket_name, Key=obj['Key'])
            message = json.loads(s3_object['Body'].read().decode('utf-8'))
            requests.append(message)

        return jsonify(requests)

    except Exception as e:
        print(f"Failed to fetch requests from S3: {e}")
        return jsonify([])  # Return empty list on failure

@app.route('/requests')
def view_requests():
    return render_template('requests.html')

if __name__ == '__main__':
    # Start the consumer thread
    consumer_thread = threading.Thread(target=consume_messages)
    consumer_thread.daemon = True
    consumer_thread.start()
    
    # Run the Flask app
    app.run(debug=True)
