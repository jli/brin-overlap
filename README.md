# BRIN overlap visualization thing

## HOWTO

### Export BRIN internals

First, dump the output of `brin_page_items`.

```sql
CREATE EXTENTION pageinspect;
SELECT blknum, value
FROM brin_page_items(get_raw_page('test_brin_idx',2), 'test_brin_idx')
ORDER BY blknum;
```

The shell script `export_brin_items.sh` runs the above query, incrementing
the page numbers until the query returns an error (which should be due to
requesting a non-existent page). Set env vars to configure.

Note: it's expected that the script will output an error like: `ERROR: block
number 418 is out of range for relation "<table>_idx"`. The script simply
keeps querying for

### Parse and render output

```shell
python3 broviz.py -i brinitems_export.csv -o broviz_$(date "+%Y%m%d_%H%M%S").svg
```


## reference

<https://blog.crunchydata.com/blog/avoiding-the-pitfalls-of-brin-indexes-in-postgres>
