# Data collection tool comparator

## Overview

**DCT comparator** is a Python project designed to facilitate the analysis and comparison of XLSForm data collection tools. This project addresses the need for effectively managing and tracking changes in XLSForm-based data collection tools, such as the WHO verbal autopsy, which is implemented in XX countries. Data collection tools often require regular updates to a master version and localized adaptations to meet specific regional or local needs. However, tracking changes across different master and child versions is a complex and time-consuming process. To simplify this, the project aims to develop a Python tool that streamlines the functional comparison of XLSForms.

The solution includes the development of a Python class designed to represents an XLSForm and provides class methods for 1-to-1 or 1-to-N comparisons of ODK forms from a functional perspective. A step-by-step workflow will be created to demonstrate how to use the class for comparing two forms or a master form with multiple child forms. The workflow will generate an Excel file with multiple tabs, providing a detailed comparison of XLSForms. It will highlight functional differences across various components using color scales, with the possibility of including additional comparisons as needed. 

## Form class features

The Form class represents an XLSForm object and provides various methods to interact with and compare 1-to-1 forms. 

Key features of the Form class include:

* **Initialization**: initialize a Form object by providing the path to the XLSForm spreadsheet file and a survey type (e.g., "SPA exit interview", "WHO verbal autopsy").
* **Retrieve form general information**: access form-related information such as the form's unique identifier, title, version, default language, and survey type.
* **Retrieve questions**: obtain a dataframe containing the survey questions, including attributes like question type, label, and group information.
* **Comparison**: compare 2 Form objects to detect differences in form ID, version, and default language. Additionally, identify added, deleted, modified questions, and similar labels between two forms. Return an excel summary of the detected differences.

A Juypter notebook **extract_info_from_xlsforms.ipynb** is available to demonstrate how the class can be used.

## Dependencies

The project requires **Python 3.13.2** to work and relies in particular on the following Python libraries:

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

## Development

If you want to contribute, follow these steps:

* Fork the repository;
* Create a feature branch based on the develop branch;
* Write clean and well-documented code;
* Commit and push your changes;
* Open a pull request

## Licensing

The project is open-sourced, with all code shared on GitHub under an MIT license to promote accessibility and collaboration.
