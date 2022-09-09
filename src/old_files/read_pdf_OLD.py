import pandas as pd
import tabula

# file paths
courses_needed_path = 'input_files/Sample Input1.pdf'
# dag_path = ""  #download and add later

# read file
courses_needed_df_list = tabula.read_pdf(courses_needed_path, pages='all')

# create blank df
courses_needed_df = pd.DataFrame()

# add each df from courses_needed_df_list to courses_needed_df
for i in range(len(courses_needed_df_list)):
    courses_needed_df = pd.concat([courses_needed_df, courses_needed_df_list[i]], axis=0, ignore_index=True)

    # personal debugger to observe issue
    # the 4th dataframe (output3.csv) does not get added to the bottom of the df, why? I don't know yet.
    # it looks like it's counted as a column title and not an actual piece of data
    # add column titles beforehand?
    # courses_needed_df_list[i].to_csv("output" + str(i) + ".csv")

# rename columns
courses_needed_df = courses_needed_df.rename(columns={'Unnamed: 0': 'Courses Needed', 'Unnamed: 1': 'Notes'})
# drop blanks
courses_needed_df.dropna(subset=['Courses Needed'], inplace=True)
# reset index after blanks are dropped
courses_needed_df = courses_needed_df.reset_index(drop=True)
# export to excel, demonstrates df can be export to excel, also gives visual to see dataframe outside of code
courses_needed_df.to_excel('output_files/courses_needed.xlsx')
