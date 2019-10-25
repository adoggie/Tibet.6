

Latchet 
------
工具服务（消息网关)，用于接收队列中的推送消息，并将其分派到http的websocket通路，便于web前端获取实时消息，例如：行情



Problems
---------
gevent-socketio 0.3.6 存在代码问题 

python2.7/site-packages/socketio/handler.py

python2.7/site-packages/socketio/transports.py

以下代码需将 3600 修改为  "3600"
<pre>
def write_plain_result(self, data):
    self.start_response("200 OK", [
        ("Access-Control-Allow-Origin", self.environ.get('HTTP_ORIGIN', '*')),
        ("Access-Control-Allow-Credentials", "true"),
        ("Access-Control-Allow-Methods", "POST, GET, OPTIONS"),
        ("Access-Control-Max-Age", 3600),
        ("Content-Type", "text/plain"),
    ])
    self.result = [data]
</pre>

使用方法
--------

## Server 配置

1. 启用websocket

<pre>
http:
  host : ''
  port : 18808
  threaded: false
  debug: true
  websocket: true   # 必须启用
</pre>

2. 在配置settings.yaml  的main配置中增加网关
<pre>
 gateway:
  - name: '/quotes'
    class: 'http.gateway.SubscribeChannel'
    event: 'data' 
</pre>
 - `/quotes` 指的是名字空间; 
 - `class` - 用于接收处理消息的对象; 
 - `event` - 消息接收类型
 
3. 定义MQ消息接收后，消息投递给那个通道对象 
 
<pre>
 channels:
  - name: 'future_ctp_tick_*'
    handler: 'handler.get_ctp_symbol_ticks'
    enable: true
    type: 'pubsub' # or queue
    data:
      ns_name: '/quotes'  # 此处mq接收消息之后转发给`/quotes` 命名的订阅通道对象
</pre>

## Javascript 客户端 

1. 连接到名字空间
> socket = io.connect('/quotes');

2. 设置 接收函数
<pre>
socket.on('data', function (symbol,tick) {
    ...
}
</pre>

3. 订阅
<pre>
socket.emit('subscribe', $('#symbol').val(), function (set) {
                alert('操作成功!' + JSON.stringify(set));
            });
            
socket.emit('unsubscribe',$('#symbol').val(), function (set) {
                alert('操作成功!'+JSON.stringify(set));

            });
</pre>