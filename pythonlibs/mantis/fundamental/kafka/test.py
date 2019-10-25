#coding:utf-8


from pykafka import  KafkaClient
from pykafka.common import OffsetType

client = KafkaClient(hosts='localhost:9092')
topic = client.topics['test']

# consumer = topic.get_simple_consumer()
# for message in consumer:
#     if message is not None:
#         print message.offset, message.value


balanced_consumer = topic.get_balanced_consumer(
    consumer_group='test_group',
        auto_commit_enable=True,
    # zookeeper_connect='localhost:2181'
    )

for message in balanced_consumer:
    if message is not None:
        print message.offset, message.value