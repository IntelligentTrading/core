# ITT Schema of BigTable 
In this document we'll share how was created our BigTable schema.


## Column Family and Col
Based in limitations about the size of column family are we'll create this families:

    BTC
    USDT
    XMR
    ETH

In these families will be inserted many others column qualifiers. Please check the [schema.json](schema.json)

## Row Key
The row keys will have this format:

**[channel] [separator] [timestamp]** 

for example:

    poloniex#201503061617

## Column Qualifiers
Inside in each colum families will be have this format of column qualifiers:

**[COIN_TO]_[TYPE]**

for example:

    BTC_ETH_LAST
    BTC_ETH_CHANGE
    BTC_ETH_HIGH
    BTC_ETH_LOW
    BTC_ETH_VOLUME 

## Reference
[Google BigTable Schema](https://cloud.google.com/bigtable/docs/schema-design)