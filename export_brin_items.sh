#!/bin/bash

set -eu -o pipefail

# Set env vars PGHOST, PGDB, PGUSER, PGPASSWORD, PGIDX.
# TODO: better way of checking that vars are set...
PGHOST=${PGHOST:-localhost}
PGUSER=${PGUSER:-postgres}
ATTNUM=${ATTNUM:-1}
FIRSTPAGE=${FIRSTPAGE:-0}  # first page to start searching for regular pages
OUTFILE=${OUTFILE:-brinitems_$(date "+%Y%m%d_%H%M%S").csv}
echo "connecting to host $PGHOST db $PGDB as $PGUSER, exporting attname $ATTNUM from $PGIDX..."

tmp=$(mktemp -d tmp-export_brin_items.XX)
trap 'rm -rf $tmp' EXIT

function load_extension {
    psql -h "$PGHOST" -d "$PGDB" -U "$PGUSER" -X -c "CREATE EXTENSION pageinspect"
}

function unload_extension {
    psql -h "$PGHOST" -d "$PGDB" -U "$PGUSER" -X -c "DROP EXTENSION pageinspect"
}

# Return type of page number.
function get_page_type {
    PAGE="$1"
    psql -h "$PGHOST" -d "$PGDB" -U "$PGUSER" --csv -t -X \
        -c "SELECT brin_page_type(get_raw_page('$PGIDX', $PAGE))"
}

# Export page number to CSV. Returns "good" or "bad" depending on error.
function export_page {
    PAGE="$1"
    PAGE_OUTFILE="$tmp/brin_export_$PAGE.csv"
    # -t to suppress headers, -X to not load .psql (suppress \timing output)
    if psql -h "$PGHOST" -d "$PGDB" -U "$PGUSER" --csv -t -X \
        -c "SELECT blknum, value FROM brin_page_items(get_raw_page('$PGIDX', $PAGE), '$PGIDX') WHERE attnum=$ATTNUM ORDER BY blknum" \
        > "$PAGE_OUTFILE"; then
        echo "good"
    else
        echo "bad"
    fi
}

echo "-> loading pageinspect..."
load_extension

# Find first normal page.
echo "-> locating first 'regular' page..."
page=$FIRSTPAGE
while true; do
    res=$(get_page_type "$page")
    echo "page $page type $res."
    if [ "$res" == "regular" ]; then
        echo "found first regular page: $page."
        break
    fi
    ((++page))
done

echo "-> exporting BRIN pages..."
while true; do
    echo "exporting BRIN page $page..."
    res=$(export_page "$page")
    if [ "$res" == "bad" ]; then
        echo "done exporting."
        break
    fi
    ((++page))
done

echo "-> unloading pageinspect..."
unload_extension

echo "-> concatenating csvs..."
(echo "blknum,value"; cat "$tmp"/*.csv) > "$OUTFILE"

echo "=> result in $OUTFILE ✨"
