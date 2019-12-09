odoo.define('pos_retail_restaurant.screens', function (require) {
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var floors = require('pos_restaurant.floors')
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var qweb = core.qweb;
    var FloorScreenWidget;
    var SplitbillScreenWidget;

    _.each(gui.Gui.prototype.screen_classes, function (o) {
        if (o.name == 'floors') {
            FloorScreenWidget = o.widget;
            FloorScreenWidget.include({
                start: function () {
                    var self = this;
                    this._super();
                    this.pos.bind('update:floor-screen', function () {
                        self.renderElement();
                    })
                },
            })
        }
        if (o.name == 'splitbill') {
            SplitbillScreenWidget = o.widget;
            SplitbillScreenWidget.include({
                pay: function (order, neworder, splitlines) {
                    var res = this._super(order, neworder, splitlines);
                    return res;
                }
            })
        }
    });

    screens.OrderWidget.include({
        remove_orderline: function (order_line) {
            var res = this._super(order_line);
            if ((order_line.syncing == false || !order_line.syncing) && this.pos.pos_bus) {
                var order = order_line.order.export_as_JSON();
                this.pos.pos_bus.push_message_to_other_sessions({
                    action: 'line_removing',
                    data: {
                        uid: order_line.uid,
                    },
                    bus_id: this.pos.config.bus_id[0],
                    order: order,
                    order_uid: order.uid,
                });
            }
            return res
        },
        update_summary: function () {
            try {
                this._super();
                var delivery_kitchen = this.pos.get_order().has_line_delivery_kitchen();
                var need_delivery = this.pos.get_order().has_data_need_delivery();
                var high_priority = this.pos.get_order().has_line_high_priority();
                var buttons = this.getParent().action_buttons;
                if (buttons && buttons.set_order_done) {
                    buttons.set_order_done.highlight(need_delivery);
                }
                if (buttons && buttons.set_line_exit_high_priority) {
                    buttons.set_line_exit_high_priority.highlight(high_priority);
                }
                if (buttons && buttons.delivery_kitchen) {
                    buttons.delivery_kitchen.highlight(delivery_kitchen);
                }
            } catch (ex) {
                console.log('dont worries, client without table select');
            }
        },
        render_orderline: function (orderline) {
            var self = this;
            var el_node = this._super(orderline);
            var cancel_button = el_node.querySelector('.cancel');
            if (cancel_button) {
                cancel_button.addEventListener('click', function () {
                    orderline.set_state('Cancel');
                });
            }
            var done_button = el_node.querySelector('.done');
            if (done_button) {
                done_button.addEventListener('click', function () {
                    orderline.set_state('Done');
                });
            }
            var error_button = el_node.querySelector('.error');
            if (error_button) {
                error_button.addEventListener('click', function () {
                    orderline.set_state('Error');
                });
            }
            var priority_button = el_node.querySelector('.priority');
            if (priority_button) {
                priority_button.addEventListener('click', function () {
                    orderline.set_state('High-Priority');
                });
            }
            var confirm_button = el_node.querySelector('.confirm');
            if (confirm_button) {
                confirm_button.addEventListener('click', function () {
                    orderline.set_state('Waiting');
                });
            }
            var put_back_button = el_node.querySelector('.put-back');
            if (put_back_button) {
                put_back_button.addEventListener('click', function () {
                    orderline.set_state('Waiting-delivery');
                });
            }
            return el_node;
        }
    });

    floors.TableWidget.include({
        init: function (parent, options) {
            this.pos = parent.pos;
            this._super(parent, options);
        },
        get_order_by_widget: function () {
            var self = this;
            var orders = this.pos.get('orders').models;
            var order = _.find(orders, function (o) {
                return o.table && o.table.id == self.table.id
            });
            return order;
        },
        need_to_order: function () {
            var order = this.get_order_by_widget();
            if (order) {
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line.state == 'Waiting-delivery') {
                        return 1;
                    }
                }
                return 0;
            } else {
                return 0;
            }
        },
        get_waiting_delivery: function () {
            var order = this.get_order_by_widget();
            if (order) {
                var count = 0;
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line.state == 'Waiting-delivery') {
                        count += 1;
                    }
                }
                return count;
            } else {
                return 0;
            }
        },
        get_info_order: function () {
            var order = this.get_order_by_widget();
            var result = {
                amount_total: 0,
                created_time: null
            };
            if (order) {
                var order_json = order.export_as_JSON();
                result['created_time'] = order_json['created_time'];
                result['amount_total'] = order_json['amount_total'];
            }
            return result;
        },
        get_error: function () {
            var order = this.get_order_by_widget();
            if (order) {
                var count = 0;
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line.state == 'Error') {
                        count += 1;
                    }
                }
                return count;
            } else {
                return 0;
            }
        }
    });

    var set_order_done = screens.ActionButtonWidget.extend({
        template: 'set_order_done',
        button_click: function () {
            var order = this.pos.get('selectedOrder');
            if (order.orderlines.length > 0) {
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line.state == 'Waiting-delivery') {
                        line.set_state('Done');
                    }
                }
            }
        }
    });
    screens.define_action_button({
        'name': 'set_order_done',
        'widget': set_order_done,
        'condition': function () {
            return this.pos.config.screen_type && this.pos.config.screen_type !== 'kitchen';
        }
    });

    var set_line_high_priority = screens.ActionButtonWidget.extend({
        template: 'set_line_high_priority',
        button_click: function () {
            var order = this.pos.get('selectedOrder');
            if (order.orderlines.length > 0) {
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line.state != 'Kitchen Waiting cancel' && line.state != 'Done' && line.state != 'Cancel' && line.state != 'Error' && line.state != 'Waiting-delivery') {
                        line.set_state('High-Priority');
                    }
                }
            }
        }
    });
    screens.define_action_button({
        'name': 'set_line_high_priority',
        'widget': set_line_high_priority,
        'condition': function () {
            return this.pos.config.screen_type && this.pos.config.screen_type !== 'kitchen';
        }
    });
    var set_line_exit_high_priority = screens.ActionButtonWidget.extend({
        template: 'set_line_exit_high_priority',
        button_click: function () {
            var order = this.pos.get('selectedOrder');
            if (order.orderlines.length > 0) {
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line && line.state && line.state == 'High-Priority') {
                        line.set_state('Waiting');
                    }
                }
            }
        }
    });
    screens.define_action_button({
        'name': 'set_line_exit_high_priority',
        'widget': set_line_exit_high_priority,
        'condition': function () {
            return this.pos.config.screen_type && this.pos.config.screen_type !== 'kitchen';
        }
    });

    var delivery_kitchen = screens.ActionButtonWidget.extend({
        template: 'delivery_kitchen',
        button_click: function () {
            var order = this.pos.get('selectedOrder');
            if (order.orderlines.length > 0) {
                for (var i = 0; i < order.orderlines.models.length; i++) {
                    var line = order.orderlines.models[i];
                    if (line && line.state && line.state == 'draft') {
                        line.set_state('Waiting');
                    }
                }
            }
        }
    });
    screens.define_action_button({
        'name': 'delivery_kitchen',
        'widget': delivery_kitchen,
        'condition': function () {
            return this.pos.config.screen_type && this.pos.config.screen_type !== 'kitchen';
        }
    });

    var KitchenScreen = screens.ScreenWidget.extend({
        template: 'kitchen_screen',
        show_numpad: false,
        show_leftpane: true,
        previous_screen: false,

        init: function (parent, options) {
            this.datas_render = [];
            this.line_by_string = "";
            this.line_by_product_name = {};
            this._super(parent, options);
        },
        start: function () {
            var self = this;
            this._super();
            this.line_cache = new screens.DomCache();
            this.pos.bind('reload:kitchen_screen', function () {
                self.renderElement()
            })
        },
        show: function () {
            var self = this;
            this._super();
        },
        product_url: function (product_id) {
            return window.location.origin + '/web/image?model=product.product&field=image_medium&id=' + product_id;
        },
        clear_search: function () {
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
            this.renderElement();
        },
        line_filter_by_string: function (line) {
            var str = line.product['display_name'];
            if (line.order.floor) {
                str += '|' + line.order.floor;
            }
            if (line.order.table) {
                str += '|' + line.order.table;
            }
            if (line.note) {
                str += '|' + line.note;
            }
            if (line.creation_time) {
                str += '|' + line.creation_time;
            }
            str = '' + line.product['display_name'] + ':' + str.replace(':', '') + '\n';
            return str;
        },
        search_line: function (query) {
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g, '.');
                query = query.replace(' ', '.+');
                var re = RegExp("([0-9]+):.*?" + query, "gi");
            } catch (e) {
                return [];
            }
            var results = [];
            for (var i = 0; i < this.limit; i++) {
                var query = this.line_by_string;
                var r = re.exec(this.line_by_string);
                if (r && r[1]) {
                    var product_name = r[1];
                    if (this.line_by_product_name[product_name] !== undefined) {
                        for (var i = 0; i < this.line_by_product_name[product_name].length; i++) {
                            results.push(this.line_by_product_name[product_name][i]);
                        }
                    } else {
                        var code = r
                    }
                } else {
                    break;
                }
            }
            return results;
        },
        renderElement: function () {
            var self = this;
            this._super();
            var orders = this.pos.get('orders').models;
            this.datas_render = [];
            for (var i = 0; i < orders.length; i++) {
                var order = orders[i];
                for (var j = 0; j < order.orderlines.models.length; j++) {
                    var curr_line = order.orderlines.models[j];
                    curr_line['product_url'] = this.product_url(curr_line['product']['id'])
                    var quantity_done = curr_line['quantity_done']
                    var quantity = curr_line['quantity']
                    if (quantity_done) {
                        curr_line['quantity_wait'] = quantity - quantity_done;
                    } else {
                        curr_line['quantity_wait'] = quantity;
                    }
                    this.datas_render.push(curr_line);
                }
            }
            if (this.datas_render) {
                this.render_items();
                this.line_actions();
            }
            this.$('.back').click(function () {
                self.gui.back();
            });
            var search_timeout = null;
            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }
            this.$('.search-line input').on('keypress', function (event) {
                var query = this.value;
                clearTimeout(search_timeout);
                search_timeout = setTimeout(function () {
                    self.search_line(query);
                }, 100);
            });
            this.$('.search-line .search-clear').click(function () {
                self.clear_search();
            });
        },
        line_actions: function () {
            var self = this;
            this.$('.kitchen_delivery').click(function () {
                var line_uid = $(this).parent().parent().data()['id'];
                var curr_line = self.pos.get_line_by_uid(line_uid);
                if (!curr_line) {
                    console.log('line not found');
                } else {
                    curr_line.set_state('Waiting-delivery');
                }
                self.renderElement();
            });
            this.$('.kitchen_cancel').click(function () {
                var line_uid = $(this).parent().parent().data()['id'];
                var curr_line = self.pos.get_line_by_uid(line_uid);
                if (!curr_line) {
                    console.log('line not found');
                } else {
                    curr_line.set_state('Not-enough-material');
                }
                self.renderElement();
            });
            this.$('.kitchen_put_back').click(function () {
                var line_uid = $(this).parent().parent().data()['id'];
                var curr_line = self.pos.get_line_by_uid(line_uid);
                if (!curr_line) {
                    console.log('line not found');
                } else {
                    curr_line.set_state('Waiting');
                }
                self.renderElement();
            });
            this.$('.kitchen_confirm_cancel').click(function () {
                var line_uid = $(this).parent().parent().data()['id'];
                var curr_line = self.pos.get_line_by_uid(line_uid);
                if (!curr_line) {
                    console.log('line not found');
                } else {
                    curr_line.set_state('Kitchen Waiting cancel');
                }
                self.renderElement();
            });
        },
        render_items: function () {
            this.line_by_string = "";
            var items = this.datas_render;
            if (items.length == 0) {
                return;
            }
            for (i = 0; i < items.length; i++) {
                var item = items[i];
                this.line_by_string += this.line_filter_by_string(item)
                if (!this.line_by_product_name[item['product']['display_name']]) {
                    this.line_by_product_name[item['product']['display_name']] = [item];
                } else {
                    this.line_by_product_name[item['product']['display_name']].push(item);
                }
            }
            items.sort(function (item1, item2) {
                return Date.parse('1970/01/01 ' + item1.creation_time.slice(0, -3) + ' ' + item1.creation_time.slice(-3)) - Date.parse('1970/01/01 ' + item2.creation_time.slice(0, -3) + ' ' + item2.creation_time.slice(-3))
            });
            for (var i = 0; i < items.length; i++) {
                var line = items[i];
                //  kiem tra xem san pham nằm trong danh mục đc hiển thị không
                var display = this.pos.db.is_product_in_category(this.pos.config.product_categ_ids, line.get_product().id);
                if (!display) {
                    continue;
                }
                var line_html = qweb.render('kitchen_line', {widget: this, line: line});
                var line_cache = document.createElement('tbody');
                line_cache.innerHTML = line_html;
                line_cache = line_cache.childNodes[1];
                console.log(line.state);
                if (line.state == 'High-Priority') {
                    this.$el[0].querySelector('.priority').appendChild(line_cache);
                } else if (line.state == 'Error') {
                    this.$el[0].querySelector('.error').appendChild(line_cache);
                } else if (line.state == 'Waiting') {
                    this.$el[0].querySelector('.waiting').appendChild(line_cache);
                } else if (line.state == 'Waiting-delivery') {
                    this.$el[0].querySelector('.waiting-delivery').appendChild(line_cache);
                } else if (line.state == 'Cancel') {
                    this.$el[0].querySelector('.cancel').appendChild(line_cache);
                } else if (line.state == 'Not-enough-material') {
                    this.$el[0].querySelector('.not-enough-material').appendChild(line_cache);
                }
            }
            if (this.pos.config.play_sound) {
                this.pos.play_sound();
            }
        }
    });
    gui.define_screen({
        'name': 'kitchen_screen',
        'widget': KitchenScreen,
    });

});
