/**

 */

$(function() {


    // DOM manipulation
    // $(function () {
        $('#btnFilter').click(function (ev) {
            // alert(JSON.stringify($('#orders').combobox('getValue')));
            $.ajax({
                url:'/api/innerbox',
                method: 'get',
                data:{
                    ip: $('#ip').textbox('getValue'),
                    orders: $('#orders').combobox('getValue')
                },
                success:function (data,status,xhr) {
                    result = data.result;
                    // alert(JSON.stringify(data));
                    $('#innerbox_list').datagrid({data:result});
                },
                error:function (xhr,status,error) {
                    
                }
            });

        });

        $('#btnCheckWarning').click(function (ev) {
            $.ajax({
                url:'/api/innerbox/warning_check',
                method: 'get',
                data:{

                },
                success:function (data,status,xhr) {
                    result = data.result;
                    // alert(JSON.stringify(data));
                    $('#innerbox_list').datagrid({data:result});
                },
                error:function (xhr,status,error) {

                }
            });

        });

    // });

});