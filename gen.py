import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config(page_title="Akinator Game", page_icon="🎩")
st.title("🎩 Akinator Game")
st.write("Think of an object. I will try to guess it within 30 questions!")


MAX_QUESTIONS = 30

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

if "history" not in st.session_state:
    st.session_state.history = ""

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "current_question" not in st.session_state:
    st.session_state.current_question = ""

if "final_guess" not in st.session_state:
    st.session_state.final_guess = ""

if "guessed_correctly" not in st.session_state:
    st.session_state.guessed_correctly = None

if "early_finish" not in st.session_state:
    st.session_state.early_finish = False


question_prompt = ChatPromptTemplate.from_template(
    """
You are playing Akinator.

Rules:
- Ask ONE yes/no question
- Avoid repeating questions
- Eliminate impossible categories
- Narrow down aggressively

Previous answers:
{history}

Next best question:
"""
)

guess_prompt = ChatPromptTemplate.from_template(
    """
You are an Akinator-style expert.

Step 1: Identify the category (person, animal, object, place, food, device, concept).
Step 2: Narrow down to the most likely candidate.
Step 3: Output ONLY the final guess (one or two words).

Answers so far:
{history}

Final guess:
"""
)

confidence_prompt = ChatPromptTemplate.from_template(
    """
Given the answers below, how confident are you (0 to 100) in your guess: {guess}?

Answers:
{history}

Respond with ONLY a number.
"""
)

def ask_question():
    chain = question_prompt | llm
    response = chain.invoke({"history": st.session_state.history})
    q = response.content.strip()
    if not q.endswith("?"):
        q += "?"
    return q

def make_guess():
    chain = guess_prompt | llm
    response = chain.invoke({"history": st.session_state.history})
    guess = response.content.strip().lower()
    return guess if guess else "something"

def get_confidence(guess):
    chain = confidence_prompt | llm
    response = chain.invoke({
        "guess": guess,
        "history": st.session_state.history
    })
    try:
        return int(response.content.strip())
    except:
        return 0


if st.session_state.question_count < MAX_QUESTIONS and not st.session_state.early_finish:

    question = ask_question()
    st.session_state.current_question = question

    st.session_state.final_guess = make_guess()

    col_main, col_right = st.columns([3, 1])

    with col_main:
        st.subheader(f"🤔 Question {st.session_state.question_count + 1}")
        st.write(question)

        if st.button("Yes", key=f"yes_{st.session_state.question_count}"):
            st.session_state.history += f"{question} → yes\n"

            if st.session_state.question_count + 1 == MAX_QUESTIONS:
                st.session_state.guessed_correctly = True

            st.session_state.question_count += 1
            st.rerun()

        if st.button("No", key=f"no_{st.session_state.question_count}"):
            st.session_state.history += f"{question} → no\n"

            if st.session_state.question_count + 1 == MAX_QUESTIONS:
                st.session_state.guessed_correctly = False

            st.session_state.question_count += 1
            st.rerun()

        if st.button("Maybe", key=f"maybe_{st.session_state.question_count}"):
            st.session_state.history += f"{question} → maybe\n"
            st.session_state.question_count += 1
            st.rerun()

    with col_right:
        st.markdown("### ✅ Correct Guess")

        if st.button("Yes, this is correct", key=f"correct_{st.session_state.question_count}"):
            st.session_state.early_finish = True
            st.session_state.guessed_correctly = True
            st.rerun()


if st.session_state.question_count >= MAX_QUESTIONS or st.session_state.early_finish:
    st.subheader("🔮 Result")

    st.write("🤖 I was guessing:", st.session_state.final_guess)

    if st.session_state.guessed_correctly is True:
        st.success(f"🎉 Yeahh!! 😄 I guessed the word **{st.session_state.final_guess}**!")
    else:
        st.error("😔 I am sorry, I couldn’t guess the thing.")

    if st.button("Play Again", key="play_again"):
        st.session_state.clear()
        st.rerun()
