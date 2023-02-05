### Summary
The aim of this project is to automate the process of web scraping across over 150 web pages,clean the scraped data and perform comprehensive textual analysis to extract valuable language parameters. The automation process will streamline the gathering of data, ensuring that only relevant and accurate information is collected. The extracted information will then be cleaned and saved into a CSV file for easy storage and future reference.

### Parameters Extracrted:

1. positive score
2. negative score
3. polarity score
4. subjectivity score
5. avg sentence length
6. percentage of complex words
7. fog index
8. avg number of words per sentence
9. complex word count
10. word count
11. syllable per word
12. personal pronouns
13. avg word length


### For Installation
- dependdencies:
```
spacy==3.4.1
pandas==1.2.5
tqdm==4.64.0
beautifulsoup4==4.8.2
```
- make docker file
```
FROM python:3.8-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["python", "nlp.py"]
```
- make container
```
docker build -t <image_name> .
docker run <image_name>
```
