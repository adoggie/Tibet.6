#coding:utf-8

# DeviceActiveListKeyHash = 'blue_earth.device.active.list'  # 存放所有上线设备id {a:Time,b:Time}
#
DeviceCommandQueue = 'smartbox.device.command.queue.{device_type}.{device_id}'
#
# DeviceSequence = 'blue_earth.device.sequence'

DeviceChannelPub = 'smartbox.device.channel.pub.{device_id}' # 设备所有原始数据读取之后分发的通道

DeviceAppChannelPub = 'smartbox.device.app.channel.pub.{device_id}'  # 设备监控应用通道，所有的前端系统将订阅此通道将监控信息推送到前端App

# DeviceChannelPubIoT = 'smartbox.device_channel_iot.{device_id}'  # 推送到绿城+的发布通道
DeviceChannelPubIoT = '{device_id}'  # 推送到绿城+的发布通道

DeviceChannelPubTraverseDown = 'smartbox.down.pub.{device_id}'  # 设备下发控制命令的通道
DeviceChannelPubTraverseUp = 'smartbox.up.pub.{device_id}'      # 设备上行消息分发通道

# DevicePositionLastest = 'blue_earth.device.position.lastest.{device_id}' # 设备当前的坐标和运行信息
#
# DevicePositionRequestTimeKey = 'blue_earth.device.position.request.time.{}' # 发送定位设备请求命令的时间
#
# DeviceLandingServerKey = 'blue_earth.device.landing_server.{}'       # 记录设备接入服务器 {url,landing_time}
#
# DeviceShareCodeCreateTimeKey = 'blue_earth.device.share_code.create_time.{}' # 分享码的生成时间
#

MaxLiveTimeDeviceLandingServerKey = 60*8


DeviceAccessHttpAPI = 'smartbox.device.api_server.{}'       # 记录设备接入服务器 {url,landing_time}
# DeviceActiveListKeyHash = 'smartbox.active_device_list'     # 存放所有上线设备与接入服务器的关联关系
DeviceServerRel = 'smartbox.device_server_rel'     # 存放所有上线设备与接入服务器的关联关系

SensorStatusHash= 'smartbox.sensor.status.{device_id}.{sensor_type}.{sensor_id}' # {device_id}_{sensor_type}_{sensor_id}'
DeviceStatusHash = 'smartbox.device.status.{device_id}'

AppRequestAuthCodeWidthIdsPrefix = 'smartbox.authcode.ids.'
AppRequestAuthCodePrefix = 'smartbox.authcode.data.'