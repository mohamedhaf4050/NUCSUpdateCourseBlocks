import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# App title and configuration
st.set_page_config(page_title="NU Course Search App", page_icon=":books:", layout="wide")
st.image("logos_new.png", width=400)
st.title("Search Courses by Group")
st.write("This tool helps you find the optimal course block for a set of selected courses. Simply choose your required courses, and the tool will analyze them to provide the best matching block, ensuring an efficient and well-organized schedule. With our recent update, it now supports AI groups,")
file_path = "CS Groups.xlsx"

if 'course_input' not in st.session_state:
    st.session_state['course_input'] = ""

def display_clickable_courses(dataframe):
    courses = dataframe['Description (COURSES)'].str.split().explode().str.upper().unique()
    unique_courses = sorted(set(courses))
    
    st.subheader("Click on courses to add them")
    
    for i in range(0, len(unique_courses), 4):
        cols = st.columns(4)
        
        for j in range(4):
            if i + j < len(unique_courses):
                course_name = unique_courses[i + j]
                if isinstance(course_name, str):
                    if cols[j].button(course_name):
                        if st.session_state['course_input']:
                            st.session_state['course_input'] += f", {course_name}"
                        else:
                            st.session_state['course_input'] = course_name

if os.path.exists(file_path):
    data = pd.read_excel(file_path)
    st.success("Data file successfully loaded!")

    display_clickable_courses(data)

    st.text_input("Selected Courses (comma-separated):", value=st.session_state['course_input'], key='course_input', disabled=False)

    def create_course_group_matrix(course_list, dataframe):
        course_list = [course.strip().upper() for course in course_list.split(',')]
        group_names = dataframe['GroupName'].unique()
        
        # Create an empty DataFrame for the matrix
        matrix = pd.DataFrame(index=group_names, columns=course_list)
        
        # Populate the matrix
        for index, row in dataframe.iterrows():
            courses_in_group = row['Description (COURSES)'].split()
            for course in course_list:
                matrix.at[row['GroupName'], course] = "Yes" if course in courses_in_group else "No"
        
        # Add a column for the match count (how many courses are "Yes" in each row)
        matrix['Match Count'] = (matrix == "Yes").sum(axis=1)
        
        # Sort the matrix by the match count in descending order
        matrix_sorted = matrix.sort_values(by='Match Count', ascending=False)
        
        return matrix_sorted

    if st.session_state['course_input']:
        # Create the course-group matrix
        course_group_matrix = create_course_group_matrix(st.session_state['course_input'], data)

        if not course_group_matrix.empty:
            st.subheader("Course-Group Matrix (Sorted by Matches):")
            
            # Function to apply color formatting based on the "Yes"/"No" values
            def highlight_cells(val):
                color = 'background-color: lightgreen' if val == "Yes" else 'background-color: lightcoral' if val == "No" else ''
                return color
            
            # Apply the style to the matrix
            styled_matrix = course_group_matrix.style.applymap(highlight_cells)
            
            # Display the styled matrix
            st.dataframe(styled_matrix)

            st.subheader("Visualized Results:")
            # Optional: Add some visualization or further data exploration here if needed
            
        else:
            st.warning("No matching groups found for the selected courses.")
else:
    st.error(f"Data file '{file_path}' not found. Please ensure the file is placed in the correct directory.")
