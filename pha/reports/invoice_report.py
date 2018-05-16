from odoo import api, models

class PhaInvoiceReport(models.AbstractModel):
    _name = 'report.pha.report_pha_invoice'
    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('pha.pha_report_invoice')
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('pha.pha_report_invoice', docargs)