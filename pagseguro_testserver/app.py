#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import uuid
from datetime import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options


define(
    'port', 
    default=443, 
    help=u'run in given port', 
    type=int
)


define(
    'certfile', 
    help=u'certfile path',
    default=os.path.join(os.path.dirname(__file__), 'server.crt'),
)


define(
    'keyfile', 
    help=u'keyfile path',
    default=os.path.join(os.path.dirname(__file__), 'server.key'),
)

define(
    'return_url', 
    help=u'return url',
    default='http://127.0.0.1:8000/pagamentos/pagseguro/retorno/',
)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/security/webpagamentos/webpagto.aspx', PaymentHandler),
            (r'/Security/NPI/Default.aspx', VerifyPaymentHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            xsrf_cookies=False,
            debug=True,
            autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class PaymentHandler(tornado.web.RequestHandler):

    def post(self):
        # get all arguments
        request_arguments = self.request.arguments

        # parse items
        items = []
        for argument in request_arguments:
            if argument.startswith('item_id'):
                # get id
                id = argument.split('_')[2]
                
                # parse amount
                valor = int(request_arguments.get('item_valor_' + id, [0])[0])
                valor = valor / 100.0
                if valor < 0:
                    valor = valor * 10.0
                valor = '%.2f' % valor
                
                # new item
                item = {
                    'ProdID_'+id: request_arguments.get('item_id_'+id, [''])[0],
                    'ProdDescricao_'+id: request_arguments.get('item_descr_'+id, [''])[0],
                    'ProdQuantidade_' + id: request_arguments.get('item_quant_'+id, [''])[0],
                    'ProdFrete_' + id: '0,00',
                    'ProdValor_' + id: valor,
                }
                items.append(item) 

        # create data
        data = {
            'VendedorEmail': request_arguments.get('email_cobranca', [''])[0],
            'TransacaoID': str(uuid.uuid1()),
            'Referencia': request_arguments.get('ref_transacao', [''])[0],
            'TipoFrete':      'FR',
            'ValorFrete':     '0,00',
            'Anotacao':       'Pagamento gerado pelo ambiente de testes',
            'DataTransacao':  datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'CliNome':        'Nome do Cliente',
            'CliEmail':       'email@cliente.com.br',
            'CliEndereco':    'Rua do Cliente',
            'CliNumero':      '0001',
            'CliComplemento': 'Complemento do Endereço do Cliente',
            'CliBairro':      'Bairro do Cliente',
            'CliCidade':      'Cidade do Cliente',
            'CliEstado':      'PB',
            'CliCEP':         '58410-000',
            'CliTelefone':    '(83) 0000-0000',
            'NumItens':       len(items),
        }

        # insert items
        for item in items:
            for k, v in item.iteritems():
                data[k] = v

        self.render('payment.html', return_url=options.return_url, data=data)


class VerifyPaymentHandler(tornado.web.RequestHandler):

    def post(self):
        self.write('VERIFICADO')


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(
        Application(),
        ssl_options={
            'certfile': options.certfile,
            'keyfile': options.keyfile,
        }
    )
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
