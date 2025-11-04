# GitHub Workflows Setup

The GitHub workflows for CI/CD could not be pushed automatically due to GitHub App permissions restrictions. You'll need to add them manually.

## Workflow Files

The workflow templates are located in the `.workflows-templates/` directory:

1. **test.yml** - CI testing workflow
   - Runs tests across Python 3.9-3.13
   - Tests on Ubuntu, Windows, and macOS
   - Runs linting, type checking, and tests
   - Uploads coverage to Codecov

2. **release.yml** - Automated versioning and release workflow
   - Triggers on push to main or manual dispatch
   - Automatically bumps version based on commit messages
   - Creates GitHub releases with changelog
   - Builds distribution packages

3. **publish.yml** - PyPI publishing workflow
   - Triggers on GitHub releases
   - Publishes package to PyPI
   - Supports TestPyPI for testing

## How to Add Workflows

### Option 1: Via Git (Requires workflow permissions)

```bash
# Copy templates to workflows directory
cp .workflows-templates/* .github/workflows/

# Commit and push
git add .github/workflows/
git commit -m "chore: add GitHub Actions workflows"
git push
```

### Option 2: Via GitHub UI

1. Go to your repository on GitHub
2. Navigate to `.github/workflows/` or create the directory
3. For each workflow file in `.workflows-templates/`:
   - Click "Add file" > "Create new file"
   - Name it appropriately (e.g., `test.yml`)
   - Copy the content from the template file
   - Commit directly to your branch

### Option 3: Via GitHub CLI

```bash
# Copy templates
cp .workflows-templates/* .github/workflows/

# Use gh to push (if you have the CLI configured)
gh workflow sync
```

## Required GitHub Secrets

Before the workflows can run successfully, add these secrets to your GitHub repository:

1. Go to Settings > Secrets and variables > Actions
2. Add the following secrets:

- `PYPI_API_TOKEN` - Your PyPI API token for publishing
  - Get from: https://pypi.org/manage/account/token/

- `TEST_PYPI_API_TOKEN` - (Optional) TestPyPI token for testing
  - Get from: https://test.pypi.org/manage/account/token/

- `CODECOV_TOKEN` - (Optional) For coverage reporting
  - Get from: https://codecov.io/

## Testing Workflows Locally

You can test the workflows locally using [act](https://github.com/nektos/act):

```bash
# Install act
# See: https://github.com/nektos/act#installation

# Test the test workflow
act -W .workflows-templates/test.yml

# Test the build
act -W .workflows-templates/release.yml
```

## Workflow Triggers

- **test.yml**: Runs on push and pull requests to main/develop
- **release.yml**: Runs on push to main or manual workflow dispatch
- **publish.yml**: Runs when a GitHub release is published

## Next Steps

1. Add the workflow files to `.github/workflows/` using one of the methods above
2. Configure the required secrets in your GitHub repository
3. Push code to trigger the test workflow
4. Use the release workflow to create versioned releases
5. Releases will automatically publish to PyPI

## Notes

- The workflows use `uv` for fast dependency management
- Version bumping is automated based on conventional commits
- The package will be tested on multiple Python versions (3.9-3.13)
- Cross-platform testing ensures compatibility
