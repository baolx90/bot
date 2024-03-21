You are able to reason from previous conversation and the recent question, to come up with a rewrite of the question which is concise but with enough information that people without knowledge of previous conversation can understand the question.

## Previous conversation
{% for item in history %}
{{item["role"]}}: {{item["content"]}}
{% endfor %}
## Question
{{question}}
## Rewritten question