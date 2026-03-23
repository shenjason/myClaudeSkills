---
name: readme-writer
description: |
  Generate or rewrite professional README.md files for projects by analyzing the codebase structure and researching similar projects on GitHub for inspiration. Use this skill whenever the user wants to create a README, improve an existing README, document a project, write project documentation, or asks about README best practices. Also trigger when users mention "documentation", "project description", "how to document my project", or want to make their repository more presentable. **IMPORTANT: This skill MUST also be invoked by any agent that is about to create, generate, or write a README.md file** - whether as part of a larger task (like scaffolding a new project, initializing a repository, or completing a project setup) or as a standalone action. If you are an agent and you're about to write content to a README.md file, consult this skill first.
---

# README Writer Skill

This skill helps create comprehensive, well-structured README files by:
1. Analyzing the project's structure and codebase
2. Researching similar projects on GitHub for README format inspiration
3. Generating a professional README tailored to the project type

## Workflow

### Step 1: Analyze the Project

First, understand what the project is about:

1. **Identify the project type** by examining:
   - Root directory files (package.json, requirements.txt, Cargo.toml, *.csproj, etc.)
   - Framework indicators (Unity ProjectSettings/, React src/, Django manage.py, etc.)
   - Build configuration files
   - Existing documentation

2. **Map the project structure**:
   - List key directories and their purposes
   - Identify main entry points
   - Note important configuration files
   - Find existing documentation fragments

3. **Extract project metadata**:
   - Project name from config files or directory name
   - Version information if available
   - Dependencies and their purposes
   - License type

4. **Understand the codebase**:
   - Read key source files to understand functionality
   - Identify main features and capabilities
   - Note any APIs, commands, or user-facing interfaces

### Step 2: Research Similar Projects on GitHub

Use the `read_url_content` tool to research similar projects:

1. **Construct a GitHub search URL** based on the project type:
   ```
   https://github.com/search?q=<keywords>+language:<language>&type=repositories&s=stars&o=desc
   ```
   
   Example searches by project type:
   - Unity project: `https://github.com/search?q=unity+ground+station+telemetry&type=repositories`
   - Python CLI: `https://github.com/search?q=python+cli+tool&type=repositories&s=stars`
   - React app: `https://github.com/search?q=react+dashboard&type=repositories&s=stars`

2. **Visit 2-3 top repositories** and read their README files:
   ```
   https://raw.githubusercontent.com/<owner>/<repo>/main/README.md
   ```
   or
   ```
   https://raw.githubusercontent.com/<owner>/<repo>/master/README.md
   ```

3. **Take notes on README patterns**:
   - Common sections used
   - Badge styles and placement
   - Screenshot/GIF usage
   - Installation instructions format
   - How they explain features
   - Documentation structure

### Step 3: Determine README Structure

Based on research, select appropriate sections. Not all projects need all sections.

**Essential sections** (almost always include):
- Project title with brief description
- Key features or what it does
- Installation/Setup instructions
- Basic usage

**Common sections** (include when relevant):
- Badges (build status, version, license)
- Screenshots or demo GIFs
- Prerequisites/Requirements
- Configuration
- API documentation
- Contributing guidelines
- License
- Credits/Acknowledgments

**Project-type specific sections**:
- **Libraries/Packages**: API reference, examples, changelog
- **CLI tools**: Command reference, options, examples
- **Web apps**: Live demo link, environment variables
- **Games/Unity**: Controls, gameplay, system requirements
- **Hardware/IoT**: Wiring diagrams, hardware requirements
- **Research/Academic**: Citations, methodology, results

### Step 4: Generate the README

Write the README following these principles and the structured guide below.

## How to Craft a Useful, Well-Written README

Follow this structure in order for a README masterpiece:

### 1. Strong H1 Title and H2 Subtitle
Just like writing an article or blog post, you need a great title and subtitle to attract search engines and humans. It doesn't need to be the exact name of your project, but it helps if your title includes the project name.

### 2. Intro Paragraph (What the Project Does)
Write an intro paragraph about what this project is, what it does, and how it's used. This section serves SEO purposes and keeps it simple about the value your project provides to users searching for it.

