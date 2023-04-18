Feature: Ingest Notion page

    Scenario: Fail to query without the correct API Key
        Given an index named "sapientone-test"
        When the user queries with the "incorrect" API Key to ingest the "identity" Notion Page
        Then the request returns http code "401"

    Scenario: Add text and metadata to an existing index
        Given an index named "sapientone-test"
        When the user queries with the "correct" API Key to ingest the "identity" Notion Page
        Then the request returns http code "200"
        When the user asks "What did I study?" with the "correct" API Key
        Then the question "What did I study?" contains "Philosophy"
