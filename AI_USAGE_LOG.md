# AI Usage Log

We expect you to use AI tools. We are not testing whether you can avoid them — we are
testing whether you understand and own what you ship. Fill this in honestly as you work.
A thin or evasive log is a worse signal than heavy, well-understood AI use.

---

## 1. Where did you use AI?

For each significant use, give: what you asked, what it produced, and what you changed or
rejected and why.

- I used AI to understand the task brief in simpler language and break the project into smaller steps. This helped me understand the overall pipeline stages before writing code.
- I used AI for starter code structure for ingestion, cleaning, deduplication, enrichment, scoring, and output generation. I then pasted, ran, checked errors, and adjusted the code step by step while building the project.
- I used AI to understand Python syntax and concepts I was not fully comfortable with, such as `if __name__ == "__main__"`, file reading with `open(...)`, API calls, retry logic, and markdown formatting for README.
- I also used AI to help draft README content, architecture documentation, and this AI usage log.


## 2. What did you NOT understand at first, and how did you resolve it?

- At first, I did not clearly understand what a pipeline project meant. I understood it later as a step-by-step data processing system where messy input goes through cleaning, grouping, enrichment, scoring, and final output.
- I was also confused about what the mock API meant and how my code should interact with it. I resolved this by understanding that it acts like a fake third-party service that returns extra company data based on a domain.
- I also did not understand some Python syntax and markdown formatting at first. I resolved this by asking for simpler explanations and then testing the code and files directly in the project.

## 3. One decision you made against what the AI suggested

What did it recommend, what did you do instead, and why?

-- AI guidance often focused on adding more features step by step, but I chose to keep the duplicate resolution logic simple by grouping mainly on cleaned domains instead of trying to add more advanced fuzzy matching. I did this because domain-based grouping was easier to defend, less risky, and more manageable for the current stage of the task.

## 4. If your reviewer asked "why this approach?" about the hardest part of your
##    pipeline, what would you say — in your own words?

-- The hardest part of the pipeline was handling messy data together with enrichment failures. I chose a simple stage-based design so that each part of the pipeline was easier to understand, debug, and explain. I used cleaned domains as the main duplicate grouping rule because domains are more stable than company names. For enrichment, I added retry handling because the mock API is intentionally unreliable, and I wanted the pipeline to continue working even when temporary errors happened. I also saved intermediate stage outputs so I could inspect the results of each step separately.
