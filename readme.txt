# Table_Annotator

This GUI is made for manually curating and annotating columns of tables. 

## Important disclaimer upfront: 

1. This GUI is under development and represents a very simple way of curating data from tables, by declaring an entity type for one or more columns and then extract the entities (including the whole table, number of rows + columns, row + column headers) as structured JSON.
2. This GUI is made for using it together with BioC-XML format [^1] and the document level annotation tool TeamTat [^2] both developed by the group of R. Islamaj. from the NCBI.

## Usage

(Usage description needs further extension in detail)

Tables have to be embedded in BioC-XML files as list of lists as shown below.

```
<passage>
    <infon key="type">title_2</infon>
    <infon key="section_type">TABLE_CAPTION</infon>
    <infon key="raw_table">[
            ["Element", "Symbol", "Atomic Number"],
            ["Hydrogen", "H", 1],
            ["Helium", "He", 2],
            ["Lithium", "Li", 3],
            ["Beryllium", "Be", 4],
            ["Boron", "B", 5],
            ["Carbon", "C", 6],
            ["Nitrogen", "N", 7],
            ["Oxygen", "O", 8],
            ["Fluorine", "F", 9],
            ["Neon", "Ne", 10]
        ]
<passage>
```

Before creating the BioC file read in the tables that you want to parse and convert them into list of lists if not already done.
Then create a BioC file using PyBioC (https://github.com/OntoGene/PyBioC) and create a Passage Object for every table.
When creating the Passage object make sure to first create an infon with key = "section_type" and "TABLE_CAPTION" as content.
Then create another infon with key = "raw_table" and the table as list of lists as content.
When you have created one passage with the mentioned infons for each table you can create the BioC document.

You can now start table_annotator with

```
cd table_annotator
python ctk_filemenu.py
```

# References

[^1]: Donald C. Comeau, Rezarta Islamaj Doğan, Paolo Ciccarese, Kevin Bretonnel Cohen, Martin Krallinger, Florian Leitner, Zhiyong Lu, Yifan Peng, Fabio Rinaldi, Manabu Torii, Alfonso Valencia, Karin Verspoor, Thomas C. Wiegers, Cathy H. Wu, W. John Wilbur, BioC: a minimalist approach to interoperability for biomedical text processing, Database, Volume 2013, 2013, bat064, [https://doi.org/10.1093/database/bat064]
[^2]: Rezarta Islamaj, Dongseop Kwon, Sun Kim, Zhiyong Lu, TeamTat: a collaborative text annotation tool, Nucleic Acids Research, Volume 48, Issue W1, 02 July 2020, Pages W5–W11, [https://doi.org/10.1093/nar/gkaa333]
