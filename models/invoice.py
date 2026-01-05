from odoo import models, fields, api

class RequirementInvoice(models.Model):
    _name = 'requirement.invoice'
    _description = 'Requirement Invoice'
    _order = 'date desc'

    name = fields.Char(string='Invoice Reference', required=True, copy=False, readonly=True, default='New')
    date = fields.Date(string='Invoice Date', default=fields.Date.today, required=True)
    project_id = fields.Many2one('requirement.project', string='Project')
    requirement_ids = fields.Many2many('requirement.requirement', string='Requirements')
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', store=True)
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('requirement.invoice') or 'New'
        return super().create(vals_list)
    
    @api.depends('requirement_ids', 'requirement_ids.change_ids', 'requirement_ids.change_ids.additional_cost', 
                 'requirement_ids.change_ids.cost_approved', 'requirement_ids.change_ids.status')
    def _compute_total_cost(self):
        for record in self:
            total = 0.0
            for requirement in record.requirement_ids:
                # Sum only approved change requests with approved costs
                for change in requirement.change_ids:
                    if change.status == 'approved' and change.cost_approved:
                        total += change.additional_cost
            record.total_cost = total
