<h1>MP Spider</h1>

<h4>Scraping project for all Bulgarian MP data from the official Parliament website. Uses the framework "Scrapy". Outputs the result in a local database and JSON file.</h4>

<br>

<h2>Installation</h2>

<p>Download/clone the repository and intall the dependancies in the requirement.txt</p>

<h2>Running the script</h2>

<p>Open the main folder in terminal and run "scrapy crawl mpdata".</p>
<p>The script return the result by creating a mpdata.db file (SQLite database) and a "mpdata + current data.json" file.</p>
