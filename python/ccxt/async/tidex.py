# -*- coding: utf-8 -*-

from ccxt.async.liqui import liqui
import math


class tidex (liqui):

    def describe(self):
        return self.deep_extend(super(tidex, self).describe(), {
            'id': 'tidex',
            'name': 'Tidex',
            'countries': 'UK',
            'rateLimit': 2000,
            'version': '3',
            'has': {
                # 'CORS': False,
                # 'fetchTickers': True
                'fetchCurrencies': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30781780-03149dc4-a12e-11e7-82bb-313b269d24d4.jpg',
                'api': {
                    'web': 'https://web.tidex.com/api',
                    'public': 'https://api.tidex.com/api/3',
                    'private': 'https://api.tidex.com/tapi',
                },
                'www': 'https://tidex.com',
                'doc': 'https://tidex.com/public-api',
                'fees': [
                    'https://tidex.com/assets-spec',
                    'https://tidex.com/pairs-spec',
                ],
            },
            'api': {
                'web': {
                    'get': [
                        'currency',
                        'pairs',
                        'tickers',
                        'orders',
                        'ordershistory',
                        'trade-data',
                        'trade-data/{id}',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'tierBased': False,
                    'percentage': True,
                    'taker': 0.1 / 100,
                    'maker': 0.1 / 100,
                },
            },
        })

    def common_currency_code(self, currency):
        if not self.substituteCommonCurrencyCodes:
            return currency
        if currency == 'XBT':
            return 'BTC'
        if currency == 'BCC':
            return 'BCH'
        if currency == 'DRK':
            return 'DASH'
        # they misspell DASH as DSH?(may not be True)
        if currency == 'DSH':
            return 'DASH'
        # their MGO stands for MGO on WAVES(aka WMGO), see issue  #1487
        if currency == 'MGO':
            return 'WMGO'
        # the MGO on ETH is called EMGO on Tidex
        if currency == 'EMGO':
            return 'MGO'
        return currency

    async def fetch_currencies(self, params={}):
        currencies = await self.webGetCurrency(params)
        result = {}
        for i in range(0, len(currencies)):
            currency = currencies[i]
            id = currency['Symbol']
            precision = currency['AmountPoint']
            code = self.common_currency_code(id)
            active = currency['Visible'] is True
            status = 'ok'
            if not active:
                status = 'disabled'
            canWithdraw = currency['WithdrawEnable'] is True
            canDeposit = currency['DepositEnable'] is True
            if not canWithdraw or not canDeposit:
                active = False
            result[code] = {
                'id': id,
                'code': code,
                'name': currency['Name'],
                'active': active,
                'status': status,
                'precision': precision,
                'funding': {
                    'withdraw': {
                        'active': canWithdraw,
                        'fee': currency['WithdrawFee'],
                    },
                    'deposit': {
                        'active': canDeposit,
                        'fee': 0.0,
                    },
                },
                'limits': {
                    'amount': {
                        'min': None,
                        'max': math.pow(10, precision),
                    },
                    'price': {
                        'min': math.pow(10, -precision),
                        'max': math.pow(10, precision),
                    },
                    'cost': {
                        'min': None,
                        'max': None,
                    },
                    'withdraw': {
                        'min': currency['WithdrawMinAmout'],
                        'max': None,
                    },
                    'deposit': {
                        'min': currency['DepositMinAmount'],
                        'max': None,
                    },
                },
                'info': currency,
            }
        return result

    def get_version_string(self):
        return ''
