from odoo import models, fields, api, _
import time
from io import BytesIO
from collections import OrderedDict
import pytz
import xlsxwriter
import base64
from datetime import datetime
from pytz import timezone
from odoo.exceptions import UserError, Warning,ValidationError
import base64
import xlrd
from xlrd import open_workbook



class ImportItemWizard(models.TransientModel):
    _name = "import.item.wizard"
    _description = "Import Items"

    file_data = fields.Binary(string='Import File')
    filename = fields.Char(string='File Name')

    @api.multi
    def action_import(self):
        try :
            if not self.file_data :
                raise Warning("Silahkan upload file.")
            wb = open_workbook(file_contents=base64.decodestring(self.file_data))
            values = []
            
            for s in wb.sheets():
                for row in range(s.nrows):
                    col_value = []
                    for col in range(s.ncols):
                        value = (s.cell(row, col).value)
                        col_value.append(value)
                    values.append(col_value)
            item_obj = self.env['master.item']
            item_lines_obj = self.env['master.item.lines']
            component_obj = self.env['master.component']
            row = 1          
            for data in values :
                # posisi : name |  start_working_date | component_name | working_day | percentage
                if row != 1 :
                    item_name = data[0]
                    if not item_name :
                        raise UserError(_("Kolom name ada yang kosong"))
                    start_working_date = data[1]
                    if not start_working_date :
                        raise UserError(_("Kolom start_working_date ada yang kosong"))
                    component_name = data[2]
                    if not component_name :
                        raise UserError(_("Kolom component_name ada yang kosong"))
                    working_day = data[3]
                    if not working_day :
                        raise UserError(_("Kolom working_day ada yang kosong"))
                    percentage = data[4]
                    if not percentage :
                        raise UserError(_("Kolom percentage ada yang kosong"))
                    start_working_date = xlrd.xldate_as_tuple(start_working_date, wb.datemode) 
                    start_working_date = datetime(*start_working_date)
                    start_working_date = start_working_date.strftime("%Y-%m-%d")
                    #start_working_date = self.make_date_valid(start_working_date)
                    # cek di master komponen
                    component_exist = component_obj.search([('name','=',component_name)],limit=1)
                    if component_exist :
                        component_id = component_exist.id
                    else :
                        component = component_obj.create({'name' : component_name,
                                                            'day' : int(working_day)})
                        component_id = component.id

                    # cek di master item
                    item_exist = item_obj.search([('name','=',item_name)],limit=1)
                    if not item_exist :
                        item = item_obj.create({'name' : item_name,
                                                'date' : start_working_date,
                                                'line_ids' : [(0, 0, {'component_id': component_id, 
                                                                        'percent' : float(percentage)})]
                                                })
                    else :
                        item = item_lines_obj.create({'item_id' : item_exist.id,
                                                        'component_id' : component_id,
                                                        'percent' : float(percentage)})

                row += 1
        except Exception as e :
            raise Warning(e)
        views = [(self.env.ref('toffin_test.item_master_tree_view').id,'tree'),(self.env.ref('toffin_test.master_item_form_view').id,'form')]
        return {
            'name' : _('Master Items'),
            'domain' : [],
            'view_type' : 'form',
            'res_model' : 'master.item',
            'context' : {},
            'view_id' : False,
            'views': views,
            'view_mode' : 'tree,form',
            'type':'ir.actions.act_window',
        }


    def make_date_valid(self, date_string):
        date_valid = '%s-%s-%s'%(date_string[-4:], month_range[date_string[3:6]], date_string[0:2])
        return date_valid

ImportItemWizard()