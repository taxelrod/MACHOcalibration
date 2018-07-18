#!/bin/csh

set field=$1

./cleanField $field

./lcstat.csh $field

./lvstat.csh $field

./buildChunkStats.csh $field

./buildChunkMatches.csh $field

./fitPhotometry.csh $field
