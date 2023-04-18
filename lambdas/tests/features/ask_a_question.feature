Feature: Ask a question

    Scenario: Unauthenticated users can't ask questions
        Given an index named "sapientone-test"
        When the user asks "What is my favourite pizza?" with the "incorrect" API Key
        Then the request returns http code "401"

    Scenario: Authenticated users can ask questions
        Given an index named "sapientone-test"
        And the index contains the text "My favourite pizza is the Viennese"
        When the user asks "What is my favourite pizza?" with the "correct" API Key
        Then the request returns http code "200"
        And the question "What is my favourite pizza?" contains "Viennese"
