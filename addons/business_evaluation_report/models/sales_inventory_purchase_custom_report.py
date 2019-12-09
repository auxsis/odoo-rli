# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class EvaloationReport(models.Model):
    _name = "report.inventory.sale.purchase"
    _description = "Purchase Sale Inventory Evalution"
    _auto = False
    _order = 'product_id asc'

    
    product_id = fields.Many2one('product.product', string='Product Name', readonly=True)
    product_categ_id = fields.Many2one('product.category', string='Product Category', readonly=True) 
    # attribute_id=fields.Many2one('product.attribute.value', string='Product Attribute', readonly=True)
   
    # product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)
   
    # location_id = fields.Many2one('stock.location', string='Location', readonly=True)

    sale_report= fields.Integer( 'Sale Quantity', readonly=True)
    inventory_report = fields.Integer('Inventory Quantity', readonly=True)
    purchase_report = fields.Integer('Purchase Quantity', readonly=True)   

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_inventory_sale_purchase')
        self._cr.execute("""
            CREATE OR REPLACE VIEW report_inventory_sale_purchase AS (
                SELECT
                    
                    min(p.id) as id,
                    p.id as product_id,
                    t.categ_id AS product_categ_id,
                    (SELECT sum(q.product_qty) FROM purchase_order_line q where p.id=q.product_id GROUP BY q.product_id) AS purchase_report,
                    (SELECT sum(sq.qty) FROM stock_quant sq where p.id=sq.product_id AND (sq.location_id='9') GROUP BY sq.product_id) AS sale_report,
                    (SELECT sum(sq.qty) FROM stock_quant sq where p.id=sq.product_id AND (sq.location_id='19' OR sq.location_id='25' OR sq.location_id='36'OR sq.location_id='71' OR sq.location_id='69'OR sq.location_id='62' OR sq.location_id='53'OR sq.location_id='42' OR sq.location_id='13' OR sq.location_id='12' OR sq.location_id='20') GROUP BY sq.product_id) AS inventory_report,
                    
                    p.product_tmpl_id AS product_tmpl_id
                   
                FROM product_product p 
                    left join product_template t on (p.product_tmpl_id=t.id)
                
                GROUP BY
                    p.id,
                    t.categ_id,
                    p.product_tmpl_id
                 
                
            )
        """)
 