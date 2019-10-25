/**
 *  quotes.js
 *  行情订阅
 */

$(function() {

    return ;
    /*
    socket = io.connect(quotes_server);

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
    });

    // 根据 变量 subscribed_symbols 开始订阅
    let symbols = subscribed_symbols.split(',')
    for(let n in symbols){
        socket.emit('subscribe', symbols[n], function (set) {
                // alert('订阅成功!' + JSON.stringify(set));
            });
    }
    */
});