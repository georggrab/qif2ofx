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
