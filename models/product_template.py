# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# Copyright 2019 ForgeFlow S.L.
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    last_purchase_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        related="product_variant_ids.last_purchase_line_ids",
        string="Last Purchase Order Lines",
    )
    last_purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        compute="_compute_last_purchase_line_id",
        string="Last Purchase Line",
    )
    last_purchase_price = fields.Float(
        compute="_compute_last_purchase_line_id_info", string="Last Purchase Price"
    )
    last_purchase_date = fields.Datetime(
        compute="_compute_last_purchase_line_id_info", string="Last Purchase Date"
    )
    last_purchase_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_last_purchase_line_id_info",
        string="Last Supplier",
    )
    last_purchase_currency_id = fields.Many2one(
        comodel_name="res.currency",
        compute="_compute_last_purchase_line_id_info",
        string="Last Purchase Currency",
    )
    show_last_purchase_price_currency = fields.Boolean(
        related="product_variant_ids.show_last_purchase_price_currency",
    )
    last_purchase_price_currency = fields.Float(
        string="Last currency purchase price",
        related="product_variant_ids.last_purchase_price_currency",
        digits=0,
    )

    standard_price_with_taxes = fields.Float(
        'Costo con Impuesto', compute='_compute_standard_price_with_taxes',
        digits='Product Price', groups="base.group_user")

    @api.depends("last_purchase_line_ids")
    def _compute_last_purchase_line_id(self):
        for item in self:
            item.last_purchase_line_id = fields.first(item.last_purchase_line_ids)

    @api.depends("last_purchase_line_id")
    def _compute_last_purchase_line_id_info(self):
        for item in self:
            item.last_purchase_price = item.last_purchase_line_id.price_unit
            item.last_purchase_date = item.last_purchase_line_id.date_order
            item.last_purchase_supplier_id = item.last_purchase_line_id.partner_id
            item.last_purchase_currency_id = item.last_purchase_line_id.currency_id
    
    @api.onchange('last_purchase_price', 'supplier_taxes_id')
    def _onchange_product_cost_taxes(self):
        for product in self:
            product._compute_standard_price_with_taxes()

    def _compute_standard_price_with_taxes(self):
        for product in self:
            product.standard_price_with_taxes = 0.0
            if product.supplier_taxes_id:
                taxes = product.supplier_taxes_id[0].compute_all(product.last_purchase_price, product.cost_currency_id, 1, product=product, partner=False)
                # price_subtotal = taxes['total_excluded']
                price_subtotal_incl = taxes['total_included']
                product.standard_price_with_taxes = price_subtotal_incl
