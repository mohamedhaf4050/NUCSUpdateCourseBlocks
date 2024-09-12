import streamlit as st
import pandas as pd
import os

# App title and configuration
st.set_page_config(page_title="Course Search App", page_icon=":books:", layout="wide")
st.title("Search Courses by Group")

# Specify the path to the Excel file (located beside the main code)
file_path = "CS Groups.xlsx"

# Function to extract and display unique courses
def display_unique_courses(dataframe):
    # Extract all the courses from the 'Description (COURSES)' column
    courses = dataframe['Description (COURSES)'].str.split().explode().unique()
    
    # Remove duplicates and sort the courses
    unique_courses = sorted(set(courses))
    
    # Create a DataFrame for display with 4 columns for better visualization
    num_columns = 4
    course_table = pd.DataFrame([unique_courses[i:i+num_columns] for i in range(0, len(unique_courses), num_columns)])
    
    # Display the table with colored style
    st.subheader("Unique Courses (No Duplicates)")
    st.dataframe(course_table.style.applymap(lambda x: "background-color: lightblue"))

# Ensure the file exists
if os.path.exists(file_path):
    # Load data into a pandas dataframe
    data = pd.read_excel(file_path)

    st.success("Data file successfully loaded!")

    # Display the unique courses table
    display_unique_courses(data)

    # Text input for courses to search
    course_input = st.text_input("Enter the courses you want to search (comma-separated):")

    # Function to search courses
    def search_courses(course_list, dataframe):
        course_list = [course.strip().upper() for course in course_list.split(',')]
        results = []
        for index, row in dataframe.iterrows():
            courses = row['Description (COURSES)'].split()
            ratio = sum(course in courses for course in course_list) / len(course_list)
            if ratio > 0:
                results.append({'GroupName': row['GroupName'], 'Ratio': ratio})
        return pd.DataFrame(results)

    # Search and display results when input is provided
    if course_input:
        results_df = search_courses(course_input, data)

        if not results_df.empty:
            # Sort the results by Ratio in descending order
            sorted_df = results_df.sort_values(by="Ratio", ascending=False)

            st.subheader("Search Results (Sorted by Match Ratio):")
            st.dataframe(sorted_df)  # Display the sorted table

            # Plot the results
            st.subheader("Visualized Results:")

            fig, ax = plt.subplots()
            ax.barh(sorted_df['GroupName'], sorted_df['Ratio'], color='skyblue')
            ax.set_xlabel("Match Ratio")
            ax.set_ylabel("GroupName")
            ax.set_title("Course Match Ratios by Group")
            plt.gca().invert_yaxis()  # Invert the y-axis to show the highest ratio at the top
            st.pyplot(fig)  # Display the plot
        else:
            st.warning("No matching groups found for the entered courses.")
else:
    st.error(f"Data file '{file_path}' not found. Please ensure the file is placed in the correct directory.")
