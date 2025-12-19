# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

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
    _sql_constraints = [
        ('name_unique', 'unique(name, parent_id)', 'Nama siswa dengan orang tua yang sama harus unik!')
    ]

    penilaian_ids = fields.One2many(
        'siswa.kursus.penilaian.sertifikat',
        'enrollment_id',
        string='Penilaian Sertifikat'
    )

    average_score = fields.Float(
        string='Rata-rata Nilai',
        related='penilaian_ids.average_score',
        store=True,
        readonly=True
    )

    assessment_line_ids = fields.One2many(
        string='Detail Penilaian',
        related='penilaian_ids.assessment_line_ids',
        readonly=True
    )
    
    # Fields and methods moved from enrollment_extension for direct availability
    has_certificate_assessment = fields.Boolean(
        string="Ada Penilaian Sertifikat",
        compute="_compute_has_certificate_assessment",
        store=False # No need to store, computed on-the-fly
    )

    @api.depends('status') 
    def _compute_has_certificate_assessment(self):
        for rec in self:
            rec.has_certificate_assessment = bool(self.env['siswa.kursus.penilaian.sertifikat'].search([('enrollment_id', '=', rec.id)], limit=1))

    def action_create_or_view_certificate_assessment(self):
        self.ensure_one()
        
        # Search for existing assessment
        existing_assessment = self.env['siswa.kursus.penilaian.sertifikat'].search([('enrollment_id', '=', self.id)], limit=1)
        
        action = self.env['ir.actions.act_window']._for_xml_id('students.action_siswa_kursus_penilaian_sertifikat')
        
        if existing_assessment:
            action['res_id'] = existing_assessment.id
            action['views'] = [(False, 'form')] 
            return action

        # Create new assessment
        new_assessment = self.env['siswa.kursus.penilaian.sertifikat'].create({
            'enrollment_id': self.id,
        })

        # Pre-fill assessment lines from modul.pembelajaran.penilaian.item
        if self.modul_id and self.modul_id.penilaian_item_ids:
            for item in self.modul_id.penilaian_item_ids:
                self.env['siswa.kursus.penilaian.sertifikat.line'].create({
                    'assessment_id': new_assessment.id,
                    'penilaian_item_id': item.id,
                    'sequence': item.sequence,
                    'score': 0.0,
                })
        
        action['res_id'] = new_assessment.id
        action['views'] = [(False, 'form')]
        return action


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
