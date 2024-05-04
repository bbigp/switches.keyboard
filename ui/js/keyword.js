




$(window).on('load', function () {



    $.fn.DataTable.ext.pager.numbers_length = 5;

    var t = $('#demo-dt-addrow').DataTable({
        processing: true,//当表格在处理的时候（比如排序操作）是否显示“处理中...”,默认false
        serverSide: true,// 服务端分页
        searching: true,
        pageLength: 10,
        pagingType: "simple_numbers",
        ordering: false,// 排序功能
        responsive: true,
        info: true,
        lengthChange: true,
        lengthMenu: [15, 20, 100],
        language: {
            processing: "数据加载中...",
            infoEmpty: "无记录",
            info: "当前 _START_ 到 _END_ , 共 _TOTAL_ 条",
            sEmptyTable: "数据为空",
            sZeroRecords: "数据为空",
            paginate: {
                first: '首页',
                previous: '<i class="demo-psi-arrow-left"></i>',
                next: '<i class="demo-psi-arrow-right"></i>'
            }
        },
        dom: '<"newtoolbar">frtlip',//https://blog.csdn.net/WuLex/article/details/86385619
        ajax: {
            url: '/api/v2/keyword',
            data: function (data) {
                console.log($.extend(data, {}))
                return {"draw": data.draw, "start": data.start, "length": data.length, "t": $('#type-select').val(), "s": data.search.value}
            },
            type: 'GET',
            dateType: 'json',
            dataSrc: function (json) {
                return json.page_list
            }
        },
        columns: [
            {data: "word"},
            {data: "type"},
            {data: "rank"},
            {data: "memo"},
            {
                data: "count",
                render: function (data, type, row, meta){
                    if (data === -1) {
                        return '--'
                    }
                    return data
                }
            },
            {data: null},
        ],
        columnDefs: [
            {
                targets: [-1],
                render: function (data, type, row, meta) {
                    let _r = '<button class="edit-btn btn btn-xs btn-default">编辑</button>'
                        + '<button class="delete-btn btn btn-xs btn-pink-basic">删除</button>';
                    return _r;
                }
            }
        ]
    });

    $('#type-select').on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {
        t.ajax.reload();
        // console.log($(this).val())
    })

    $('div.newtoolbar').append($('#type-select-div'))


    $('#add-btn').click(function () {
        $('#row-id').text('')
        $('#rank-input').val('0')
        $('#memo-input').val('')
        $('#word-input').val('')
        $('select[name=keyword-type]').selectpicker('val', [$('#type-select').val()]).attr('disabled', false)
        $('#demo-default-modal').modal('show')
    })

    $('#confirm-btn').click(function () {
        $.ajax({
             type: 'POST',
             url: '/api/v2/keyword',
             contentType: 'application/json',
             data: JSON.stringify({
                 'id': $('#row-id').text(),
                 'rank': $('#rank-input').val(),
                 'word': $('#word-input').val(),
                 'type': $('#type-select-modal').val(),
                 'memo': $('#memo-input').val()
             }),
             dataType: 'json',
             success: function (data) {
                 console.log(data)
                 if (data.status === 'ok') {
                     $('#demo-default-modal').modal('hide')
                     t.ajax.reload();
                 }else {

                 }
             },
             error: function (err) {
                 console.log(err)
             }
         })

    })

    $('#demo-dt-addrow').on('click', 'button.edit-btn', function () {
        let w = $(this).parent().parent().children().eq(0).text()
        $('#row-id').text(w)
        $('#word-input').val(w)
        $('select[name=keyword-type]').selectpicker('val', [$(this).parent().parent().children().eq(1).text()]).attr('disabled', true)
        $('#rank-input').val($(this).parent().parent().children().eq(2).text())
        $('#memo-input').val($(this).parent().parent().children().eq(3).text())
        $('#demo-default-modal').modal('show')
    }).on('click', 'button.delete-btn', function (){
        $.ajax({
             type: 'DELETE',
             url: '/api/v2/keyword',
             contentType: 'application/json',
             data: JSON.stringify({
                 'word': $(this).parent().parent().children().eq(0).text(),
                 'type': $(this).parent().parent().children().eq(1).text()
             }),
             dataType: 'json',
             success: function (data) {
                 console.log(data)
                 if (data.status === 'ok') {
                    t.ajax.reload();
                 }else {
                    $.niftyNoty({
                        type: 'danger',
                        icon : 'pli-cross icon-2x',
                        message : '<strong>' + data.msg +'</strong>',
                        container : 'floating',
                        timer : 5000
                    });
                 }
             },
             error: function (err) {
                 console.log(err)
             }
         })
    })






});
