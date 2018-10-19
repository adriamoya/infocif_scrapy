```shell
.
├── infocif_scrapy              # /scrapy project directory
│   ├── spiders                 # /spiders directory
│   │   └── infocif_spider.py   # spider
│   ├── items.py                # items
│   ├── middlewares.py          # middlewares
│   ├── pipelines.py            # pipelines
│   └── settings.py             # settings
├── output                      # /output files directory
│   ├── companies.csv
│   └── companies.json
├── utils                       # /aux functions
│   └── functions.py
├── README.md
├── crawl.py                    # main script
├── json_to_csv.py              # json output to csv
├── requirements.txt            # pip install -r requirements.txt
└── scrapy.cfg                  # scrapy config file
```

## Running the cralwer

```shell
# python crawl.py -h
usage: crawl.py [-h] [-s START_PAGE] [-e END_PAGE] [--single-page]

optional arguments:
-h, --help     show this help message and exit
-s START_PAGE  Start page (default=1)
-e END_PAGE    End page (default=596)
--single-page  Scrape only one page (default all pages)
```

 To scrape **all** companies:

```shell
python crawl.py  # from root/
```

## Other use cases

To scrape companies listed **between page 10 and 20**:

```shell
python crawl.py -s 10 -e 20
```

To **only** scrape companies listed **on page 15**:

```shell
python crawl.py -s 15 --single-page
```
