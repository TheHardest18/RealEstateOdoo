# -*- coding: utf-8 -*-
{
    'name': "Real State",
    'summary': """
        Module Real Estate""",
    'description': """
        Module Real EState
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Customizations',
    'version': '13.0.0.0.1',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
        'report/estate_report_templates.xml',
        'report/estate_report_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml'
    ],
}
