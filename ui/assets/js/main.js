(function ($) {
    "use strict";
    
    new WOW().init();

    // Slick Slider Activation
    var $sliderActvation = $('.slick_slider_activation');
    if($sliderActvation.length > 0){
        $sliderActvation.slick({
          prevArrow:'<button class="prev_arrow"><i class="icon-arrow-left icons"></i></button>',
          nextArrow:'<button class="next_arrow"><i class="icon-arrow-right icons"></i></button>',
        });
    };

    // Slick Slider Activation
    $('.zoom_tab_img').slick({
        centerMode: true,
        centerPadding: '0',
        slidesToShow: 4,
        arrows:false,
        vertical: true,
        focusOnSelect: true,
        asNavFor: '.product_zoom_main_img',
        responsive:[
            {
              breakpoint: 576,
              settings: {
                slidesToShow: 3,
                 vertical: false,  
                  arrows: false,
              }
            },
            {
              breakpoint: 768,
              settings: {
                  slidesToShow: 4,
              }
            },
            {
              breakpoint: 992,
              settings: {
                slidesToShow: 3,
              }
            },
        ]

    });

      $(window).on('load', function () {
          $(".preloader").addClass("loaded");
      });


// Slick Slider Activation
                $('.product_zoom_main_img').slick({
                    centerMode: true,
                    centerPadding: '0',
                    slidesToShow: 1,
                    arrows:false,
                    vertical: true,
                    draggable: false,      // 禁用鼠标拖动
                    swipe: false,          // 禁用触摸滑动
                    touchMove: false,       // 禁用触摸移动
                    asNavFor: '.zoom_tab_img',
                    responsive:[
                        {
                          breakpoint: 576,
                          settings: {
                             vertical: false,
                             draggable: true,      // 禁用鼠标拖动
                             swipe: true,          // 禁用触摸滑动
                             touchMove: true,       // 禁用触摸移动
                          }
                        },
                    ]
                });

    
    
    /*---canvas menu activation---*/
    $('.canvas_open').on('click', function(){
        $('.offcanvas_menu_wrapper,.body_overlay').addClass('active')
    });
    
    $('.canvas_close,.body_overlay').on('click', function(){
        $('.offcanvas_menu_wrapper,.body_overlay').removeClass('active')
    });
    
    
    //Shopping Cart addClass removeClass
    $('.shopping_cart > a').on('click', function(){
        $('.mini_cart,.body_overlay').addClass('active')
    });
    $('.mini_cart_close a,.body_overlay').on('click', function(){
        $('.mini_cart,.body_overlay').removeClass('active')
    });
    
    
    //Search Box addClass removeClass
    $('.header_search > a').on('click', function(){
        $('.page_search_box').addClass('active')
    });
    $('.search_close > i').on('click', function(){
        $('.page_search_box').removeClass('active')
    });
    
    
    $(document).ready(function() {
      $('select,.select_option').niceSelect();
    });
    
    
      /*---  ScrollUp Active ---*/
    $.scrollUp({
        scrollText: '<i class="ion-android-arrow-up"></i>',
        easingType: 'linear',
        scrollSpeed: 900,
        animation: 'fade'
    });
    
    /*---Off Canvas Menu---*/
    var $offcanvasNav = $('.offcanvas_main_menu'),
        $offcanvasNavSubMenu = $offcanvasNav.find('.sub-menu');
    $offcanvasNavSubMenu.parent().prepend('<span class="menu-expand"><i class="fa fa-angle-down"></i></span>');
    
    $offcanvasNavSubMenu.slideUp();
    
    $offcanvasNav.on('click', 'li a, li .menu-expand', function(e) {
        var $this = $(this);
        if ( ($this.parent().attr('class').match(/\b(menu-item-has-children|has-children|has-sub-menu)\b/)) && ($this.attr('href') === '#' || $this.hasClass('menu-expand')) ) {
            e.preventDefault();
            if ($this.siblings('ul:visible').length){
                $this.siblings('ul').slideUp('slow');
            }else {
                $this.closest('li').siblings('li').find('ul:visible').slideUp('slow');
                $this.siblings('ul').slideDown('slow');
            }
        }
        if( $this.is('a') || $this.is('span') || $this.attr('clas').match(/\b(menu-expand)\b/) ){
        	$this.parent().toggleClass('menu-open');
        }else if( $this.is('li') && $this.attr('class').match(/\b('menu-item-has-children')\b/) ){
        	$this.toggleClass('menu-open');
        }
    });
    



    //Quantity Counter
    $(".pro-qty").append('<a href="#" class="inc qty-btn">+</a>');
      $(".pro-qty").prepend('<a href="#" class= "dec qty-btn">-</a>');
    
      $(".qty-btn").on("click", function (e) {
        e.preventDefault();
        var $button = $(this);
        var oldValue = $button.parent().find("input").val();
        if ($button.hasClass("inc")) {
          var newVal = parseFloat(oldValue) + 1;
        } else {
          // Don't allow decrementing below zero
          if (oldValue > 1) {
            var newVal = parseFloat(oldValue) - 1;
          } else {
            newVal = 1;
          }
        }
        $button.parent().find("input").val(newVal);
    });
    
    
    
})(jQuery);	
