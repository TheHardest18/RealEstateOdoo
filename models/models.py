# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError
import datetime
# from datetime import date, timedelta


class state(models.Model):
    _name = 'estate.property'
    _description = 'state.state'
    _rec_name = 'name'
    _order = 'id desc'
    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'The name must be unique'),
        ('check_expectecd_price', 'check(expected_price >=0)', 'Valor debe ser positivo'),
        ('check_selling_price', 'check(selling_price >=0)', 'Valor debe ser positivo'),
    ]


    name = fields.Char(required=True)

    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=lambda self: fields.Date.today())
    expected_price = fields.Float(required=True, string="Expected Price")
    selling_price = fields.Float(copy=False, readonly=True, string="Selling Price")
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[
            ('N', 'North'),
            ('S', 'South'),
            ('E', 'East'),
            ('W', 'West'),])
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offerr','Offer Received'),
            ('offera','Offer Accepted'),
            ('sold','Sold'),
            ('cancel','Canceled'),], required=True, default='new', copy=False)
    ResPartner = fields.Many2one('res.partner', string="Buyer")
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True,
                              default=lambda self: self.env.user)
    property_type = fields.Many2one('estate.property.type',required=True)
    offer_ids = fields.One2many('estate.property.offer', 'property_id')
    tags_id = fields.Many2many('estate.property.tag')
    total_area = fields.Float(compute="_compute_total", string="Total Area (sqm)")
    best_price = fields.Float(compute="_compute_best", string="Best Offer")



    def unlink(self):
        for rec in self:
            if rec.state != "new" and rec.state != "cancel":
                raise exceptions.Warning('No puede eliminar este registro')
            else:
                pass
        return super(state, self).unlink()


    @api.constrains('selling_price')
    def _check_date_end(self):
        for record in self:
            porcentaje = record.expected_price * 90.0 / 100.0
            if record.selling_price < porcentaje:
                raise ValidationError("El Selling Price no puede ser inferior al 90% del expected price")

    def action_sold(self):
        if self.state == 'cancel':
            raise exceptions.Warning('No se puede Vender una propiedad Cancelada')
        else:
            self.state = 'sold'
        return True

    def action_cancel(self):
        if self.state == 'sold':
            raise exceptions.Warning("No se puede Cancelar una propiedad Vendida")
        else:
            self.state = 'cancel'
        return True

    @api.depends("living_area", "garden_area")
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best(self):
        for record in self:
        #todo: Hacer esto cuan buscas un maximo o te dira que la lista esta vacia
            record.best_price = 0
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden == True:
            self.garden_orientation = 'N'
            self.garden_area = 10
        else:
            self.garden_orientation = ''
            self.garden_area = 0

class stateProperty(models.Model):
    _name = 'estate.property.type'
    _description = 'Property'
    _order = 'name'
    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'The name must be unique')
    ]

    name = fields.Char(required=True)
    sequence = fields.Integer(default=1)
    property_ids = fields.One2many('estate.property', 'property_type')
    offer_ids = fields.One2many(related='property_ids.offer_ids')
    count = fields.Integer()
    offer_count = fields.Integer(compute='_compute_count')
    # Todo: Esto es realmente nuevo: contar registros relacionados entre si.
    @api.depends('offer_ids')
    def _compute_count(self):
        if self.ids:
            # count = 1
            for rec in self:
                rec.offer_count = 0
                rec.offer_count = self.env['estate.property.offer'].search_count([('property_type_id', '=', rec.id)])


class statePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'tags propertys'
    _order = 'name'
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The name must be unique')
    ]

    name = fields.Char(required=True)
    color = fields.Integer()

class statePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'offer propertys'
    _order = 'price desc'
    _sql_constraints = [
        ('check_price', 'check(price >=0)', 'El valor de Price debe ser positivo'),
    ]

    price = fields.Float()
    status = fields.Selection(selection=[('accepted','Accepted'),('refu','Refused')], copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Dealine", compute="_compute_validity_offer", inverse="_inverse_validity_offer")
    property_id = fields.Many2one('estate.property', required=True)
    property_type_id = fields.Many2one(related='property_id.property_type', store=True)

    # @api.model
    # def create(self, vals):
    #
    #     return super(state, self).create(vals)
    @api.model
    def create(self, vals):
        #todo: Buscar Objeto de un modelo (Esto analizalo)
        mobject = self.env['estate.property'].browse(vals["property_id"])
        for rec in mobject.offer_ids:
            if vals["price"] < rec.price:
                raise exceptions.Warning("No se puede crear una oferta menor a la existente")
        if vals["property_id"]:
            mobject.state = "offerr"

        return super(statePropertyOffer, self).create(vals)






    def action_offer_accepted(self):
        if self.status == 'refu':
            raise exceptions.Warning('La oferta ya fue rechazada no se puede aceptar.')
        else:
            self.status = 'accepted'
            self.property_id.state = 'offera'
            self.property_id.selling_price = self.price
            self.property_id.ResPartner = self.partner_id.id
        return True


    def action_offer_refused(self):
        self.status = 'refu'
        return True

    @api.depends("create_date", "validity")
    def _compute_validity_offer(self):
        for record in self:
            record.date_deadline = fields.Date.today()
            if record.create_date:
                record.date_deadline = record.create_date + datetime.timedelta(days=record.validity)

    def _inverse_validity_offer(self):
        for record in self:
            if record.validity:
                validity_delta = record.date_deadline - datetime.datetime.date(record.create_date)

                record.validity = validity_delta.days

class state_inherit(models.Model):
    # _name = "inherited.model"
    _inherit = "res.users"

    property_ids = fields.One2many('estate.property', 'user_id',
                                   domain="[('state', '=', 'new')]")
