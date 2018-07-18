#!/bin/csh

set field=$1

./cleanField.csh $field

./lcstat.csh $field

./lvstat.csh $field

./buildChunkStats.csh $field

./buildChunkMatches.csh $field

./fitPhotometry.csh $field
