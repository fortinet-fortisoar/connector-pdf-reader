""" Copyright start
  Copyright (C) 2008 - 2021 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

from connectors.core.connector import Connector, ConnectorError, get_logger
from .operations import operations

logger = get_logger('pdf-reader')


class PDFReader(Connector):
    def execute(self, config, operation_name, params, **kwargs):
        try:
            logger.info("Action name: {}".format(operation_name))
            operation = operations.get(operation_name)
            result = operation(params)
            return result
        except Exception as e:
            logger.exception("An exception occurred {}".format(e))
            raise ConnectorError(e)



