
# Resume Builder: Multi-Agent ATS Optimization

This project uses a multi-agent system powered by LLMs to iteratively optimize your resume for a specific job description, ensuring a high ATS (Applicant Tracking System) score.

## 1. Download & Clone

Clone the repository and navigate to the project root:

```bash
git clone <repo-url>
cd ats-llm-resume-builder
```

## 2. Python Environment Setup

Create and activate a virtual environment (recommended):

```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

## 3. Install Dependencies

Install required Python packages:

```bash
pip install -r ./requirements.txt
```

## 4. Environment Variables

Create a `.env` file in the project root with your OpenAI or Azure OpenAI credentials. Example for Azure OpenAI:

```env
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://<your-resource-name>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## 5. Prepare Input Files

- Place your resume in Markdown format at `./docs/resume.md`.
- Place the job description at `./docs/sample/job-description.md` (or update the script to point to your file).

### Sample Files

The project includes sample files in both English and Dutch:

**English samples:**
- Resume: `./docs/resume.md`
- Job Description: `./docs/sample/job-description.md`

**Dutch samples:**
- Resume: `./docs/sample/resume-nl.md`
- Job Description: `./docs/sample/job-description-nl.md`

To test with Dutch samples:
```bash
python ./src/resume-builder.py --resume ./docs/sample/resume-nl.md --jobdesc ./docs/sample/job-description-nl.md --language nl
```

## 6. Run the Script

From the project root, you can run the script with default input files:

```bash
python ./src/resume-builder.py
```


Or specify custom input and output files using command-line arguments:

```bash
python ./src/resume-builder.py --resume path/to/your-resume.md --jobdesc path/to/job-description.md --output path/to/output-conversation.md --language en
```

Arguments:

- `--resume` : Path to the resume markdown file (default: `./docs/resume.md`)
- `--jobdesc` : Path to the job description markdown file (default: `./docs/sample/job-description.md`)
- `--output` : Path to the output conversation markdown file (default: `./docs/entire-conversation.md`)
- `--language` : Language for resume generation - `en` for English (default) or `nl` for Dutch

## Language Support

The application supports generating resumes in two languages:

- **English** (`--language en`) - Default language
- **Dutch** (`--language nl`) - All agent communications and the generated resume will be in Dutch

Example for Dutch resume generation:

```bash
python ./src/resume-builder.py --language nl
```

When using Dutch mode, all agents will:
- Analyze the job description and provide feedback in Dutch
- Generate the resume content in Dutch
- Provide all communications and scoring analysis in Dutch


## 7. Output

- The optimized resume and the full agent conversation will be saved to the file specified by `--output` (default: `./docs/entire-conversation.md`).
- Review this file for the final result and the reasoning process.

## Troubleshooting

- If you see errors about missing environment variables, check your `.env` file.
- If you get import errors, ensure your `PYTHONPATH` includes the project root.
- For Azure OpenAI, ensure your API version, endpoint, and deployment are correct and active.

## Notes

- All dependencies are listed in `src/requirements.txt`.
- You can customize agent instructions in `src/resume-builder.py`.
- For best results, use well-formatted Markdown for your resume and job description.
