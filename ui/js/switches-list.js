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

    let globalSearch = ''
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
        autoWidth: true,
        stateSave: true,
        stateDuration: 60 * 30,
        stateSaveParams: function(settings, data){
            data.stash = $('#storBoxSelect').val()
        },
        stateLoadParams: function(settings, data) {
            console.log(data)
            console.log(new Date().getTime())
            console.log(data.time)
            console.log(new Date().getTime() - data.time)
            if (new Date().getTime() - data.time < 60 * 30 * 1000) {
                $('#storBoxSelect').val(data.stash)
            }
        },
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
        dom: '<"newtoolbar">frptlpi',//https://blog.csdn.net/WuLex/article/details/86385619
        ajax: {
            url: '/api/v2/switches/filter',
            data: function (data) {
                console.log($.extend(data, {}))
                let storBox = $('#storBoxSelect').val()
                let search = data.search.value.trim()
                let params = {"draw": data.draw, "start": data.start, "length": data.length}
                if(search){
                    params['s'] = search
                }
                if(storBox){
                    if (storBox === '-1'){
                        params['is_available'] = false
                    }else{
                        params['stor_box'] = storBox
                    }
                }
                return params
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
            {data: "name"},
            {
                data: "manufacturer",
                render: function (data, type, row, meta) {
                    let _r = '<div>' + row.studio + '</div>'
                    if (data === '无' || data === '') {
                        return _r
                    }
                    _r += '<div><span class="label label-default" style="font-size: 90%">' + data + '</span></div>'
                    return _r
                }
            },
            {
                data: "type",
                render: function (data, type, row, meta) {
                   if (data === '青轴') {
                       return '<span class="label" style="background-color: #42a5f5;font-size: 90%">' + data + '</span>'
                    }else if (data === '茶轴') {
                       return '<span class="label" style="background-color: #8F4F04;font-size: 90%">' + data + '</span>'
                   }else if (data === '静音线性轴' || data === '静音段落轴'){
                       return '<span class="label" style="background-color: #f38234;font-size: 90%">' + data + '</span>'
                   } else if(data === '提前大段落轴') {
                       return '<span class="label" style="background-color: #3c763d;font-size: 90%">' + data + '</span>'
                    } else if (data === '') {
                       return '<span class="label" style="background-color: #d9534f;font-size: 90%">-</span>'
                    }
                    return '<span class="label label-default" style="font-size: 90%">' + data + '</span>'
                }
            },
            {
                data: 'mark',
                render: function (data) {
                    if (data === '') {
                        return '<span class="label label-danger">-</span>'
                    }
                    return data;
                }
            },
            {
                data:"stor_loc_box",
                render: function (data, type, row, meta) {
                    if (data === '') {
                        return '<span class="label label-danger">-</span>'
                    }
                    let stor = data
                    if (row.stor_loc_row){
                        stor += ':'
                        stor += row.stor_loc_row
                    }
                    if (row.stor_loc_col){
                        stor += '-'
                        stor += row.stor_loc_col
                    }
                    return stor
                }
            },
            {data: "num", render: function (data, type, row, meta){
                    if (data > 0) {
                        return data;
                    }
                    return '<span class="label label-danger">0</span>'
                }
            },
            {
                render: function (data, type, row, meta) {
                    return appendP('触发压力', row.actuation_force, row.actuation_force_tol, 'g')
                        + appendP('触底压力', row.bottom_force, row.bottom_force_tol, 'g')
                        + appendP('触发行程', row.pre_travel, row.pre_travel_tol, 'mm')
                        + appendP('触底行程', row.total_travel, row.total_travel_tol, 'mm')
                }
            },
            {
                render: function (data, type, row, meta) {
                    let top = row.top_mat === '' ? '<strong style="color: #d9534f;">--</strong>' : row.top_mat
                    let bottom = row.bottom_mat === '' ? '<strong style="color: #d9534f;">--</strong>' : row.bottom_mat
                    let stem = row.stem_mat === '' ? '<strong style="color: #d9534f;">--</strong>' : row.stem_mat
                    let spring = row.spring === '' ? '<strong style="color: #d9534f;">--</strong>' : row.spring
                    return '<div>上盖: ' + top + '</div>'
                        + '<div>底壳: ' + bottom + '</div>'
                        +'<div>轴心: ' + stem + '</div>'
                        + '<div>弹簧: ' + spring +'</div>'
                }
            },
            {
                render: function (data, type, row, meta) {
                    let light_style = row.light_style === '' ? '<strong style="color: #d9534f;">--</strong>' : row.light_style
                    let pins = '<strong style="color: #d9534f;">--</strong>'
                    if (row.pins === 3 || row.pins === 5){
                        pins = row.pins
                    }
                    return '<span>' + light_style + ' | ' + pins + '</span>'
                }
            },
            {data: "price", defaultContent: ""},
            {data: "create_time", defaultContent: ""},
            {data: null}
        ],
        columnDefs: [
            {
                targets: [-1],
                render: function (data, type, row, meta) {
                    var jumpUrl = '/control/switches/' + row.id
                    let _r = '<a href="' +  jumpUrl + '"><button class="btn btn-xs btn-pink-basic">编辑</button></a>';
                    _r += '<div><button class="btn btn-xs btn-default copy-btn" data-id="' + row.id + '">创建副本</button></div>'
                    _r += '<div><button class="btn btn-xs btn-default delete-btn" data-id="' + row.id + '">删除</button></div>'
                    if (row.desc !== ''){
                        _r += '<div><button class="btn btn-xs btn-default other-btn" data="' + row.desc + '">其他</button></div>'
                    }
                    return _r;
                }
            }
        ]
    }).on('click', '.main-pic', function () {
        $('#modal-body').empty()
        $('#demo-default-modal').modal('show')
        $('#show-main-pic-img').attr('src', $(this).attr("src"))
    }).on('click', '.other-btn', function () {
        // console.log(this.attributes.data.value)
        $('#show-main-pic-img').attr('src', '')
        let data = this.attributes.data.value
        if (data !== '') {
            // console.log(SimpleMDE.prototype.markdown(data))
            let d = SimpleMDE.prototype.markdown(data).replaceAll('<img', '<img style="max-width:100%;height:auto;"')
            $('#modal-body').empty().append(d)
        }
        $('#demo-default-modal').modal('show')
    }).on('click', '.copy-btn', function () {
        let id = this.attributes['data-id'].value
        $.ajax({type: 'GET', url: '/api/v2/switches/copy?id=' + id,
            success: function (data) {
                if (data.status === 'ok') {
                    t.ajax.reload();
                } else {
                    $.niftyNoty({type: 'danger', icon : 'pli-cross icon-2x', message : '系统错误: <strong>' + data.msg +'</strong>', container : 'floating', timer : 2000});
                }
            },
            error: function (err) {
                $.niftyNoty({type: 'danger', icon : 'pli-cross icon-2x', message : '系统错误', container : 'floating', timer : 2000});
            }
        })
    }).on('click', '.delete-btn', function () {
        let id = this.attributes['data-id'].value
        $.ajax({type: 'DELETE', url: '/api/v2/switches?id=' + id,
            success: function (data) {
                if (data.status === 'ok') {
                    t.ajax.reload();
                } else {
                    $.niftyNoty({type: 'danger', icon : 'pli-cross icon-2x', message : '系统错误: <strong>' + data.msg +'</strong>', container : 'floating', timer : 2000});
                }
            },
            error: function (err) {
                $.niftyNoty({type: 'danger', icon : 'pli-cross icon-2x', message : '系统错误', container : 'floating', timer : 2000});
            }
        })
    })

    function appendP(s, a, b, e){
        let r = '<div>' + s + ': '
        if (a === '' || a == null) {
            r = r + '<strong style="color: #d9534f;">--</strong>'
            return r;
        }
        r += a
        if (b === '' || b == null) {
            r = r + e + '</div>'
            return r;
        }
        r = r + b + e + '</div>'
        return r;
    }



    $('#close-btn').click(function (){
        $('#show-main-pic-img').attr('src', '')
        $('#demo-default-modal').modal('hide')
    })

    $('#storBoxSelect').on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {
        t.ajax.reload();
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
