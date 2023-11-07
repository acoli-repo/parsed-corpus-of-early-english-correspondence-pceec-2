import os,sys,re,argparse

src2norm={
	"cum":"com",
	"ond":"and", # ynglond
	"yis":"yes", # yisterday
	"yr":"er", # yestyrday
	"ir":"er",
	"id":"ed",
	"yd":"ed",
	"in":"en",
	"yn":"en",
	"ph":"f",
	"ae":"e",
	"ey":"e",
	"ee":"e",
	"ti":"ci",
	"rr":"r",
	"gg":"g",
	"ck":"k",
	"mm":"m",
	"nn":"n",
	"pp":"p",
	"ff":"f",
	"j":"y",
	"ow":"u",
	"v":"u",
	"ou":"u",
	"c":"s",
	"oo":"o",
	"ay":"ey",
	"ee":"e",
	"au":"a",
	"dd":"d",
	"ea":"e",
	"ss":"s",
	"w":"u",
	"f":"u",
	"ll":"l",
	"i": "y",
	"gh": "",
	"oa":"o",
	"ely":"ly",
	"er":"r",
	"o":"u", # young ~ yong ~ yung
}

def stem(form,pos=None, strip_final=None):
	orig=form

	# remove duplicate characters
	for c in set(orig):
		form=c.join(form.split(c+c))

	form=form.lower()
	
	if strip_final!=None:
		form=form.rstrip(strip_final)
	
	for src,norm in src2norm.items():
		form=norm.join(form.split(src))

	if pos == None:
		if form==orig:
			return form
		else:
			return stem(form,pos=pos,strip_final=strip_final)

	else:		
		if pos in ["ADJR", "ADVR" ]:
			pos=pos[0:-1]
			form=form.rstrip("r")
		
		if pos in ["ADJS", "ADVS" ]:
			pos=pos[0:-1]
			form=form.rstrip("st")

		if pos in [ "OTHERS","NPRS","NS"]:
			pos=pos[0:-1]
			form=form.rstrip("s")

		if pos in ["VBD","VAN","VBN"]:
			if len(form)>1 and (form.endswith("d") or form.endswith("n")):
				form=form[0:-1]
			# if form[0] in ["y"] and pos in [ "VAN","VBN" ]:
			#	# yporposed, ypromesed, yreported # BUT: yelded, joined (!= wynne)
			#	form=form[1:]
			pos="VB"

		if pos in ["VAG"]:
			pos="VB"
			if form.endswith("ing") or form.endswith("yng"):
				form=form[0:-3]

		if pos in ["VBI"]:
			pos="VB"

		if pos in ["VBP"]:
			pos="VB"
			if form.endswith("s"):
				form=form.rstrip("s")
			elif form.endswith("th"):
				form=form[0:-2]

		if strip_final!=None:
			form=form.rstrip(strip_final)

		if form==orig:
			return form, pos
		else:
			return stem(form,pos=pos,strip_final=strip_final)

args=argparse.ArgumentParser(description="Early Modern English stemmer, for PCEED2 corpus, to be used for spelling normalization (i.e., take the most frequent form), reads one or more TSV files, appends a column of normalized forms to the end")
args.add_argument("FILES", type=str, nargs="*", help="one or more TSV files", default=None)
args.add_argument("-c","--source_column", type=int, help="column from which to read source forms")
args.add_argument("-pos","--pos_column", type=int, help="column from which to read part of speech tags")
args.add_argument("-dict","--induce_dict", action="store_true", help="if set, return a dictionary of possible base forms and variants (and hide stems), by default, annotate with stem candidates")
args=args.parse_args()

if args.FILES==None or len(args.FILES)==0:
	sys.stderr.write("reading from stdin\n")
	sys.stderr.flush()
	args.FILES=[sys.stdin]

stem2pos2pos2form2freq={}

for file in args.FILES:
	if(isinstance(file,str)):
		file=open(file,"rt",errors="ignore")
	for line in file:
		line=line.rstrip()
		if line.startswith("#"):
			print(line)
		elif len(line)==0:
			print(line)
		else:
			fields=line.split("\t")
			if args.source_column>=len(fields):
				print(line)
			else:
				form=fields[args.source_column]
				pos="_"
				outpos="_"
				if args.pos_column!=None and args.pos_column<len(fields):
					pos=fields[args.pos_column]
					base,outpos=stem(form,pos,strip_final="e")
				else:
					base=stem(form,strip_final="e")
				stemmed=base

				if not base in stem2pos2pos2form2freq: stem2pos2pos2form2freq[base]={}
				if not outpos in stem2pos2pos2form2freq[stemmed]: stem2pos2pos2form2freq[stemmed][outpos]={}
				if not pos in stem2pos2pos2form2freq[stemmed][outpos]: stem2pos2pos2form2freq[stemmed][outpos][pos]={}
				if not form in stem2pos2pos2form2freq[stemmed][outpos][pos]: stem2pos2pos2form2freq[stemmed][outpos][pos][form]=0
				stem2pos2pos2form2freq[stemmed][outpos][pos][form]+=1

				if not args.induce_dict:
					print(line+"\t"+base+"\t"+outpos)
	file.close()

if args.induce_dict:
	base2pos2pos2form2freq={}
	for stemmed in stem2pos2pos2form2freq:
		for pos in stem2pos2pos2form2freq[stemmed]:
			freq_pos_form=[]
			for xpos in stem2pos2pos2form2freq[stemmed][pos]:
				for form,freq in stem2pos2pos2form2freq[stemmed][pos][xpos].items():
					freq_pos_form.append((freq,xpos,form))
			freq_pos_form=list(reversed(sorted(freq_pos_form)))
			_,basepos,base=freq_pos_form[0]
			if pos in stem2pos2pos2form2freq[stemmed][pos]:
				for i in range(0,len(freq_pos_form)):
					_,basepos,base=freq_pos_form[i]
					if basepos==pos: break
			# for debugging:
			# base=base+f" ({stemmed})"
			if not base in base2pos2pos2form2freq: base2pos2pos2form2freq[base]={}
			if not basepos in base2pos2pos2form2freq[base]: base2pos2pos2form2freq[base][basepos]={}
			for _,xpos,_ in freq_pos_form:
				if not xpos in base2pos2pos2form2freq[base][basepos]:
					base2pos2pos2form2freq[base][basepos][xpos]={}
					for freq,ypos,form in freq_pos_form:
						if xpos==ypos:
							base2pos2pos2form2freq[base][basepos][xpos][form]=freq
	for base in sorted(base2pos2pos2form2freq):
		for pos in base2pos2pos2form2freq[base]:
			for xpos in base2pos2pos2form2freq[base][pos]:
				for form,freq in base2pos2pos2form2freq[base][pos][xpos].items():
					print(f"{base}\t{pos}\t{xpos}\t{form}\t{freq}")
		