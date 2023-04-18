Feature: Ingest text

    Scenario: Fail to query without the correct API Key
        Given an index named "sapientone-test"
        When the user queries with the "incorrect" API Key to add "My favourite pizza is The Viennese"
        Then the request returns http code "401"

    Scenario: Add text and metadata to an existing index
        Given an index named "sapientone-test"
        When the user queries with the "correct" API Key to add "My favourite pizza is The Viennese"
        Then the request returns http code "200"
        When the user asks "What is my favourite pizza?" with the "correct" API Key
        Then the question "What is my favourite pizza?" contains "Viennese"

    Scenario: Add text and metadata to a new index
        Given an index named "sapientone-new" doesn't exist
        When the user queries with the "correct" API Key to add "My favourite pizza is The Viennese"
        Then the request returns http code "201"
        When the user asks "What is my favourite pizza?" with the "correct" API Key
        Then the question "What is my favourite pizza?" contains "Viennese"
