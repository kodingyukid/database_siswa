# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StudentProfile(models.Model):
    _name = 'm.siswa'
    _description = 'Profil Siswa'
    # Tambahkan chatter di bawah (log histori)
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # --- Data Siswa ---
    name = fields.Char(string='Nama Siswa', required=True, tracking=True) # New direct name field

    class_name = fields.Char(string='Kelas', help="Contoh: 2 SD, TK B")
    school_origin = fields.Char(string='Asal Sekolah')
    
    # Relasi ke Master Tingkat
    level_id = fields.Many2one(
        'm.level.siswa', 
        string='Level',
        tracking=True
    )
    
    join_date = fields.Date(
        string='Tanggal Pertama Masuk',
        default=fields.Date.context_today,
        tracking=True
    )
    
    # Relasi ke Master Jenis Kelas
    class_type_id = fields.Many2one(
        'm.class.type', 
        string='Jenis Kelas',
        tracking=True
    )
    
    # Relasi ke Orang Tua (res.partner) - now exclusively for parent
    parent_id = fields.Many2one(
        'res.partner', 
        string='Nama Orang Tua',
        domain=[('is_company', '=', False)],
        help="Pilih kontak Orang Tua yang juga ada di modul Kontak."
    )
    
    # Ambil nomor telepon dari Orang Tua secara otomatis
    parent_contact = fields.Char(
        string='Contact Person (HP)',
        related='parent_id.phone', # Bisa diganti ke 'mobile'
        readonly=True
    )
    
    status = fields.Selection(
        [
            ('active', 'Siswa Aktif'),
            ('leave', 'Cuti'),
            ('graduated', 'Lulus'),
            ('inactive', 'Tidak Aktif'),
        ],
        string='Status',
        default='active',
        tracking=True
    )
    
    notes = fields.Text(string='Keterangan')

    # --- SQL Constraints ---
    # No partner_id_uniq constraint as partner_id is now for parent and not unique per student profile
    _sql_constraints = [
        ('name_unique', 'unique(name, parent_id)', 'Nama siswa dengan orang tua yang sama harus unik!')
    ]

    # --- Helper ---
    # Removed @api.onchange('partner_id') as partner_id is no longer for the student
