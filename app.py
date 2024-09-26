import streamlit as st
import pandas as pd
import pickle
import os


@st.cache_data
def load_data(pickle_file):
    with open(pickle_file, 'rb') as file:
        df = pickle.load(file)
    return df


pickle_file = 'Out_42.json'
# st.set_page_config(layout="wide")
# Load the dataframe
st.title("LLM Answer Judging App")

st.markdown(
    """
    <style>
    .fixed-container {
        height: 200px;
        overflow-y: scroll;
        padding: 10px;
        border: 2px solid #ccc;
        border-radius: 6px;
        background-color: #f9f9f9;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if os.path.exists(pickle_file):
    df = pd.read_json(pickle_file)

    # Ensure that the dataframe has the expected columns
    if {'question', 'context', 'answer', 'LLM_answer'}.issubset(df.columns):
        if 'current_idx' not in st.session_state:
            st.session_state.current_idx = 0
        if 'ratings' not in st.session_state:
            # Initialize ratings and comments in session state
            st.session_state.ratings = [{'rating': None, 'comment': ''} for _ in range(len(df))]

        total_rows = len(df)
        current_idx = st.session_state.current_idx

        if current_idx < total_rows:
            row = df.iloc[current_idx]

            # Display progress
            st.progress((current_idx + 1) / total_rows)
            st.write(f"Progress: {current_idx + 1}/{total_rows} rows rated.")

            # Two-column design to make the layout compact
            col1, col2 = st.columns(2)

            # Column 1: Question and Context
            with col1:
                st.subheader("Question")
                st.markdown(f"<div class='fixed-container'>{row['question']}</div>", unsafe_allow_html=True)

                st.subheader("Context")
                st.markdown(f"<div class='fixed-container'>{row['context']}</div>", unsafe_allow_html=True)

            # Column 2: Correct Answer and LLM Answer
            with col2:
                st.subheader("Ground Truth")
                st.markdown(f"<div class='fixed-container'>{row['answer']}</div>", unsafe_allow_html=True)

                st.subheader(":green[LLM's Answer]")
                answer = row['LLM_answer'].replace('\\n', '\n')
                st.markdown(f"<div class='fixed-container'>{answer}</div>", unsafe_allow_html=True)

            st.write("")
            expander = st.expander("Expand LLM Answer")
            expander.write(answer)

            # st.divider()
            # Create a form for rating and comments
            with st.form(key="rating_form"):
                st.subheader(f"Rate the LLM's Answer of Question:{current_idx+1}")

                # Rating slider
                rating = st.slider(
                    "Your Rating (1-5 stars)",
                    min_value=1,
                    max_value=5,
                    value=st.session_state.ratings[current_idx]['rating'] or 3,
                )

                # Comment input
                comment = st.text_input(
                    "Recommend your answer here (if any)",
                    value=st.session_state.ratings[current_idx]['comment']
                )

                # Submit button inside the form
                submitted = st.form_submit_button("Submit", type='primary')

                if submitted:
                    # Save the current rating and comment in the session state when form is submitted
                    st.session_state.ratings[current_idx]['rating'] = rating
                    st.session_state.ratings[current_idx]['comment'] = comment
                    st.success("Rating and comment saved!")

            # Navigation buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Previous", disabled=current_idx == 0):
                    if current_idx > 0:
                        st.session_state.current_idx -= 1
                        st.rerun()

            with col3:
                if st.button("Next", disabled=current_idx >= total_rows - 1):
                    if current_idx < total_rows - 1:
                        st.session_state.current_idx += 1
                        st.rerun()

            # Check if we've gone through all rows and show the download button
            if st.session_state.current_idx >= total_rows - 1 and st.button("Finish", type='primary'):
                st.success("You've rated all answers! Thank you.")
                ratings_df = pd.DataFrame(st.session_state.ratings)
                # ratings_df.to_csv('ratings_autosave.csv')
                st.write(ratings_df)
                st.download_button("Download Ratings", ratings_df.to_csv(index=False), "ratings.csv")
        else:
            st.success("You've rated all the rows. Thank you!")
    else:
        st.error("The dataframe does not contain the required columns: 'question', 'context', 'answer', 'LLM_answer'.")
else:
    st.error(f"Pickle file not found: {pickle_file}. Please check the file path.")
