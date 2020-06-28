# qif2ofx

Convert credit card transactions in [Quicken Interchange format](https://en.wikipedia.org/wiki/Quicken_Interchange_Format) (QIF) to [Open Financial Exchange](https://www.ofx.net/) (OFX).
Use this if you can only comfortably import OFX in your finance tool of choice. For example, I use [beancount-import](https://github.com/jbms/beancount-import) (what an excellent tool!), but so far it only directly supports ingesting OFX. My bank decides to only distribute in QIF, so hence this (lazy) way of solving the problem.

The converter assumes you have credit card transactions in your QIF, and not whatever else QIF can be used to represent, because that's my only use-case so far.

## Install

The following provides the executable `qif2ofx` and the python library `qif2ofx`:

`pip install qif2ofx`

## Usage

OFX is a lot richer than QIF, from what I gathered from briefly looking at [the specification](https://www.ofx.net/downloads/OFX%202.2.pdf) (don't, if you want to preserve your sanity. It hurts my eyes. Why did they make all the tags in capital letters). QIF is basically a list of transactions, without real context, while OFX offers rich descriptions of all sorts of financial concepts. Hell, QIF doesn't even have a concept of currency. Hence to convert our QIF input to OFX we need to provide a bunch of metadata:


```
qif2ofx \ 
  # A glob expression, or path for that matter, of QIF files
  # we'd like to convert to OFX
  --glob "path/to/**/*.qif" \

  # The currency we'd like to set in our OFX file. 
  --currency GBP \

  # Again, QIF has no notion of accounts, OFX does. Tools handling
  # OFX expect an account identifier so they can reconcile with
  # the appropriate account in the money management tool.
  --acctid puppies
```

This is the bare minimum we need to generate a valid-ish OFX out of your QIF. You can set a few more options through the command line to control some details, see `qif2ofx --help` for more details.

## Converting CSV to OFX

A CSV containing transactions can be converted as well. Don't worry, all the options you need to parse your horrible bank's CSV export may be there (possibly).


```
csv2ofx \
    --csv-file "path/to/transactions.csv" \
    --csv-delim ';' \
    # If your bank's csv is doing something horrible like mine,
    # writing something in front of the CSV, this options skips the
    # first N lines
    --csv-skip-leading-rows 13 \
    # With my bank, the last row is a balance assertion, which makes
    # absolutely no sense at all given I have the feeling there is
    # a small difference between a transaction and account balance,
    # but hey, easy to skip
    --csv-skip-trailing-rows 1 \
    # In the valid-ish CSV that's left, the zero-based index that 
    # contains something like the recipient
    --csv-col-recipient 2 \
    # The amount
    --csv-col-amount 11 \
    # A Reference
    --csv-col-reference 8 \
    # The date
    --csv-col-date 0 \
    # The transaction type (Credit/Debit)
    --csv-col-type 12 \
    # The content of the transaction type column we should interpret
    # as the "debit" column. Anything that does not match we assume
    # to be Credit (I know)
    --csv-col-type-debit "S" \
    # The curency we should slap into the OFX
    --currency EUR \
    # An account identifier which will be present in the CSV
    --acctid my-horrible-bank \
    # No worries, we know how horrible your bank is, not using utf-8.
    # Set an arbitrary encoding here.
    --csv-encoding iso-8859-1 \
    # The format of the date column
    --csv-date-format '%d.%m.%Y'
```