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
        processing: true,//当表格在处理的时候（比如排序操作）是否显示“处理中...”,默认false
        serverSide: true,// 服务端分页
        searching: true,
        pageLength: 10,
        pagingType: "simple_numbers",
        ordering: false,// 排序功能
        responsive: true,
        info: true,
        lengthChange: true,
        lengthMenu: [10, 20, 100],
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
            url: '/api/mkslist',
            data: function (data) {
                console.log($.extend(data, {}))
                return {"draw": data.draw, "start": data.start, "length": data.length, "s": data.search.value}
            },
            type: 'GET',
            dateType: 'json',
            dataSrc: function (json) {
                return json.page_list
            }
        },
        columns: [
            {
                data: "pic",
                render: function (data, type, row, meta) {
                    return '<img style="width: 96px;height: 74px;display: block;margin: auto auto;" class="main-pic" src="' + row.pic +'"/>'
                }
            },
            {
                data: "name",
                render: function (data, type, row, meta){
                    if (row.variation === '') {
                        return data;
                    }
                    return data + ' <span class="badge badge-danger">' + row.variation.split(' ').length + '</span>'
                }
            },
            {data: "studio"},
            {
                data: "manufacturer",
                render: function (data) {
                    if (data === '无') {
                        return '<span class="label label-danger">' + data + '</span>'
                    }
                    return '<span class="label label-default" style="font-size: 90%">' + data + '</span>'
                }
            },
            {
                data: "type",
                render: function (data, type, row, meta) {
                    if (data === '轻压力线性轴') {
                        return '<span class="label" style="background-color: #F57AC0;font-size: 90%">' + data + '</span>'
                    }else if (data === '线性快轴') {
                        return '<span class="label" style="background-color: #049FD7;font-size: 90%">' + data + '</span>'
                    }else if (data === '静音线性轴' || data === '静音段落轴'){
                        return '<span class="label" style="background-color: #f38234;font-size: 90%">' + data + '</span>'
                    } else if(data === '无') {
                        return '<span class="label label-danger" style="">' + data + '</span>'
                    } else if(data === '段落轴') {
                        return '<span class="label" style="background-color: #8F4F04;font-size: 90%">' + data + '</span>'
                    }
                    return '<span class="label label-default" style="font-size: 90%">' + data + '</span>'
                }
            },
            {data: 'logo', defaultContent: ''},
            {
                data:"stash",
                render: function (data) {
                    if (data === '') {
                        return '<span class="label label-danger">-</span>'
                    }
                    return data;
                }
            },
            {
                data: "tag",
                render: function (data, type, row, meta){
                    return data + ' ' + row.variation
                }
            },
            {
                render: function (data, type, row, meta) {
                    if (row.specs == null) {
                        return ''
                    }
                    return appendP('触发压力', row.specs.actuation_force, row.specs.actuation_force_p, 'g')
                        + appendP('触底压力', row.specs.end_force, row.specs.end_force_p, 'g')
                        + appendP('触发行程', row.specs.pre_travel, row.specs.pre_travel_p, 'mm')
                        + appendP('触底行程', row.specs.total_travel, row.specs.total_travel_p, 'mm')
                }
            },
            {
                render: function (data, type, row, meta) {
                    if (row.specs == null) {
                        return ''
                    }
                    let top = row.specs.top === '' ? '<strong style="color: #d9534f;">???</strong>' : row.specs.top
                    let bottom = row.specs.bottom === '' ? '<strong style="color: #d9534f;">???</strong>' : row.specs.bottom
                    let stem = row.specs.stem === '' ? '<strong style="color: #d9534f;">???</strong>' : row.specs.stem
                    let spring = row.specs.spring === '' ? '<strong style="color: #d9534f;">???</strong>' : row.specs.spring
                    return '<div>上盖: ' + top + '</div>'
                        + '<div>底壳: ' + bottom + '</div>'
                        +'<div>轴心: ' + stem + '</div>'
                        + '<div>弹簧: ' + spring +'</div>'
                }
            },
            {
                render: function (data, type, row, meta) {
                    if (row.specs == null) {
                        return ''
                    }
                    let pin = row.specs.pin === '' ? '<strong style="color: #d9534f;">???</strong>脚' : row.specs.pin
                    let light_pipe = row.specs.light_pipe === '' ? '<strong style="color: #d9534f;">???</strong>' : row.specs.light_pipe
                    return '<span>' + pin + ',' + light_pipe +'导光柱</span>'
                }
            },
            {data: "quantity", render: function (data, type, row, meta){
                    if (data > 0) {
                        return data;
                    }
                    return '<span class="label label-danger">0</span>'
                }},
            {data: "price", defaultContent: ""},
            {data: "create_time", defaultContent: ""},
            {data: null}
        ],
        columnDefs: [
            {
                targets: [-1],
                render: function (data, type, row, meta) {
                    var jumpUrl = '/p/mks/' + row.id
                    let _r = '<a href="' +  jumpUrl + '"><button class="btn btn-xs btn-pink-basic">编辑</button></a>';
                    if (row.desc !== ''){
                        _r += '<button style="margin-left: 5px;" class="btn btn-xs btn-default other-btn" data="' + row.desc + '">其他</button>'
                    }
                    return _r;
                }
            }
        ]
    });

    function appendP(s, a, b, e){
        let r = '<div>' + s + ': '
        if (a === '') {
            r = r + '<strong style="color: #d9534f;">???</strong>'
            return r;
        }
        r += a
        if (b === '') {
            r = r + e + '</div>'
            return r;
        }
        r = r + '±' + b + e + '</div>'
        return r;
    }



    $('#demo-dt-addrow').on('click', '.main-pic', function () {
        $('#modal-body').empty()
        $('#demo-default-modal').modal('show')
        $('#show-main-pic-img').attr('src', $(this).attr("src"))
    })

    $('#demo-dt-addrow').on('click', '.other-btn', function () {
        // console.log(this.attributes.data.value)
        $('#show-main-pic-img').attr('src', '')
        let data = this.attributes.data.value
        if (data !== '') {
            // console.log(SimpleMDE.prototype.markdown(data))
            let d = SimpleMDE.prototype.markdown(data).replaceAll('<img', '<img style="max-width:100%;height:auto;"')
            $('#modal-body').empty().append(d)
        }
        $('#demo-default-modal').modal('show')

    })

    $('#close-btn').click(function (){
        $('#show-main-pic-img').attr('src', '')
        $('#demo-default-modal').modal('hide')
    })


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
