##############################################################################
#
#    HZ
#    Copyright (C) 2017.
#
##############################################################################

from odoo.osv import expression
from odoo import api, fields, models, _
import pdb

class ProgressionStatusUpdate(models.TransientModel):
    _name = 'progression.status.update'

    completation = fields.Integer(string='Completation')
    state = fields.Selection([('on_progress', 'On Progress'), ('warning', 'Warning'), ('delay', 'Delay'), ('done', 'Done')], default='on_progress', string='Status', required=True)

    @api.model
    def default_get(self, fields):
        completation_jasa = self.env['project.progression'].search([('id', '=', self._context.get('active_id'))]).completation_jasa
        rec = super(ProgressionStatusUpdate, self).default_get(fields)
        rec['completatio_jasan'] = completation_jasa
        return rec

    @api.one
    def update_state(self):
        self.env['project.progression'].search([('id', '=', self._context.get('active_id'))]).write({'state':self.state, 'completation_jasa':self.completation})
