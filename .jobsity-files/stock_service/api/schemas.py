# encoding: utf-8

from stock_service.extensions import marsh


class StockSchema(marsh.Schema):

    symbol = marsh.String(dump_only=True)
    name = marsh.String(dump_only=True)
    date = marsh.Date(dump_only=True)
    time = marsh.Time(dump_only=True)
    open = marsh.Float(dump_only=True)
    high = marsh.Float(dump_only=True)
    low = marsh.Float(dump_only=True)
    close = marsh.Float(dump_only=True)
