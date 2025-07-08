from kafka import KafkaProducer
import json
import time
import random
from faker import Faker

# Initialize Faker for generating fake data
fake = Faker()

# Kafka broker configuration
# We use 'localhost:9092' because our Python script runs on the host machine
# and the Kafka container exposes port 9092 to the host.
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
QUOTE_TOPIC = 'marketdata.quotes'
ORDER_REQUEST_TOPIC = 'orders.requests'

def serialize_json(data):
    """Serializes Python dictionary to JSON bytes."""
    return json.dumps(data).encode('utf-8')

def create_producer():
    """Creates and returns a KafkaProducer instance."""
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        value_serializer=serialize_json,
        # For trading, consider a key serializer to ensure ordering for specific instruments/orders
        # e.g., key_serializer=lambda key: str(key).encode('utf-8')
        acks='all',  # Ensure all in-sync replicas have received the message (high durability)
        retries=5,   # Retry sending messages up to 5 times on failure
        enable_idempotence=True # Guarantees exactly-once delivery for the producer
    )
    print(f"Kafka Producer initialized for {KAFKA_BOOTSTRAP_SERVERS}")
    return producer

def generate_fake_quote():
    """Generates a fake stock quote."""
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA']
    symbol = random.choice(symbols)
    price = round(random.uniform(100.0, 2000.0), 2)
    bid_spread = round(random.uniform(0.01, 0.50), 2)
    ask_spread = round(random.uniform(0.01, 0.50), 2)
    timestamp = time.time()
    return {
        'symbol': symbol,
        'bid_price': price - bid_spread,
        'ask_price': price + ask_spread,
        'timestamp': timestamp,
        'source': 'simulated_exchange'
    }

def generate_fake_order_request():
    """Generates a fake order request."""
    order_types = ['LIMIT', 'MARKET']
    sides = ['BUY', 'SELL']
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA']
    order_id = fake.uuid4()
    client_id = fake.numerify(text='client_####')
    symbol = random.choice(symbols)
    order_type = random.choice(order_types)
    side = random.choice(sides)
    quantity = random.randint(10, 1000) * 10 # Multiples of 10
    price = round(random.uniform(100.0, 2000.0), 2) if order_type == 'LIMIT' else None
    timestamp = time.time()

    return {
        'order_id': order_id,
        'client_id': client_id,
        'symbol': symbol,
        'order_type': order_type,
        'side': side,
        'quantity': quantity,
        'price': price, # Price is only for LIMIT orders
        'timestamp': timestamp
    }

def send_message(producer, topic, key, value):
    """Sends a message to a Kafka topic."""
    try:
        # For market data, use symbol as key for consistent partitioning
        # For orders, use order_id or client_id as key
        future = producer.send(topic, key=str(key).encode('utf-8'), value=value)
        metadata = future.get(timeout=10) # Blocks until message is sent or timeout
        # print(f"Sent to Topic: {metadata.topic}, Partition: {metadata.partition}, Offset: {metadata.offset}, Key: {key}")
    except Exception as e:
        print(f"Error sending message to {topic} (Key: {key}): {e}")

if __name__ == "__main__":
    producer = create_producer()
    message_count = 0

    try:
        while True:
            # Send a fake market quote
            quote = generate_fake_quote()
            send_message(producer, QUOTE_TOPIC, quote['symbol'], quote)
            print(f"Published Quote: {quote['symbol']} - Bid: {quote['bid_price']}, Ask: {quote['ask_price']}")

            # Send a fake order request every 5 quotes
            if message_count % 5 == 0:
                order_request = generate_fake_order_request()
                # Use order_id as key for orders to ensure all events for an order go to the same partition
                send_message(producer, ORDER_REQUEST_TOPIC, order_request['order_id'], order_request)
                print(f"Published Order Request: {order_request['order_id']} - {order_request['side']} {order_request['quantity']} {order_request['symbol']}")

            message_count += 1
            time.sleep(0.5) # Adjust sending rate
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.flush() # Ensure all buffered messages are sent
        producer.close()
        print("Producer closed.")