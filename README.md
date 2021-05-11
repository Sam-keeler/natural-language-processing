# Natural Language Processing Project
## Description
- Project that analyzes the contents readmes in order to predict the primary coding language of the repo
- Data was acquired by webscraping repos after searching the word "repository"

## Goals
- Find features associated with primary coding language
- Create a model that predicts primary coding language

## Data Dictionary
| column name           | type   | description                                                   |
|:----------------------|:-------|:--------------------------------------------------------------|
| repo                  | str    | The name of the repo the data was pulled from                 |
| language              | str    | The primary coding language used in the repo                  |
| readme_contents_clean | str    | The cleaned version of the repository's text                  |
| readme_length         | int    | How long the readme is by characters                          |
| languages_in_readme   | str    | Coding languages found to be in the contents of the readme    |
| has_X                 | Bool   | Says if the specified coding language was found in the readme |

## Project Plan
- Acquire data by scraping some repos
- Prepare data by handling nulls, cleaning readme contents, and create new features such as "readme length" and "languages in readme"
- Explore data, see what words are popularly used in each coding language
- Prepare for modeling removing unnecessary columns and split the data
- Model on train and validate
- Take best performing model and use it on test
- Document results

## Project Takeaways
- It was found that Python, Java, and C++ were the most common coding languages
- Only about a third of the repositories had specific coding languages mentioned in their readmes
- The common words found in each coding language group varied from group to group
- The best performing model (KNN) beat my baseline by 19%

## Instructions for Recreation
- All necessary functions are in the acquire and prepare files including get_repo_data, prep_repos, add_language_dummies_and_length_feature, and split.
- Explore and model code is in the notebook