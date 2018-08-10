# coding=utf-8
import binascii
import random
import re
import string
import hashlib

import xlrd
from django.utils.crypto import get_random_string

BIT = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
UNIT = ['', '十', '百', '千']
SECOND_UNIT = ['', '万', '亿']


def pretty_hexlify(data):
    if len(data) == 0:
        return ''
    return binascii.hexlify(data).decode('ascii').upper()


def cnum(num):
    result = ''
    strNum = str(num)
    unitStep = -1
    for i in range(-1, -len(strNum) - 1, -4):
        unitStep += 1
        digits = strNum[i: i - 4: -1]
        if digits == '0000': continue
        digitStr = ''
        for j in range(0, len(digits)):
            d = int(digits[j])
            digitStr = BIT[d] + (d > 0 and UNIT[j] or '') + digitStr
        digitStr = re.sub('零{2,}', '零', digitStr)
        if digitStr[-1] == '零':
            digitStr = digitStr[: -1]
        result = digitStr + SECOND_UNIT[unitStep] + result
    return result


def get_unique_id(length=16):
    return get_random_string(length)


def get_random_number(length=6):
    items = []
    chars = list(string.digits)
    for i in range(length):
        items.append(chars[random.randint(0, len(chars) - 1)])
    return ''.join(items)


def get_cell_text_value(cell):
    if cell.ctype == xlrd.XL_CELL_NUMBER:
        int_value = int(cell.value)
        str_value = str(int_value).strip()
        return str_value
    elif cell.ctype == xlrd.XL_CELL_TEXT:
        return str(cell.value).strip()
    else:
        return None


def generate_md5(original):
    hl = hashlib.md5()
    hl.update(original.encode(encoding='utf-8'))
    return hl.hexdigest()
