def filter_redundant(input, output):
	f = open(input)
	fout = open(output,'w')
	for l in f.readlines():
		token = l.rstrip().split(',')
		n = 0
		legal = True
		allsame = True
		name = ''
		for t in token:
			s = t.split()
			try:
				id = int(s[-1])
				if id<n:
					legal = False
					break
				n = id
			except:
				pass
			if name=='':
				name = ' '.join(s[:-1]).lower()
			else:
				allsame = allsame and name == ' '.join(s[:-1]).lower()
		if legal and not allsame:
			fout.write(l)
	f.close()
	fout.close()

filter_redundant('data/duplicate_authors_unconfident_subset.csv','data/suspect_6_9.csv')