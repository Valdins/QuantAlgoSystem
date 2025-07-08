from kafka import KafkaConsumer
import json
import os

# Kafka broker configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
QUOTE_TOPIC = 'marketdata.quotes'
ORDER_REQUEST_TOPIC = 'orders.requests'
# Define consumer group ID for your application
CONSUMER_GROUP_ID = 'trading_system_consumer_group'

def deserialize_json(data):
    """Deserializes JSON bytes to a Python dictionary."""
    if data is None:
        return None
    try:
        return json.loads(data.decode('utf-8'))
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e} - Data: {data}")
        return None

def create_consumer(topics):
    """Creates and returns a KafkaConsumer instance for multiple topics."""
    consumer = KafkaConsumer(
        *topics, # Unpack the list of topics
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        group_id=CONSUMER_GROUP_ID,
        auto_offset_reset='earliest', # Start consuming from the beginning of the topic if no offset is committed
        enable_auto_commit=True,    # Automatically commit offsets (for development, manual commit for production)
        value_deserializer=deserialize_json,
        key_deserializer=lambda k: k.decode('utf-8') if k else None
    )
    print(f"Kafka Consumer initialized for topics: {topics} in group: {CONSUMER_GROUP_ID}")
    return consumer

if __name__ == "__main__":
    # Consumer will subscribe to both market data and order requests
    consumer = create_consumer([QUOTE_TOPIC, ORDER_REQUEST_TOPIC])

    try:
        print("Starting consumer, waiting for messages...")
        for message in consumer:
            # Message is a ConsumerRecord object
            # print(f"Received message: {message}") # Full message object for debugging

            topic = message.topic
            partition = message.partition
            offset = message.offset
            key = message.key
            value = message.value # Already deserialized by our function

            if topic == QUOTE_TOPIC:
                if value:
                    print(f"[{topic} P{partition} O{offset}] Key: {key}, Quote: {value['symbol']} Bid: {value['bid_price']} Ask: {value['ask_price']}")
            elif topic == ORDER_REQUEST_TOPIC:
                if value:
                    print(f"[{topic} P{partition} O{offset}] Key: {key}, Order: {value['side']} {value['quantity']} {value['symbol']} (ID: {value['order_id']})")
            else:
                print(f"[{topic} P{partition} O{offset}] Unknown message type. Key: {key}, Value: {value}")

    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()
        print("Consumer closed.")