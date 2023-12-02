




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
        dom: '<"newtoolbar">rt',
        ajax: {
            url: '/api/mkstable',
            data: function (data) {
                console.log($.extend(data, {}))
                return {"draw": data.draw, "start": 1, "length": 100, "stash": $('#stash-select').val()}
            },
            type: 'GET',
            dateType: 'json',
            dataSrc: function (json) {
                let result = []
                json.data.forEach(function (e) {
                    result.push({'_data': e})
                })
                return result
            }
        },
        columns: [
            tE(0), tE(1), tE(2), tE(3), tE(4), tE(5), tE(6), tE(7), tE(8), tE(9)
        ],
    });

    function tE(i){
        return {
            render: function (data, type, row, meta){
                return row._data[i]
            },
        }
    }

    $('#stash-select').on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {
        t.ajax.reload();
    })

    $('div.newtoolbar').append($('#type-select-div'))


});
