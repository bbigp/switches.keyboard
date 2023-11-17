




$(window).on('load', function () {

    var myData = [];
     $('#word-input').typeahead({
         source: function (query, process) {
             if (myData.length === 0) {
                 $.get('/api/mkslist?length=100000', function (data, status) {
                     for (var i = 0; i < data.page_list.length; i++){
                         myData.push(data.page_list[i].name)
                     }
                 })
             }
             return process(myData)
         }
     });


    $.fn.DataTable.ext.pager.numbers_length = 5;

    var t = $('#demo-dt-addrow').DataTable({
        processing: true,//当表格在处理的时候（比如排序操作）是否显示“处理中...”,默认false
        serverSide: true,// 服务端分页
        searching: true,
        pageLength: 100,
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
            paginate: {
                first: '首页',
                previous: '<i class="demo-psi-arrow-left"></i>',
                next: '<i class="demo-psi-arrow-right"></i>'
            }
        },
        dom: '<"newtoolbar">frtlip',//https://blog.csdn.net/WuLex/article/details/86385619
        ajax: {
            url: '/api/box',
            data: function (data) {
                console.log($.extend(data, {}))
                return {"draw": data.draw, "name": $('#type-select').val()}
            },
            type: 'GET',
            dateType: 'json',
            dataSrc: function (json) {
                return json.page_list
            }
        },
        columns: [
            {data: "name"},
            {data: "deleted"},
            {data: "create_time"},
            {data: null},
        ],
        columnDefs: [
            {
                targets: [-1],
                render: function (data, type, row, meta) {
                    let _r = '<button class="delete-btn btn btn-xs btn-pink-basic">删除</button>';
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
        $('#word-input').val('').attr('disabled', false)
        $('#demo-default-modal').modal('show')
    })

    $('#confirm-btn').click(function () {
        $.ajax({
             type: 'POST',
             url: '/api/keyword',
             contentType: 'application/json',
             data: JSON.stringify({
                 'rank': $('#rank-input').val(),
                 'word': $('#word-input').val(),
                 'type': $('#type-select-modal').val()
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

    $('#demo-dt-addrow').on('click', 'button.delete-btn', function (){
        $.ajax({
             type: 'DELETE',
             url: '/api/keyword',
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

                 }
             },
             error: function (err) {
                 console.log(err)
             }
         })
    })






});
