import csv

paper_author_file = "data/PaperAuthor.csv"
trainFile = "data/Train.csv"
validFile = "data/Valid.csv" 
finalResultFile = "data/PaperAuthor_cleaned.csv"  

dict_author_keptPaper = dict()
dict_author_deletedPaper = dict()
dict_author_validPaper = dict()

#use info from dict_author_keptPaper and dict_author_validPaper
dict_paper_keptAuthor = dict()  

#use info from dict_author_deletedPaper
dict_paper_delAuthor = dict()  

#Step 1: Read data from train.csv and valid.csv
with open(trainFile, 'rb') as train_file:
    csv_reader = csv.reader(train_file, delimiter=',')
    next(csv_reader) 
    for row in csv_reader:
        authorID = int(row[0])
        keptPaper = map( int, row[1].split(' ') )
        delPaper = map( int, row[2].split(' ') )
        if len(keptPaper) > 0:
            dict_author_keptPaper[authorID] = list( set( keptPaper) )
        if len(delPaper) > 0:
            dict_author_deletedPaper[authorID] = list( set(delPaper) )

with open(validFile, 'rb') as valid_file:
    csv_reader = csv.reader(valid_file, delimiter=',')
    next(csv_reader) 
    for row in csv_reader:
        authorID = int(row[0])
        keptPaper = map( int, row[1].split(' ') )
        if len(keptPaper) > 0:
            dict_author_validPaper[authorID] = list( set(keptPaper) )

##Step 2: Resolve conflict: a paper ID is identified to belong to & not belong to an author
dict_conflict_Author_paper = dict() #length = 353
for author in dict_author_keptPaper.iterkeys():
    overlap = set(dict_author_keptPaper[author]) & set(dict_author_deletedPaper[author])
    if len( overlap ):
        dict_conflict_Author_paper[author] = list(overlap)
        #print "Dup papers in both keptPaper and delPaper: authorID =", author
        #remove the overlap from kept and del paper dictionaory
        for paperID in overlap:
            if paperID in dict_author_keptPaper[author]:
                dict_author_keptPaper[author].remove(paperID)
            if paperID in dict_author_deletedPaper[author]:
                dict_author_deletedPaper[author].remove(paperID)   
 
print "Conflicting <author, paper> relation affected # of authors:", len(dict_conflict_Author_paper)       
 
##Step 3: Build dict_paper_keptAuthor
for author in dict_author_keptPaper.iterkeys():
    papers = dict_author_keptPaper[author]
    for i in range(0, len(papers)):
        if papers[i] in dict_paper_keptAuthor:
            dict_paper_keptAuthor[papers[i]] += [author]
        else:
            dict_paper_keptAuthor[papers[i]] = [author]

for author in dict_author_validPaper.iterkeys():
    papers = dict_author_validPaper[author]
    for i in range(0, len(papers)):
        if papers[i] in dict_paper_keptAuthor:
            dict_paper_keptAuthor[papers[i]] += [author]
        else:
            dict_paper_keptAuthor[papers[i]] = [author]

##Step 4: Build dict_paper_delAuthor
for author in dict_author_deletedPaper.iterkeys():
    papers = dict_author_deletedPaper[author]
    for i in range(0, len(papers)):
        if papers[i] in dict_paper_delAuthor:
            dict_paper_delAuthor[papers[i]] += [author]
        else:
            dict_paper_delAuthor[papers[i]] = [author]
 
print "Size of dict_paper_keptAuthor:", len(dict_paper_keptAuthor)  
print "Size of dict_paper_delAuthor:", len(dict_paper_delAuthor)  
     
