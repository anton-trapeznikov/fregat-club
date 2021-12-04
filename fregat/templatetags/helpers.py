from django import template
import math
import string


register = template.Library()


@register.filter
def callable_phone(src):
    raw_phone = src or ''
    raw_phone = str(raw_phone).split(',')[0]

    phone = ''.join([x for x in raw_phone if x in string.digits])

    if phone and phone[0] == '8':
        phone = '7%s' % phone[1:]

    return phone


@register.filter(name='draw_price')
def draw_price(value):
    value = value or 0

    if isinstance(value, (str, bytes)):
        value = float(value.replace(',', '.'))

    price = float(value)

    int_price = int(math.floor(price))
    residue = int(math.floor((price - int_price) * 100))

    parts = '{0:,}'.format(int_price).replace(',', ' ').split(' ')
    result = ''
    pairs = []
    for index, digit in enumerate(parts):
        class_name = "price__digit price__digit_%s" % (index + 1)

        if index + 1 == len(parts):
            class_name += ' price__digit_last'

        pairs.append([digit, class_name])

    if residue > 0:
        pairs[-1][1] += ' price__digit_before-cents'
        pairs.append([
            ',%s' % residue,
            'price__digit price__digit_cents'
        ])

    pairs[-1][1] += ' price__digit_before-ruble'
    pairs.append(['₽', 'price__ruble'])

    result = '<span class="price">'
    for data_and_class in pairs:
        result += '<span class="%s">%s</span>' % (
            data_and_class[1],
            data_and_class[0]
        )
    result += '</span>'

    return result