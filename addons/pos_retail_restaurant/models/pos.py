# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class pos_config(models.Model):

    _inherit = "pos.config"

    floor_ids = fields.Many2many('restaurant.floor', 'pos_config_restaurant_floor_rel', 'pos_config_id', 'floor_id', string="Floors")
    sync_between_waiters = fields.Boolean('Sync between waiters', default=1, help='If checked, only sync between cashiers and kitchen/bar. Not sync between cashiers, waiters')
    screen_type = fields.Selection([
        ('waiter', 'Waiter'),
        ('kitchen', 'Kitchen'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
    ], string='Session Type', default='cashier')
    play_sound = fields.Boolean('Sound', help='Sound notify when new transaction coming')
    display_floor = fields.Boolean('Display floors', help='Display floors on Kitchen/bar screen', default=1)
    display_table = fields.Boolean('Display tables', help='Display tables on Kitchen/bar screen', default=1)
    display_product_image = fields.Boolean('Display product image', help='Display product image on Kitchen/bar screen', default=1)
    product_categ_ids = fields.Many2many('pos.category', 'config_pos_category_rel', 'config_id', 'categ_id', string='Categories display', help='Categories of product will display on kitchen/bar screen')

    @api.onchange('screen_type')
    def on_change_staff_level(self):
        if self.screen_type and self.screen_type == 'kitchen':
            self.display_floor = True
            self.display_table = True
            self.display_product_image = True

class restaurant_table(models.Model):

    _inherit = "restaurant.table"

    floor_id = fields.Many2one('restaurant.floor', 'Floor')

