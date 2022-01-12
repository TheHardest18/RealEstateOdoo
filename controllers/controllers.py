# -*- coding: utf-8 -*-
# from odoo import http


# class State(http.Controller):
#     @http.route('/state/state/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/state/state/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('state.listing', {
#             'root': '/state/state',
#             'objects': http.request.env['state.state'].search([]),
#         })

#     @http.route('/state/state/objects/<model("state.state"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('state.object', {
#             'object': obj
#         })
