import csv
import sys
import datetime
import argparse
from decimal import Decimal

from ofxtools.utils import UTC

from .qif import QIFFile, QIFEntry
from .qif2ofx import genofx

def main():
    parser = argparse.ArgumentParser('csv2ofx')
    parser.add_argument('--csv-file', required=True)
    parser.add_argument('--csv-delim', required=False, default=',')
    parser.add_argument('--csv-col-recipient', required=True, type=int)
    parser.add_argument('--csv-col-amount', required=True, type=int)
    parser.add_argument('--csv-col-reference', required=True, type=int)
    parser.add_argument('--csv-col-date', required=True, type=int)
    parser.add_argument('--csv-col-type', required=True, type=int)
    parser.add_argument('--csv-col-type-debit', required=True)
    parser.add_argument('--csv-skip-leading-rows', required=False, type=int, default=0)
    parser.add_argument('--csv-skip-trailing-rows', required=False, type=int, default=0)
    parser.add_argument('--csv-date-format', required=False, default='%d/%m/%y')
    parser.add_argument('--csv-decimal-delim', required=False, default=',')
    parser.add_argument('--csv-encoding', required=False, default='utf-8')
    parser.add_argument('--currency', required=True, help='Currency, example: GBP')
    parser.add_argument('--acctid', required=True, help='Account ID. Important for reconciling transactions. Example: "Halifax123"')
    parser.add_argument('--trnuid', required=False, help='Client ID. 1234 if unspecified.', default='1234')
    parser.add_argument('--org', required=False, help='Org to set in the OFX. "Illuminati" if not supplied', default="Illuminati")
    parser.add_argument('--balance', required=False, help='Start Balance of the QIF files, or zero if unspecified', default='0')

    args = parser.parse_args()

    qif_file = csv_to_qif(
        args.csv_file,
        args.csv_col_recipient,
        args.csv_col_amount,
        args.csv_col_reference,
        args.csv_col_date,
        args.csv_col_type,
        args.csv_col_type_debit,
        args.csv_date_format,
        args.csv_decimal_delim,
        args.csv_delim,
        args.csv_skip_leading_rows,
        args.csv_skip_trailing_rows,
        args.csv_encoding
    )

    ofx = genofx(qif_file, args.currency, args.acctid, args.trnuid, args.org, args.balance)
    print(ofx)



def csv_to_qif(csv_file,
    col_recipient,
    col_amount,
    col_reference,
    col_date,
    col_type,
    col_type_debit,
    date_format='%d/%m/%y',
    decimal_delim=',',
    delim=',',
    skip_leading_rows=0,
    skip_trailing_rows=0,
    csv_encoding='utf-8',
):
    with open(csv_file, 'r', encoding=csv_encoding) as csv_file_fd:
        lines = csv_file_fd.readlines()
    relevant_lines = lines[skip_leading_rows:len(lines)-skip_trailing_rows]
    reader = csv.reader(relevant_lines, delimiter=delim)
    entries = []
    for row in reader:
        try:
            recipient = row[col_recipient]
            amount = Decimal(row[col_amount].replace(decimal_delim, '.'))
            reference = row[col_reference]
            date = datetime.datetime.strptime(row[col_date], date_format).replace(tzinfo=UTC)
            transaction_sign = -1 if row[col_type] == col_type_debit else 1
            entries.append(QIFEntry(transaction_sign * amount, recipient, date, reference))
        except IndexError:
            print("Skipping bad row: {}".format(row), file=sys.stderr)
    return QIFFile('csv', entries[:len(entries) - skip_trailing_rows])