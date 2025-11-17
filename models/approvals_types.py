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
    visible_user_ids = fields.Many2many('res.users', 'approvals_types_visible_users_rel', 'approvals_types_id', 'user_id', string='Visible To Users', help='Users who can view this approval type')
    approver_ids = fields.One2many('approval.type.approver', 'approval_type_id', string='Approvers')

    approved_request_count = fields.Integer(string='Approved Requests', compute='_compute_request_counts')
    rejected_request_count = fields.Integer(string='Rejected Requests', compute='_compute_request_counts')
    to_review_request_count = fields.Integer(string='To Review Requests', compute='_compute_request_counts')
    to_verify_request_count = fields.Integer(string='To Verify', compute='_compute_request_counts')

    finance = fields.Boolean(string="Finance", default=False)

    @api.model_create_multi
    def create(self, vals_list):
        """Create approval types and notify approvers"""
        records = super().create(vals_list)
        
        for record in records:
            # Get all approvers for this approval type
            approvers = record.approver_ids.mapped('approver_id')
            
            if approvers:
                # Create log message in chatter
                message = f"<p>New approval type <strong>{record.approvals_type}</strong> has been created.</p>"
                message += f"<p><strong>Description:</strong> {record.description or 'N/A'}</p>"
                message += f"<p><strong>Approvers assigned:</strong> {', '.join([a.name for a in approvers])}</p>"
                
                record.message_post(body=message, message_type='comment')
                
                # Send email notification to each approver
                for approver in approvers:
                    try:
                        # Create email content
                        subject = f"New Approval Type Created: {record.approvals_type}"
                        body = f"""
                        <p>Hi {approver.name},</p>
                        <p>A new approval type has been created and you have been assigned as an approver.</p>
                        <p><strong>Approval Type:</strong> {record.approvals_type}</p>
                        <p><strong>Description:</strong> {record.description or 'N/A'}</p>
                        <p>Please log in to the system to view details and process approvals as needed.</p>
                        <p>Best regards,<br/>The Approval System</p>
                        """
                        
                        # Send email
                        mail_values = {
                            'subject': subject,
                            'body_html': body,
                            'email_to': approver.email,
                            'email_from': self.env.user.email,
                        }
                        self.env['mail.mail'].create(mail_values).send()
                    except Exception as e:
                        # Log error but don't fail the creation
                        print(f"Error sending email to {approver.name}: {str(e)}")
        
        return records

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
