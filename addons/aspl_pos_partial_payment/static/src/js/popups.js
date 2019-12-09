odoo.define('aspl_pos_partial_payment.popups', function (require) {
	"use strict";
	var gui = require('point_of_sale.gui');
	var keyboard = require('point_of_sale.keyboard').OnscreenKeyboardWidget;
	var Model = require('web.DataModel');
	var chrome = require('point_of_sale.chrome');
	var utils = require('web.utils');
	var PopupWidget = require('point_of_sale.popups');
	
	var core = require('web.core');
	var QWeb = core.qweb;
	var round_pr = utils.round_precision;
	var _t = core._t;

	var MaxCreditExceedPopupWidget = PopupWidget.extend({
	    template: 'MaxCreditExceedPopupWidget',
	    show: function(options){
	        var self = this;
	        this._super(options);
	    },
        events: _.extend({}, PopupWidget.prototype.events, {
            'click .button.override_payment':  'click_override_payment',
        }),
        click_override_payment: function(){
        	var self = this;
        	if(self.options.payment_obj){
            	this.options.payment_obj.finalize_validation();
            } else if(self.options.draft_order){
            	this.pos.push_order(this.pos.get_order());
            	self.gui.show_screen('receipt');
            }
            this.gui.close_popup();
        },
	});
	gui.define_popup({name:'max_limit', widget: MaxCreditExceedPopupWidget});

	/* Product POPUP */
	var ProductPopup = PopupWidget.extend({
	    template: 'ProductPopup',
	    show: function(options){
	    	var self = this;
			this._super();
			this.product_list = options.product_list || "";
			this.order_id = options.order_id || "";
			this.state = options.state || "";
			this.renderElement();
			self = this;
			
			$(".del_order").click(function(){
				var result = self.pos.db.get_order_by_id(self.order_id);
				if(result && result.state == 'draft'){
					self.gui.show_popup('confirm',{
		                'title': _t('Delete Order'),
		                'body': _t("Are you sure you want to delete "+ result.pos_reference +" ?"),
		                confirm: function(){
		                	new Model("pos.order").get_func("unlink")(result.id).then(function(){
		        				$(".reload").click();
		        				self.gui.close_popup();
		        			});
		                },
		            });
				}
			});
	    },
	    click_confirm: function(){
	        if (this.state == "paid" || this.state == "done"){
                $( "#re_order_duplicate" ).data("id",self.order_id);
    			$( "#re_order_duplicate" ).trigger("click");
	        } else if(this.state == "draft") {
                $( "#re_order" ).data("id",self.order_id);
                $( "#re_order" ).trigger("click");
			}
			this.gui.close_popup();
	    },
    	click_cancel: function(){
    		this.gui.close_popup();
    	}
	    
	});
	gui.define_popup({name:'product_popup', widget: ProductPopup});

});