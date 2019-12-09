odoo.define('pos_restaurant_kitchen.chrome', function (require) {
    "use strict";
    var chrome = require('point_of_sale.chrome');

    // neu la kitchen thi mac dinh dua vao man hinh kitchen
    chrome.Chrome.include({
        build_widgets: function () {
            this._super();
            if (this.pos.config.screen_type && this.pos.config.screen_type == 'kitchen') {
                this.gui.set_startup_screen('kitchen_screen');
                this.gui.set_default_screen('kitchen_screen');
            }
        }
    });

    chrome.OrderSelectorWidget.include({
        renderElement: function () {
            this._super();
            var orders = this.pos.get('orders').models;
            for (var i = 0; i < orders.length; i++) {
                var has_line_waitinng_delivery = orders[i].has_data_need_delivery();
                if (has_line_waitinng_delivery) {
                    var $order_content = $("[data-uid='" + orders[i].uid + "']");
                    $order_content.addClass('order-waiting-delivery');
                } else {
                    var $order_content = $("[data-uid='" + orders[i].uid + "']");
                    $order_content.removeClass('order-waiting-delivery');
                }
            }
        }
    });

    var screens = require('point_of_sale.screens');
    screens.ScreenWidget.include({
        show: function () {
            this._super();
            var config = this.pos.config;
            if (config.screen_type && config.screen_type == 'kitchen') {
                $('.layout-table').replaceWith();
                $('.centerPage').replaceWith();
                $('.collapsed').replaceWith();
                $('.leftpane').replaceWith();
                $('.pos-rightheader').css("right", '0px');
                $('.pos-rightheader').css("left", '90%', 'float', 'right');
                $('.rightpane').replaceWith();
                $('.pos-branding').replaceWith();
                $('.pos-logo').replaceWith();
                $('.username').replaceWith();
                $('.order-selector').replaceWith();
                $('.top-content').replaceWith();
                $('.oe_status ').replaceWith();
                setTimeout(function () {
                    $('.full-content').css("top", '0px');
                }, 500);
            }
        },
        renderElement: function () {
            this._super();
            var config = this.pos.config;
            if (config.screen_type && config.screen_type == 'kitchen') {
                $('.full-content').css("top", '0px');
            }

        }
    });

});
