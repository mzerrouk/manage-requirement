from odoo import models, fields, api

class Requirement(models.Model):
    _name = 'requirement.requirement'
    _description = 'Project Requirement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, created_date desc'

    name = fields.Char(string='Requirement Title', required=True, tracking=True)
    description = fields.Text(string='Description')
    
    type = fields.Selection([
        ('epic', 'Epic'),
        ('user_story', 'User Story'),
        ('task', 'Task')
    ], string='Type', required=True, default='task', tracking=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Priority', default='medium', required=True, tracking=True)
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True)
    
    created_date = fields.Datetime(string='Created Date', default=fields.Datetime.now, readonly=True)
    modified_date = fields.Datetime(string='Modified Date', readonly=True)
    
    # Relationships
    owner_id = fields.Many2one('res.users', string='Owner', required=True, default=lambda self: self.env.user, tracking=True)
    project_id = fields.Many2one('requirement.project', string='Project', ondelete='cascade', tracking=True)
    parent_id = fields.Many2one('requirement.requirement', string='Parent Requirement', ondelete='cascade', tracking=True)
    
    # One2many relationships
    child_ids = fields.One2many('requirement.requirement', 'parent_id', string='Sub-Requirements')
    change_ids = fields.One2many('requirement.change', 'requirement_id', string='Changes')
    comment_ids = fields.One2many('requirement.comment', 'requirement_id', string='Comments')
    
    # Computed fields
    child_count = fields.Integer(string='Sub-Requirements Count', compute='_compute_child_count')
    change_count = fields.Integer(string='Changes Count', compute='_compute_change_count')
    comment_count = fields.Integer(string='Comments Count', compute='_compute_comment_count')
    total_change_cost = fields.Float(string='Total Change Cost', compute='_compute_total_change_cost', store=True)
    
    @api.depends('child_ids')
    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.child_ids)
    
    @api.depends('change_ids')
    def _compute_change_count(self):
        for record in self:
            record.change_count = len(record.change_ids)
    
    @api.depends('comment_ids')
    def _compute_comment_count(self):
        for record in self:
            record.comment_count = len(record.comment_ids)
    
    @api.depends('change_ids', 'change_ids.additional_cost', 'change_ids.cost_approved', 'change_ids.status')
    def _compute_total_change_cost(self):
        for record in self:
            total = 0.0
            for change in record.change_ids:
                if change.status == 'approved' and change.cost_approved:
                    total += change.additional_cost
            record.total_change_cost = total
    
    def write(self, vals):
        vals['modified_date'] = fields.Datetime.now()
        return super(Requirement, self).write(vals)
    
    def action_view_children(self):
        return {
            'name': 'Sub-Requirements',
            'type': 'ir.actions.act_window',
            'res_model': 'requirement.requirement',
            'view_mode': 'list,form',
            'domain': [('parent_id', '=', self.id)],
            'context': {'default_parent_id': self.id}
        }
    
    def action_view_changes(self):
        return {
            'name': 'Change Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'requirement.change',
            'view_mode': 'list,form',
            'domain': [('requirement_id', '=', self.id)],
            'context': {'default_requirement_id': self.id}
        }
    
    def action_view_comments(self):
        return {
            'name': 'Comments',
            'type': 'ir.actions.act_window',
            'res_model': 'requirement.comment',
            'view_mode': 'list,form',
            'domain': [('requirement_id', '=', self.id)],
            'context': {'default_requirement_id': self.id}
        }
