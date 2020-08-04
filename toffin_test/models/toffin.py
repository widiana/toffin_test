#-*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MasterItem(models.Model):
    _name           = "master.item"
    _description    = "Master Items"

    name = fields.Char('name',required=True)
    date = fields.Date('Date', default=fields.Date.context_today,required=True)
    expected_date = fields.Date('Expected Date', compute='_compute_total_percent_and_days', store=True)
    real_date = fields.Date('Real Date', track_visibility='on_change')
    line_ids = fields.One2many('master.item.lines','item_id','Details')
    total_percent = fields.Float('Total Percentage', compute='_compute_total_percent_and_days', store=True)

    @api.one
    @api.depends('line_ids.percent','line_ids.day')
    def _compute_total_percent_and_days(self):
        days = sum(self.line_ids.mapped('day'))
        if days > 0 :
            date  = datetime.strptime(str(self.date), '%Y-%m-%d')
            expected_date =  date + timedelta(days=days)
            self.expected_date = str(expected_date)
        self.total_percent = sum(self.line_ids.mapped('percent'))

    @api.one
    @api.constrains('total_percent') 
    def _check_total_percent(self):
        total_percent = self.total_percent
        if total_percent > 100.0 or total_percent < 0.0:
            raise ValidationError(_('Total Maximum percentage cannot be more than 100 %'))

    _sql_constraints = [
        ('name_uniq', 'unique(name)',("Item name must be uniq."))
    ]

MasterItem()


class MasterItemLines(models.Model):
    _name           = "master.item.lines"
    _description    = "Master Items Lines"

    item_id = fields.Many2one('master.item','Item',ondelete='cascade')
    component_id = fields.Many2one('master.component','Component', required=True)
    day = fields.Integer('Days', related='component_id.day', store=True)
    percent = fields.Float('Percent (%)', required=True, default=0.1)

    @api.onchange('percent')
    def _onchange_percent(self):
        if self.percent < 0.0 :
            raise ValidationError(_('Percent must be positif'))
        elif self.percent > 100.0 :
            raise ValidationError(_('Maximum percent cannot be more than 100 %'))



MasterItemLines()


class MasterComponent(models.Model):
    _name           = "master.component"
    _description    = "Master Component"

    name = fields.Char('Name',required=True, size=200)
    day = fields.Integer('Days', required=True, default=1)

    @api.one
    @api.constrains('day') 
    def _check_day(self):
        total_percent = self.day
        if total_percent < 0.0:
            raise ValidationError(_('Days must be positif'))

    _sql_constraints = [
        ('name_uniq', 'unique(name)',("Component Name must be uniq."))
    ]

MasterComponent()