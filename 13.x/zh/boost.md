# Laravel Boost

- [简介](#introduction)
- [安装](#installation)
    - [配置智能体](#set-up-your-agents)
    - [保持 Boost 资源更新](#keeping-boost-resources-updated)
- [MCP 服务器](#mcp-server)
    - [可用的 MCP 工具](#available-mcp-tools)
    - [手动注册 MCP 服务器](#manually-registering-the-mcp-server)
- [AI 指南](#ai-guidelines)
    - [可用的 AI 指南](#available-ai-guidelines)
    - [添加自定义 AI 指南](#adding-custom-ai-guidelines)
    - [覆盖 Boost AI 指南](#overriding-boost-ai-guidelines)
    - [第三方扩展包的 AI 指南](#third-party-package-ai-guidelines)
- [智能体技能](#agent-skills)
    - [可用的技能](#available-skills)
    - [自定义技能](#custom-skills)
    - [覆盖技能](#overriding-skills)
    - [第三方扩展包的技能](#third-party-package-skills)
- [指南与技能](#guidelines-vs-skills)
- [项目规则](#project-rules)
    - [记录规则](#recording-rules)
    - [推断应用的约定](#inferring-your-applications-conventions)
    - [禁用项目规则](#disabling-project-rules)
- [文档 API](#documentation-api)
- [扩展 Boost](#extending-boost)
    - [添加对其他 IDE / AI 智能体的支持](#adding-support-for-other-ides-ai-agents)

<a name="introduction"></a>
## 简介

Laravel Boost 通过提供必要的指南和智能体技能，加快 AI 辅助开发，帮助 AI 智能体编写遵循 Laravel 最佳实践的高质量 Laravel 应用。

Boost 还提供强大的 Laravel 生态系统文档 API，将内置 MCP 工具与包含超过 17,000 条 Laravel 专属信息的庞大知识库相结合。该 API 利用嵌入向量进行语义搜索，提供精确且符合上下文的结果。Boost 会指导 Claude Code、Cursor 等 AI 智能体使用此 API，了解 Laravel 的最新功能和最佳实践。

<a name="installation"></a>
## 安装

你可以通过 Composer 安装 Laravel Boost：

```shell
composer require laravel/boost --dev
```

接下来，安装 MCP 服务器和编码指南：

```shell
php artisan boost:install
```

`boost:install` 命令会为安装过程中所选的编码智能体生成相应的智能体指南和技能文件。如果 `CLAUDE.md` 或 `AGENTS.md` 等指南文件已存在，Boost 只会替换其 `<laravel-boost-guidelines>` 区块内的内容，区块外由你编写的内容会被保留。

安装 Laravel Boost 后，你就可以开始使用 Cursor、Claude Code 或其他喜欢的 AI 智能体编写代码了。

> [!NOTE]
> 你可以将生成的 MCP 配置文件（`.mcp.json`）、指南文件（`CLAUDE.md`、`AGENTS.md`、`junie/` 等）以及 `boost.json` 配置文件添加到应用的 `.gitignore` 中，因为运行 `boost:install` 和 `boost:update` 时会自动重新生成这些文件。

<a name="set-up-your-agents"></a>
### 配置智能体

```text tab=Cursor
1. 打开命令面板（`Cmd+Shift+P` 或 `Ctrl+Shift+P`）
2. 在「/open MCP Settings」上按 `enter`
3. 打开 `laravel-boost` 的开关
```

```text tab=Claude Code
Claude Code 支持通常会自动启用。如果未启用，请在项目目录中打开终端，并运行以下命令：

claude mcp add -s local -t stdio laravel-boost php artisan boost:mcp
```

```text tab=Codex
Codex 支持通常会自动启用。如果未启用，请在项目目录中打开终端，并运行以下命令：

codex mcp add laravel-boost -- php "artisan" "boost:mcp"
```

```text tab=GitHub Copilot (VS Code)
1. 打开命令面板（`Cmd+Shift+P` 或 `Ctrl+Shift+P`）
2. 在「MCP: List Servers」上按 `enter`
3. 使用方向键选择 `laravel-boost`，然后按 `enter`
4. 选择「Start server」
```

```text tab=Junie
1. 连按两次 `shift`，打开命令面板
2. 搜索「MCP Settings」，然后按 `enter`
3. 勾选 `laravel-boost` 旁的复选框
4. 点击右下角的「Apply」
```

<a name="keeping-boost-resources-updated"></a>
### 保持 Boost 资源更新

你可能需要定期更新本地 Boost 资源（AI 指南和技能），使其与已安装的 Laravel 生态系统扩展包的最新版本保持一致。为此，可以使用 `boost:update` Artisan 命令。

```shell
php artisan boost:update
```

你也可以将此命令添加到 Composer 的「post-update-cmd」脚本中，自动执行更新：

```json
{
  "scripts": {
    "post-update-cmd": [
      "@php artisan boost:update --ansi"
    ]
  }
}
```

默认情况下，`boost:update` 命令还会扫描应用中新安装的扩展包，并提示你发布相应的指南和技能。当命令以非交互方式运行时（例如在 Composer 脚本中），会跳过此提示。如果你只想更新应用中已经发布的 Boost 资源，可以使用 `--no-discover` 选项：

```shell
php artisan boost:update --no-discover
```

<a name="mcp-server"></a>
## MCP 服务器

Laravel Boost 提供一个 MCP（模型上下文协议）服务器，向 AI 智能体开放用于与你的 Laravel 应用交互的工具。这些工具让智能体能够检查应用结构、查询数据库、执行代码等。

<a name="available-mcp-tools"></a>
### 可用的 MCP 工具

<div class="overflow-auto" markdown="1">

| 名称 | 说明 |
| -------------------- | ----------------------------------------------------------------------------------------------------------- |
| Application Info | 读取 PHP 和 Laravel 版本、数据库引擎、生态系统扩展包及其版本列表，以及 Eloquent 模型 |
| Browser Logs | 读取浏览器日志和错误 |
| Database Connections | 检查可用的数据库连接，包括默认连接 |
| Database Query | 对数据库执行查询 |
| Database Schema | 读取数据库结构 |
| Get Absolute URL | 将相对路径 URI 转换为绝对路径，让智能体生成有效的 URL |
| Last Error | 读取应用日志文件中的最后一个错误 |
| Read Log Entries | 读取最近 N 条日志 |
| Record Rule | 将持久保存的[项目规则](#project-rules)记录到 `.ai/rules` 中，供后续智能体沿用 |
| Search Docs | 查询 Laravel 托管的文档 API 服务，根据已安装的扩展包检索文档 |

</div>

<a name="manually-registering-the-mcp-server"></a>
### 手动注册 MCP 服务器

有时，你可能需要在所用的编辑器中手动注册 Laravel Boost MCP 服务器。请使用以下信息注册：

<table>
<tr><td><strong>命令</strong></td><td><code>php</code></td></tr>
<tr><td><strong>参数</strong></td><td><code>artisan boost:mcp</code></td></tr>
</table>

JSON 示例：

```json
{
    "mcpServers": {
        "laravel-boost": {
            "command": "php",
            "args": ["artisan", "boost:mcp"]
        }
    }
}
```

<a name="ai-guidelines"></a>
## AI 指南

AI 指南是可组合的指令文件，会预先加载，为 AI 智能体提供有关 Laravel 生态系统扩展包的必要上下文。这些指南包含核心约定、最佳实践和框架特有的模式，帮助智能体生成一致、高质量的代码。

<a name="available-ai-guidelines"></a>
### 可用的 AI 指南

Laravel Boost 为以下扩展包和框架提供 AI 指南。`core` 指南为 AI 提供适用于该扩展包所有版本的通用建议。

<div class="overflow-auto" markdown="1">

| 扩展包 | 支持的版本 |
| ----------------- | ---------------------- |
| Core & Boost      | core                   |
| Laravel Framework | core, 10.x, 11.x, 12.x, 13.x |
| Livewire          | core, 2.x, 3.x, 4.x    |
| Flux UI           | core, free, pro        |
| Folio             | core                   |
| Herd              | core                   |
| Inertia Laravel   | core, 1.x, 2.x, 3.x    |
| Inertia React     | core, 1.x, 2.x, 3.x    |
| Inertia Vue       | core, 1.x, 2.x, 3.x    |
| Inertia Svelte    | core, 1.x, 2.x, 3.x    |
| MCP               | core                   |
| Pennant           | core                   |
| Pest              | core, 3.x, 4.x         |
| PHPUnit           | core                   |
| Pint              | core                   |
| Sail              | core                   |
| Tailwind CSS      | core, 3.x, 4.x         |
| Livewire Volt     | core                   |
| Wayfinder         | core                   |
| Enforce Tests     | conditional            |

</div>

> **注意：**要保持 AI 指南更新，请参阅[保持 Boost 资源更新](#keeping-boost-resources-updated)一节。

<a name="adding-custom-ai-guidelines"></a>
### 添加自定义 AI 指南

要为 Laravel Boost 添加自定义 AI 指南，请在应用的 `.ai/guidelines/*` 目录中添加 `.blade.php` 或 `.md` 文件。运行 `boost:install` 时，这些文件会自动包含在 Laravel Boost 的指南中。

<a name="overriding-boost-ai-guidelines"></a>
### 覆盖 Boost AI 指南

你可以创建路径与现有 Boost 指南相同的自定义指南，覆盖 Boost 的内置指南。当自定义指南的文件路径与某个内置指南匹配时，Boost 会使用你的自定义版本。

例如，要覆盖 Boost 的「Inertia React v2 表单指南」，请创建 `.ai/guidelines/inertia-react/2/forms.blade.php` 文件。运行 `boost:install` 时，Boost 会使用你的自定义指南替代默认指南。

<a name="third-party-package-ai-guidelines"></a>
### 第三方扩展包的 AI 指南

如果你维护第三方扩展包，并希望 Boost 为其提供 AI 指南，可以在扩展包中添加 `resources/boost/guidelines/core.blade.php` 文件。当扩展包用户运行 `php artisan boost:install` 时，Boost 会自动加载你的指南。

AI 指南应简要介绍扩展包的用途，概述所需的文件结构或约定，并说明如何创建或使用其主要功能（附带示例命令或代码片段）。请保持简洁、具体，并聚焦于最佳实践，帮助 AI 为用户生成正确的代码。例如：

```markdown
## 扩展包名称

此扩展包提供[功能简述]。

### 功能

- 功能 1：[清晰、简短的描述]。
- 功能 2：[清晰、简短的描述]。用法示例：

@verbatim
<code-snippet name="How to use Feature 2" lang="php">
$result = PackageName::featureTwo($param1, $param2);
</code-snippet>
@endverbatim
```

<a name="agent-skills"></a>
## 智能体技能

[智能体技能](https://agentskills.io/home)是轻量、专用的知识模块，智能体可以在处理特定领域的任务时按需启用。指南会预先加载，而技能仅在相关任务需要时加载详细模式和最佳实践，减少上下文冗余，并提高 AI 生成代码的相关性。

当你运行 `boost:install` 并选择安装技能功能时，Boost 会根据 `composer.json` 中检测到的扩展包自动安装技能。例如，如果项目包含 `livewire/livewire`，就会自动安装 `livewire-development` 技能。Boost 自带的技能（例如 `infer-conventions`）则始终安装，不受项目所用扩展包的影响。

<a name="available-skills"></a>
### 可用的技能

<div class="overflow-auto" markdown="1">

| 技能 | 扩展包 |
| -------------------------- | -------------- |
| fluxui-development         | Flux UI        |
| folio-routing              | Folio          |
| infer-conventions          | Boost          |
| inertia-react-development  | Inertia React  |
| inertia-svelte-development | Inertia Svelte |
| inertia-vue-development    | Inertia Vue    |
| livewire-development       | Livewire       |
| mcp-development            | MCP            |
| pennant-development        | Pennant        |
| pest-testing               | Pest           |
| tailwindcss-development    | Tailwind CSS   |
| volt-development           | Volt           |
| wayfinder-development      | Wayfinder      |

</div>

> **注意：**要保持技能更新，请参阅[保持 Boost 资源更新](#keeping-boost-resources-updated)一节。

<a name="custom-skills"></a>
### 自定义技能

要创建自定义技能，请在应用的 `.ai/skills/{skill-name}/` 目录中添加 `SKILL.md` 文件。运行 `boost:update` 时，Boost 会将自定义技能与内置技能一同安装。

例如，为应用的领域逻辑创建一个自定义技能：

```
.ai/skills/creating-invoices/SKILL.md
```

<a name="overriding-skills"></a>
### 覆盖技能

你可以创建与现有 Boost 技能同名的自定义技能，覆盖 Boost 的内置技能。当自定义技能与某个内置技能同名时，Boost 会使用你的自定义版本。

例如，要覆盖 Boost 的 `livewire-development` 技能，请创建 `.ai/skills/livewire-development/SKILL.md` 文件。运行 `boost:update` 时，Boost 会使用你的自定义技能替代默认技能。

<a name="third-party-package-skills"></a>
### 第三方扩展包的技能

如果你维护第三方扩展包，并希望 Boost 为其提供技能，可以在扩展包中添加 `resources/boost/skills/{skill-name}/SKILL.md` 文件。当扩展包用户运行 `php artisan boost:install` 时，Boost 会根据用户的偏好自动安装你的技能。

Boost 技能支持 [Agent Skills 格式](https://agentskills.io/what-are-skills)，应以文件夹形式组织，其中包含一个带有 YAML frontmatter 和 Markdown 指令的 `SKILL.md` 文件。`SKILL.md` 文件必须包含必要的 frontmatter 字段（`name` 和 `description`），也可以包含脚本、模板和参考资料。

技能应概述所需的文件结构或约定，并说明如何创建或使用其主要功能（附带示例命令或代码片段）。请保持简洁、具体，并聚焦于最佳实践，帮助 AI 为用户生成正确的代码：

```markdown
---
name: package-name-development
description: 构建和使用 PackageName 的功能，包括组件和工作流。
---

# PackageName 开发

## 何时使用此技能
在使用 PackageName 功能时启用此技能……

## 功能

- 功能 1：[清晰、简短的描述]。
- 功能 2：[清晰、简短的描述]。用法示例：

$result = PackageName::featureTwo($param1, $param2);
```

<a name="guidelines-vs-skills"></a>
## 指南与技能

Laravel Boost 通过两种不同的方式为 AI 智能体提供应用上下文：**指南**和**技能**。

**指南**会在 AI 智能体启动时预先加载，提供适用于整个代码库的 Laravel 约定和最佳实践等必要上下文。

**技能**会在处理特定任务时按需启用，包含特定领域（例如 Livewire 组件或 Pest 测试）的详细模式。仅在需要时加载技能，可以减少上下文冗余并提高代码质量。

<div class="overflow-auto" markdown="1">

| 方面 | 指南 | 技能 |
| ----------- | --------------------------------- | -------------------------------- |
| **加载时机** | 预先加载，始终存在 | 按需加载，仅在相关时启用 |
| **范围** | 广泛、基础性 | 聚焦于特定任务 |
| **用途** | 核心约定和最佳实践 | 详细的实现模式 |

</div>

指南和技能都描述 Laravel 生态系统。要记录你自己的应用约定，应使用[项目规则](#project-rules)。

<a name="project-rules"></a>
## 项目规则

指南和技能教智能体如何使用 Laravel 编写代码，而项目规则教它们如何编写你的应用。规则是指那些你原本需要在每次新会话中重新解释的内容：

<div class="content-list" markdown="1">

- 你、智能体或团队成员在开发过程中做出的决策。
- 智能体难以遵循的风格指南和偏好。
- 无法从周边代码推断出的陷阱和约束。

</div>

规则以 Markdown 文件的形式存储在应用的 `.ai/rules` 目录中，应提交到版本控制系统。智能体自身的记忆属于个人，且仅限当前会话；你的规则则由团队以及所有参与开发此应用的智能体共享。

每个规则文件在 frontmatter 中声明其适用的文件 glob 模式：

```markdown
---
paths:
  - app/Http/Controllers/**
---

# HTTP 控制器

## 继承 BaseController 以限定租户范围

所有控制器都必须继承 `App\Http\Controllers\BaseController`，该类会应用
当前租户的查询作用域。直接继承 Laravel 的基础控制器会导致
数据在租户之间泄漏。
```

此外，Boost 还维护一个 `.ai/rules/index.md` 文件，将 glob 模式映射到对应的规则文件。智能体会被要求在规划或编辑任何文件之前查阅此索引，因此只会在相关时加载规则：

```markdown
# 项目规则索引

在规划或编辑之前，找到 glob 模式与文件路径匹配的那一行，并阅读对应的规则文件。

| 适用范围 | 规则文件 |
| --- | --- |
| app/Http/Controllers/** | .ai/rules/controllers.md |
| app/Models/** | .ai/rules/models.md |
```

> [!NOTE]
> 与 `.mcp.json` 和生成的指南文件不同，`.ai/rules` 目录应提交到版本控制系统，以便与团队共享规则。

<a name="recording-rules"></a>
### 记录规则

要记录规则，你只需让智能体记住它：

```text
请记住，所有金额都以整数分为单位存储，绝不能使用浮点数。
```

智能体会调用 Boost 的 `record-rule` MCP 工具，传入 `glob`、简短的 `title` 和 `note`。随后，Boost 会将规则归入相应领域，必要时创建规则文件，并更新索引。

你应始终使用 `record-rule` 工具记录规则。Boost 会在记录规则时重新生成 `.ai/rules/index.md`，而智能体依靠该索引发现当前文件适用的规则。手动添加的规则文件要等到索引下次重新生成后，才会被发现。

<a name="inferring-your-applications-conventions"></a>
### 推断应用的约定

逐条记录规则适用于后续开发，但已有应用往往已经积累了多年的约定。`infer-conventions` 技能可以根据现有代码初始化规则。首先，让智能体使用该技能：

```text
使用 infer-conventions 技能
```

此技能会按 Laravel 约定的各个维度检查应用，包括验证、控制器、授权、模型、架构、测试、前端、数据库和控制台，随后还会进一步查找基类、共享 trait、模块布局等模式。

此技能记录代码实际采用的做法，而非代码应该采用的做法。它只记录有充分依据且不同于默认行为的约定，跳过框架默认行为以及 Pint 或 Rector 已强制执行的规则；对于确实混用的模式，只会报告，不会将其记为规则。在写入任何规则之前，此技能会列出发现的每条约定及其依据，供你批准。如果希望它直接记录所有发现的约定，可以告诉它「yolo」。

<a name="disabling-project-rules"></a>
### 禁用项目规则

项目规则默认启用。要完全禁用，请定义以下环境变量。这会移除 `record-rule` MCP 工具，并停止由 Boost 管理 `.ai/rules` 目录：

```ini
BOOST_RULES_ENABLED=false
```

<a name="documentation-api"></a>
## 文档 API

Laravel Boost 包含一个文档 API，为 AI 智能体提供包含超过 17,000 条 Laravel 专属信息的庞大知识库。该 API 利用嵌入向量进行语义搜索，提供精确且符合上下文的结果。

`Search Docs` MCP 工具允许智能体查询 Laravel 托管的文档 API 服务，根据已安装的扩展包检索文档。Boost 的 AI 指南和技能会自动指导编码智能体使用此 API。

<div class="overflow-auto" markdown="1">

| 扩展包 | 支持的版本 |
| ----------------- | ------------------ |
| Laravel Framework | 10.x, 11.x, 12.x, 13.x |
| Filament          | 2.x, 3.x, 4.x, 5.x |
| Flux UI           | 2.x Free, 2.x Pro  |
| Inertia           | 1.x, 2.x           |
| Livewire          | 1.x, 2.x, 3.x, 4.x |
| Nova              | 4.x, 5.x           |
| Pest              | 3.x, 4.x           |
| Tailwind CSS      | 3.x, 4.x           |

</div>

<a name="extending-boost"></a>
## 扩展 Boost

Boost 开箱即支持多种流行的 IDE 和 AI 智能体。如果你使用的编码工具尚未受支持，可以创建自己的智能体，并将其与 Boost 集成。

<a name="adding-support-for-other-ides-ai-agents"></a>
### 添加对其他 IDE / AI 智能体的支持

要添加对新 IDE 或 AI 智能体的支持，请创建一个继承 `Laravel\Boost\Install\Agents\Agent` 的类，并根据需要实现以下一个或多个接口：

- `Laravel\Boost\Contracts\SupportsGuidelines` - 添加对 AI 指南的支持。
- `Laravel\Boost\Contracts\SupportsMcp` - 添加对 MCP 的支持。
- `Laravel\Boost\Contracts\SupportsSkills` - 添加对智能体技能的支持。

<a name="writing-the-agent"></a>
#### 编写智能体

```php
<?php

declare(strict_types=1);

namespace App;

use Laravel\Boost\Contracts\SupportsGuidelines;
use Laravel\Boost\Contracts\SupportsMcp;
use Laravel\Boost\Contracts\SupportsSkills;
use Laravel\Boost\Install\Agents\Agent;

class CustomAgent extends Agent implements SupportsGuidelines, SupportsMcp, SupportsSkills
{
    // 你的实现代码……
}
```

实现示例请参阅 [ClaudeCode.php](https://github.com/laravel/boost/blob/main/src/Install/Agents/ClaudeCode.php)。

<a name="registering-the-agent"></a>
#### 注册智能体

在应用的 `App\Providers\AppServiceProvider` 的 `boot` 方法中注册自定义智能体：

```php
use Laravel\Boost\Boost;

public function boot(): void
{
    Boost::registerAgent('customagent', CustomAgent::class);
}
```

注册后，运行 `php artisan boost:install` 时就可以选择你的智能体。
