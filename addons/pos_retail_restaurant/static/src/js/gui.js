odoo.define('pos_restaurant_kitchen.gui', function (require) {
    "use strict";
    var gui = require('point_of_sale.gui');

    gui.Gui.include({
        show_popup: function (name, options) {
            if (this.pos.config.screen_type != 'kitchen') {
                return this._super(name, options);
            } else {
                return null;
            }
        },
    });
})
