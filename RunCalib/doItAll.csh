#!/bin/csh

set field=$1

./lcstat.csh $field

./lvstat.csh $field

./buildChunkStats.csh $field

./buildChunkMatches.csh $field

./fitPhotometry.csh $field
