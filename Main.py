import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# App title and configuration
st.set_page_config(page_title="NU Course Search App", page_icon=":books:", layout="wide")
st.image("logos_new.png", width=400)
st.title("Search Courses by Group")
st.write("""
    This tool helps you find the optimal course block for a set of selected courses.
    Simply choose your required courses, and the tool will analyze them to provide 
    the best matching block, ensuring an efficient and well-organized schedule. 
    With our recent update, it now supports AI groups.
""")
file_path = "CS Groups.xlsx"

# Check if session state has 'course_input', if not initialize it
if 'course_input' not in st.session_state:
    st.session_state['course_input'] = ""

def load_data(file_path):
    """
    Load data from an Excel file and return the DataFrame.
    
    Args:
        file_path (str): Path to the Excel file.
    
    Returns:
        pd.DataFrame: DataFrame containing the loaded Excel data.
    """
    if os.path.exists(file_path):
        data = pd.read_excel(file_path)
        st.success("Data file successfully loaded!")
        return data
    else:
        st.error(f"Data file '{file_path}' not found. Please ensure the file is placed in the correct directory.")
        return None

def display_clickable_courses(dataframe):
    """
    Display clickable course buttons for users to add courses.
    
    Args:
        dataframe (pd.DataFrame): DataFrame containing course descriptions.
    """
    courses = dataframe['Description (COURSES)'].str.split().explode().str.upper().unique()
    unique_courses = sorted(set(courses))
    
    st.subheader("Click on courses to add them")
    
    for i in range(0, len(unique_courses), 4):
        cols = st.columns(4)  # Create columns to display multiple buttons per row
        
        for j in range(4):
            if i + j < len(unique_courses):
                course_name = unique_courses[i + j]
                if isinstance(course_name, str):
                    if cols[j].button(course_name):  # If button is clicked
                        if st.session_state['course_input']:
                            st.session_state['course_input'] += f", {course_name}"
                        else:
                            st.session_state['course_input'] = course_name

def create_course_group_matrix(course_list, dataframe):
    """
    Create a matrix showing if courses are present in each group, and sort by match count.
    
    Args:
        course_list (list): List of selected courses.
        dataframe (pd.DataFrame): DataFrame containing course group data.
    
    Returns:
        pd.DataFrame: Sorted matrix showing course matches for each group.
    """
    course_list = [course.strip().upper() for course in course_list.split(',')]
    group_names = dataframe['GroupName'].unique()
    
    # Initialize an empty matrix with group names as rows and selected courses as columns
    matrix = pd.DataFrame(index=group_names, columns=course_list)
    
    # Populate the matrix with "Yes" or "No" values based on course presence in each group
    for index, row in dataframe.iterrows():
        courses_in_group = row['Description (COURSES)'].split()
        for course in course_list:
            matrix.at[row['GroupName'], course] = "Yes" if course in courses_in_group else "No"
    
    # Add a column to count how many courses match for each group
    matrix['Matched Count'] = (matrix == "Yes").sum(axis=1)
    total_courses = len(course_list)
    
 
    # Add a percentage column showing the ratio of matched courses
    matrix['Percentage'] = (matrix['Matched Count'] / total_courses * 100).round(10).astype(str) + '%'
    
    # Sort the matrix by the match count in descending order
    matrix_sorted = matrix.sort_values(by='Matched Count', ascending=False)
    
    return matrix_sorted

def highlight_cells(val):
    """
    Highlight cells with different colors based on their value ("Yes" or "No").
    
    Args:
        val (str): Value in the cell ("Yes" or "No").
    
    Returns:
        str: Background color for the cell.
    """
    color = 'background-color: lightgreen' if val == "Yes" else 'background-color: lightcoral' if val == "No" else ''
    return color

def display_course_group_matrix(matrix):
    """
    Display the course-group matrix with conditional formatting and adjustable height.
    
    Args:
        matrix (pd.DataFrame): DataFrame containing the course-group matrix.
    """
    if not matrix.empty:
        st.subheader("Course-Group Matrix (Sorted by Matches)")
        
        # Apply color formatting to the matrix
        styled_matrix = matrix.style.applymap(highlight_cells)
        
        # Dynamically set the height of the table based on the number of rows
        num_rows = matrix.shape[0]
        table_height = 40 + num_rows * 35  # Adjust based on row height
        
        # Display the matrix with dynamic height
        st.dataframe(styled_matrix, height=table_height)

def main():
    """
    Main function to run the Streamlit app, handles data loading, course selection, 
    and matrix generation.
    """
    # Load the data from the Excel file
    data = load_data(file_path)
    
    if data is not None:
        # Display clickable course buttons
        display_clickable_courses(data)
        
        # Show input text box for selected courses
        st.text_input("Selected Courses (comma-separated):", value=st.session_state['course_input'], key='course_input', disabled=False)
        
        if st.session_state['course_input']:
            # Create and display the course-group matrix
            course_group_matrix = create_course_group_matrix(st.session_state['course_input'], data)
            display_course_group_matrix(course_group_matrix)

# Run the main function if the script is executed
if __name__ == "__main__":
    main()
