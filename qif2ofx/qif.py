from typing import List
from datetime import datetime
from operator import attrgetter
from dateutil import parser
from glob import glob
from dataclasses import dataclass

from decimal import Decimal
from datetime import datetime

import xml.etree.ElementTree as ET

from ofxtools.utils import UTC

@dataclass
class QIFEntry:
    # Code T
    # Amount of the item. For payments, a leading minus sign 
    # is required. For deposits, either no sign or a leading plus 
    # sign is accepted. Do not include currency symbols 
    # ($, £, ¥, etc.). Comma separators between thousands are 
    # allowed. 
    amount: Decimal

    # Code P
    # Payee. Or a description for deposits, transfers, etc. 
    payee: str

    # Code D
    # Date. Leading zeroes on month and day can be skipped. 
    # Year can be either 4 digits or 2 digits or '6 (=2006). 
    date: datetime

    # Free text, not used in QIF
    reference: str

    @staticmethod
    def parse(raw_transaction: List[str]):
        amount = None
        payee = None
        date = None
        for line in raw_transaction:
            if line.startswith('P'):
                payee = line[1:].strip()
            elif line.startswith('T'):
                amount = Decimal(line[1:].strip().replace(',', ''))
                # We're only dealing with CCs here, negative means debit
                # and positive means credit
                amount = amount * -1
            elif line.startswith('D'):
                date = parser.parse(line[1:].strip(), dayfirst=True, yearfirst=True).replace(tzinfo=UTC)
        return QIFEntry(amount, payee, date, None)

@dataclass
class QIFFile:
    type: str
    transactions: List[QIFEntry]

    def balance(self):
        return sum([ x.amount for x in self.transactions ])

    def last_transaction_date(self):
        return self.transactions[-1].date

    @staticmethod
    def parse(content: str):
        lines = content.splitlines()
        type_ = lines[0].split(':')[1].strip()
        transactions = []
        transaction_buffer = []
        for line in lines:
            if line.startswith('^'):
                transactions.append(QIFEntry.parse(transaction_buffer))
                transaction_buffer = []
            else:
                transaction_buffer.append(line)
        return QIFFile(type_, sorted(transactions, key=attrgetter('date')))

    @staticmethod
    def parse_file(file):
        with open(file, 'r') as fp:
            content = fp.read()
            return QIFFile.parse(content)

    @staticmethod
    def merge(qif_files):
        if len(qif_files) == 0:
            raise ValueError("Need at least one QIF file")
        transactions = []
        type_ = qif_files[0].type
        for qif_file in qif_files:
            if qif_file.type != type_:
                raise ValueError("QIF type mismatch")
            transactions += qif_file.transactions
        return QIFFile(type_, transactions)

    @staticmethod
    def parse_files(glob_expr):
        files = glob(glob_expr, recursive=True)
        qif_buffer = []
        for file_ in files:
            qif_buffer.append(QIFFile.parse_file(file_))
        return QIFFile.merge(qif_buffer)

