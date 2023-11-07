SHELL=bash

all: dict.tsv

dict.tsv:
	@for file in `find ../data/parsed/*`; do \
		cat $$file; \
	done \
	| perl -pe 's/\s+/ /g; s/\)/\)\n/g; s/\(/\n\(/g;' \
	| grep -P '^\(.*\)$$' \
	| sed s/'[\(\)]'//g \
	| grep -P -v 'FW|CODE|0|LETTER|X|UNKNOWN|ID|AUTHOR|RECIPIENT|FRAG|<|\*|\@|\$$|=|\+|\.\.\.|[0-9]|[\{\}]|'"'" \
	| perl -pe 's/ /\t/g; s/~//g; s/[\.:;,`+_\-]//g;' \
	| egrep -v '\t.*\t' \
	| sed s/'\t.*$$'/'\L&'/g \
	| perl -pe 's/^([^\t\n]+)\t([^\t\n]+)$$/$$2\t$$1/g;' \
	| python3 stemmer.py -c 0 -pos 1 -dict \
	> dict.tsv	

old_dict.tsv:
	@for file in `find ../data/parsed/*`; do \
		cat $$file; \
	done \
	| perl -pe 's/\s+/ /g; s/\)/\)\n/g; s/\(/\n\(/g;' \
	| grep -P '^\(.*\)$$' \
	| sed s/'[\(\)]'//g \
	| egrep -v 'FW|CODE|0|LETTER|ID|AUTHOR|RECIPIENT|FRAG|<|\*|\@|\$$|=|\+|\.\.\.|[0-9]|'"'" \
	| perl -pe 's/ /\t/g; s/~//g; s/[\.:;,`+_\-]//g;' \
	| egrep -v '\t.*\t' \
	| sed s/'\t.*$$'/'\L&'/g \
	| perl -pe 's/^([^\t\n]+)\t([^\t\n]+)$$/$$2\t$$1/g;' \
	| sort \
	| perl -pe 's/^([^\t\n]+)\t([^\t\n]+)$$/\2\t\1/g;' \
	| uniq -c \
	| sed s/'  *'/'\t'/g \
	| cut -f 2- \
	| perl -pe 's/^([^\t]+)\t(.+)$$/\2\t\1/;' \
	| egrep -v '^X|UNKNOWN' \
	| grep -P -v '\t[1-4]$$' \
	| perl -pe 's/^([^\t\n]+)\t([^\t\n]+)\t/\2\t\1\t/g;' \
	| tee dict.tsv
	#| cat; echo \
	#| cat #| grep -P -v '^(ADJR|ADJS|ADVR|ADVS|.*AG|.*AN|DO|H|MD|NPRS|ONES|OTHERS|QR|QS|VAG|VAN|VB.)' \
	