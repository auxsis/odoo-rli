from odoo import api, fields, models, _
import logging
from odoo.exceptions import UserError

_log = logging.getLogger(__name__)

class product_template(models.Model):
    _inherit = 'product.template'

    integration_kitchen = fields.Boolean('Integration Kitchen', help='Auto manufacturing when kitchen process product to DONE')

    @api.model
    def process_from_kitchen(self, vals):
        """
        {
        'qty': 1,
        'price_unit': 15,
        'discount': 0,
        'product_id': 88,
        'tax_ids': [[6, False, [1]]],
        'id': 4,
        'pack_lot_ids': [],
        'combo_items': [],
        'variants': [],
        'uid': '00001-010-0007-4',
        'session_info': {'bus_id': 1, 'user': {'id': 1, 'name': 'Administrator'}, 'pos': {'id': 1, 'name': 'Main'}, 'date': '2:32:02 PM'},
        'order_uid': '00001-010-0007',
        'mp_skip': False,
        'note': '',
        'state': 'Waiting-delivery',
        'creation_time': '2:32:02 PM'
        }
        :param vals:
        :return:
        """
        _log.info('begin process_from_kitchen')
        _log.info(vals)
        if not vals:
            return False
        product = self.env['product.product'].browse(vals['product_id'])
        _log.info(product.name)
        if not product.bom_id:
            return False
        else:
            if not vals['quantity_wait'] or vals['quantity_wait'] <= 0:
                return False
            mrp_order = self.env['mrp.production'].create({
                'product_id': vals['product_id'],
                'product_qty': vals['quantity_wait'],
                'bom_id': product.bom_id.id,
                'product_uom_id': product.bom_id.product_uom_id.id,
                'origin': vals['uid'],
                'pos_user_id': self.env.user.id,
            })
            if product.manufacturing_state == 'manual':
                mrp_order.action_assign()
                _log.info('Kitchen process action_assign')
            if product.manufacturing_state == 'auto':
                mrp_order.action_assign()
                _log.info('Kitchen process button_mark_done')
                mrp_order.button_plan()
                work_orders = self.env['mrp.workorder'].search([('production_id', '=', mrp_order.id)])
                if work_orders:
                    work_orders.button_start()
                    work_orders.record_production()
                else:
                    produce_wizard = self.env['mrp.product.produce'].with_context({
                        'active_id': mrp_order.id,
                        'active_ids': [mrp_order.id],
                    }).create({
                        'product_qty': vals['qty'],
                    })
                    produce_wizard.do_produce()
                mrp_order.button_mark_done()
        return True