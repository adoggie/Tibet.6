/**

 */


function show_boll(){
    let lasttime = null ;
    let num =$('#k_num').val();
    let cycle = $('#k_cycle').val();
    lasttime =$('#date').val() + ' ' + $('#time2').val();
     $.ajax({
                url:'/fisher/api/strategy/chart/boll',
                method: 'get',
                data:{
                    symbol: code,
                    strategy_id: strategy_id,
                    code : code ,
                    num:num,
                    lasttime: lasttime,
                    cycle: cycle
                },
                success:function (data,status,xhr) {
                    result = data.result;
                    // alert(JSON.stringify(data));
                    $('#img_boll').attr('src',result);
                },
                error:function (xhr,status,error) {

                }
            });
}

function show_ticks(){
    let lasttime = null ;
    let firsttime = null;

    firsttime =$('#date').val() + ' ' + $('#tick_time1').val();
    lasttime =$('#date').val() + ' ' + $('#tick_time2').val();
     $.ajax({
                url:'/fisher/api/strategy/ticks',
                method: 'get',
                data:{
                    symbol: code,
                    strategy_id: strategy_id,
                    code : code ,
                    num:2000,
                    firsttime:firsttime,
                    lasttime:lasttime

                },
                success:function (data,status,xhr) {
                    result = data.result;
                    // alert(JSON.stringify(data));
                    $('#img_ticks').attr('src',result);
                },
                error:function (xhr,status,error) {

                }
            });
}


function show_wr_atr(){

     $.ajax({
                url:'/fisher/api/strategy/chart/wr_atr',
                method: 'get',
                data:{
                    code: code,
                    strategy_id: strategy_id,
                },
                success:function (data,status,xhr) {
                    result = data.result;
                    // alert(JSON.stringify(data));
                    $('#chart_img').attr('src',result.data_base64);
                    $('#issue_time').text(result.issue_time);
                    $('#message').text(result.message);


                },
                error:function (xhr,status,error) {

                }
            });
}

function show_charts(){
    show_wr_atr();
    // show_boll();
    // show_ticks();
}
$(function() {
    // show_boll();
    show_charts();
    window.setInterval(show_charts,5000);
});