##Step 5: Build dict from PaperAuthor.csv
count_del_paper = 0
count_kept_paper = 0
current_paper_id = 1
dict_paper_authorID_fromCSV = dict()
dict_paper_authorName_fromCSV = dict()
dict_paper_authorAffili_fromCSV = dict()
countOriFile = 0
newFileLineCnt = 0
with open(paper_author_file, 'rb') as csv_file:
    paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"') 
    next(paper_author_reader) 
    for row in paper_author_reader:
        countOriFile += 1
        if countOriFile % 2000000 == 0:
            print "Finish analysing " + str(countOriFile) + " lines of the file."
        paper_id = int(row[0])
        author_id = int(row[1])
        author_name = row[2]
        author_affili = row[3] 
        if paper_id in dict_paper_authorID_fromCSV: 
            if author_id not in dict_paper_authorID_fromCSV[paper_id]:
                dict_paper_authorID_fromCSV[paper_id] += [author_id]
                dict_paper_authorName_fromCSV[paper_id] += [author_name]
                dict_paper_authorAffili_fromCSV[paper_id] += [author_affili]
        else:
            dict_paper_authorID_fromCSV[paper_id] = [author_id]
            dict_paper_authorName_fromCSV[paper_id] = [author_name]
            dict_paper_authorAffili_fromCSV[paper_id] = [author_affili]

##Step 6: Clean PaperAuthor.csv      
#Use: dict_paper_keptAuthor = dict() and dict_author_deletedPaper = dict() 
cntFalseAuthor = 0
with open( 'logCleaning.txt', 'wb') as log_file:
    for paper_id in dict_paper_authorID_fromCSV.iterkeys():    
        authors_fromCSV = dict_paper_authorID_fromCSV[paper_id]
        #Case 1: the paper is never mentioned by the author (most frequent case)
        #   do nothing
        
        #Case 2: the paper is added by the author but missing in author-paper.csv
        if paper_id in dict_paper_keptAuthor:
            missingAuthors = list( set( dict_paper_keptAuthor[paper_id] ) - set(authors_fromCSV) )
            if len(missingAuthors):
                for i in range(0, len(missingAuthors)): 
                    dict_paper_authorID_fromCSV[paper_id] += [missingAuthors[i]]
                    dict_paper_authorName_fromCSV[paper_id] += ['']
                    dict_paper_authorAffili_fromCSV[paper_id] += ['']
                    log_file.write( "Missed author detected: paper = " + str(paper_id) +  "; author = " + str(missingAuthors[i]) + "\n" )
                    
        #Case 3: the paper is deleted by the author 
        if paper_id in dict_paper_delAuthor:
            overlap = list( set( dict_paper_delAuthor[paper_id] ) & set(authors_fromCSV) )
            if len(overlap):
                for i in range(0, len(overlap)):
                    pos = authors_fromCSV.index( overlap[i] )
                    tmp = dict_paper_authorID_fromCSV[paper_id].pop(pos)
                    tmp = dict_paper_authorName_fromCSV[paper_id].pop(pos)
                    tmp = dict_paper_authorAffili_fromCSV[paper_id].pop(pos)
                    cntFalseAuthor += 1
                    log_file.write( "False author detected: paper = " + str(paper_id) +  "; author = " + str(overlap[i]) + "\n" ) 
print "Cleaning is done: see logCleaning.txt"
print "Writing to ../data/PaperAuthor_cleaned.csv"
             
##Step 7: Output to PaperAuthor_cleaned.csv                   
with open( finalResultFile, 'wb') as result_file:
    result_file.write('PaperId, AuthorId, Name, Affiliation\n')
    for paper_id in dict_paper_authorID_fromCSV.iterkeys():    
        authorIDs = dict_paper_authorID_fromCSV[paper_id]
        authorNames = dict_paper_authorName_fromCSV[paper_id]
        authorAfflis = dict_paper_authorAffili_fromCSV[paper_id]
        for i in range( 0, len(authorIDs) ):
            result_file.write( str(paper_id) + ',' + str(authorIDs[i]) + ',' + \
                            authorNames[i] + ',' + '\"' + authorAfflis[i] + '\"' + '\n' )        
 
##Step 8: Test PaperAuthor_cleaned.csv          
# countCleanedFile = 0   
# with open(finalResultFile, 'rb') as csv_file:
    # paper_author_reader = csv.reader(csv_file, delimiter=',', quotechar='"') 
    # next(paper_author_reader) 
    # for row in paper_author_reader:
        # countCleanedFile += 1 
        
# print countCleanedFile - countOriFile