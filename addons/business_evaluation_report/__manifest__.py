{
    'name': 'Purchase Inventory Sales Report',
    'summary': """This module allows to generate Sales, Inventory and Purchase Reports with variant wise filter.""",
    'version': '10.0.1.0',
    'description': """This module allows to generate Sales, Inventory and Purchase Reports with variant wise filter. All variants of any particular product can be filtered which adds great business intelligence in terms which variant is popular or which are not. The report can also be downloaded as Excel compatible file.""",
    'author': 'Metamorphosis',
    'company': 'Metamorphosis ltd.',
    'website': 'http://metamorphosis.com.bd/',
    'category': 'Extra Tools',
    'images': [
        'static/description/purchase-inventory-sales.png',
        ],
    'license': 'OPL-1',
    'depends': [
        'base',
        'sale',
        'stock',
        'purchase'
    ],
    'data': [
        'views/sales_inventory_purchase_custom_report.xml',
    ],
    'installable': True,
    'auto_install': False,
} 
