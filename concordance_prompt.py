# concordance_prompt.py

PROMPT_TEMPLATE = (
    "Given the question, human answer, and AI output, respond ONLY in the following JSON format: "
    '{{"concordant": 1 or 0, "helpful": 1 or 0, "explanation": "your explanation here"}}\n'
    "Is the human answer concordant with the AI output? 1 for concordant, 0 for discordant. "
    "Is the human answer helpful in answering the question? 1 for helpful, 0 for not helpful. "
    "Provide a 2-3 sentence explanation.\n"
    "\n"
    "Here are two examples of how to answer:\n"
    "\n"
    "EXAMPLE 1\n"
    "Question: \"I am requesting an eConsult from Hematology for VTE/Thrombophilia. <<AGE>> yo F w/ history of class III obesity, agoraphobia, LLE DVT, factor V leiden mutation and Afib on Warfarin.Patient is very sedentary due to obesity and at high risk for recurrent DVT. I am wondering if it would be reasonable to try a different anticoagulant as opposed to warfarin, or If warfarin is the best in this case? There is a mention in her chart of MVP, but her last TTE did not make any mention of MVP.\"\n"
    "Answer A: \"In this patient, direct oral anticoagulants (DOACs) are generally preferred over warfarin for atrial fibrillation (AF) without significant valvular disease, due to lower bleeding risk and no need for routine INR monitoring ...\"\n"
    "Answer B: \"Recommendation and Rationale: 1) It is reasonable to consider whether indefinite full-dose anticoagulation is indeed 'axiomatic' for this patient. ...\"\n"
    "Concordance: 1\n"
    "Helpfulness: 0\n"
    "Thoughts: The answers are similar but the LLM answer is more vague and then goes into a lot of unnecessary information which is already provided in the patient history whereas the physician answer is more direct\n"
    "\n"
    "EXAMPLE 2\n"
    "Question: \"Could a high copper level be the cause for tingling/neuropathy?\"\n"
    "Answer A: \"Yes, high copper levels can cause tingling and neuropathy. Copper is essential for nerve function, but excessive copper can lead to neurological symptoms due to its role in oxidative stress and nerve damage ...\"\n"
    "Answer B: \"Recommendation and Rationale: 03/01/2024 note reports symptoms of tingling in her left arm as well as burning in her right lower extremity ...\"\n"
    "Concordance: 0\n"
    "Helpfulness: 0\n"
    "Thoughts: The specialist is saying copper deficiency could cause the symptoms and not excess whereas the LLM is suggesting the copper excess could cause it and taking the patient down the copper workup\n"
    "\n"
    "Now, answer for the following input:\n"
    "Question: {question}\n"
    "Answer A: {answer}\n"
    "Answer B: {ai_output}"
)

def make_concordance_prompt(question, answer, ai_output):
    return PROMPT_TEMPLATE.format(question=question, answer=answer, ai_output=ai_output) 