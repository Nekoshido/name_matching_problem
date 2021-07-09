# Data Engineering @ PeakData

The goal of this task is to recreate a minimal working scenario of data engineers at PeakData, in order to see the following:

- Ability to manipulate data using modern Python data tools
- Knowledge of Python best practices
- Ability to decompose tasks and high-level thinking
- Basic programming principles

## Task

Given a list of medical publications, provide a list of unique authors and institutions.

Note that authors can appear in multiple publications and may have slight differences in their names, initials, etc. between articles.

In addition to your code, we expect a `README.md` containing:
- How to build and run the code
- Documentation on your approach, i.e. what did you do and why?
- A reporting of potential failure points and bottlenecks
- An accounting of the remaining steps needed before putting deploying your code to a production system

### Input

The full input csv can be found in this repository. Here we provide an example:

`publications_min.csv.gz`:

| temp_id | abstract | title | pubdate | journal | affiliations | publication_uuid | authors |
| ------- | -------- | ----- | ------- | ------- | ------------ | ---------------- | ------- |
| 0 | "The pulmonary effects of hyperventilation following infusion of sodium salicylate into the cisterna magna was studied in 16 spontaneously breathing adult sheep. We found a fall in PaO2, a decrease in the static compliance of the respiratory system, abnormal chest roentgenographic films, and grossly abnormal lungs following 3.5 to 13 h of hyperventilation..." | Acute respiratory failure following pharmacologically induced hyperventilation: an experimental animal study. | 1988-01-01 00:00:00 | "Intensive care medicine, Issue: 1, Volume: 15 1988" | "National Institutes of Health, Laboratory of Technical Development, Bethesda, Maryland., , , , , " | 0.0 | "['D Mascheroni', 'T Kolobow', 'R Fumagalli', 'M P Moretti', 'V Chen', 'D Buckhold']" |
| 1 | "Ten patients with acute respiratory failure (ARF), (4 pneumonia, 4 sepsis, 2 polytrauma), underwent computerized tomography (CT) of the lungs, (apex, hilum, base), at 5, 10, 15 cm H2O positive end expiratory pressure (PEEP)..." | Morphological response to positive end expiratory pressure in acute respiratory failure. Computerized tomography study. | 1986-01-01 00:00:00 | "Intensive care medicine, Issue: 3, Volume: 12 1986" | ", , , , , , , , , " | 1.0 | "['L Gattinoni', 'D Mascheroni', 'A Torresin', 'R Marcolin', 'R Fumagalli', 'S Vesconi', 'G P Rossi', 'F Rossi', 'S Baglioni', 'F Bassi']" |

### Expected output

`unique_people.csv`:

| firstname | lastname |
| --------- | -------- |
| Reinhard | Dummer |
| Alexander | Navarini |
| Gerhard | Rogler |
| Pierre | Michetti |
| Gerhard | Garhöfer |
| Stephan | Hoffmann |

## Time is limited

We understand your time is precious and would not want you to spend more than `2 to 4 hours over the span of one week`. The outcome should be locally runnable on a UNIX-flavored OS (MacOS, Linux).

It is OK if the challenge is not completed. Try to prioritize by what you think is most important. Tell us what motivated your choices, how you tackled the task, what you would do differently were you given more time, what you would differently a second time around, etc.

## Submission

Please zip and email your solution to `ethan@peakdata.com`. We will confirm your submission and get back to you about next steps within 1 week.


## Solution

### 1. Running the Solution

#### 1.a - Running with Docker

Building the Docker image:

```
docker build -t data_engineering_hiring .
```
Running the command terminal inside the container
```
docker run -v $(pwd):/unique_people_etl -it data_engineering_hiring bash
```
Executing the code:
```
python unique_people_etl/reader.py
```
The application accepts arguments:
- `input`: the name of the input file, by default is the provided file.
- `output`: the name of the output file, by default is the requested name.
- `header`: are the headers of the requested file, by default are the requested ones.

#### 1.b - Running in Python locally

Install the libraries in the `requirements.txt` and execute the command:

```
python unique_people_etl/reader.py
```

The arguments are the same as above.

#### 1.c - Running Unit Test

There is a small sample of unit testing, to execute run the following command:

```
pytest -vv
```

### 2. Explanation of the Name Matching Algorithm

####  2.a - Rejected approaches
There are many different theories in name matching. 
The first one is using `Levenshtein` distance, however for our use case is not going to work effectively, because a name can differ a little from another using the Levenstein distance and be 2 complete different names.
Other names can be the same person missing a middle name and have a big `Levenstein` distance. It didn't seem a good approach.
I rejected `Soundex` because is a name encoding based on English phoenetics and the encoding result was only 4 characters, creating many false positive.
Similar issue happened with `Metaphone` method.

####  2.b - The selected approach

My solution is a combination of the `Double Metaphone` algorithm and the `NYSIIS` algorithm.
In a method to identify different names referring to the same person, what we want is a method that has few false positives risking having false negative because is better to have 1 duplicate name being the same person than having 2 different people attached to the same name. 
With that in mind, I chose to combine both encoding to make the algorithm solid and try to remove all the false positives.
In the data set there is a `Simone Koch` and `Susanne Koch`, is impossible to classify with only those algorithms to which person we are referring by `S Koch`.
For that example, I kept them as a 3 separated people.

### 2.c - Future improvements

In that test I only focused in the column `authors`, however I've reach the limit on the algorithm being not able to distinguish between close names as the example mentioned.
For that reason, I think  is important to check the other columns while matching taking the research area or the related institutions as well in the algorithm.

### 3. Explanation of Selected Solution

### 3.a - Explaining the library
For this take to home I use Pandas library to deal with the data. As the exercise requires Python, Pandas is the best library to process data in pure Python.

### 3.b - Explaining the method
One of the problems I was facing was the complexity, if I was comparing the similarity between 2 person to distinguish if they were the same person or not, I was having a complexity O(n^2).
I come with an approach of encoding each name and inserting them into a hash table, in that way, same encoding are inserted in the same row, having a complexity of O(n).

### 3.c - Future problems
I'm afraid that solution is not scabable if the data increase. 
Pandas is difficult to parallelize, so in some point, we will need a bigger cluster to process. 
The solution proposed from my side is use PySpark to build the ETL since the team already know Python and it's a scalable language. If the data size increase, we can parallelize into different clusters (machines) to make it faster.

Another problem is the output file format. `CSV ` is not a format optimized for data exploration when it gets bigger.
It's heavy on its size, costly on time to query  over it and also expensive to store. I would like to recommend a parquet format, since is much lighter on size, is created to read/write it on parallel and is cheaper to store.