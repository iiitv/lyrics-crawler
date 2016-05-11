# Custom Crawler for Summer Design Project 2016

[![Code Climate](https://codeclimate.com/github/iiitv/lyrics-crawler/badges/gpa.svg)](https://codeclimate.com/github/iiitv/lyrics-crawler)
[![Issue Count](https://codeclimate.com/github/iiitv/lyrics-crawler/badges/issue_count.svg)](https://codeclimate.com/github/iiitv/lyrics-crawler)

This is the custom crawler for the **Lyrics Search Engine** project of summer 2016.

### Supported sites
* [hindilyrics.net](http://hindilyrics.net)  
    Version 0.2  
    Usage - `python hindilyrics-crawler-v0.2.py -t <type of crawl DEFAULT : 'full'> -n <number of threads DEFAULT : 4> -o <output destination DEFAULT : 'downloads/'>`  
    
    Schema of storage of lyrics : 
    ```
    File - <initial>/<movie>.json
    Structure -
    -> 'movie_name'
    -> 'website_prefix'
    -> 'movie_url'
    -> 'songs' (array)
        -> 'song_name'
        -> 'song_url'
        -> 'lyrics'
        -> 'singers' (array)
            -> 'singer_name'
            -> 'singer_url'
        -> 'music_by' (array)
            -> 'artist_name'
            -> 'artist_url'
        -> 'lyricists' (array)
            -> 'artist_name'
            -> 'artist_url'
    -> 'last_crawled' (YYYY-mm-dd HH:MM:SS)
    ```

* [smriti.com](http://smriti.com)  
    Version 0.1  
    Usage - `python smriti-crawler-v0.1.py -o <output directory DEFAULT : 'downloads/'> -n <number of threads DEFAULT : 4>`
    
    Schema of storage of lyrics : 
    ```
    File - <initlal>/<movie>.json
    Structure -
    -> 'movie_name'
    -> 'website_prefix'
    -> 'movie_url'
    -> 'songs' (array)
        -> 'song_name'
        -> 'song_url'
        -> 'lyrics'
        -> 'singers' (array)
        -> 'music_by' (array)
        -> 'lyricists' (array)
    -> 'last_crawled' (YYYY-mm-dd HH:MM:SS)
    ```