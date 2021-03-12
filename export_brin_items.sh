#!/bin/bash

set -eu -o pipefail

# Set env vars PGHOST, PGUSER, and PGPASS.
# TODO: better way of checking that vars are set...
PGHOST=${PGHOST:-localhost}
PGUSER=${PGUSER:-postgres}
OUTFILE=${OUTFILE:-brin_export_full.csv}
echo "connecting to host $PGHOST as $PGUSER w/ $PGPASS, exporting $PGIDX"

tmp=$(mktemp -d tmp-export_brin_items.XX)
trap 'rm -rf $tmp' EXIT

function export_page {
    PAGE="$1"
    PAGE_OUTFILE="$tmp/brin_export_$PAGE.csv"
    if psql -h "$PGHOST" -U "$PGUSER" "password=$PGPASS" --csv -t -X \
        -c "SELECT blknum, value FROM brin_page_items(get_raw_page('$PGIDX', $PAGE), '$PGIDX') ORDER BY blknum" \
        > "$PAGE_OUTFILE"; then
        echo "good"
    else
        echo "bad"
    fi
}

page=2
while true; do
    echo "exporting brin page $page..."
    if [ "$(export_page $page)" == "bad" ]; then
        echo "exported $page pages"
        break
    fi
    ((++page))
done

echo "concatenating csvs..."
(echo "blknum,value"; cat "$tmp"/*.csv) > "$OUTFILE"

echo "result in $OUTFILE ✨"
