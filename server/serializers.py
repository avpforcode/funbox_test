import re
from marshmallow import Schema, fields
from urllib.parse import urlparse
from datetime import datetime


class TimeSerializer(fields.String):
    def _deserialize(self, time_value: str, *args, **kwargs):
        """ Check if time format is correct """
        try:
            datetime.fromtimestamp(int(time_value))
            return time_value
        except (TypeError, OverflowError, OSError):
            return {"bad_value": time_value}


class LinkField(fields.String):
    def _deserialize(self, link: str, *args, **kwargs):
        """ Eject domain from link. Domain can be next formats:
        example.com
        example.com:8080
        localhost
        127.0.0.1
        10.10.0.1:4000

        :param link: an uri
        :return: domain string ejected from link or dict["bad_value]
        """
        try:
            # url must be string
            if not isinstance(link, str):
                return {"bad_value": str(link)}

            parse = urlparse(link)
            if parse.netloc:
                return parse.netloc

            # check with regexp if urlparse didn't find a domain
            domain_reg = re.compile(
                r'^([a-z\d]+\.\w{2,4}'  # simple domain check
                r'|localhost)'  # maybe localhost
                r'(:\d{2,5})?'  # possible port
            )
            domain_without_scheme = re.match(domain_reg, link)
            if domain_without_scheme:
                return domain_without_scheme[0]

            # check if domain is an ip address
            ip_address_reg = re.compile(
                r'((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}'  # ip
                r'(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])'  # ip
                r'(:\d{2,5})?'  # possible port
                r'($|/)'  # end of domain
            )
            ip_address_without_scheme = re.match(ip_address_reg, link)
            if ip_address_without_scheme:
                return ip_address_without_scheme[0].rstrip('/')

            return {"bad_value": link}
        except (AttributeError, TypeError):
            return {"bad_value": link}


class LinksSerializer(Schema):
    """ Schema of post request body (visited_domains) """
    links = fields.List(LinkField())
