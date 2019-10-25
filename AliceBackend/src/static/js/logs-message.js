/**
 *  quotes.js
 *  行情订阅
 */



String.prototype.format = function() {
 if(arguments.length == 0) return this;
 var param = arguments[0];
 var s = this;
 if(typeof(param) == 'object') {
  for(var key in param)
   s = s.replace(new RegExp("\\{" + key + "\\}", "g"), param[key]);
  return s;
 } else {
  for(var i = 0; i < arguments.length; i++)
   s = s.replace(new RegExp("\\{" + i + "\\}", "g"), arguments[i]);
  return s;
 }
}

$(function() {
    // socket = io.connect('/quotes');
    socket = io.connect(log_server);
    // socket = io.connect('http://localhost:18808/quotes');

    socket.on('connect', function () {
        $('#status').addClass('connected');
        $('#status').text('已连接');
    });

    socket.on('error', function (e) {
        console.debug(JSON.stringify(e));

    });

    socket.on('data', function (icon,m) {
        let tr= "<tr >\
        <td >{0}</td>\
        <td >{1}</td>\
        <td >{2}</td>\
        <td >{3}</td>\
        <td >{4}</td>\
        <td >{5}</td>\
        </tr>".format(m.issue_time,m.strategy_id,m.code,m.level,m.title,m.message);
        // alert(JSON.stringify($('message_table tr:eq(0)')) );
        $('#message_table tr:eq(0)').after(
            tr
        );


    });


    // 订阅指定策略编号的运行消息
    socket.emit('subscribe', strategy_id, function (set) {
            // alert('订阅成功!' + JSON.stringify(set));
        });


});

