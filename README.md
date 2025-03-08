# Data collection tool comparator

## Overview

**DCT comparator** is a Python project designed to facilitate the analysis and comparison of XLSForm and REDCap data collection tools. This project provides a set of Python classes to extract, process, and compare information from XLSForms () and REDCap data dictionaries (experimental).

## Form class features

The Form class represents an XLSForm object and provides various methods to interact with and compare 1-to-1 forms. 

Key features of the Form class include:

* **Initialization**: initialize a Form object by providing the path to the XLSForm spreadsheet file and a survey type (e.g., "SPA exit interview", "WHO verbal autopsy").
* **Retrieve form general information**: access form-related information such as the form's unique identifier, title, version, default language, and survey type.
* **Retrieve questions**: obtain a dataframe containing the survey questions, including attributes like question type, label, and group information.
* **Comparison**: compare 2 Form objects to detect differences in form ID, version, and default language. Additionally, identify added, deleted, modified questions, and similar labels between two forms. Return an excel summary of the detected differences.

A notebook extract_info_from_xlsforms.ipynb is available to demonstrate how the class can be used.

## DataDic class features (experimental)

The DataDic class represents an REDCap data dictionary and provides various methods to interact with and compare REDcap data dictionaries.

Key features of the Form class include:

* Initialization: initialize a DataDic object by providing the path to the CSV data dictionary and a dictionary type.
* Comparison: compare two DataDic objects to identify added, deleted, modified questions, and similar labels between two forms.

## Dependencies

The project requires Python 3.13.2 to work and relies in particular on the following Python libraries:

* pandas 2.2.3
* Levenshtein 0.26.1
* nltk 3.9.1
* skrub 0.5.1

Make sure to install these dependencies before using this code.

A file `requirements.txt` is also available.

## Installation

## Screenshots

![image](https://github.com/user-attachments/assets/0d8b4b6c-b9f5-476c-84a9-b5c952c44f4e)

![image](https://github.com/user-attachments/assets/891149d5-7c71-4e8f-b5f6-c618c2fee24f)

![image](https://github.com/user-attachments/assets/5f423d76-c23c-407b-91a5-df58c75221ca)
