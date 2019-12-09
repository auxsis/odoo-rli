from odoo import _, api, fields, models

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'
    
    @api.multi
    def send_mail_action(self):
        # TDE/ ???
        ctx = dict(self._context) or {}
        ctx.update({'block_follower_mail':True})
        self.env['mail.compose.message'].with_context(ctx)
        res = super(MailComposer, self.with_context(ctx)).send_mail_action()
        return res