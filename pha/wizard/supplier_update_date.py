from odoo import api, fields, models, _


class ResPartner(models.TransientModel):
    _name="supplier.update.date.wizard"

    start_date= fields.Date("Date debut")
    end_date= fields.Date("Date fin")
    supplier_id = fields.Many2one("res.partner")


    def update_date(self):
        for s in self.supplier_id.suppliers_ids:
            s.write(
                {'date_start': self.start_date,
                 'date_end': self.end_date})