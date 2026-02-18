
### **1. Core Concept of STORM**

STORM is a writing system designed to automatically generate grounded, long-form articles (similar to Wikipedia pages) from scratch.

Its core philosophy differentiates it from standard Retrieval-Augmented Generation (RAG) by focusing heavily on the **pre-writing stage**. Instead of just retrieving information and writing immediately, STORM mimics the human writing process: **research $\rightarrow$ outline $\rightarrow$ write**.

The system is built on two key hypotheses:
1.  **Diverse Perspectives:** researching a topic from different viewpoints leads to more varied and comprehensive questions.
2.  **Iterative Inquiry:** formulating in-depth questions requires an iterative process where new answers trigger follow-up questions.

### **2. How to Implement STORM (Step-by-Step)**

STORM automates the writing process by breaking it down into two main phases: the **Pre-writing Stage** (Research & Outline) and the **Writing Stage**.

#### **Phase 1: Pre-writing (Research & Outlining)**

This phase aims to gather comprehensive information and structure it.

**Step 1: Survey and Identify Perspectives**
*   **Goal:** Discover different angles to approach the topic.
*   **Implementation:**
    1.  **Survey:** Given a topic $t$, prompt an LLM to find related topics. Use a tool (like the Wikipedia API) to retrieve the **Table of Contents (ToC)** for these related articles.
    2.  **Identify:** Concatenate these ToCs and prompt the LLM to identify $N$ distinct **perspectives** (personas) that would contribute to a comprehensive article (e.g., for a topic like "2022 Winter Olympics," perspectives might include "Event Planner," "Sports Journalist," "International Relations Expert").
    3.  Add a default "Basic Fact Writer" perspective to ensure fundamental facts are covered.

**Step 2: Simulate Conversations (Data Collection)**
*   **Goal:** Deep research through "conversation".
*   **Implementation:** Simulate a multi-turn conversation between two LLM agents for *each* identified perspective.
    *   **Agent A (Wikipedia Writer):** Prompted with a specific perspective. Its job is to ask questions. It uses the conversation history to ask follow-up questions.
    *   **Agent B (Topic Expert):** Its job is to answer questions using the internet.
        1.  Receives the question from Agent A.
        2.  Generates search queries based on the question.
        3.  Searches the internet (e.g., using a search API like You.com).
        4.  Sifts results to exclude unreliable sources.
        5.  Synthesizes the search results into an answer with citations.
    *   **Loop:** Repeat this Q&A process for $M$ rounds (e.g., 5 rounds). Collect all references ($R$) found during these conversations.

**Step 3: Create the Outline**
*   **Goal:** Organize the chaotic research into a structured framework.
*   **Implementation:**
    1.  **Draft:** Prompt the LLM to generate a "Draft Outline" ($O_D$) based *only* on the topic to get a general framework.
    2.  **Refine:** Prompt the LLM again, providing the **Topic**, the **Draft Outline**, and the **Conversation Logs** from Step 2. Ask the LLM to refine and expand the outline into a final version ($O$) based on the gathered information.

#### **Phase 2: Writing**

This phase turns the outline and references into a full article.

**Step 4: Write Full Article**
*   **Goal:** Generate text with citations.
*   **Implementation:**
    1.  Iterate through each section in the Outline ($O$).
    2.  **Retrieval:** Since the full set of references ($R$) is too large for the context window, retrieve only relevant references for the specific section. Use the section title and subsections as queries to find relevant documents in $R$ (using semantic similarity, e.g., Sentence-BERT).
    3.  **Generation:** Prompt the LLM to write the content for that section using the retrieved references. Ensure the prompt instructs the LLM to include citations.

**Step 5: Polish**
*   **Goal:** Ensure coherence.
*   **Implementation:** Concatenate the generated sections. Prompt the LLM to read the full draft to remove repetitive information and write a summary lead section.

