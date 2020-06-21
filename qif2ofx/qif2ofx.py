import argparse
from dataclasses import dataclass
from typing import List
from datetime import datetime
from operator import attrgetter
from dateutil import parser
from glob import glob

import ofxtools.models as m
from ofxtools.utils import UTC
from ofxtools.header import make_header
from decimal import Decimal
from datetime import datetime

import xml.etree.ElementTree as ET

from .qif import QIFFile

def qif_to_stmttrn(qif_file):
    stmttrns = []
    for transaction in qif_file.transactions:
        trntype = 'DEBIT' if transaction.amount<0 else 'CREDIT'
        dtposted = transaction.date.replace(tzinfo=UTC)
        trnamt = transaction.amount
        name = transaction.payee
        fitid = '{}{}{}'.format(dtposted, trnamt, name)
        stmttrns.append(m.STMTTRN(
            dtposted=dtposted,
            fitid=fitid,
            trnamt=trnamt,
            trntype=trntype,
            name=name
        ))
    return stmttrns

def main():
    parser = argparse.ArgumentParser('qif2ofx')
    parser.add_argument('--glob', required=True, help='Glob expression for QIF files, for example "./data/**/*.qif"')
    parser.add_argument('--currency', required=True, help='Currency, example: GBP')
    parser.add_argument('--acctid', required=True, help='Account ID. Important for reconciling transactions. Example: "Halifax123"')
    parser.add_argument('--trnuid', required=False, help='Client ID. 1234 if unspecified.', default='1234')
    parser.add_argument('--org', required=False, help='Org to set in the OFX. "Illuminati" if not supplied', default="Illuminati")
    parser.add_argument('--balance', required=False, help='Start Balance of the QIF files, or zero if unspecified', default='0')

    args = parser.parse_args()

    qif = QIFFile.parse_files(args.glob)
    trans = qif_to_stmttrn(qif)

    balamt = Decimal(args.balance) + qif.balance()
    ledgerbal = m.LEDGERBAL(balamt=balamt,
                          dtasof=qif.last_transaction_date()
                          )
    ccacctfrom = m.CCACCTFROM(acctid=args.acctid)  # OFX Section 11.3.1
    banktranlist = m.BANKTRANLIST(*trans, dtstart=datetime(2019,1,1,12,tzinfo=UTC),dtend=datetime(2018,1,1,12,tzinfo=UTC))
    status = m.STATUS(code=0, severity='INFO')
    ccstmtrs = m.CCSTMTRS(curdef=args.currency, ccacctfrom=ccacctfrom, banktranlist=banktranlist, ledgerbal=ledgerbal)
    ccstmttrnrs = m.CCSTMTTRNRS(trnuid=args.trnuid, status=status, ccstmtrs=ccstmtrs)        
    ccmsgsrsv1 = m.CREDITCARDMSGSRSV1(ccstmttrnrs)
    fi = m.FI(org=args.org, fid='666')  # Required for Quicken compatibility
    sonrs = m.SONRS(status=status,
                  dtserver=datetime.now(tz=UTC),
                  language='ENG', fi=fi)
    signonmsgs = m.SIGNONMSGSRSV1(sonrs=sonrs)
    ofx = m.OFX(signonmsgsrsv1=signonmsgs, creditcardmsgsrsv1=ccmsgsrsv1)
    root = ofx.to_etree()
    message = ET.tostring(root).decode()
    header = str(make_header(version=220))

    print(header+message)
    