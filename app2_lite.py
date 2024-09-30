import time
import streamlit as st
import pandas as pd
# import pickle
import os


@st.cache_data
def load_data(json_file):
    _df = pd.read_json(json_file)
    _df = _df.fillna(0)
    sampled_df = _df.sample(frac=1).reset_index(drop=True)
    return sampled_df


pickle_file = 'FAQ-THA.json'
# st.set_page_config(layout="wide")
# Load the dataframe
st.title("Medical Chatbot Answer Rating")

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
    df = load_data(pickle_file)
    # Ensure that the dataframe has the expected columns
    if {'question', 'search_term', 'contexts', 'ground_truth', 'LLM_answer'}.issubset(df.columns):
        if 'current_idx' not in st.session_state:
            st.session_state.current_idx = 0
        if 'ratings' not in st.session_state:
            # Initialize ratings and comments in session state
            st.session_state.ratings = [{'trace_id': None, 'rating': None, 'comment': ''} for _ in range(len(df))]

        total_rows = len(df)
        current_idx = st.session_state.current_idx

        if current_idx < total_rows:
            row = df.iloc[current_idx]

            with st.sidebar:
                st.subheader(f"Question: {current_idx + 1}")
                st.progress(row['faithfulness'], text="Accuracy of answer to context:")
                st.progress(row['answer_relevancy'], text="Relatedness to the question:")
                st.progress(row['context_recall'], text="Amount of relevant info retrieved:")
                st.progress(row['context_precision'], text="Quality of retrieved information:")
                st.progress(row['answer_similarity'], text="Match to ground-truth:")
                expander1 = st.expander("View AI-retrieved Context")
                try:
                    context_string = "".join(row['contexts'])
                except TypeError:
                    context_string = "No context available as Chatbot didn't query the database"
                expander1.write(context_string)

            # Display progress
            st.progress((current_idx + 1) / total_rows)
            st.write(f"Progress: {current_idx + 1}/{total_rows}")

            # Two-column design to make the layout compact
            col1, col2 = st.columns(2)

            # Column 1: Question
            with col1:
                st.subheader("Question")
                st.markdown(f"<div class='fixed-container'>{row['question']}</div>", unsafe_allow_html=True)

            # Column 2: Correct Answer
            with col2:
                st.subheader("Ground Truth")
                st.markdown(f"<div class='fixed-container'>{row['ground_truth']}</div>", unsafe_allow_html=True)

            st.subheader(":green[Chatbot's Answer]")
            answer = row['LLM_answer'].replace('\\n', '\n')

            # st.write("")
            # co1, co2 = st.columns(2)

            # expander1 = st.expander("Expand Context")
            # try:
            #     context_string = "".join(row['contexts'])
            # except TypeError:
            #     context_string = "No context available as Chatbot didn't query the database"
            # expander1.write(context_string)

            expander2 = st.expander("Expand Chatbot Answer", expanded=True)
            expander2.write(answer)
            # st.divider()
            # Create a form for rating and comments
            with st.form(key="rating_form"):
                st.subheader(f"Rate Chatbot's Answer of Question:{current_idx + 1}")

                # Rating slider
                rating = st.slider(
                    "Your Rating (1-5 stars)",
                    min_value=1,
                    max_value=5,
                    value=st.session_state.ratings[current_idx]['rating'] or 3,
                )

                # Comment input
                comment = st.text_input(
                    "Enter your comments here (if any)",
                    value=st.session_state.ratings[current_idx]['comment']
                )
                cola, colb = st.columns(2, vertical_alignment="center")
                with cola:
                    # Submit button inside the form
                    submitted = st.form_submit_button("Submit", type='primary')
                with colb:
                    st.info("Click submit to save your rating!")

                if submitted:
                    # Save the current rating and comment in the session state when form is submitted
                    st.session_state.ratings[current_idx]['trace_id'] = row['trace_id']
                    st.session_state.ratings[current_idx]['rating'] = rating
                    st.session_state.ratings[current_idx]['comment'] = comment
                    st.success("Rating and comment saved! Loading next question .....")
                    time.sleep(1)
                    if st.session_state.current_idx < total_rows - 1:
                        st.session_state.current_idx += 1
                    st.rerun()

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

            # Check if gone through all rows and show the download button
            if st.session_state.current_idx >= total_rows - 1 and st.button("Finish", type='primary'):
                st.success("You've rated all answers! Thank you. Please download the records.")
                ratings_df = pd.DataFrame(st.session_state.ratings)
                # ratings_df.to_csv('ratings_autosave.csv')
                st.dataframe(ratings_df, width=750)
                st.download_button("Download Ratings", ratings_df.to_csv(index=False), "chatbot_ratings.csv")
        elif st.session_state.current_idx >= total_rows - 1:
            ratings_df = pd.DataFrame(st.session_state.ratings)
            st.success("You've rated all the rows. Thank you! Please download the records.")
            st.dataframe(ratings_df, width=750)
            st.download_button("Download Ratings", ratings_df.to_csv(index=False), "chatbot_ratings.csv")
    else:
        st.error("The dataframe does not contain the required columns!")
else:
    st.error(f"JSON file not found: {pickle_file}. Please check the file path.")
