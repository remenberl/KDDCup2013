SELECT author."id", paperauthor.name, paperauthor.affiliation, paper.*  FROM "public"."author", paperauthor, paper WHERE author."name" = '' and author.id = paperauthor.authorid and paper.id = paperauthor.paperid order by author.id

SELECT author."id", paperauthor.name, paperauthor.affiliation, paper.*  FROM "public"."author", paperauthor, paper WHERE author."name" LIKE 'Stephen Gill' and author.id = paperauthor.authorid and paper.id = paperauthor.paperid order by author.id

SELECT author."id", paperauthor.name, paperauthor.affiliation, paper.*  FROM "public"."author", paperauthor, paper WHERE author."name" LIKE '%\?%' and author.id = paperauthor.authorid and paper.id = paperauthor.paperid order by author.id