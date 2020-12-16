# -*- coding: utf-8 -*-
{
    'name': "payment_stripe_extended",

    'summary': """
        Extend payment_stripe integration""",

    'description': """
        -Allways create new PO from new SO
    """,

    'author': "pmmarquez@gmx.com",

    'category': 'Accounting/Payment',
    'version': '0.1',
    
    'depends': ['payment_stripe'],

    # always loaded
    # 'data': [
    #     # 'security/ir.model.access.csv',
    #     'views/views.xml',
    #     'views/templates.xml',
    # ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
