#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""My first wheezy.web app"""

import csv
import datetime
import locale
import logging
import traceback

from wheezy.http import WSGIApplication
from wheezy.web.middleware import bootstrap_defaults
from wheezy.web.middleware import path_routing_middleware_factory

from wheezy.web import handlers
from wheezy.routing import url
from wheezy.web.handlers import file_handler

from haskybanking import config

LOG = logging.getLogger('qiqnote.app')


locale.setlocale(locale.LC_ALL, 'cs_CZ.utf8')


class MainView(handlers.BaseHandler):

    def __init__(self, request):
        super(MainView, self).__init__(request)

        self._r = request
        self.ignored = []

    def _bool(self, field, default=''):
        val = self._r.form.get(field, self._r.query.get(field, default))
        print(field + ' = ' + str(val))
        print(val == ['true'])
        return val == ['true']

    def get(self):
        return self.render_response('upload.html')

    def post(self):
        try:
            if 'exported' not in self._r.files:
                raise Exception('File not uploaded!')
            fields = self._r.files['exported']
            fileinfo = fields[0]
            payments = self._parse_file(
                fileinfo.file,
                semicol=self._bool('semicol'),
                skip_first=self._bool('skipfirst'))
            payments = self._filter_valid(payments)

            accounts = {}
            months = []
            for p in payments:
                if p['accname'] not in accounts:
                    accounts[p['accname']] = p['account']
                if p['month'] not in months:
                    months.append(p['month'])

            payments = self._group_by_account_and_month(payments, months)

            #raise ValueError(self.ignored)
            return self.render_response(
                'processed.html',
                payments=payments,
                accounts=accounts,
                months=months,
                ignored=self.ignored)
        except Exception as e:
            return self.render_response('exception.html',
                                        exc=traceback.format_exc(e))

    def _filter_valid(self, payments):
        valid = []
        for record in payments:
            if record['value'] <= 0:
                continue
            valid.append(record)
        return valid

    def _group_by_account_and_month(self, payments, months=None):
        grouped = self._group_by_account(payments)
        for acc in grouped:
            grouped[acc] = self._group_by_month(grouped[acc], months)
        return grouped

    def _group_by(self, payments, col_number, getter=None,
                  padto=None):
        if getter is None:
            getter = lambda (item): item[col_number]
        if padto is None:
            padto = []

        grouped = {}
        for payment in payments:
            val = getter(payment)
            grouped.setdefault(val, []).append(payment)
        for pad_val in padto:
            if not pad_val in grouped:
                grouped[pad_val] = []
        return grouped

    def _group_by_account(self, payments):
        return self._group_by(payments, 'accname')

    def _group_by_month(self, payments, months):
        return self._group_by(
            payments, None,
            getter=lambda (item): item['month'],
            padto=months)

    def _parse_file(self, csvfile, semicol=False, skip_first=True):
        payments = []
        if semicol:
            delim = ';'
        else:
            delim = ','
        reader = csv.reader(csvfile, delimiter=delim)
        for line in reader:
            if skip_first:
                skip_first = False
                continue
            try:
                payments.append(self._convert_line(line))
            except InvalidLineError as e:
                self.ignored.append(e)
            #info['csv_fields'].append(line[0].decode('cp1250'))
        return payments

    def _convert_line(self, line):
        # 0 "Typ transakce"
        # 1 "Datum zaúčtování"    <----------------------
        # 2 "Variabilní symbol 2"
        # 3 "Částka v měně účtu (orientační hodnota)"    <-------------
        # 4 "Měna účtu"    <----------------------
        # 5 "Bankovní spojení"    <----------------------
        # 6 "Datum zpracování"
        # 7 "Variabilní symbol 1"    <----------------------
        # 8 "Částka v měně transakce"
        # 9 "Měna transakce"
        # 10 "Název protiúčtu"    <----------------------
        # 11 "Konstantní symbol"    <----------------------
        # 12 "Specifický symbol"    <----------------------
        # 13 "Storno"
        # 14 "Zpráva pro příjemce"    <----------------------
        # 15 "Zpráva pro mě"
        # 16 "Referenční číslo transakce"

        # 17 "Klientská poznámka"

        # "Tento export obsahuje seznam transakcí zobrazených na aktuální
        #  ... obrazovce internetbankingu. Nejedná se o úplný seznam
        #  ... transakcí odpovídající zadaným filtračním kritériím."
        obj = {
            'account': line[5],
            'accname': line[10],
            'date': line[1],
            'value': line[3],
            'currency': line[4],
            'varsym': line[7],
            'consym': line[11],
            'specsym': line[12],
            'note': line[14],
            'extra': ';'.join(line)
        }
        for key in obj:
            obj[key] = obj[key].decode('cp1250')

        try:
            obj['date'] = datetime.datetime.strptime(obj['date'], '%Y/%m/%d')
            obj['value'] = float(obj['value'].replace(',', '.'))
            obj['month'] = obj['date'].strftime('%Y-%m')
            #obj['month'] = obj['date'].strftime('%Y-%B').decode('utf-8')
        except Exception as e:
            raise InvalidLineError(obj, str(e))
        return obj


class InvalidLineError(Exception):
    def __init__(self, line_obj, exc):
        super(InvalidLineError, self).__init__()
        self.line = line_obj
        self.exc = exc

    def __str__(self):
        msg = []
        for v in self.line.values():
            msg.append(unicode(v))
        msg.append(unicode(self.exc))
        return u' | '.join(msg)

url_map = [
    url('', MainView, name='index'),
    url('static/{path:any}',
        file_handler(root=config.app_path('static/')),
        name='static'),
]

application = WSGIApplication(
    middleware=[
        bootstrap_defaults(url_mapping=url_map),
        path_routing_middleware_factory
    ],
    options=config.options)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    try:
        LOG.info('Launching on http://localhost:5000/ ...')
        make_server('', 5000, application).serve_forever()
    except KeyboardInterrupt:
        LOG.info('... exiting')
    LOG.info('\nThanks for trying me!')
