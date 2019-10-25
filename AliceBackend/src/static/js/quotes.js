/**
 *  quotes.js
 *  行情订阅
 */

$(function() {
    // socket = io.connect('/quotes');
    socket = io.connect(quotes_server);
    // socket = io.connect('http://localhost:18808/quotes');

    socket.on('connect', function () {
        $('#status').addClass('connected');
        $('#status').text('已连接');
    });

    socket.on('error', function (e) {
        console.debug(JSON.stringify(e));

    });
    var  counter = 0
    socket.on('data', function (symbol,tick) {
        counter +=1;
        $('#'+symbol+"_code").text(symbol);
        $('#'+symbol+'_lastprice').text(tick.LastPrice);
        $('#'+symbol+'_ask1').text(tick.AskPrice1 +"/"+ tick.AskVolume1);
        $('#'+symbol+'_ask2').text(tick.AskPrice2+"/"+ tick.AskVolume2);
        $('#'+symbol+'_ask3').text(tick.AskPrice3+"/"+ tick.AskVolume3);
        $('#'+symbol+'_bid1').text(tick.BidPrice1+"/"+ tick.BidVolume1);
        $('#'+symbol+'_bid2').text(tick.BidPrice2+"/"+ tick.BidVolume2);
        $('#'+symbol+'_bid3').text(tick.BidPrice3+"/"+ tick.BidVolume3);
        $('#'+symbol+'_datetime').text(tick.DateTime);
        $('#'+symbol+'_volume').text(tick.Volume);
        $('#'+symbol+'_uplimit').text(tick.UpperLimitPrice);
        $('#'+symbol+'_downlimit').text(tick.LowerLimitPrice);


    });



    // 根据 变量 subscribed_symbols 开始订阅
    let symbols = subscribed_symbols.split(',')
    for(let n in symbols){
        socket.emit('subscribe', symbols[n], function (set) {
                // alert('订阅成功!' + JSON.stringify(set));
            });
    }

});