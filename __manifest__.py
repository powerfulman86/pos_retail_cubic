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
        'views/area.xml',
        'views/import.xml',
        'views/payment.xml',
        'views/pos_config.xml',
        'views/pos_reporting.xml',
        'views/pos_sale_report.xml',
        'views/pos_session.xml',
        'report/pos_analysis.xml',
        'report/pos_sale_report_template.xml',
        'report/pos_warehouse_branch_report.xml',
        'report/pos_warehouse_move_report.xml',
    ],
    'qweb': [
        'static/src/xml/Report.xml',
        'static/src/xml/OrderReceiptHtmlVersion20.xml',
        'static/src/xml/KeyboardGuideWdiget.xml',
        'static/src/xml/screens/Payment.xml',
        # 'static/src/xml/screens/ActionpadWidget.xml',
    ],
}
