# -*- coding: utf-8 -*-
from odoo import models, fields

class StudentLevel(models.Model):
    _name = 'm.level.siswa'
    _description = 'Master Tingkat Siswa (Builder, Creator, dll.)'
    _order = 'sequence, name'

    name = fields.Char(string='Nama Tingkat', required=True)
    sequence = fields.Integer(string='Urutan', default=10)
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Nama tingkat harus unik!')
    ]