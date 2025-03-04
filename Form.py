import pandas as pd
import os
import string
import Levenshtein
import re
import nltk
nltk.download('punkt_tab')
#nltk.download('punkt')
nltk.download('stopwords')

import skrub

stop_words = set(nltk.corpus.stopwords.words('english'))
stop_words.add("please")
stop_words.add("specify")
stop_words.discard("where")
stop_words.discard("how")
stop_words.discard("when")
stop_words.discard("why")

def get_normalized_edit_distance(s1, s2):
    try:
        edit_distance = Levenshtein.distance(s1, s2)
        edit_distance /= max(len(s1), len(s2))
    except:
        edit_distance = 1.0
    return edit_distance

def find_common_words(df, lbl_col):
    full_text = ""
    df = df[df[lbl_col].notnull()]
    for index, row in df.iterrows():
        full_text = full_text + " " + row[lbl_col]
    allWords = nltk.tokenize.word_tokenize(full_text)
    allWordDist = nltk.FreqDist(w.lower() for w in allWords)
    mostCommon= allWordDist.most_common(10)
    common_words = []
    for item in mostCommon:
        common_words.append(item[0])
    return common_words

def remove_common_words(df,
                        lbl_col,
                        common_words):

    for index, row in df.iterrows():
        sentence = row[lbl_col]
        word_tokens = nltk.tokenize.word_tokenize(sentence)
        filtered_sentence = " "
        for w in word_tokens:
            if w not in common_words:
                filtered_sentence = filtered_sentence + " " + w
        row[lbl_col] = filtered_sentence

def process_label(s):

    try:
        # remove call to ODK variable
        s = re.sub(r'[$]+{.*?}', '', s)
        # remove HTML tags
        s = re.sub(r'<.*?>', '', s)
        # Remove question number
        s = re.sub(r'\w*[0-9]*.*[0-9]*\) ', '', s)
        # Remove punctuations and convert characters to lower case
        #s = "".join([char.lower() for char in s if char not in string.punctuation]).strip()
        s = s.lower().replace(".", "").replace("?", "").replace("'", "").strip()
        # Remove stop words
        word_tokens = nltk.tokenize.word_tokenize(s)
        out = " ".join([w for w in word_tokens if not w in stop_words])
    except:
        out = s

    return out

"""The Form class is a Python class designed to represent and manipulate information related to XLSForm surveys.
XLSForm is a standard format for authoring surveys in a spreadsheet format, often used in conjunction with data collection tools like ODK."""

