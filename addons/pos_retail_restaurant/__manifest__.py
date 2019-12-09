# -*- coding: utf-8 -*-
{
    'name': "POS Kitchen/Bar screen",
    'version': '10.5.3.3',
    'live_test_url': 'http://posodoo.com/web/signup',
    'category': 'Point of Sale',
    'author': 'TL Technology',
    'price': '100',
    'website': 'http://posodoo.com',
    'sequence': 0,
    'description': "At Restaurant we're have multi device (cashiers, waiters, kitchens ) "
                   "and use multi devices, module support syncing all devices at restaurant"
                   "Syncing between kitchen/bar room with cashiers, waiters ...",
    'depends': ['pos_retail', 'pos_restaurant'],
    'data': [
        'import/template.xml',
        'views/restaurant.xml',
        'views/pos_config.xml',
        'views/product.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'demo': ['demo/demo.xml'],
    "currency": 'EUR',
    'application': True,
    'images': ['static/description/icon.png'],
    'support': 'thanhchatvn@gmail.com',
    "license": "OPL-1"
}