### 3. Diagram (Optional)
If necessary, add a diagram showing where this project fits and how it works. For CLI or graphical tools, add an **animated GIF** of your project in action. Even better, adding a **YouTube video demo** to your README can be very beneficial for gaining more users.

### 4. Installation and Usage Instructions (For End-Users)
If a user has gotten this far into your README, they likely want to use your project. Give clear instructions on how to install or use the tool. **Don't confuse this with contributor instructions** - this section is only about how to be a *consumer* of the project.

### 5. Installation and Usage Instructions (For Contributors)
The best part of open source? Others will want to help make it better! Give instructions on how to pull the code down and start up the tool for development purposes. This section is usually technical and may require instructions on how to build from source. Anything you can do to make the development experience easier will help you gain more contributors.

### 6. Contributor Expectations
If you're looking for contributors, set the ground rules. There's nothing worse than someone wanting to help but not knowing how! This section gives guidelines for contributions:
- Do you expect someone to create an issue first, then resolve it with a pull request?
- Do you want squashed commits?
- Do you have a pull request template?
- Explain it all here.

### 7. Known Issues
Make a brief list of known issues so people don't report bugs you already know about!

### 8. Support/Donations (Optional)
Don't be ashamed to ask for support! You put a lot of effort into this project and if someone likes it, they might throw you a few bucks. Add a link to [Buy Me a Coffee](https://www.buymeacoffee.com/) or similar platforms.

---

## Additional Writing Principles

1. **Start strong**: The first paragraph should clearly explain what the project does and why someone would use it

2. **Use visual hierarchy**:
   - Clear headings (## for main sections)
   - Bullet points for lists
   - Code blocks for commands and code
   - Tables for structured data

3. **Be concise but complete**: Provide enough detail to get started without overwhelming

4. **Include practical examples**: Show, don't just tell

5. **Consider the audience**: Match technical depth to likely users

### README Template

```markdown
# Project Name

Brief one-line description of what this project does.

![Screenshot or Demo GIF](path/to/image.png)

## Features

- **Feature 1**: Brief description
- **Feature 2**: Brief description
- **Feature 3**: Brief description

## Prerequisites

- Requirement 1 (version X.X+)
- Requirement 2

## Installation

```bash
# Clone the repository
git clone https://github.com/username/project.git

# Navigate to project directory
cd project

# Install dependencies
<install command>
```

## Usage

Explain how to use the project with examples.

```bash
# Example command
<command>
```

## Configuration

Explain any configuration options if applicable.

## Project Structure

```
project/
├── src/           # Source files
├── docs/          # Documentation
├── tests/         # Test files
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [LICENSE_TYPE] License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Credit contributors, libraries, or inspiration sources
```

### Step 5: Review and Refine

Before finalizing:

1. **Check completeness**: Can someone new to the project understand and use it?
2. **Verify accuracy**: Are paths, commands, and versions correct?
3. **Test instructions**: Would the installation steps actually work?
4. **Review formatting**: Does it render correctly in Markdown?
5. **Check links**: Are all referenced files and URLs valid?

## Tips for Specific Project Types

### Unity Projects
- Include Unity version requirement
- List any required packages from Package Manager
- Explain scene structure
- Document any custom editor tools
- Include build instructions for different platforms

### Python Projects
- Show pip/conda installation
- Document virtual environment setup
- List Python version requirements
- Include example code snippets

### Node.js/JavaScript Projects
- Include npm/yarn commands
- Document environment variables
- Show build and development commands
- Link to deployed demo if available

### Hardware/Embedded Projects
- Include wiring diagrams or schematics
- List all hardware components
- Document communication protocols
- Provide calibration instructions

## Example Research Queries

When searching GitHub, use specific keywords:

| Project Type | Search Keywords |
|-------------|-----------------|
| Ground station software | `ground station telemetry satellite` |
| Unity game | `unity game <genre>` |
| Data dashboard | `dashboard visualization <framework>` |
| CLI tool | `cli tool <language> <purpose>` |
| API wrapper | `api wrapper <service> <language>` |

## Output

After completing the analysis and research, present the user with:
1. A summary of what you learned about the project
2. The README sections you recommend including
3. The complete README.md content

Ask if they want any modifications before finalizing.
