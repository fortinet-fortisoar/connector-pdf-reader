""" Copyright start
  Copyright (C) 2008 - 2023 Fortinet Inc.
  All rights reserved.
  FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE
  Copyright end """

import io, os
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from os.path import join
from connectors.core.connector import get_logger, ConnectorError
from connectors.cyops_utilities.builtins import download_file_from_cyops
from integrations import settings

logger = get_logger('pdf-reader')


def extract_text_by_page(pdf_path, password=None):
    try:
        with open(pdf_path, 'rb') as fh:
            for page in PDFPage.get_pages(fh, password=password, caching=True, check_extractable=True):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(resource_manager, fake_file_handle)
                page_interpreter = PDFPageInterpreter(resource_manager, converter)
                page_interpreter.process_page(page)
                text = fake_file_handle.getvalue()
                yield text
                converter.close()
                fake_file_handle.close()
    except Exception as e:
        logger.error(e)
        raise ConnectorError(e)


def extract_text_per_page(pdf_path, page_num, password=None):
    try:
        with open(pdf_path, 'rb') as fh:
            for pagenumber, page in enumerate(
                    PDFPage.get_pages(fh, password=password, caching=True, check_extractable=True)):
                if pagenumber == (page_num - 1):
                    resource_manager = PDFResourceManager()
                    fake_file_handle = io.StringIO()
                    converter = TextConverter(resource_manager, fake_file_handle)
                    page_interpreter = PDFPageInterpreter(resource_manager, converter)
                    page_interpreter.process_page(page)
                    text = fake_file_handle.getvalue()
                    yield text
                    converter.close()
                    fake_file_handle.close()
    except Exception as e:
        logger.error(e)
        raise ConnectorError(e)


def extract_text(pdf_path):
    ext_text = ""
    for page in extract_text_by_page(pdf_path):
        ext_text += page
    return ext_text


def export_as_json(pdf_path, page_num=None, password=None):
    try:
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        data = {'filename': filename}
        data['pages'] = []
        counter = 1
        if page_num == None:
            for page in extract_text_by_page(pdf_path, password=password):
                data.get('pages').append(page)
                counter += 1
            return data
        for page in extract_text_per_page(pdf_path, page_num, password=password):
            data.get('pages').append(page)
            return data
    except Exception as e:
        logger.error(e)
        raise ConnectorError(e)


def get_file_location(params):
    try:
        file_iri = params.get('file_iri')
        file_path = params.get('file_path')
        if file_iri:
            file_iri = settings.CRUD_HUB_URL + file_iri
            file_download_response = download_file_from_cyops(file_iri)
            file_path = join('/tmp', file_download_response['cyops_file_path'])
            return file_path
        if file_path:
            if not file_path.startswith('/tmp/'):
                file_path = '/tmp/' + file_path
                return file_path
            else:
                return file_path
    except Exception as e:
        logger.error(e)
        raise ConnectorError(e)


def read_all_pages(params):
    try:
        file_path = get_file_location(params)
        password = params.get('password')
        # set password to None if no password or an empty string is provided
        if not password:
            password = None
        data = export_as_json(file_path, password=password)
        return data
    except Exception as e:
        logger.error(e)
        raise ConnectorError(e)


def read_page(params):
    try:
        file_path = get_file_location(params)
        page_num = params.get('page_num')
        password = params.get('password')
        # set password to None if no password or an empty string is provided
        if not password:
            password = None
        return export_as_json(file_path, page_num, password=password)
    except Exception as e:
        logger.error(e)
        raise ConnectorError(e)


operations = {
    'read_all_pages': read_all_pages,
    'read_page': read_page}
