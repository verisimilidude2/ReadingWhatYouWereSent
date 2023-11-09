# ReadingWhatYouWereSent
A python program that will read the text of an article without javascript manipulations.

The program requires the _pip install_ of the packages Beautiful Soup 4 (bs4) and requests.

Reads the html of an article on Wired.com and extracts and prints only the
text of the article, leaving out all ads, promo links, and pictures.

> $ python cleanup.py -h
> 
> usage: WiredArticleCleanup [-h] [-u URL] [-f FNAME] path
>
> 
> positional arguments:
>   path                  URL of the article to download (starting with
>                         http[s]?://), or the filename of an already downloaded
>                         HTML file
> 
> options:
>   -h, --help            show this help message and exit
> 
>   -u URL, --url URL     Alternative way to specify the URL of the article to download
> 
>   -f FNAME, --file FNAME
>                         Alternative way to specify the path to an already downloaded HTML file

The program spits out the output to standard out so it can be saved or piped to _less_.

You can also create a bash function to run the program from the command line (in the file cleanup.sh)

> cleanup() {
>     python3 ~/path_to_program/cleanup.py $* | less;
> }
