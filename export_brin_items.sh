#!/bin/bash

# TODO: could probably make this way more efficient with better queries.

set -eu -o pipefail

PGHOST=${PGHOST:-localhost}
PGUSER=${PGUSER:-postgres}
ATTNUM=${ATTNUM:-1}
[ -z ${PGDB+x} ] && echo "missing required env var PGDB" && exit 1
[ -z ${PGPASSWORD+x} ] && echo "missing required env var PGPASSWORD" && exit 1
[ -z ${PGIDX+x} ] && echo "missing required env var PGIDX" && exit 1
FIRSTPAGE=${FIRSTPAGE:-0}  # first page to start searching for regular pages
OUTFILE=${OUTFILE:-brinexport_$(date "+%Y%m%d_%H%M%S").csv}

echo "=> connecting to host $PGHOST db $PGDB as $PGUSER."
echo "=> exporting attname $ATTNUM from $PGIDX to $OUTFILE."

function load_extension {
    # if fails, most likely because it was already loaded
    psql -h "$PGHOST" -d "$PGDB" -U "$PGUSER" -X -c "CREATE EXTENSION pageinspect" || true
}

function unload_extension {
    echo "-> unloading pageinspect..."
    psql -h "$PGHOST" -d "$PGDB" -U "$PGUSER" -X -c "DROP EXTENSION pageinspect"
}

tmp=$(mktemp -d tmp-export_brin_items.XX)
function cleanup {
    rm -rf "$tmp" || true
    unload_extension || true
}
trap 'cleanup' EXIT

# Return type of page number.
function get_page_type {
    PAGE="$1"
    psql -h "$PGHOST" -d "$PGDB" -U "$PGUSER" --csv -t -X \
        -c "SELECT brin_page_type(get_raw_page('$PGIDX', $PAGE))"
}

# Export page number to CSV. Returns "good" or "bad" depending on error.
function export_page {
    PAGE="$1"
    # add date to get better ordering. still not perfect, but %N nanoseconds only works w/ GNU coreutils, sigh.
    PAGE_OUTFILE="$tmp/brin_export_$(date +%s)_$PAGE.csv"
    # if attnum is set to -1, we export all columns
    if [ "$ATTNUM" == -1 ]; then
        COLS="blknum,attnum,value"
        WHERE=""
        ORDER_COLS="blknum,attnum"
    else
        COLS="blknum,value"
        WHERE="WHERE attnum=$ATTNUM"
        ORDER_COLS="blknum"
    fi
    # -t to suppress headers, -X to not load .psql (suppress \timing output)
    if psql -h "$PGHOST" -d "$PGDB" -U "$PGUSER" --csv -t -X \
        -c "SELECT $COLS FROM brin_page_items(get_raw_page('$PGIDX', $PAGE), '$PGIDX') $WHERE ORDER BY $ORDER_COLS" \
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

echo "-> concatenating csvs..."
# TODO: way to dedup this?
COLS=""
if [ "$ATTNUM" == -1 ]; then
    COLS="blknum,attnum,value"
else
    COLS="blknum,value"
fi
(echo "$COLS"; cat "$tmp"/*.csv) > "$OUTFILE"

echo "=> result in $OUTFILE ✨"
