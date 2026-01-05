from odoo import models, fields, api

class RequirementProject(models.Model):
    _name = 'requirement.project'
    _description = 'Requirement Project'
    _order = 'name'

    name = fields.Char(string='Project Name', required=True)
    description = fields.Text(string='Description')
    
    # One2many relationships
    requirement_ids = fields.One2many('requirement.requirement', 'project_id', string='Requirements')
    
    # Computed fields
    requirement_count = fields.Integer(string='Requirements Count', compute='_compute_requirement_count')
    
    @api.depends('requirement_ids')
    def _compute_requirement_count(self):
        for record in self:
            record.requirement_count = len(record.requirement_ids)
    
    def action_view_requirements(self):
        return {
            'name': 'Requirements',
            'type': 'ir.actions.act_window',
            'res_model': 'requirement.requirement',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id}
        }
