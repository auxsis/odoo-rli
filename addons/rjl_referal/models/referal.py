##############################################################################
#
#    HZ
#    Copyright (C) 2017.
#
##############################################################################

from odoo.osv import expression
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
import odoo.addons.decimal_precision as dp
import pdb

class SaleBonusConfig(models.Model):
    _name = 'sale.bonus.config'

    sale_amount = fields.Float(string='Sale Amount', required=True)
    bonus_trans = fields.Float(string='Bonus Transaksi (%)')
    bonus_referal = fields.Float(string='Bonus Referal (%)')
    bonus_sponsor = fields.Float(string='Bonus Sponsor (Rp.)')
    bonus_gen = fields.Float(string='Bonus Gen (%)')
    bonus_level = fields.Selection([('1', 'Level 1'), ('2', 'Level 2'), ('3', 'Level 3')], default='1', required=True)

class SaleLead(models.Model):
    _name = 'sale.lead'
    _rec_name = 'customer_name'
    _inherit = ['mail.thread', 'ir.needaction_mixin']


    customer_name = fields.Char(string='Customer Name', required=True)
    company_name = fields.Char(string='Company Name')
    street = fields.Char(string='Alamat')
    bidang = fields.Char(string='Bidang')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    partner_id = fields.Many2one('res.partner', string='Partner')
    project_estimation = fields.Float(string='Project Estimation Amount')
    followup_date = fields.Datetime(string='Tanggal Ekspektasi Difollowup', required=True, default=fields.Datetime.now)
    notes = fields.Text(string='Notes')
    salesman_id = fields.Many2one('res.users', string='Salesman')
    referal_id = fields.Many2one('res.users', string='Referal', default=lambda self: self.env.user.id)
    order_id = fields.Many2one('sale.order', string='SO Number')
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting Salesman'),('open', 'Follow UP'), ('done', 'Goal'), ('lose', 'Lose')], string='State', default='draft')

    
    @api.multi
    def accept_order(self):
        self.write({'salesman_id': self.env.user.id})

    @api.multi
    def confirm(self):
        self.write({'state': 'waiting'})

    @api.multi
    def convert_to_quotation(self):
        partner_id = self.env['res.partner'].create({
            'name': self.customer_name,
            'customer': True,
            'phone': self.phone,
            'email': self.email,
            'street': self.street
        })
        so_id = self.env['sale.order'].create({'partner_id': partner_id.id, 'referal_id': self.referal_id.id})

        self.write({'state': 'done'})

        return {
            'name': _('Quotation'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': so_id.id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.multi
    def convert_to_lose(self):
        self.write({'state': 'lose'})

class SalesOrder(models.Model):
    _inherit = 'sale.order'

    referal_id = fields.Many2one('res.users', string='Referal')

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def _compute_total_bonus(self):
        for self in self:
            bonus_referal = 0
            bonus_sponsor = 0
            bonus_transaksi = 0
            bonus_gen = 0
            sale_ids = []
            # COMPUTE BONUS SPONSOR & TRANSAKSI
            for x in self.sales_ids:
                bonus_config  = self.env['sale.bonus.config'].search([('sale_amount', '<=', x.amount_total), ('bonus_level', '=', self.env.user.bonus_level)], order="sale_amount desc", limit=1)
                if not bonus_config:
                    continue
                if x.state not in ('draft', 'cancel'):
                    bonus_sponsor += bonus_config.bonus_sponsor
                    bonus_transaksi += x.amount_total * (bonus_config.bonus_trans / 100)

            # COMPUTE BONUS REFERAL  
            # SELECT DISTINCT PARTNER COZ BONUS APPLY JUST ONLY ONCE PER PARTNER
            self.env.cr.execute("""SELECT DISTINCT ON(partner_id) partner_id, id  FROM sale_order WHERE invoice_status = 'invoiced' AND referal_id = %s """ %(self.id,))
            sale_data = self.env.cr.dictfetchall()
            for ids in sale_data:
                sale_ids.append(ids['id'])
            
            orders = self.env['sale.order'].search([('id', 'in', sale_ids)])
            for x in orders:
                bonus_config  = self.env['sale.bonus.config'].search([('sale_amount', '<=', x.amount_total), ('bonus_level', '=', self.env.user.bonus_level)], order="sale_amount desc", limit=1)
                if not bonus_config:
                    continue
                if x.state not in ('draft', 'cancel'):
                    bonus_referal += x.amount_total * (bonus_config.bonus_referal / 100)

            # COMPUTE BONUS GEN
            for y in self.child_ids:
                for x in sale_ids:
                    bonus_config  = self.env['sale.bonus.config'].search([('sale_amount', '<=', x.amount_total), ('bonus_level', '=', self.env.user.bonus_level)], order="sale_amount desc", limit=1)
                    if not bonus_config:
                        continue
                    if x.state not in ('draft', 'cancel'):
                        bonus_gen += x.amount_total * (bonus_config.bonus_gen / 100)

            self.bonus_sponsor = bonus_sponsor
            self.bonus_transaksi = bonus_transaksi
            self.bonus_referal = bonus_referal
            self.bonus_gen = bonus_gen
            self.total_bonus = bonus_referal + bonus_sponsor + bonus_transaksi + bonus_gen

    @api.one
    def _compute_bonus_due(self):
        self.bonus_due = self.total_bonus - self.paid_bonus

    @api.one
    def _compute_paid_bonus(self):
        paid = 0
        payment = self.env['account.payment'].search([('partner_id', '=', self.partner_id.id), ('payment_type', '=', 'outbound'), ('state', '=', 'posted')])
        for y in payment:
            paid += y.amount
        self.paid_bonus = paid


    @api.one
    def _compute_bonus_level(self):
        if self.parent_id:
            if self.parent_id.parent_id:
                self.bonus_level = '3'
            else:
                self.bonus_level = '2'
        else:
            self.bonus_level = '1'


    parent_id = fields.Many2one('res.users', string='Parent Referal')
    child_ids = fields.One2many('res.users', 'parent_id', string='Child Referal')
    bonus_referal = fields.Float(string='Total Bonus Referal', digits=dp.get_precision('Product Price'), compute="_compute_total_bonus")
    bonus_sponsor = fields.Float(string='Total Bonus Sponsor', digits=dp.get_precision('Product Price'), compute="_compute_total_bonus")
    bonus_transaksi = fields.Float(string='Total Bonus Transaksi', digits=dp.get_precision('Product Price'), compute="_compute_total_bonus")
    bonus_gen = fields.Float(string='Total Bonus Gen', digits=dp.get_precision('Product Price'), compute="_compute_total_bonus")
    total_bonus = fields.Float(string='Total Bonus', digits=dp.get_precision('Product Price'), compute='_compute_total_bonus')
    bonus_due = fields.Float(string='Bonus Due', digits=dp.get_precision('Product Price'), compute='_compute_bonus_due')
    paid_bonus = fields.Float(string='Paid Bonus', digits=dp.get_precision('Product Price'), compute='_compute_paid_bonus')
    sales_ids = fields.One2many('sale.order', 'referal_id', domain=[('invoice_status', '=', 'invoiced')], string='Sales Order')
    parent_id = fields.Many2one('res.users', string='Parent')
    bonus_level = fields.Selection([('1', 'Level 1'), ('2', 'Level 2'), ('3', 'Level 3')], compute='_compute_bonus_level')
