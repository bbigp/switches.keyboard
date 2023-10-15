// Tables-DataTables.js
// ====================================================================
// This file should not be included in your project.
// This is just a sample how to initialize plugins or components.
//
// - ThemeOn.net -


$(window).on('load', function () {


    // DATA TABLES
    // =================================================================
    // Require Data Tables
    // -----------------------------------------------------------------
    // http://www.datatables.net/
    // =================================================================

    $.fn.DataTable.ext.pager.numbers_length = 5;


    // Add Row
    // -----------------------------------------------------------------
    var t = $('#demo-dt-addrow').DataTable({
        "processing": true,//当表格在处理的时候（比如排序操作）是否显示“处理中...”,默认false
        "serverSide": true,// 服务端分页
        "searching": true,
        "pageLength": 1,
        "pagingType": "simple_numbers",
        "ordering": false,// 排序功能
        "responsive": true,
        "info": true,
        // "lengthChange": true,
        // "lengthMenu": [10, 20, 100],
        "language": {
            "processing": "数据加载中...",
            "infoEmpty": "无记录",
            "info": "当前 _START_ 到 _END_ , 共 _TOTAL_ 条",
            "paginate": {
                'first': '首页',
                "previous": '<i class="demo-psi-arrow-left"></i>',
                "next": '<i class="demo-psi-arrow-right"></i>'
            }
        },
        "dom": '<"newtoolbar">frtip',
        "ajax": {
            "url": '/a/axlist',
            "data": function (data) {
                console.log($.extend(data, {}))
                return {"draw": data.draw, "start": data.start, "length": data.length, "s": data.search.value}
            },
            "type": 'GET',
            "dateType": 'json',
            "dataSrc": function (json) {
                return json.page_list
            }
        },
        "columns": [
            {
                "data": "pic",
                "defaultContent": ""
            },
            {"data": "name"},
            {"data": "studio"},
            {
                "data": "type",
                "render": function (data, type, row, meta) {
                    return data == null ? '' : data
                }
            },
            {
                "data": "foundry",
                "defaultContent": ""
            },
            {
                "data": "remark",
                "defaultContent": ""
            },
            {
                "data": "operating_force",
                "render": function (data, type, row, meta) {
                    const operating_force = row['operating_force'] == null ? '' : row['operating_force'];
                    const pre_travel = row['pre_travel'] == null ? '' : row['pre_travel'];
                    return operating_force + '|' + pre_travel
                }
            },
            {
                "data": "end_force",
                "render": function (data, type, row, meta) {
                    const end_force = row['end_force'] == null ? '' : row['end_force'];
                    const full_travel = row['full_travel'] == null ? '' : row['full_travel'];
                    return end_force + '|' + full_travel
                }
            },
            {
                "data": "price",
                "defaultContent": ""
            },
            {
                "data": "upper",
                "render": function (data, type, row, meta) {
                    const upper = row['upper'] == null ? '' : row['upper'];
                    const bottom = row['bottom'] == null ? '' : row['bottom'];
                    const shaft = row['shaft'] == null ? '' : row['shaft'];
                    const light_pipe = row['light_pipe'] == null ? '' : row['light_pipe'];
                    return upper + ' | ' + bottom + ' | ' + shaft + ' | ' + light_pipe
                },
            },
            {"data": "create_time"},
            {"data": null}
        ],
        "columnDefs": [
            {
                "targets": [-1],
                "render": function (data, type, row, meta) {
                    var jumpUrl = '/p/ax/' + row.id
                    return '<a href="' +  jumpUrl + '" target="_blank"><button class="btn btn-xs btn-default">编辑</button></a>'
                }
            }
        ]
    });
    $('#demo-custom-toolbar2').appendTo($("div.newtoolbar"));

    $('#refresh-btn').click(function(){
        t.ajax.reload();
    });

    $('#demo-dt-addrow-btn1111').on('click', function () {
        t.row.add([
            'Adam Doe',
            'New Row',
            'New Row',
            2,
            '2015/10/15',
            '$2,000'
        ]).draw();
    });


});
