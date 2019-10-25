/**
 *  quotes.js
 *  行情订阅
 */

$(function() {
    socket = io.connect('/quotes');
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
        $('#sub_quotes').text(JSON.stringify(tick));
        $('#counter').text(counter);
        $('#q_symbol').text(tick.symbol);
        $('#q_datetime').text(tick.date + ' ' + tick.time);
        $('#q_lastPrice').text(tick.lastPrice);
        $('#q_openInterest').text(tick.openInterest);
        $('#q_askPrice1').text(tick.askPrice1);
        $('#q_askVolume1').text(tick.askVolume1);
        $('#q_bidPrice1').text(tick.bidPrice1);
        $('#q_bidVolume1').text(tick.bidVolume1);


    });


    // DOM manipulation
    $(function () {
        $('#btn_sub').click(function (ev) {
            socket.emit('subscribe', $('#symbol').val(), function (set) {
                alert('操作成功!' + JSON.stringify(set));
            });
            return false;
        });
        $('#btn_unsub').click(function (e) {
            socket.emit('unsubscribe',$('#symbol').val(), function (set) {
                alert('操作成功!'+JSON.stringify(set));

            });
        });

    });

});