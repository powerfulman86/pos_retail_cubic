# -*- coding: utf-8 -*-
{
    'name': "pos_retail_cubic",
    'summary': """POS cubic custom """,
    'description': """POS cubic custom """,
    'author': "",
    'category': 'Uncategorized',
    'version': '13.0.0.1',
    'depends': ['base', 'point_of_sale', 'pos_retail'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/pos_config.xml',
        'security/ir.model.access.csv',

        'views/import.xml',
        'views/pos_config.xml',
        'views/stock_warehouse.xml',
        'views/pos_sale_report.xml',
        'views/pos_session.xml',

        'report/pos_sale_report_template.xml',
        'report/warehouse_product.xml',
    ],
    'qweb': [
        'static/src/xml/Report.xml',
        'static/src/xml/OrderReceiptHtmlVersion20.xml',
        'static/src/xml/KeyboardGuideWdiget.xml',
    ],

}
