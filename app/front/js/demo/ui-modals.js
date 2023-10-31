




 $(document).ready(function() {

     var myData = [];
     $('#studio-inputnormal').typeahead({
         source: function (query, process) {
             if (myData.length === 0) {
                 $.get('/api/keyword', function (data, status) {
                     myData = data
                 })
             }
             return process(myData)
         }
     });



     $('#cancel-btn').click(function (){
         window.location.replace('/p/mkslist')
     })

    let uploadType = 1;

     var simplemde = new SimpleMDE({
         element: document.getElementById("editor"),
         toolbar: [
             {
                 name: 'bold',
                 action: SimpleMDE.toggleBold,
                 className: "fa fa-bold",
                 title: "粗体",
             },
             {
                 name: 'italic',
                 action: SimpleMDE.toggleItalic,
                 className: 'fa fa-italic',
                 title: '斜体'
             },
             '|',
             {
                 name: 'link',
                 action: SimpleMDE.drawLink,
                 className: 'fa fa-link',
                 title: '链接'
             },
             {
                 name: 'image',
                 action: SimpleMDE.drawImage,
                 className: 'fa fa-picture-o',
                 title: '图片'
             },
             '|',
             {
                 name: 'preview',
                 action: SimpleMDE.togglePreview,
                 className: 'fa fa-eye no-disable',
                 title: '预览'
             },
             {
                 name: 'side-by-side',
                 action: SimpleMDE.toggleSideBySide,
                 className: 'fa fa-columns no-disable no-mobile',
                 title: '预览模式'
             },
             {
                 name: 'fullscreen',
                 action: SimpleMDE.toggleFullScreen,
                 className: 'fa fa-arrows-alt no-disable no-mobile',
                 title: '全屏'
             },
             '|',
             {
                 name: 'custom',
                 action: function customFunction(editor) {
                     uploadType = 2
                     $('#demo-default-modal').modal('show')
                 },
                 className: 'fa fa-unsorted',
                 title: '插入图片'
             }
         ]
     });
     simplemde.value($('#desc-input').val())
     $('#save-btn').click(function () {
         console.log(simplemde.markdown(simplemde.value()))
         let light_pipe = $('input[name=light-pipe-inline-form-radio]:checked').val()
         if (light_pipe === '其它') {
             light_pipe = $('#light-pipe-other-input').val()
         }
         const data = {
             id: $('#id-input').val(),
             name: $('#name-inputsmall').val(),
             pic: $('#main-pic-img').attr('src'),
             studio: $('#studio-inputnormal').val(),
             manufacturer: $('#manufacturer-select').val(),
             type: $('#type-select').val(),
             tag: $('#tag-inputlarge').val(),
             quantity: $('#quantity-input').val(),
             price: $('#price-input').val(),
             desc: simplemde.value(),
             specs: {
                 actuation_force: $('#act-force-input').val(),
                 actuation_force_p: $('#act-force-p-input').val(),
                 end_force: $('#end-force-input').val(),
                 end_force_p: $('#end-force-p-input').val(),
                 pre_travel: $('#pre-travel-input').val(),
                 pre_travel_p: $('#pre-travel-p-input').val(),
                 total_travel: $('#total-travel-input').val(),
                 total_travel_p: $('#total-travel-p-input').val(),
                 pin: $('input[name=pin-inline-form-radio]:checked').val(),
                 top: $('#top-input').val(),
                 bottom: $('#bottom-input').val(),
                 stem: $('#stem-input').val(),
                 spring: $('#spring-inputlarge').val(),
                 light_pipe: light_pipe,
             }
         }
         $.ajax({
             type: 'POST',
             url: '/api/mks',
             contentType: 'application/json',
             data: JSON.stringify(data),
             dataType: 'json',
             success: function (data) {
                 console.log(data)
                 if (data.status === 'ok') {
                     window.location.replace('/p/mkslist')
                 }else {

                 }
                 // window.location.href = ''
             },
             error: function (err) {
                 console.log(err)
             }
         })
         console.log(data)
     })


     $('#download-pic-btn').click(function () {
         const url = $('#download-pic-input').val()
         $.ajax({
             type: 'POST',
             url: '/api/download_pic',
             contentType: 'application/json',
             data: JSON.stringify({url: url}),
             dataType: 'json',
             success: function (data) {
                 $('#cropper-main-pic-img').attr('src', data.data)
             },
             error: function (err) {
                 console.log(err)
             }
         })
     });

     $('#cropper-btn').click(function () {
         initcropper()
         cropper.clear()
     })

     var cropper = null
     function initcropper(){
         let aspectRatio;
         if (uploadType === 1) {
             aspectRatio = 13 / 10
         }
         cropper = new Cropper(document.getElementById('cropper-main-pic-img'),
         {
             aspectRatio: aspectRatio,
             viewMode: 1,
             preview:'.small',//开启预览效果
             dragMode:'move',//参数：move-能够移动图片和框，crop-拖拽新建框
             modal:true,//是否开启遮罩，将未选中的地方暗色处理
             guides:true,//是否显示裁剪的虚线
             highlight:true,//将选中的区域亮色处理
             background:true,//是否显示网格背景
             center:true,//裁剪框是否在图片的中心
             autoCrop:true,//当初始化的时候（是否自动显示裁剪框）.
             autoCropArea:0.8,//当初始化时，裁剪框的大小与原图的比例 0.8是默认，1是1比1
             zoomable:true,//是否能够缩放图片 false为不能放大缩小
             zoomOnTouch:true,//是否能够经过触摸的形式来放大图片(手机端)
             zoomOnWheel:true,//是否容许用鼠标来放大货缩小图片
             wheelZoomRatio:0.2,//设置鼠标控制缩放的比例
             cropBoxMovable:true,//是否能够移动裁剪框 裁剪框不动，图片动。当movable:true
             cropBoxResizable:true,//是否能够调整裁剪框的大小，默认true
             crop: function (event) {
                // console.log(event)
             },
         })
     }

     $('#confirm-cropper-btn').click(function (){
         cropper.getCroppedCanvas().toBlob((blob) => {
             const formData = new FormData();
             formData.append('image', blob/*, 'example.png' */);
             $.ajax('/api/upload_pic', {
                 method: 'POST',
                 data: formData,
                 processData: false,
                 contentType: false,
                 success(data) {
                     if (uploadType === 1) {
                         $('#main-pic-img').attr('src', data.data)
                     } else{
                         simplemde.value(simplemde.value() + '\n![](' + data.data + ')')
                     }
                     $('#download-pic-input').val('')
                     $('#cropper-main-pic-img').attr('src', '')
                     cropper.destroy()
                     $('#demo-default-modal').modal('hide')
                     uploadType = 1
                 },
                 error(err) {
                     console.log(err);
                 },
             });
         });
     })

     $('#cancel-cropper-btn').click(function (){
         if (cropper){
             cropper.destroy()
         }
         uploadType = 1
         $('#demo-default-modal').modal('hide')
     })



    // BOOTBOX - ALERT MODAL
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    // =================================================================
    $('#demo-bootbox-alert').on('click', function(){
        bootbox.alert("Hello world!", function(){
            $.niftyNoty({
                type: 'info',
                icon : 'pli-exclamation icon-2x',
                message : 'Hello world callback',
                container : 'floating',
                timer : 5000
            });
        });
    });



    // BOOTBOX - CONFIRM MODAL
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    // =================================================================
    $('#demo-bootbox-confirm').on('click', function(){
        bootbox.confirm("Are you sure?", function(result) {
            if (result) {
                $.niftyNoty({
                    type: 'success',
                    icon : 'pli-like-2 icon-2x',
                    message : 'User confirmed dialog',
                    container : 'floating',
                    timer : 5000
                });
            }else{
                $.niftyNoty({
                    type: 'danger',
                    icon : 'pli-cross icon-2x',
                    message : 'User declined dialog.',
                    container : 'floating',
                    timer : 5000
                });
            };

        });
    });



    // BOOTBOX - PROMPT MODAL
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    // =================================================================
    $('#demo-bootbox-prompt').on('click', function(){
        bootbox.prompt("What is your name?", function(result) {
            if (result) {
                $.niftyNoty({
                    type: 'success',
                    icon : 'pli-consulting icon-2x',
                    message : 'Hi ' + result,
                    container : 'floating',
                    timer : 5000
                });
            }else{
                $.niftyNoty({
                    type: 'danger',
                    icon : 'pli-cross icon-2x',
                    message : 'User declined dialog.',
                    container : 'floating',
                    timer : 5000
                });
            };
        });
    });



    // BOOTBOX - CUSTOM DIALOG
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    // =================================================================
    $('#demo-bootbox-custom').on('click', function(){
        bootbox.dialog({
            message: "I am a custom dialog",
            title: "Custom title",
            buttons: {
                success: {
                    label: "Success!",
                    className: "btn-success",
                    callback: function() {
                        $.niftyNoty({
                            type: 'success',
                            message : '<strong>Well done!</strong> You successfully read this important alert message. ',
                            container : 'floating',
                            timer : 5000
                        });
                    }
                },

                danger: {
                    label: "Danger!",
                    className: "btn-danger",
                    callback: function() {
                        $.niftyNoty({
                            type: 'danger',
                            message : '<strong>Oh snap!</strong> Change a few things up and try submitting again.',
                            container : 'floating',
                            timer : 5000
                        });
                    }
                },

                main: {
                    label: "Click ME!",
                    className: "btn-primary",
                    callback: function() {
                        $.niftyNoty({
                            type: 'primary',
                            message : "<strong>Heads up!</strong> This alert needs your attention, but it's not super important.",
                            container : 'floating',
                            timer : 5000
                        });
                    }
                }
            }
        });
    });



    // BOOTBOX - CUSTOM HTML CONTENTS
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    // =================================================================
    $('#demo-bootbox-custom-h-content').on('click', function(){
        bootbox.dialog({
            title: "That html",
            message: '<div class="media"><div class="media-left"><img class="media-object img-lg img-circle" src="img/profile-photos/3.png" alt="Profile picture"></div><div class="media-body"><p class="text-semibold text-main">You can also use <strong class="text-primary">HTML</strong></p>Cras sit amet nibh libero, in gravida nulla. Nulla vel metus scelerisque ante sollicitudin commodo. Cras purus odio, vestibulum in vulputate at, tempus viverra turpis. Fusce condimentum nunc ac nisi vulputate fringilla.</div></div>',
            buttons: {
                confirm: {
                    label: "Save"
                }
            }
        });
    });



    // BOOTBOX - CUSTOM HTML FORM
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    // =================================================================
    $('#demo-bootbox-custom-h-form').on('click', function(){
        bootbox.dialog({
            title: "This is a form in a modal.",
            message:'<div class="row"> ' + '<div class="col-md-12"> ' +
                    '<form class="form-horizontal"> ' + '<div class="form-group"> ' +
                    '<label class="col-md-4 control-label" for="name">Name</label> ' +
                    '<div class="col-md-4"> ' +
                    '<input id="name" name="name" type="text" placeholder="Your name" class="form-control input-md"> ' +
                    '<span class="help-block"><small>Here goes your name</small></span> </div> ' +
                    '</div> ' + '<div class="form-group"> ' +
                    '<label class="col-md-4 control-label" for="awesomeness">How awesome is this?</label> ' +
                    '<div class="col-md-8"> <div class="form-block"> ' +
                    '<label class="form-radio form-icon demo-modal-radio active"><input type="radio" autocomplete="off" name="awesomeness" value="Really awesome" checked> Really awesome</label>' +
                    '<label class="form-radio form-icon demo-modal-radio"><input type="radio" autocomplete="off" name="awesomeness" value="Super awesome"> Super awesome </label> </div>' +
                    '</div> </div>' + '</form> </div> </div><script></script>',
            buttons: {
                success: {
                    label: "Save",
                    className: "btn-purple",
                    callback: function() {
                        var name = $('#name').val();
                        var answer = $("input[name='awesomeness']:checked").val();

                        $.niftyNoty({
                            type: 'purple',
                            icon : 'fa fa-check',
                            message : "Hello " + name + ".<br> You've chosen <strong>" + answer + "</strong>",
                            container : 'floating',
                            timer : 4000
                        });
                    }
                }
            }
        });

        $(".demo-modal-radio").niftyCheck();
    });



    // BOOTBOX - ZOOM IN/OUT ANIMATION
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    //
    // Animate.css
    // http://daneden.github.io/animate.css/
    // =================================================================
    $('#demo-bootbox-zoom').on('click', function(){
        bootbox.confirm({
            message : "<p class='text-semibold text-main'>Zoom In/Out</p><p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.</p>",
            buttons: {
                confirm: {
                    label: "Save"
                }
            },
            callback : function(result) {
                //Callback function here
            },
            animateIn: 'zoomInDown',
            animateOut : 'zoomOutUp'
        });
    });



    // BOOTBOX - BOUNCE IN/OUT ANIMATION
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    //
    // Animate.css
    // http://daneden.github.io/animate.css/
    // =================================================================
    $('#demo-bootbox-bounce').on('click', function(){
        bootbox.confirm({
            message : "<p class='text-semibold text-main'>Bounce</p><p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.</p>",
            buttons: {
                confirm: {
                    label: "Save"
                }
            },
            callback : function(result) {
                //Callback function here
            },
            animateIn: 'bounceIn',
            animateOut : 'bounceOut'
        });
    });



    // BOOTBOX - RUBBERBAND & WOBBLE ANIMATION
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    //
    // Animate.css
    // http://daneden.github.io/animate.css/
    // =================================================================
    $('#demo-bootbox-ruberwobble').on('click', function(){
        bootbox.confirm({
            message : "<p class='text-semibold text-main'>RubberBand & Wobble</p><p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.</p>",
            buttons: {
                confirm: {
                    label: "Save"
                }
            },
            callback : function(result) {
                //Callback function here
            },
            animateIn: 'rubberBand',
            animateOut : 'wobble'
        });
    });



    // BOOTBOX - FLIP IN/OUT ANIMATION
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    //
    // Animate.css
    // http://daneden.github.io/animate.css/
    // =================================================================
    $('#demo-bootbox-flip').on('click', function(){
        bootbox.confirm({
            message : "<p class='text-semibold text-main'>Flip</p><p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.</p>",
            buttons: {
                confirm: {
                    label: "Save"
                }
            },
            callback : function(result) {
                //Callback function here
            },
            animateIn: 'flipInX',
            animateOut : 'flipOutX'
        });
    });



    // BOOTBOX - LIGHTSPEED IN/OUT ANIMATION
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    //
    // Animate.css
    // http://daneden.github.io/animate.css/
    // =================================================================
    $('#demo-bootbox-lightspeed').on('click', function(){
        bootbox.confirm({
            message : "<p class='text-semibold text-main'>Light Speed</p><p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.</p>",
            buttons: {
                confirm: {
                    label: "Save"
                }
            },
            callback : function(result) {
                //Callback function here
            },
            animateIn: 'lightSpeedIn',
            animateOut : 'lightSpeedOut'
        });
    });



    // BOOTBOX - SWING & HINGE IN/OUT ANIMATION
    // =================================================================
    // Require Bootbox
    // http://bootboxjs.com/
    //
    // Animate.css
    // http://daneden.github.io/animate.css/
    // =================================================================
    $('#demo-bootbox-swing').on('click', function(){
        bootbox.confirm({
            message : "<p class='text-semibold text-main'>Swing & Hinge</p><p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.</p>",
            buttons: {
                confirm: {
                    label: "Save"
                }
            },
            callback : function(result) {
                //Callback function here
            },
            animateIn: 'swing',
            animateOut : 'hinge'
        });
    });


 })
