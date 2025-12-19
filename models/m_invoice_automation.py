# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class StudentProfileInvoiceAutomation(models.Model):
    # Ini bukan class baru, tapi kita menempelkan method baru ke class 'm.siswa'
    _inherit = 'm.siswa'

    def _cron_auto_create_invoice(self):
        """
        Metode ini dirancang untuk dijalankan oleh Cron Job Odoo.
        Fungsinya untuk memeriksa semua siswa aktif dan membuat invoice secara otomatis
        berdasarkan skema pembayaran dan jumlah pertemuan yang telah dihadiri.
        """
        _logger.info("Memulai Cron Job: Pembuatan Invoice Siswa Otomatis...")
        
        active_students = self.search([
            ('status', '=', 'active'),
        ])
        
        if not active_students:
            _logger.info("Tidak ada siswa aktif yang ditemukan.")
            _logger.info("Cron Job: Pembuatan Invoice Siswa Otomatis selesai.")
            return True

        for student in active_students:
            _logger.info(f"Mengecek siswa: {student.name} "
                         f"[Parent: {student.parent_id.name if student.parent_id else 'TIDAK ADA'}] | "
                         f"[Produk: {student.product_id.name if student.product_id else 'TIDAK ADA'}] | "
                         f"[Hadir: {student.jumlah_pertemuan_hadir}] | "
                         f"[Ditagih: {student.jumlah_pertemuan_ditagih}]")

            # Tentukan threshold berdasarkan skema pembayaran
            threshold = 0
            if student.skema_pembayaran == 'monthly':
                threshold = 4
            elif student.skema_pembayaran == 'semester':
                threshold = 12
            
            # Lewati jika skema tidak valid, orang tua tidak ada, atau produk tidak diset
            if not threshold or not student.parent_id or not student.product_id:
                _logger.warning(f"--> MELEWATI {student.name}: Data tidak lengkap (Skema/Orang Tua/Produk).")
                continue

            sessions_to_invoice = student.jumlah_pertemuan_hadir - student.jumlah_pertemuan_ditagih
            
            if sessions_to_invoice >= threshold:
                
                invoice_batch_count = sessions_to_invoice // threshold
                num_sessions_in_invoice = invoice_batch_count * threshold

                if num_sessions_in_invoice == 0:
                    continue

                _logger.info(f"--> AKAN MEMBUAT INVOICE untuk siswa: {student.name} ({num_sessions_in_invoice} pertemuan).")

                try:
                    product_to_use = student.product_id
                    invoice_vals = {
                        'partner_id': student.parent_id.id,
                        'move_type': 'out_invoice',
                        'invoice_date': fields.Date.context_today(self),
                        'invoice_line_ids': [(0, 0, {
                            'product_id': product_to_use.id,
                            'name': f"{product_to_use.name} - {student.name}",
                            'quantity': invoice_batch_count, # Tagih per batch (misal 1x produk bulanan)
                        })],
                    }
                    
                    new_invoice = self.env['account.move'].create(invoice_vals)
                    _logger.info(f"--> BERHASIL: Invoice {new_invoice.name} dibuat untuk {student.name}.")
                    
                    # Update jumlah ditagih dengan jumlah sesi yang baru saja masuk invoice
                    student.jumlah_pertemuan_ditagih += num_sessions_in_invoice
                    
                    # Lakukan commit untuk menyimpan perubahan jumlah_pertemuan_ditagih
                    self.env.cr.commit()

                except Exception as e:
                    _logger.error(f"--> GAGAL membuat invoice untuk {student.name}: {e}")
                    # Batalkan perubahan jika terjadi error
                    self.env.cr.rollback()
            else:
                _logger.info(f"--> MELEWATI {student.name}: Jumlah sesi belum mencapai threshold ({sessions_to_invoice}/{threshold}).")

        _logger.info("Cron Job: Pembuatan Invoice Siswa Otomatis selesai.")
        return True
