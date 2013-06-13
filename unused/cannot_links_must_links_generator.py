#-*- coding: UTF-8 -*-
import csv

paper_author_file = "./data/PaperAuthor.csv"
trainFile = "./data/Train.csv"
validFile = "./data/Valid.csv" 
finalResultFile = "./data/PaperAuthor_cleaned.csv"  

dict_author_keptPaper = dict()
dict_author_deletedPaper = dict()
dict_author_validPaper = dict()

#use info from dict_author_keptPaper and dict_author_validPaper
dict_paper_keptAuthor = dict()  

#use info from dict_author_deletedPaper
dict_paper_delAuthor = dict()  

#Added upon request from Jialu: find papers confirmed by Author1 but deleted by Author2
dict_confirm_paper_author = dict()
dict_del_paper_author = dict()

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
 

##Step 5: Build dict_paper_authorID_fromCSV
current_paper_id = 1
dict_paper_authorID_fromCSV = dict() 
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
        if paper_id in dict_paper_authorID_fromCSV: 
            if author_id not in dict_paper_authorID_fromCSV[paper_id]:
                dict_paper_authorID_fromCSV[paper_id] += [author_id] 
        else:
            dict_paper_authorID_fromCSV[paper_id] = [author_id] 

            
##########################      
######### OUTPUT #########                 
##########################         
#1. Must-coAuthor links
mustLinkFileName = "must_links.py" 
print 'Writing', mustLinkFileName
with open( mustLinkFileName, 'wb') as result_file:
    # result_file.write('#Each line includes the authors who have confirmed the same paper. Could be either co-author, or same-author. First column: shared paper ID. The following column: confirmed authors. \n')
    result_file.write('must_links = set([\n')
    for paper in dict_paper_keptAuthor.iterkeys():
        authors = dict_paper_keptAuthor[paper]
        if len(authors) > 1:
            # result_file.write( str(paper) + ',')
            for author1 in authors:
                for author2 in authors:
                    if author1 < author2:
                        result_file.write('\t(' + str(author1) + ', ' + str(author2) + '),\n')
    result_file.write('])\n')      

#2. Cannot-sameAuthor links:
#if author A delete paper P, and paper P has authors B1, ... Bn (according to authorPaper.csv), then A is not the same author as B1, ... Bn (except himself if A is a co-author of P)
dict_author_cannotLinkedAuthor = dict()

for author_id in dict_author_deletedPaper.iterkeys():
    delPapers = dict_author_deletedPaper[author_id]
    for del_paper in delPapers:
        if del_paper in dict_paper_authorID_fromCSV:
            authors_del_paper = dict_paper_authorID_fromCSV[del_paper]
            if author_id in dict_author_cannotLinkedAuthor: 
                dict_author_cannotLinkedAuthor[author_id] += authors_del_paper
            else:
                dict_author_cannotLinkedAuthor[author_id] = authors_del_paper
            #not done with dict_author_cannotLinkedAuthor yet. Will remove self in the following code

cannotLinkFileName = "cannot_links.py"
print 'Writing', cannotLinkFileName
with open( cannotLinkFileName, 'wb') as result_file:
    # result_file.write('#In each line: first column is a key author ID who deleted a paper. The following column are the authors who wrote the paper according to authorPaper.csv \n')
    result_file.write('cannot_links = set([\n')
    for author in dict_author_cannotLinkedAuthor.iterkeys():
        cannotLinkedAuthors = set( dict_author_cannotLinkedAuthor[author] ) #only unique cannotLinkedAuthors
        if author in cannotLinkedAuthors:
            cannotLinkedAuthors.remove(author) #remove self
        cannotLinkedAuthors = list(cannotLinkedAuthors)
        if len(cannotLinkedAuthors) > 0:
            for i in range(0, len(cannotLinkedAuthors)):
                result_file.write('\t(' + str(author) + ', ' + str(cannotLinkedAuthors[i]) + '),\n')
    result_file.write('])\n')
               

