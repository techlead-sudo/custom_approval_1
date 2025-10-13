# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ApprovalsTypes(models.Model):
    """This model stores approval types."""
    _name = 'approvals.types'
    _description = 'Approval Types'
    _rec_name = 'approvals_type'
    _inherit = 'mail.thread'

    approvals_type = fields.Char(string='Approval Type')
    approval_image = fields.Binary(string='Approval Image')
    description = fields.Text(string='Description')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    approver_ids = fields.One2many('approval.type.approver', 'approval_type_id', string='Approvers')

    approved_request_count = fields.Integer(string='Approved Requests', compute='_compute_request_counts')
    rejected_request_count = fields.Integer(string='Rejected Requests', compute='_compute_request_counts')
    to_review_request_count = fields.Integer(string='To Review Requests', compute='_compute_request_counts')
    to_verify_request_count = fields.Integer(string='To Verify', compute='_compute_request_counts')

    finance = fields.Boolean(string="Finance", default=False)

    @api.depends('approvals_type')
    def _compute_request_counts(self):
        for record in self:
            ApprovalRequest = self.env['approval.request']

            record.approved_request_count = ApprovalRequest.search_count([
                ('approval_type_id', '=', record.id),
                ('state', '=', 'approved')
            ])
            record.rejected_request_count = ApprovalRequest.search_count([
                ('approval_type_id', '=', record.id),
                ('state', '=', 'rejected')
            ])
            record.to_review_request_count = ApprovalRequest.search_count([
                ('approval_type_id', '=', record.id),
                ('state', '=', 'submitted')
            ])
            record.to_verify_request_count = ApprovalRequest.search_count([
                ('approval_type_id', '=', record.id),
                ('state', '=', 'verification')
            ])

    # --- Actions ---
    def action_new_approval_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'approval.request',
            'target': 'current',
            'context': {
                'default_approval_type_id': self.id,
                'create': True,
            }
        }

    def action_get_approval_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approval Requests',
            'view_mode': 'kanban,form',
            'res_model': 'approval.request',
            'domain': [('approval_type_id', '=', self.id)],
            'context': {'create': True},
        }

    def btn1(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Approved Requests',
            'view_mode': 'kanban,form',
            'res_model': 'approval.request',
            'domain': [('approval_type_id', '=', self.id), ('state', '=', 'approved')],
        }

    def btn2(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rejected Requests',
            'view_mode': 'kanban,form',
            'res_model': 'approval.request',
            'domain': [('approval_type_id', '=', self.id), ('state', '=', 'rejected')],
        }

    def btn3(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'To Review Requests',
            'view_mode': 'kanban,form',
            'res_model': 'approval.request',
            'domain': [('approval_type_id', '=', self.id), ('state', '=', 'submitted')],
        }

    def btn4(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'To Verify Requests',
            'view_mode': 'kanban,form',
            'res_model': 'approval.request',
            'domain': [('approval_type_id', '=', self.id), ('state', '=', 'verification')],
        }
