#coding:utf-8

DeviceActiveListKeyHash = 'blue_earth.device.active.list'  # 存放所有上线设备id {a:Time,b:Time}

DeviceCommandQueue = 'blue_earth.device.command.queue.{device_type}.{device_id}'

DeviceSequence = 'blue_earth.device.sequence'

DeviceChannelPub = 'blue_earth.device.channel.pub.{device_id}' # 设备所有原始数据读取之后分发的通道

DeviceAppChannelPub = 'blue_earth.device.app.channel.pub.{device_id}'  # 设备监控应用通道，所有的前端系统将订阅此通道将监控信息推送到前端App

DevicePositionLastest = 'blue_earth.device.position.lastest.{device_id}' # 设备当前的坐标和运行信息

DevicePositionRequestTimeKey = 'blue_earth.device.position.request.time.{}' # 发送定位设备请求命令的时间

DeviceLandingServerKey = 'blue_earth.device.landing_server.{}'       # 记录设备接入服务器 {url,landing_time}

DeviceShareCodeCreateTimeKey = 'blue_earth.device.share_code.create_time.{}' # 分享码的生成时间


MaxLiveTimeDeviceLandingServerKey = 60*8
