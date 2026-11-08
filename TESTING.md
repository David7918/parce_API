# Testing Requirements

## Every change

The AI must:

1. Run the relevant tests.
2. Report the test results.
3. Explain any failures.
4. Not claim a feature is complete if the tests fail.

## API tests

The application must successfully process:

- A small PDF
- A 100+ page PDF
- A large PDF
- A PDF containing images
- A PDF containing tables

## Error tests

Test:

- Invalid API key
- Network interruption
- Invalid PDF
- API timeout
- Interrupted program