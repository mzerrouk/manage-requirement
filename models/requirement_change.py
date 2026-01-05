from odoo import models, fields, api

class RequirementChange(models.Model):
    _name = 'requirement.change'
    _description = 'Requirement Change Request'
    _order = 'request_date desc'

    name = fields.Char(string='Change Reference', readonly=True, copy=False)
    requirement_id = fields.Many2one('requirement.requirement', string='Requirement', required=True, ondelete='cascade')
    
    change_type = fields.Selection([
        ('update', 'Update'),
        ('remove', 'Remove'),
        ('add_detail', 'Add Detail')
    ], string='Change Type', required=True)
    
    description = fields.Text(string='Description', required=True)
    
    requested_by = fields.Many2one('res.users', string='Requested By', required=True, default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending', required=True)
    
    request_date = fields.Datetime(string='Request Date', default=fields.Datetime.now, readonly=True)
    approval_date = fields.Datetime(string='Approval Date', readonly=True)
    
    # One2many relationships
    comment_ids = fields.One2many('requirement.comment', 'change_id', string='Comments')
    
    # Cost tracking fields
    additional_cost = fields.Float(string="Additional Cost", help="Extra cost requested due to this change")
    cost_justification = fields.Text(string="Cost Justification", help="Reason for additional cost")
    cost_approved = fields.Boolean(string="Cost Approved", default=False)
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super(RequirementChange, self).create(vals_list)
        for record in records:
            if not record.name:
                record.name = f"CHG-{record.id}"
        return records
    
    def action_approve(self):
        self.write({
            'status': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
    
    def action_reject(self):
        self.write({
            'status': 'rejected',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
