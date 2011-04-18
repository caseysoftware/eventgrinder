def slugify(value):
     """
     Normalizes string, converts to lowercase, removes non-alpha characters,
     and converts spaces to hyphens.
     Borrowed from Django, while trying to decouple my models from Django itself
     """
     import unicodedata
     value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
     value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
     return unicode(re.sub('[-\s]+', '-', value))