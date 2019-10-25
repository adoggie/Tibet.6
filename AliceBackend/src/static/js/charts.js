/**

 */


function show_boll(){
     $.ajax({
                url:'/fisher/api/strategy/chart/boll',
                method: 'get',
                data:{
                    symbol: symbol,
                    num:80
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

$(function() {
    show_boll();
    window.setInterval(show_boll,2000);
});