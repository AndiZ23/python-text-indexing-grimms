# python-text-indexing-grimms
An assignment project completed in 2017. This is a Python program that indexed words from the full Grimm’s Fairy Tales, processed users’ Boolean queries of words, and output the story titles and lines that match the given queries.

Please download all files and keep them in the same folder. 
The program will output all story titles at first while indexing and striping stopwords, then feel free to type queries in the following formats.

## Input format: (please avoid putting any stopwords in queries) 
1. Input a single word. 
Example: `beautiful`, `alive`

2. Input multiple words (can be more than two words), the output will be stories that contain all inputted words (AND). 
Example: `beautiful love`, `beautiful queen love princess`, `owl raven dove`, `boy girl mother father`

3. Support "and" queries, but please be sure all in lower case. 
Example: `beautiful and love`, `owl and raven`, `shame and ugly`

4. Support "or" queries, but please be sure all in lower case. 
Example: `owl or raven`, `shame or ugly`, `winter or spring`

5. Support "morethan" queries, but please be sure all in lower case. It will output if the word to the left appears more than the word or number to the right. 
Example: `raven morethan 5`, `raven morethan snow` 

6. Support "near" queries, but please be sure all in lower case. It will output if the two inputted words occur within the same or contiguous lines of each other in a story. 
Example: `princess near love`, `mother near father`
