from pyramid.response import Response

__author__ = 'Igor Maculan <n3wtron@gmail.com>'


def __new_response(json_data, headers=[]):
    resp = Response(json_body=json_data)
    if isinstance(headers, list):
        for header in headers:
            resp.headerlist.append(header)
    else:
        if isinstance(headers, tuple):
            resp.headerlist.append(headers)
    return resp