class Form:

    # Class Attributes
    """_defaults (Class-level attribute): This dictionary defines default values for certain attributes of the Form class.
    Currently, it includes the key "survey" with a default value of None."""
    _defaults = {
        "survey_type": None
    }
    
    # Constructor
    """The constructor initializes a new Form object with the provided parameters.

    in_xlsx (string): The path to the XLSForm spreadsheet file from which the survey information is read.
    survey_type (string): A string representing the survey type, which is passed as an argument to the constructor.
    
    Inside the constructor, the provided XLSForm file is read, and relevant survey information is extracted and stored as instance variables:
    
    _id (string): The unique identifier of the form extracted from the XLSForm.
    _label (string): The title or label of the form extracted from the XLSForm.
    _version (tuple): The version information extracted from the XLSForm.
    _default_language (tuple): The default language information extracted from the XLSForm.
    _survey_type (object): The survey type object passed as a parameter to the constructor.
    
    It is important to ensure that the Form objects are properly initialized with the required survey information before using these comparison methods."""
    def __init__(self,
                 in_xlsx,
                 survey_type):

        print ("Create Form object from " + os.path.basename(in_xlsx))
        
        # Read and import raw data from XLSForm
        try:
            self._survey_df   = pd.read_excel(in_xlsx, sheet_name="survey").reset_index()
            dims = self._survey_df.shape 
            print ("\t - Info: survey sheet with " + str(dims[1]) + " columns and " + str(dims[0]) + " rows")
        except:
            self._survey_df = None
            print ("\t - Info: no survey sheet found")
        try:
            self._choices_df  = pd.read_excel(in_xlsx, sheet_name="choices")
            dims = self._choices_df.shape 
            print ("\t - Info: choices sheet with " + str(dims[1]) + " columns and " + str(dims[0]) + " rows")
        except:
            self._choices_df = None
            print ("\t - Info: no choices sheet found")
        try:
            self._settings_df = pd.read_excel(in_xlsx, sheet_name="settings")
            dims = self._settings_df.shape 
            print ("\t - Info: settings sheet with " + str(dims[1]) + " columns")
        except:
            self._settings_df = None
            print ("\t - Info: no settings sheet found")
        try:
            self._entities_df = pd.read_excel(in_xlsx, sheet_name="entities")
            dims = self._entities_df.shape 
            print ("\t - Info: entities sheet with " + str(dims[1]) + " columns")
        except:
            self._entities_df = None
            print ("\t - Info: no entities sheet found")
        
        # Extract general form attributes
        self._id               = self._settings_df.at[0, "form_id"]
        self._title            = self._settings_df.at[0, "form_title"]
        self._version          = self._settings_df.at[0, "version"]
        self._default_language = self._settings_df.at[0, "default_language"]
        self._label            = "::".join(x for x in ["label", self._default_language] if x)

        self._survey_type      = survey_type

        # Load choice list names
        self._list_names = self._choices_df["list_name"].dropna().unique().tolist() 

        # Load survey columns
        self._survey_columns = self._survey_df.columns.tolist()

        # Load survey group names
        self._group_names = self._survey_df[self._survey_df["type"].isin(["begin group", "begin_group"])]["name"].tolist()

        # Load survey repeat names
        self._repeat_names = self._survey_df[self._survey_df["type"].isin(["begin repeat", "begin_repeat"])]["name"].tolist()

        # Load questions
        questions = self._survey_df[self._survey_df["name"].notnull()]
        questions = questions[questions["type"] != "note"]
        questions = questions[["index",
                               "type",
                               "name",
                               self._label]]
        questions[self._label] = questions.apply(lambda row: process_label(row[self._label]), axis = 1)
        questions = questions.assign(group_id = "",
                                     group_lbl = "")
        group_ids = [0]
        for index, row in questions.iterrows():
            if row["type"] == "begin_group":
                group_ids.append(row["name"]) # Append the name to the list 'g'
            elif row["type"] == "end_group":
                if len(group_ids) > 1:
                    group_ids = group_ids[:-1]
            else:
                questions.loc[index, "group_id"] = group_ids[-1]
        questions = questions[(questions["type"] != "begin_group") & (questions["type"] != "end_group")]
        self._questions = questions.reset_index(drop=True)

        # Common words
        self._common_words = find_common_words(self._questions, self._label)

    # Instance Methods

    def getSurvey(self):

        return self._survey_df

    def getSurveyColumns(self):

        return self._survey_columns

    def getGroupNames(self):

        return self._group_names

    def getRepeatNames(self):
        
        return self._repeat_names
    
    def getChoices(self):

        return self._choices_df

    def getListNames(self):

        return self._list_names
    
    def getSettings(self):

        return self._settings_df

    """This method returns the unique identifier of the form."""

    def getID(self):

        return self._id

    """This method returns the title of the form."""

    def getTitle(self):

        return self._title
    
    """This method returns the version information of the form."""

    def getVersion(self):

        return self._version
    
    """This method returns the default language information of the form."""

    def getDefaultLanguage(self):

        return self._default_language
    
    """This method returns the main label information of the form."""

    def getMainLabel(self):

        return self._label
    
    """This method returns the survey type associated with the form."""

    def getSurveyType(self):

        return self._survey_type
    
    def getQuestions(self):

        return self._questions
    
    def getCommonWords(self):

        return self._common_words
    
    """This method is intended to return the parent of the form. However, the parent attribute (_parent) is not set within the class, so this method may not provide the expected functionality without additional implementation."""
    
    def getParent(self):

        return self._parent
    
    def compare(self, f, output_xlsx = ""):

        """
        This method takes another Form object (f) as an argument and compares various attributes of the current form with the attributes of the provided form.
        It returns a formatted string containing comparison results.
        """

        # Perform comparisons
        comparisons = [
            self.compareID(f),
            self.compareVersion(f),
            self.compareDefaultLanguage(f)
        ]

        # Create formatted output string
        formatted_output = ""# "\n".join(f"{comp_type}: {finding} {f1} {f2}" for comp_type, finding, f1, f2 in comparisons)

       # Save results to an Excel file if requested
        if output_xlsx:
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

            # Create DataFrame with required format
            df = pd.DataFrame(comparisons, columns=["Variable", "Finding", "f1", "f2"])
            output_path = os.path.join(output_dir, output_xlsx)

            # Write to Excel with formatting
            with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="settings", index=False)

                # Access the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets["settings"]

                # Define formatting styles
                green_format = workbook.add_format({"bg_color": "#C6EFCE", "font_color": "#006100"})  # Green
                red_format = workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})  # Red

                # Apply formatting based on "Finding" column
                for row in range(1, len(df) + 1):  # Skip header row
                    finding = df.iloc[row - 1, 1]  # "Finding" column
                    
                    # Apply green for "identical", red for "different"
                    cell_format = green_format if finding == "identical" else red_format
                    
                    # Apply color formatting to the entire row (Finding, f1, f2 columns)
                    worksheet.set_row(row, None, cell_format)

        return formatted_output


    def compareSettings(self, f):

        comparisons = [
            self.compareID(f),
            self.compareVersion(f),
            self.compareDefaultLanguage(f)
        ]
        df = pd.DataFrame(comparisons, columns=["variable", "status", "current", "ref"])
        return df

    """This method compares the version attribute of the current form with the version attribute of the provided form. It returns a string indicating whether the versions are identical or different."""
    def compareVersion(self, f):

        cver = f.getVersion()
        out = ""
        if self._version != cver:
            out = ("version", "different", self._version, cver)#"Versions are different: {} and {}".format(self._version, cver)
        else:
            out = ("version", "identical", self._version, cver)#"Version is identical: {}".format(self._version)
        return out
    
    """This method compares the unique identifier attribute of the current form with the identifier attribute of the provided form. It returns a string indicating whether the form IDs are identical or different."""
    def compareID(self, f):

        cid = f.getID()
        out = ""
        if self._id != cid:
            out = ("form_id", "different", self._id, cid)#, "Form IDs are different: {} and {}".format(self._id, cid))
        else:
            out = ("form_id", "identical", self._id, cid)#, "Form ID is identical: {}".format(self._id))
        return out
    
    def compareDefaultLanguage(self, f):

        cdl = f.getDefaultLanguage()
        out = ""
        if self._default_language != cdl:
            out = ("default_language", "different", self._default_language, cdl)#"Default languages are different: {} and {}".format(self._default_language, cdl)
        else:
            out = ("default_language", "identical", self._default_language, cdl)#"Default language is identical: {}".format(self._default_language))
        return out

    # Survey columns

    def detectRepeatSurveyColumns(self, f):
        return detectChanges(self._survey_columns, f.getSurveyColumns())

    def compareSurveyColumns(self, f):
        return summariseChanges(self._survey_columns, f.getSurveyColumns())

    # Survey group names

    def detectGroupNameChanges(self, f):
        return detectChanges(self._group_names, f.getGroupNames())

    def compareGroupNames(self, f):
        return summariseChanges(self._group_names, f.getGroupNames())

    # Survey repeat names

    def detectRepeatNameChanges(self, f):
        return detectChanges(self._repeat_names, f.getRepeatNames())

    def compareRepeatNames(self, f):
        return summariseChanges(self._repeat_names, f.getRepeatNames())

    # Choice list names

    def detectRepeatListNames(self, f):
        return detectChanges(self._list_names, f.getListNames())

    def compareListNames(self, f):
        return summariseChanges(self._list_names, f.getListNames())

    # Questions
    
    def detectAddedQuestions(self, f):

        out = pd.merge(left = self._questions.rename(columns = {self._label: "label"}),
                       right = f.getQuestions().rename(columns = {f.getMainLabel(): "label"}),
                       on = "name",
                       how = 'outer')
        out = out[out["type_x"].isnull() & out["type_y"].notnull()]
        out = out.reset_index(drop = True)
        out = out[["index_y",
                   "name",
                   "type_y",
                   "label_y"]] \
                    .rename(columns = {"index_y": "row",
                                       "type_y": "type",
                                       "label_y": "label"}) \
                    .astype({'row':'int'})

        if (out.shape[0] == 0):
            out = None

        if out is not None:
            tmp = self._questions.copy(deep=True)
            tmp = tmp[tmp[self._label].notnull()]
            out = skrub.fuzzy_join(out[["row", "name", "label"]],
                                   tmp[["index", "name", self._label]],
                                   left_on='label',
                                   right_on=self._label,
                                   drop_unmatched = False,
                                   add_match_info = True)
            """ 
            print (out)
            out = out[["row",
                       "name_x",
                      "label",
                      "name_y",
                      self._label,
                      "matching_score"]] \
                      .rename(columns = {"name_x": "name",
                                         "name_y": "name_of_closest_lbl",
                                         self._label: "closest_lbl"}) \
                      .fillna("") \
                      .reset_index(drop=True)
            """

        return out
    
    def detectDeletedQuestions(self, f):

        out = pd.merge(left = self._questions.rename(columns = {self._label: "label"}),
                       right = f.getQuestions().rename(columns = {f.getMainLabel(): "label"}),
                       on = "name",
                       how = 'outer')
        out = out[out["type_x"].notnull() & out["type_y"].isnull()]
        out = out.reset_index(drop = True)
        out = out[["index_x",
                   "name",
                   "type_x",
                   "label_x",
                   "group_id_x",
                   "group_lbl_x"]] \
                   .rename(columns = {"index_x": "row",
                                       "type_x": "type",
                                       "label_x": "label"}) \
                   .astype({'row':'int'})
        if (out.shape[0] == 0):
            out = None

        # if out is not None:
        #     tmp = f.getQuestions().copy(deep=True)
        #     tmp = tmp[tmp[f.getMainLabel()].notnull()]
        #     out = skrub.fuzzy_join(out[["row", "name", "label"]],
        #                            tmp[["index", "name", f.getMainLabel()]],
        #                            left_on='label',
        #                            right_on=f.getMainLabel(),
        #                            how='left',
        #                            match_score=0,
        #                            return_score=True)
        #     out = out[["row",
        #                "name_x",
        #                "label",
        #                "name_y",
        #                f.getMainLabel(),
        #                "matching_score"]] \
        #                 .rename(columns = {"name_x": "name",
        #                                    "name_y": "name_of_closest_lbl",
        #                                    f.getMainLabel(): "closest_lbl"}) \
        #                 .fillna("") \
        #                 .reset_index(drop=True)

        if out is None:
            out = pd.DataFrame()
            
        return out
    
    def detectModifiedLabels(self, f):

        out = pd.merge(left = self._questions.rename(columns = {self._label: "label"}),
                       right = f.getQuestions().rename(columns = {f.getMainLabel(): "label"}),
                       on = "name",
                       how = 'inner')
        out["edit_distance"] = out.apply(lambda row: get_normalized_edit_distance(s1 = row["label_x"], s2 = row["label_y"]), axis = 1)

        # Major modifications
        major = out[(out["label_x"].notnull()) & (out["edit_distance"] > 0.2)]
        major = major.reset_index(drop = True)
        major = major[["name",
                       "index_x",
                       "label_x",
                       "index_y",
                       "label_y"]] \
                        .rename(columns = {"index_x": "row1",
                                           "index_y": "row2",
                                           "label_x": "label1",
                                           "label_y": "label2"}) \
                        .astype({'row1':'int', 'row2':'int'})
        if (major.shape[0] == 0):
            major = None
        
        # Minor modifications
        minor = out[(out["label_x"].notnull()) & (out["edit_distance"] > 0) & (out["edit_distance"] <= 0.2)]
        minor = minor.reset_index(drop = True)
        minor = minor[["name",
                       "index_x",
                       "label_x",
                       "index_y",
                       "label_y"]] \
                        .rename(columns = {"index_x": "row1",
                                           "index_y": "row2",
                                           "label_x": "label1",
                                           "label_y": "label2"}) \
                        .astype({'row1':'int', 'row2':'int'})
        if (minor.shape[0] == 0):
            minor = None

        return major, minor
    
    def detectModifiedTypes(self, f):

        out = pd.merge(left = self._questions.rename(columns = {self._label: "label"}),
                       right = f.getQuestions().rename(columns = {f.getMainLabel(): "label"}),
                       on = "name",
                       how = 'inner')
        out["edit_distance"] = out.apply(lambda row: get_normalized_edit_distance(s1 = row["type_x"], s2 = row["type_y"]), axis = 1)

        out = out[(out["type_x"].notnull()) & (out["edit_distance"] > 0)]
        out = out.reset_index(drop = True)
        out = out[["name",
                   "index_x",
                   "type_x",
                   "index_y",
                   "type_y"]] \
                   .rename(columns = {"index_x": "row1",
                                      "index_y": "row2",
                                      "type_x": "type1",
                                      "type_y": "type2"}) \
                   .astype({'row1':'int', 'row2':'int'})
        if (out.shape[0] == 0):
            out = None

        return out
    
    def detectSimilarLabels(self, f):
            
        tmp1 = self._questions.copy(deep=True).rename(columns = {self._label: "label"})
        tmp1 = tmp1[tmp1["label"].notnull()]

        tmp2 = f.getQuestions().rename(columns = {f.getMainLabel(): "label"})
        tmp2 = tmp2[tmp2["label"].notnull()]

        out = skrub.fuzzy_join(tmp1[["index", "name", "label", "type"]],
                               tmp2[["index", "name", "label", "type"]],
                               on='label',
                               how='left',
                               match_score=0,
                               return_score=True)
        out = out[out["matching_score"] >= 0.6] \
               .rename(columns = {"index_x": "row1",
                                  "index_y": "row2",
                                  "name_x": "name1",
                                  "name_y": "name2",
                                  "type_x": "type1",
                                  "type_y": "type2",
                                  "label_x": "label1",
                                  "label_y": "label2"}) \
              .reset_index(drop=True) \
              .sort_values(by=["matching_score", "row1"],
                           ascending=[False, True])
            
        if (out.shape[0] == 0):
            out = None

        return out
    
    """Please note that the compare, compareVersion, and compareID methods are designed to provide comparison functionality but should be used with care, as they rely on the assumption that certain attributes of the form are set correctly during initialization."""

"""Note: This documentation assumes that the class is used as provided and that any missing implementations or additional functionality required for specific use cases are handled outside of the class definition."""

# Static methods

def detectChanges(current, reference):

    """Static method to detect unchanged, added, and removed items."""
    current_set, reference_set = set(current), set(reference)
    unchanged = list(current_set & reference_set)
    added = list(current_set - reference_set)
    removed = list(reference_set - current_set)
    return unchanged, added, removed

def summariseChanges(current, reference):

    """Static method to compare names and return a DataFrame."""
    unchanged, added, removed = detectChanges(current, reference)
    return pd.DataFrame({
        "name": unchanged + added + removed,
        "status": (
            ['unchanged'] * len(unchanged) +
            ['added'] * len(added) +
            ['removed'] * len(removed)
        )
    }).sort_values(by="name", ascending=True)

class ListAnswers:

    def __init__(self,
                 name):
        self._name = name
        
    # Instance Methods
    """This method returns the list name."""
    def getName(self):
        return self._name    

class Answer:

    def __init__(self,
                 list_name):
        self._list_name = list_name
        
    # Instance Methods
    """This method returns the list name."""
    def getListName(self):
        return self._list_name    