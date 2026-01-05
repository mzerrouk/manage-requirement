from odoo import models, fields, api

class RequirementComment(models.Model):
    _name = 'requirement.comment'
    _description = 'Requirement Comment'
    _order = 'date desc'

    requirement_id = fields.Many2one('requirement.requirement', string='Requirement', ondelete='cascade')
    change_id = fields.Many2one('requirement.change', string='Change Request', ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    content = fields.Text(string='Comment', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)
    
    @api.constrains('requirement_id', 'change_id')
    def _check_parent(self):
        for record in self:
            if not record.requirement_id and not record.change_id:
                raise models.ValidationError('Comment must be linked to either a Requirement or a Change Request.')
