# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StudentCourseEnrollment(models.Model):
    _name = 'siswa.kursus.enrollment'
    _description = 'Pendaftaran Kursus Siswa'
    _order = 'tanggal_mulai desc'

    name = fields.Char(string="Pendaftaran", compute='_compute_name', store=True)
    
    siswa_id = fields.Many2one(
        'm.siswa', 
        string='Siswa', 
        required=True, 
        ondelete='cascade',
        index=True
    )
    modul_id = fields.Many2one(
        'modul.pembelajaran', 
        string='Kursus/Modul', 
        required=True
    )
    tanggal_mulai = fields.Date(
        string='Tanggal Mulai', 
        default=fields.Date.context_today,
        required=True
    )
    tanggal_selesai = fields.Date(string='Tanggal Selesai')
    
    status = fields.Selection([
        ('aktif', 'Aktif'),
        ('lulus', 'Lulus'),
        ('berhenti', 'Berhenti')
    ], string='Status', default='aktif', required=True, tracking=True)

    jumlah_pertemuan_wajib = fields.Integer(
        string="Sesi Wajib",
        compute='_compute_jumlah_pertemuan_wajib',
        store=True
    )

    # Field ini akan diisi oleh modul absensi_siswa
    jumlah_pertemuan_diikuti = fields.Integer(
       string="Sesi Diikuti",
       readonly=True,
       default=0
    )

    @api.depends('siswa_id.name', 'modul_id.name')
    def _compute_name(self):
        for rec in self:
            if rec.siswa_id and rec.modul_id:
                rec.name = f"{rec.siswa_id.name} - {rec.modul_id.name}"
            else:
                rec.name = "Pendaftaran Baru"

    @api.depends('modul_id.materi_ids')
    def _compute_jumlah_pertemuan_wajib(self):
        for rec in self:
            if rec.modul_id:
                rec.jumlah_pertemuan_wajib = len(rec.modul_id.materi_ids)
            else:
                rec.jumlah_pertemuan_wajib = 0
