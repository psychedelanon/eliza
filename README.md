# Eliza

A framework for multi-agent development and deployment

## ✨ Features

- 🛠️ Full-featured Discord, X (Twitter) and Telegram connectors (and many more!)
- 🔗 Support for every model (Llama, Grok, OpenAI, Anthropic, Gemini, etc.)
- 🎨 Modern and professional UI with a redesigned dashboard for managing agents and groups.
- 💬 Robust real-time communication with enhanced channel and message handling.
- 👥 Multi-agent and group support with intuitive management.
- 📚 Easily ingest and interact with your documents.
- 💾 Retrievable memory and document store.
- 🚀 Highly extensible - create your own actions and clients.
- 📦 Just works!

## Video Tutorials

[AI Agent Dev School](https://www.youtube.com/watch?v=ArptLpQiKfI&list=PLx5pnFXdPTRzWla0RaOxALTSTnVq53fKL)

## 🎯 Use Cases

- 🤖 Chatbots
- 🕵️ Autonomous Agents
- 📈 Business Process Handling
- 🎮 Video Game NPCs
- 🧠 Trading

## 🚀 Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) (v18 or higher recommended)
- [bun](https://bun.sh/docs/installation)

> **Note for Windows Users:** [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install-manual) is required.

### Use the Starter (Recommended)

```bash
git clone https://github.com/elizaos/eliza-starter.git
cd eliza-starter
cp .env.example .env
bun i && bun run build && bun start
```

### Manually Start Eliza (Only recommended if you know what you are doing)

#### Prerequisites

- **Node.js** (v18+ recommended)
- **bun** (for CLI and dependencies)
- **bats** (shell test runner, install globally via npm or bun)
- **git** (for project/plugin tests)

#### Install Bats (Test Runner)

You need the [bats-core](https://github.com/bats-core/bats-core) test runner for shell tests.

To install globally:

```bash
npm install -g bats
# or, if you use bun:
bun add -g bats
```

#### Checkout the latest release

```bash
# Clone the repository
git clone https://github.com/elizaos/eliza.git

# This project iterates fast, so we recommend checking out the latest release
git checkout $(git describe --tags --abbrev=0)
# If the above doesn't checkout the latest release, this should work:
# git checkout $(git describe --tags `git rev-list --tags --max-count=1`)
```

#### Edit the .env file

Copy .env.example to .env and fill in the appropriate values.

```
cp .env.example .env
```

Note: .env is optional. If you're planning to run multiple distinct agents, you can pass secrets through the character JSON

#### Install Python Dependencies

Some features, including the scheduler and Python-based tests, require additional Python packages such as `APScheduler`. Install them with:

```bash
pip install -r requirements.txt
```

This includes the optional Quickfire generation library provided by the
[blacksmith-forge](https://github.com/psychedelanon/blacksmith-forge) project.

You can also run the `setup.sh` script, which installs both Node dependencies (including `turbo`) and these Python requirements:

```bash
bash setup.sh
```

#### Start Eliza

Important! We now use Bun. If you are using npm, you will need to install Bun:
https://bun.sh/docs/installation

```bash
bun install
bun run build # npm will work too
bun start # npm will work too
```

### Interact via Browser

Once Eliza is running, access the modern web interface at http://localhost:3000. It has been professionally redesigned and features:

- A welcoming dashboard with a gradient hero section and clear calls-to-action for creating agents and groups.
- Visually enhanced cards for managing agents and groups, including status indicators and member counts.
- Real-time chat capabilities with your agents.
- Character configuration options.
- Plugin management.
- Comprehensive memory and conversation history.
- Responsive design for an optimal experience on various screen sizes.

### OpenTelemetry Instrumentation (Optional)

Eliza supports OpenTelemetry for tracing and monitoring agent behavior. This allows you to gain insights into the performance and execution flow of your agents.

**Enabling Instrumentation:**

Set the following environment variable:

```bash
INSTRUMENTATION_ENABLED=true
```

When enabled, Eliza will:

- Initialize an OpenTelemetry tracer.
- Automatically trace key operations within the core `AgentRuntime` and supported plugins (e.g., the `plugin-openai`).

**Service Name:**

The default service name for traces will be `agent-<character_name>-<agent_id>`.

**PostgreSQL Exporter Setup (Example):**

If you plan to export traces to a PostgreSQL database (e.g., using a compatible OpenTelemetry exporter), you can start a local instance using Docker:

```bash
docker run -d --name postgres-tracing -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=eliza_tracing postgres:15
```

You will also need to configure the connection URL via the following environment variable, adjusting it based on your database setup:

```bash
INSTRUMENTATION_ENABLED=true
POSTGRES_URL_INSTRUMENTATION="postgresql://postgres:postgres@localhost:5432/eliza_tracing"
```

### Quickfire Hashtags

You can override the default hashtags used by the `quickfire` helper by setting
the `AQUA_HASHTAGS` environment variable:

```bash
export AQUA_HASHTAGS="#Foo,#Bar,#Baz"
```

If provided, these comma-separated tags will be chosen instead of the built in
defaults.

### Metrics

Set `METRICS_PORT` to expose Prometheus metrics at `/metrics`. The default port
is `8000`.

### Launching the Gremlin Swarm

Run the coordinated hype agents in dry-run mode:

```bash
python run.py --agent AgentLoreMaster,AgentHypeBeast,AgentCynical,AgentSage --dry-run
```

## 🚀 Swarm Quality Boost

The Eliza swarm now features **Swarm Quality Boost** - an enhanced system for generating high-signal, cross-amplifying content with smart engagement patterns.

### Features

- **Smart Post Generation**: Persona-specific content with proper hashtags, emojis, and mentions
- **Quality Validation**: Ensures posts meet length, content, and engagement standards
- **Adaptive Cross-Engagement**: Persona-specific engagement patterns (likes, replies, quotes)
- **Event-Driven Content**: Hot token events trigger topical posts
- **Quality Gates**: Automatic validation and scoring of all posts

### Quick Test

Test the enhanced swarm with high-quality content generation:

```bash
# Run the enhanced swarm in demo mode
python run.py --swarm --dry-run --demo

# This will generate:
# - LoreMaster: Mythic lore posts with dramatic tone
# - MemeLord: Viral meme content with humor
# - AlphaScry: Market insights and trading wisdom
# - GremlinGM: Chaotic gaming hype content
# - SwarmCoordinator: Hot token event generation
```

### Quality Validation

All posts are automatically validated for:

- Length (140-240 characters)
- Required hashtags (#HarryPotterObamaSonic10Inu, $BITCOIN)
- Emoji presence
- Spam detection
- Cross-engagement mentions

### Persona Engagement Styles

Each persona has unique engagement patterns:

- **LoreMaster**: 20% quote, 50% reply, 30% like
- **MemeLord**: 60% reply, 40% like
- **AlphaScry**: 70% reply, 30% quote
- **GremlinGM**: 80% reply, 20% like

### Testing

Run comprehensive tests for the quality system:

```bash
# Test quality validation
python -m pytest tests/test_quality.py -v

# Test cross-engagement patterns
python -m pytest tests/test_cross_style.py -v

# Quick functionality test
python simple_test.py
```

---

### Automatically Start Eliza

The start script provides an automated way to set up and run Eliza:

## Citation

We now have a [paper](https://arxiv.org/pdf/2501.06781) you can cite for the Eliza OS:

```bibtex
@article{walters2025eliza,
  title={Eliza: A Web3 friendly AI Agent Operating System},
  author={Walters, Shaw and Gao, Sam and Nerd, Shakker and Da, Feng and Williams, Warren and Meng, Ting-Chien and Han, Hunter and He, Frank and Zhang, Allen and Wu, Ming and others},
  journal={arXiv preprint arXiv:2501.06781},
  year={2025}
}
```

## Contributors

<a href="https://github.com/elizaos/eliza/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=elizaos/eliza" alt="Eliza project contributors" />
</a>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=elizaos/eliza&type=Date)](https://star-history.com/#elizaos/eliza&Date)

## Git Hooks

This project uses git hooks to ensure code quality:

- **pre-commit**: Automatically formats staged files using Prettier before committing

To run the pre-commit hook manually:

```bash
bun run pre-commit
```

## 📂 Repository Structure

Eliza is organized as a monorepo using Bun, Lerna, and Turbo for efficient package management and build orchestration. Here's a detailed overview of the project structure:

- **`/` (Root)**:

  - `.github/`: GitHub Actions workflows for CI/CD pipelines and issue templates
  - `.husky/`: Git hooks configuration, including pre-commit formatting
  - `.devcontainer/`: Development container configurations for consistent environments
  - `packages/`: Core packages and modules (detailed below)
  - `scripts/`: Build, development, and utility scripts
  - `data/`: Application and user data storage
  - `AGENTS.md`: Comprehensive agent documentation and specifications
  - `CHANGELOG.md`: Detailed version history and changes
  - `Dockerfile`, `docker-compose.yaml`: Container configurations for deployment
  - `lerna.json`, `package.json`, `turbo.json`: Monorepo configuration and workspace definitions

- **`/packages/`**: Core components of the Eliza framework:
  - `core/`: The foundational package (@elizaos/core) implementing:
    - OpenTelemetry instrumentation for tracing and monitoring
    - LangChain integration for AI model interactions
    - PDF processing capabilities
    - Logging and error handling infrastructure
  - `app/`: Tauri-based cross-platform application (@elizaos/app)
    - React-based UI implementation
    - Tauri plugins for system integration
    - Desktop and mobile builds support
  - `autodoc/`: Documentation automation tool (@elizaos/autodoc)
    - LangChain-powered documentation generation
    - TypeScript parsing and analysis
    - GitHub integration via Octokit
  - `cli/`: Command-line interface for Eliza management
  - `client/`: Client libraries for web interfaces
  - `create-eliza/`: Project scaffolding tool
  - `docs/`: Official documentation source files
  - `plugin-bootstrap/`: Core agent initialization (@elizaos/plugin-bootstrap)
    - Provides fundamental agent actions (reply, follow/unfollow, mute/unmute)
    - Implements core evaluators and providers
    - Handles message processing and world events
  - `plugin-sql/`: Database integration (@elizaos/plugin-sql)
    - PostgreSQL integration with PGLite support
    - Drizzle ORM for type-safe queries
    - Migration management tools
    - Integration testing support
  - `plugin-starter/`: Template for creating new plugins
  - `project-starter/`, `project-tee-starter/`: Project templates

This architecture enables modular development, clear separation of concerns, and scalable feature implementation across the Eliza ecosystem.

## Tauri Application CI/CD and Signing

The Eliza application, built with Tauri and located in `packages/app`, is configured for cross-platform continuous integration and deployment. This setup automates the building and releasing of the application for various operating systems.

### Overview

The Tauri application is designed to be built for:

- Desktop: Linux, macOS, and Windows.
- Mobile: Android and iOS.

### CI/CD Workflows

Two main GitHub Actions workflows handle the CI/CD process for the Tauri application:

- **`tauri-ci.yml`**:

  - Triggered on pushes to `main` and `develop` branches.
  - Performs debug builds of the desktop application (Linux, macOS, Windows) to ensure code integrity and catch build issues early.

- **`tauri-release.yml`**:
  - Triggered when new tags (e.g., `v*`) are pushed or when a new release is created/published on GitHub.
  - Builds release-ready versions of the application for all supported desktop platforms (Linux AppImage & .deb, macOS .dmg, Windows .exe NSIS installer).
  - Builds release versions for mobile platforms (Android .apk, iOS .ipa).
  - Uploads all generated binaries and installers as artifacts to the corresponding GitHub Release.

### Mobile Application Backend

The mobile versions of the Eliza Tauri application (Android and iOS) are configured to connect to an external backend service hosted at `https://api.eliza.how`. This connection is essential for certain functionalities of the mobile app.

The Content Security Policy (CSP) in `packages/app/src-tauri/tauri.conf.json` has been updated to allow `connect-src` directives to this specific domain, ensuring that the mobile app can securely communicate with its backend.

### Application Signing (Important for Releases)

For the `tauri-release.yml` workflow to produce _signed_ and deployable mobile applications suitable for app stores or distribution, specific secrets must be configured in the GitHub repository settings (`Settings > Secrets and variables > Actions`).

**Android Signing Secrets:**

- `ANDROID_KEYSTORE_BASE64`: Base64 encoded content of your Java Keystore file (`.jks` or `.keystore`).
- `ANDROID_KEYSTORE_ALIAS`: The alias of your key within the keystore.
- `ANDROID_KEYSTORE_PRIVATE_KEY_PASSWORD`: The password for the private key associated with the alias.
- `ANDROID_KEYSTORE_PASSWORD`: The password for the keystore file itself.

> **Note**: The CI workflow currently includes a step to generate a dummy, unsigned keystore for Android if these secrets are not provided. This allows the release build to complete and produce an unsigned APK, but this APK cannot be published to app stores. For official releases, providing the actual signing credentials via these secrets is crucial.

**iOS Signing Secrets:**

- `APPLE_DEVELOPMENT_CERTIFICATE_P12_BASE64`: Base64 encoded content of your Apple Distribution Certificate (`.p12` file).
- `APPLE_CERTIFICATE_PASSWORD`: The password used to encrypt the `.p12` certificate file.
- `APPLE_PROVISIONING_PROFILE_BASE64`: Base64 encoded content of your Distribution Provisioning Profile (`.mobileprovision` file).
- `APPLE_DEVELOPMENT_TEAM`: Your Apple Developer Team ID (e.g., `A1B2C3D4E5`).

> **Note**: The CI workflow currently includes placeholder steps for setting up the Apple development environment and signing for iOS. These steps will require the above secrets to be populated. If these secrets are not provided and the signing steps are made active (by uncommenting them in the workflow), the iOS build will likely fail.

### Artifacts

Upon successful completion of the `tauri-release.yml` workflow (triggered by a new tag/release), all compiled application installers and mobile packages will be available as downloadable artifacts on the GitHub Releases page for that specific tag. This includes:

- Linux: `.AppImage` and `.deb` files.
- macOS: `.dmg` file.
- Windows: `.exe` NSIS installer.
- Android: `.apk` file.
- iOS: `.ipa` file.

## Usage

# dry‑run all gremlins

python run.py --agent Agent3,Agent4,Agent5,Agent6 --once --dry-run

### Engage CLI

Use the `eliza engage` command to coordinate bot accounts for public engagement on a target tweet.

```
eliza engage --tweet https://twitter.com/Someone/status/1234567890 --likes BotA,BotB --dry-run
```

Set `TWITTER_<ACCOUNT>_API_KEY`, `TWITTER_<ACCOUNT>_API_SECRET`, `TWITTER_<ACCOUNT>_ACCESS_TOKEN`, and `TWITTER_<ACCOUNT>_ACCESS_SECRET` for each account.

Only operate clearly disclosed bot accounts and follow all Twitter Rules.
