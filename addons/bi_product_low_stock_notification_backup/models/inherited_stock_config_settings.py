# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import fields,models,api, _

from odoo.tools.safe_eval import safe_eval



class StockSettings(models.TransientModel):
    _name = 'stock.config.settings'
    _inherit = ['stock.config.settings']



    # user_res_id=fields.Many2one('res.users',default=lambda self: self.env.uid)
    # company_res_id=fields.Many2one('res.company',related='user_res_id.company_id')
    # company_res_id = fields.Many2one('res.company',default = lambda self:self.company_id)
    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id.id)
    notification_base = fields.Selection([('on_hand','On hand quantity'),('fore_cast','Forecast')],related='company_id.notification_base',string='Notification Based on')
    notification_products = fields.Selection([('for_all','Global for all product'),('fore_product',' Individual for all products')],related='company_id.notification_products',string='Min Quantity Based On')
    min_quantity = fields.Float(related='company_id.min_quantity',string = 'Quantity Limit')
    
    notification_user_id = fields.Many2one('res.users',related='company_id.notification_user_id',string = 'Notify User')
    email_user = fields.Char(related='company_id.email',string="Email from") 
    low_stock_products_ids=fields.One2many('low.stock.transient','stock_product_id',store=True)






    @api.model
    def get_default_low_stock_fields(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        
        return {
            'notification_base': safe_eval(IrConfigParam.get_param('bi_product_low_stock_notification.notification_base', 'False')),
            'notification_products': safe_eval(IrConfigParam.get_param('bi_product_low_stock_notification.notification_products', 'False')),
            'min_quantity': safe_eval(IrConfigParam.get_param('bi_product_low_stock_notification.min_quantity', 'False')),
            
            'notification_user_id': safe_eval(IrConfigParam.get_param('bi_product_low_stock_notification.notification_user_id', 'False')),
            'email_user': safe_eval(IrConfigParam.get_param('bi_product_low_stock_notification.email_user', 'False')),

        }

    @api.multi
    def set_low_stock_fields(self):
        self.ensure_one()
        IrConfigParam = self.env['ir.config_parameter']
        
        IrConfigParam.set_param('bi_product_low_stock_notification.notification_base', repr(self.notification_base))
        IrConfigParam.set_param('bi_product_low_stock_notification.notification_products', repr(self.notification_products))
        IrConfigParam.set_param('bi_product_low_stock_notification.min_quantity', repr(self.min_quantity))

        IrConfigParam.set_param('bi_product_low_stock_notification.notification_user_id', repr(self.notification_user_id.id))
        IrConfigParam.set_param('bi_product_low_stock_notification.email_user', repr(self.email_user))
        

    

    
    def action_list_products_(self):
        products_list=[]
        
        res = self.env['stock.config.settings'].search([],order="id desc", limit=1)
        
        products_dlt = [(2,dlt.id,0)for dlt in res.low_stock_products_ids]
        
        

        res.low_stock_products_ids = products_dlt

        if res.notification_base == 'on_hand':
            if res.notification_products == 'for_all':
                result = self.env['product.product'].search([('qty_available','<',res.min_quantity)])
                
                
                for product in result:
                    products_list.append([0,0,{'name':product.name,
                                            'limit_quantity':res.min_quantity,
                                            'stock_quantity':product.qty_available}])
    
            
            if res.notification_products == 'fore_product':
                
                result = self.env['product.product'].search([])
                

                for product in result:
                    if product.qty_available < product.min_quantity:
                        products_list.append([0,0,{'name':product.name,
                                                    'limit_quantity':product.min_quantity,
                                                'stock_quantity':product.qty_available}])


        if res.notification_base=='fore_cast':
            if res.notification_products=='for_all':
                result = self.env['product.product'].search([('virtual_available','<',res.min_quantity)])
                for product in result:
                    products_list.append([0,0,{'name':product.name,
                                            'stock_quantity':product.virtual_available}])
            if res.notification_products == 'fore_product':
                result = self.env['product.product'].search([])

                for product in result:
                    if product.virtual_available < product.min_quantity:
                        products_list.append([0,0,{'name':product.name,
                                                    'limit_quantity':product.min_quantity,
                                                'stock_quantity':product.virtual_available}])

            

        
        res.low_stock_products_ids = products_list
                
        return 


    
        
    

    
    def action_low_stock_send(self):
        
        self.action_list_products_()
        
        res = self.env['stock.config.settings'].search([],order="id desc", limit=1)
        
       
        
        
            
        template_id = self.env.ref('bi_product_low_stock_notification.low_stock_email_template')
        
        send = template_id.send_mail(res.id, force_send=True)
        

        
        
    

        return True


    


    

class low_stock_product(models.TransientModel):
    _name='low.stock.transient'


    name=fields.Char(string='Product name')
    stock_quantity=fields.Float(string='Quantity')
    limit_quantity=fields.Float(string='Quantity limit')
    stock_product_id=fields.Many2one('stock.config.settings')

