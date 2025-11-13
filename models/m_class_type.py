# -*- coding: utf-8 -*-
from odoo import models, fields

class StudentClassType(models.Model):
    _name = 'm.class.type'
    _description = 'Master Jenis Kelas (Merakit, Scratch Jr, dll.)'
    _order = 'name'

    name = fields.Char(string='Nama Jenis Kelas', required=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Nama jenis kelas harus unik!')
    ]