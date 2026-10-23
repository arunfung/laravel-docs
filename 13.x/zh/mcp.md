# Laravel MCP

- [简介](#introduction)
- [安装](#installation)
    - [发布路由](#publishing-routes)
- [创建服务器](#creating-servers)
    - [注册服务器](#server-registration)
    - [Web 服务器](#web-servers)
    - [本地服务器](#local-servers)
    - [缓存提示](#cache-hints)
- [工具](#tools)
    - [创建工具](#creating-tools)
    - [可搜索的工具目录](#searchable-tool-catalogs)
    - [工具输入模式](#tool-input-schemas)
    - [工具输出模式](#tool-output-schemas)
    - [验证工具参数](#validating-tool-arguments)
    - [工具依赖注入](#tool-dependency-injection)
    - [工具注解](#tool-annotations)
    - [有条件地注册工具](#conditional-tool-registration)
    - [工具响应](#tool-responses)
- [提示词](#prompts)
    - [创建提示词](#creating-prompts)
    - [提示词参数](#prompt-arguments)
    - [验证提示词参数](#validating-prompt-arguments)
    - [提示词依赖注入](#prompt-dependency-injection)
    - [有条件地注册提示词](#conditional-prompt-registration)
    - [提示词响应](#prompt-responses)
- [资源](#resources)
    - [创建资源](#creating-resources)
    - [资源模板](#resource-templates)
    - [资源 URI 和 MIME 类型](#resource-uri-and-mime-type)
    - [资源请求](#resource-request)
    - [资源依赖注入](#resource-dependency-injection)
    - [资源注解](#resource-annotations)
    - [有条件地注册资源](#conditional-resource-registration)
    - [资源响应](#resource-responses)
- [应用](#apps)
    - [创建应用资源](#creating-app-resources)
    - [通过工具渲染应用](#rendering-apps-from-tools)
    - [应用工具的可见性](#app-tool-visibility)
    - [应用配置](#app-configuration)
    - [使用 Boost 构建应用](#building-apps-with-boost)
- [元数据](#metadata)
- [图标](#icons)
- [身份认证](#authentication)
    - [OAuth 2.1](#oauth)
    - [Sanctum](#sanctum)
- [授权](#authorization)
- [MCP 客户端](#client)
    - [连接服务器](#client-connecting)
    - [命名客户端](#named-clients)
    - [客户端身份认证](#client-authentication)
    - [工具](#client-tools)
    - [提示词](#client-prompts)
    - [资源](#client-resources)
- [测试服务器](#testing-servers)
    - [MCP Inspector](#mcp-inspector)
    - [单元测试](#unit-tests)

<a name="introduction"></a>
## 简介

[Laravel MCP](https://github.com/laravel/mcp) 为 AI 客户端提供了一种简单、优雅的方式，使其能够通过[模型上下文协议](https://modelcontextprotocol.io/docs/getting-started/intro)与你的 Laravel 应用交互。它提供富有表现力的流畅接口，用于定义服务器、工具、资源和提示词，让 AI 能够与你的应用交互。

<a name="installation"></a>
## 安装

首先，使用 Composer 包管理器将 Laravel MCP 安装到你的项目中：

```shell
composer require laravel/mcp
```

<a name="publishing-routes"></a>
### 发布路由

安装 Laravel MCP 后，执行 `vendor:publish` Artisan 命令，发布用于定义 MCP 服务器的 `routes/ai.php` 文件：

```shell
php artisan vendor:publish --tag=ai-routes
```

此命令会在应用的 `routes` 目录中创建 `routes/ai.php` 文件，你将在其中注册 MCP 服务器。

<a name="creating-servers"></a>
## 创建服务器

你可以使用 `make:mcp-server` Artisan 命令创建 MCP 服务器。服务器作为统一的通信入口，向 AI 客户端开放工具、资源和提示词等 MCP 功能：

```shell
php artisan make:mcp-server WeatherServer
```

此命令将在 `app/Mcp/Servers` 目录中创建一个新的服务器类。生成的服务器类继承 Laravel MCP 的基类 `Laravel\Mcp\Server`，并提供特性和属性，用于配置服务器以及注册工具、资源和提示词：

```php
<?php

namespace App\Mcp\Servers;

use Laravel\Mcp\Server\Attributes\Instructions;
use Laravel\Mcp\Server\Attributes\Name;
use Laravel\Mcp\Server\Attributes\Version;
use Laravel\Mcp\Server;

#[Name('Weather Server')]
#[Version('1.0.0')]
#[Instructions('This server provides weather information and forecasts.')]
class WeatherServer extends Server
{
    /**
     * 在此 MCP 服务器中注册的工具。
     *
     * @var array<int, class-string<\Laravel\Mcp\Server\Tool>>
     */
    protected array $tools = [
        // GetCurrentWeatherTool::class,
    ];

    /**
     * 在此 MCP 服务器中注册的资源。
     *
     * @var array<int, class-string<\Laravel\Mcp\Server\Resource>>
     */
    protected array $resources = [
        // WeatherGuidelinesResource::class,
    ];

    /**
     * 在此 MCP 服务器中注册的提示词。
     *
     * @var array<int, class-string<\Laravel\Mcp\Server\Prompt>>
     */
    protected array $prompts = [
        // DescribeWeatherPrompt::class,
    ];
}
```

<a name="server-registration"></a>
### 注册服务器

创建服务器后，你必须在 `routes/ai.php` 文件中注册它，才能使其可被访问。Laravel MCP 提供两种注册服务器的方法：`web` 用于可通过 HTTP 访问的服务器，`local` 用于命令行服务器。

<a name="web-servers"></a>
### Web 服务器

Web 服务器是最常见的服务器类型，可通过 HTTP POST 请求访问，非常适合远程 AI 客户端或基于 Web 的集成。使用 `web` 方法注册 Web 服务器：

```php
use App\Mcp\Servers\WeatherServer;
use Laravel\Mcp\Facades\Mcp;

Mcp::web('/mcp/weather', WeatherServer::class);
```

与普通路由一样，你可以为 Web 服务器应用中间件来保护它们：

```php
Mcp::web('/mcp/weather', WeatherServer::class)
    ->middleware(['throttle:mcp']);
```

<a name="local-servers"></a>
### 本地服务器

本地服务器以 Artisan 命令的形式运行，非常适合构建 [Laravel Boost](/docs/{{version}}/installation#installing-laravel-boost) 等本地 AI 助手集成。使用 `local` 方法注册本地服务器：

```php
use App\Mcp\Servers\WeatherServer;
use Laravel\Mcp\Facades\Mcp;

Mcp::local('weather', WeatherServer::class);
```

注册后，你通常无需手动运行 `mcp:start` Artisan 命令。你可以配置 MCP 客户端（AI 智能体）来启动服务器，或使用 [MCP Inspector](#mcp-inspector)。

<a name="cache-hints"></a>
### 缓存提示

对于服务器发现、基础组件列表和资源读取等可缓存的响应，Laravel MCP 会附带缓存提示。默认情况下，这些响应被标记为私有，存活时间为零毫秒。

你可以使用 `Cacheable` 特性自定义服务器的默认缓存提示：

```php
use Laravel\Mcp\Enums\CacheScope;
use Laravel\Mcp\Server\Attributes\Cacheable;

#[Cacheable(ttlMs: 60_000, scope: CacheScope::Public)]
class WeatherServer extends Server
{
    /**
     * 获取各个 MCP 方法的缓存提示。
     *
     * @return array<string, \Laravel\Mcp\Server\Attributes\Cacheable>
     */
    protected function cacheHints(): array
    {
        return [
            'tools/list' => new Cacheable(ttlMs: 30_000, scope: CacheScope::Public),
        ];
    }
}
```

`CacheScope::Private` 作用域将缓存响应限制在相同的授权上下文内，而 `CacheScope::Public` 允许在用户之间共享响应。缓存提示仅供参考，响应是否实际缓存由 MCP 客户端或宿主决定。`cacheHints` 返回的特定方法缓存提示优先于服务器的 `Cacheable` 特性。

你可以在资源类上应用 `Cacheable` 特性，为单个资源覆盖服务器的缓存提示：

```php
#[Cacheable(ttlMs: 300_000, scope: CacheScope::Public)]
class WeatherGuidelinesResource extends Resource
{
    // ...
}
```

资源的 `Cacheable` 特性优先于特定方法的缓存提示和服务器的默认缓存提示。

<a name="tools"></a>
## 工具

工具使服务器能够向 AI 客户端开放可调用的功能，让语言模型执行操作、运行代码或与外部系统交互：

```php
<?php

namespace App\Mcp\Tools;

use Illuminate\Contracts\JsonSchema\JsonSchema;
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Attributes\Description;
use Laravel\Mcp\Server\Tool;

#[Description('Fetches the current weather forecast for a specified location.')]
class CurrentWeatherTool extends Tool
{
    /**
     * 处理工具请求。
     */
    public function handle(Request $request): Response
    {
        $location = $request->get('location');

        // 获取天气……

        return Response::text('The weather is...');
    }

    /**
     * 获取工具的输入模式。
     *
     * @return array<string, \Illuminate\JsonSchema\Types\Type>
     */
    public function schema(JsonSchema $schema): array
    {
        return [
            'location' => $schema->string()
                ->description('The location to get the weather for.')
                ->required(),
        ];
    }
}
```

<a name="creating-tools"></a>
### 创建工具

要创建工具，请运行 `make:mcp-tool` Artisan 命令：

```shell
php artisan make:mcp-tool CurrentWeatherTool
```

创建工具后，在服务器的 `$tools` 属性中注册它：

```php
<?php

namespace App\Mcp\Servers;

use App\Mcp\Tools\CurrentWeatherTool;
use Laravel\Mcp\Server;

class WeatherServer extends Server
{
    /**
     * 在此 MCP 服务器中注册的工具。
     *
     * @var array<int, class-string<\Laravel\Mcp\Server\Tool>>
     */
    protected array $tools = [
        CurrentWeatherTool::class,
    ];
}
```

<a name="searchable-tool-catalogs"></a>
### 可搜索的工具目录

当服务器具有大量工具时，可以将其中一些工具放入可搜索的目录，而无需向 AI 客户端公布每个工具。可搜索的目录会开放两个工具：`search_tools` 按工具名称、描述和输入模式搜索目录；`execute_tools` 则调用搜索结果中的一个或多个工具。

要创建可搜索的目录，请在服务器的 `$tools` 属性中使用 `ToolSearch` 类作为数组键：

```php
<?php

namespace App\Mcp\Servers;

use App\Mcp\Tools\CurrentWeatherTool;
use App\Mcp\Tools\HistoricalWeatherTool;
use App\Mcp\Tools\WeatherAlertsTool;
use Laravel\Mcp\Server;
use Laravel\Mcp\Server\Tools\ToolSearch;

class WeatherServer extends Server
{
    /**
     * 在此 MCP 服务器中注册的工具。
     *
     * @var array<int|string, \Laravel\Mcp\Server\Tool|class-string<\Laravel\Mcp\Server\Tool>|array<int, \Laravel\Mcp\Server\Tool|class-string<\Laravel\Mcp\Server\Tool>>>
     */
    protected array $tools = [
        CurrentWeatherTool::class,

        ToolSearch::class => [
            HistoricalWeatherTool::class,
            WeatherAlertsTool::class,
        ],
    ];
}
```

在此示例中，`CurrentWeatherTool` 会直接公布，而历史天气和天气警报工具则通过可搜索的目录提供。搜索或执行目录中的工具时，仍会遵守有条件注册工具的规则。

单次 `execute_tools` 调用可执行的工具数量上限和响应大小上限，分别由 `mcp.tool_search.max_tool_calls` 和 `mcp.tool_search.max_output_bytes` 配置项控制。

<a name="tool-name-title-description"></a>
#### 工具名称、标题和描述

默认情况下，工具的名称和标题由类名派生而来。例如，`CurrentWeatherTool` 的名称为 `current-weather`，标题为 `Current Weather Tool`。你可以使用 `Name` 和 `Title` 特性自定义这些值：

```php
use Laravel\Mcp\Server\Attributes\Name;
use Laravel\Mcp\Server\Attributes\Title;

#[Name('get-optimistic-weather')]
#[Title('Get Optimistic Weather Forecast')]
class CurrentWeatherTool extends Tool
{
    // ...
}
```

工具描述不会自动生成。你应始终使用 `Description` 特性提供有意义的描述：

```php
use Laravel\Mcp\Server\Attributes\Description;

#[Description('Fetches the current weather forecast for a specified location.')]
class CurrentWeatherTool extends Tool
{
    //
}
```

> [!NOTE]
> 描述是工具元数据的关键部分，它能帮助 AI 模型理解何时以及如何有效地使用工具。

<a name="tool-input-schemas"></a>
### 工具输入模式

工具可以定义输入模式，指定它们接受 AI 客户端传入哪些参数。使用 Laravel 的 `Illuminate\Contracts\JsonSchema\JsonSchema` 构建器定义工具的输入要求：

```php
<?php

namespace App\Mcp\Tools;

use Illuminate\Contracts\JsonSchema\JsonSchema;
use Laravel\Mcp\Server\Tool;

class CurrentWeatherTool extends Tool
{
    /**
     * 获取工具的输入模式。
     *
     * @return array<string, \Illuminate\JsonSchema\Types\Type>
     */
    public function schema(JsonSchema $schema): array
    {
        return [
            'location' => $schema->string()
                ->description('The location to get the weather for.')
                ->required(),

            'units' => $schema->string()
                ->enum(['celsius', 'fahrenheit'])
                ->description('The temperature units to use.')
                ->default('celsius'),
        ];
    }
}
```

<a name="tool-output-schemas"></a>
### 工具输出模式

工具可以定义[输出模式](https://modelcontextprotocol.io/specification/2026-07-28/server/tools#output-schema)，以指定响应的结构。这有助于与需要可解析工具结果的 AI 客户端集成。使用 `outputSchema` 方法定义工具的输出结构：

```php
<?php

namespace App\Mcp\Tools;

use Illuminate\Contracts\JsonSchema\JsonSchema;
use Laravel\Mcp\Server\Tool;

class CurrentWeatherTool extends Tool
{
    /**
     * 获取工具的输出模式。
     *
     * @return array<string, \Illuminate\JsonSchema\Types\Type>
     */
    public function outputSchema(JsonSchema $schema): array
    {
        return [
            'temperature' => $schema->number()
                ->description('Temperature in Celsius')
                ->required(),

            'conditions' => $schema->string()
                ->description('Weather conditions')
                ->required(),

            'humidity' => $schema->integer()
                ->description('Humidity percentage')
                ->required(),
        ];
    }
}
```

<a name="validating-tool-arguments"></a>
### 验证工具参数

JSON Schema 定义提供了工具参数的基本结构，但你可能还需要执行更复杂的验证规则。

Laravel MCP 与 Laravel 的[验证功能](/docs/{{version}}/validation)无缝集成。你可以在工具的 `handle` 方法中验证传入的工具参数：

```php
<?php

namespace App\Mcp\Tools;

use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Tool;

class CurrentWeatherTool extends Tool
{
    /**
     * 处理工具请求。
     */
    public function handle(Request $request): Response
    {
        $validated = $request->validate([
            'location' => 'required|string|max:100',
            'units' => 'in:celsius,fahrenheit',
        ]);

        // 使用验证后的参数获取天气数据……
    }
}
```

验证失败时，AI 客户端会根据你提供的错误消息采取行动。因此，提供清晰且能指导下一步操作的错误消息至关重要：

```php
$validated = $request->validate([
    'location' => ['required','string','max:100'],
    'units' => 'in:celsius,fahrenheit',
],[
    'location.required' => 'You must specify a location to get the weather for. For example, "New York City" or "Tokyo".',
    'units.in' => 'You must specify either "celsius" or "fahrenheit" for the units.',
]);
```

<a name="tool-dependency-injection"></a>
#### 工具依赖注入

Laravel [服务容器](/docs/{{version}}/container)负责解析所有工具。因此，你可以在工具的构造函数中通过类型提示声明所需的依赖。这些依赖会自动解析并注入工具实例：

```php
<?php

namespace App\Mcp\Tools;

use App\Repositories\WeatherRepository;
use Laravel\Mcp\Server\Tool;

class CurrentWeatherTool extends Tool
{
    /**
     * 创建一个新的工具实例。
     */
    public function __construct(
        protected WeatherRepository $weather,
    ) {}

    // ...
}
```

除了构造函数注入，你还可以在工具的 `handle()` 方法中通过类型提示声明依赖。调用该方法时，服务容器会自动解析并注入这些依赖：

```php
<?php

namespace App\Mcp\Tools;

use App\Repositories\WeatherRepository;
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Tool;

class CurrentWeatherTool extends Tool
{
    /**
     * 处理工具请求。
     */
    public function handle(Request $request, WeatherRepository $weather): Response
    {
        $location = $request->get('location');

        $forecast = $weather->getForecastFor($location);

        // ...
    }
}
```

<a name="tool-annotations"></a>
### 工具注解

你可以为工具添加[注解](https://modelcontextprotocol.io/specification/2026-07-28/schema#toolannotations)，向 AI 客户端提供额外的元数据。这些注解有助于 AI 模型理解工具的行为和能力。注解通过特性添加到工具上：

```php
<?php

namespace App\Mcp\Tools;

use Laravel\Mcp\Server\Tools\Annotations\IsIdempotent;
use Laravel\Mcp\Server\Tools\Annotations\IsReadOnly;
use Laravel\Mcp\Server\Tool;

#[IsIdempotent]
#[IsReadOnly]
class CurrentWeatherTool extends Tool
{
    //
}
```

可用的注解包括：

<div class="overflow-auto" markdown="1">

| 注解 | 类型 | 描述 |
| ------------------ | ------- | -------------------------------------------------------------------------------------------- |
| `#[IsReadOnly]` | boolean | 表示工具不会修改其运行环境。 |
| `#[IsDestructive]` | boolean | 表示工具可能执行破坏性更新（仅在非只读时有意义）。 |
| `#[IsIdempotent]` | boolean | 表示使用相同参数重复调用不会产生额外影响（非只读时）。 |
| `#[IsOpenWorld]` | boolean | 表示工具可能与外部实体交互。 |

</div>

你可以使用布尔参数显式设置注解值：

```php
use Laravel\Mcp\Server\Tools\Annotations\IsReadOnly;
use Laravel\Mcp\Server\Tools\Annotations\IsDestructive;
use Laravel\Mcp\Server\Tools\Annotations\IsOpenWorld;
use Laravel\Mcp\Server\Tools\Annotations\IsIdempotent;
use Laravel\Mcp\Server\Tool;

#[IsReadOnly(true)]
#[IsDestructive(false)]
#[IsOpenWorld(false)]
#[IsIdempotent(true)]
class CurrentWeatherTool extends Tool
{
    //
}
```

<a name="conditional-tool-registration"></a>
### 有条件地注册工具

你可以在工具类中实现 `shouldRegister` 方法，在运行时有条件地注册工具。此方法允许你根据应用状态、配置或请求参数，确定是否应提供某个工具：

```php
<?php

namespace App\Mcp\Tools;

use Laravel\Mcp\Request;
use Laravel\Mcp\Server\Tool;

class CurrentWeatherTool extends Tool
{
    /**
     * 确定是否应注册此工具。
     */
    public function shouldRegister(Request $request): bool
    {
        return $request?->user()?->subscribed() ?? false;
    }
}
```

当工具的 `shouldRegister` 方法返回 `false` 时，它不会出现在可用工具列表中，AI 客户端也无法调用它。

<a name="tool-responses"></a>
### 工具响应

工具必须返回 `Laravel\Mcp\Response` 实例。Response 类提供了多种便捷方法，用于创建不同类型的响应：

对于简单的文本响应，使用 `text` 方法：

```php
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;

/**
 * 处理工具请求。
 */
public function handle(Request $request): Response
{
    // ...

    return Response::text('Weather Summary: Sunny, 72°F');
}
```

要表示工具执行期间发生错误，使用 `error` 方法：

```php
return Response::error('Unable to fetch weather data. Please try again.');
```

要返回图像或音频内容，使用 `image` 和 `audio` 方法：

```php
return Response::image(file_get_contents(storage_path('weather/radar.png')), 'image/png');

return Response::audio(file_get_contents(storage_path('weather/alert.mp3')), 'audio/mp3');
```

你也可以使用 `fromStorage` 方法，直接从 Laravel 文件系统磁盘加载图像和音频内容。MIME 类型会根据文件自动检测：

```php
return Response::fromStorage('weather/radar.png');
```

如果需要，你可以指定磁盘或覆盖 MIME 类型：

```php
return Response::fromStorage('weather/radar.png', disk: 's3');

return Response::fromStorage('weather/radar.png', mimeType: 'image/webp');
```

<a name="multiple-content-responses"></a>
#### 多内容响应

工具可以通过返回 `Response` 实例数组来返回多项内容：

```php
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;

/**
 * 处理工具请求。
 *
 * @return array<int, \Laravel\Mcp\Response>
 */
public function handle(Request $request): array
{
    // ...

    return [
        Response::text('Weather Summary: Sunny, 72°F'),
        Response::text("**Detailed Forecast**\n- Morning: 65°F\n- Afternoon: 78°F\n- Evening: 70°F")
    ];
}
```

<a name="structured-responses"></a>
#### 结构化响应

工具可以使用 `structured` 方法返回[结构化内容](https://modelcontextprotocol.io/specification/2026-07-28/server/tools#structured-content)。这既为 AI 客户端提供可解析的数据，又通过 JSON 编码的文本表示保持向后兼容：

```php
return Response::structured([
    'temperature' => 22.5,
    'conditions' => 'Partly cloudy',
    'humidity' => 65,
]);
```

如果需要在结构化内容之外提供自定义文本，请在响应工厂上使用 `withStructuredContent` 方法：

```php
return Response::make(
    Response::text('Weather is 22.5°C and sunny')
)->withStructuredContent([
    'temperature' => 22.5,
    'conditions' => 'Sunny',
]);
```

<a name="streaming-responses"></a>
#### 流式响应

对于耗时较长的操作或实时数据流，工具可以从 `handle` 方法返回[生成器](https://www.php.net/manual/en/language.generators.overview.php)，以便在最终响应之前向客户端发送中间状态更新：

```php
<?php

namespace App\Mcp\Tools;

use Generator;
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Tool;

class CurrentWeatherTool extends Tool
{
    /**
     * 处理工具请求。
     *
     * @return \Generator<int, \Laravel\Mcp\Response>
     */
    public function handle(Request $request): Generator
    {
        $locations = $request->array('locations');

        foreach ($locations as $index => $location) {
            yield Response::notification('processing/progress', [
                'current' => $index + 1,
                'total' => count($locations),
                'location' => $location,
            ]);

            yield Response::text($this->forecastFor($location));
        }
    }
}
```

使用 Web 服务器时，流式响应会自动打开 SSE（服务器发送事件）流，将每条通过 yield 产生的消息作为事件发送给客户端。

<a name="prompts"></a>
## 提示词

[提示词](https://modelcontextprotocol.io/specification/2026-07-28/server/prompts)使服务器能够共享可复用的提示词模板，供 AI 客户端与语言模型交互。它们为组织常见查询和交互提供了标准化方式。

<a name="creating-prompts"></a>
### 创建提示词

要创建提示词，请运行 `make:mcp-prompt` Artisan 命令：

```shell
php artisan make:mcp-prompt DescribeWeatherPrompt
```

创建提示词后，在服务器的 `$prompts` 属性中注册它：

```php
<?php

namespace App\Mcp\Servers;

use App\Mcp\Prompts\DescribeWeatherPrompt;
use Laravel\Mcp\Server;

class WeatherServer extends Server
{
    /**
     * 在此 MCP 服务器中注册的提示词。
     *
     * @var array<int, class-string<\Laravel\Mcp\Server\Prompt>>
     */
    protected array $prompts = [
        DescribeWeatherPrompt::class,
    ];
}
```

<a name="prompt-name-title-and-description"></a>
#### 提示词名称、标题和描述

默认情况下，提示词的名称和标题由类名派生而来。例如，`DescribeWeatherPrompt` 的名称为 `describe-weather`，标题为 `Describe Weather Prompt`。你可以使用 `Name` 和 `Title` 特性自定义这些值：

```php
use Laravel\Mcp\Server\Attributes\Name;
use Laravel\Mcp\Server\Attributes\Title;

#[Name('weather-assistant')]
#[Title('Weather Assistant Prompt')]
class DescribeWeatherPrompt extends Prompt
{
    // ...
}
```

提示词描述不会自动生成。你应始终使用 `Description` 特性提供有意义的描述：

```php
use Laravel\Mcp\Server\Attributes\Description;

#[Description('Generates a natural-language explanation of the weather for a given location.')]
class DescribeWeatherPrompt extends Prompt
{
    //
}
```

> [!NOTE]
> 描述是提示词元数据的关键部分，它能帮助 AI 模型理解何时以及如何充分利用提示词。

<a name="prompt-arguments"></a>
### 提示词参数

提示词可以定义参数，允许 AI 客户端使用具体的值自定义提示词模板。使用 `arguments` 方法定义提示词接受的参数：

```php
<?php

namespace App\Mcp\Prompts;

use Laravel\Mcp\Server\Prompt;
use Laravel\Mcp\Server\Prompts\Argument;

class DescribeWeatherPrompt extends Prompt
{
    /**
     * 获取提示词的参数。
     *
     * @return array<int, \Laravel\Mcp\Server\Prompts\Argument>
     */
    public function arguments(): array
    {
        return [
            new Argument(
                name: 'tone',
                description: 'The tone to use in the weather description (e.g., formal, casual, humorous).',
                required: true,
            ),
        ];
    }
}
```

<a name="validating-prompt-arguments"></a>
### 验证提示词参数

提示词参数会根据其定义自动验证，但你可能还需要执行更复杂的验证规则。

Laravel MCP 与 Laravel 的[验证功能](/docs/{{version}}/validation)无缝集成。你可以在提示词的 `handle` 方法中验证传入的提示词参数：

```php
<?php

namespace App\Mcp\Prompts;

use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Prompt;

class DescribeWeatherPrompt extends Prompt
{
    /**
     * 处理提示词请求。
     */
    public function handle(Request $request): Response
    {
        $validated = $request->validate([
            'tone' => 'required|string|max:50',
        ]);

        $tone = $validated['tone'];

        // 使用给定的语气生成提示词响应……
    }
}
```

验证失败时，AI 客户端会根据你提供的错误消息采取行动。因此，提供清晰且能指导下一步操作的错误消息至关重要：

```php
$validated = $request->validate([
    'tone' => ['required','string','max:50'],
],[
    'tone.*' => 'You must specify a tone for the weather description. Examples include "formal", "casual", or "humorous".',
]);
```

<a name="prompt-dependency-injection"></a>
### 提示词依赖注入

Laravel [服务容器](/docs/{{version}}/container)负责解析所有提示词。因此，你可以在提示词的构造函数中通过类型提示声明所需的依赖。这些依赖会自动解析并注入提示词实例：

```php
<?php

namespace App\Mcp\Prompts;

use App\Repositories\WeatherRepository;
use Laravel\Mcp\Server\Prompt;

class DescribeWeatherPrompt extends Prompt
{
    /**
     * 创建一个新的提示词实例。
     */
    public function __construct(
        protected WeatherRepository $weather,
    ) {}

    //
}
```

除了构造函数注入，你还可以在提示词的 `handle` 方法中通过类型提示声明依赖。调用该方法时，服务容器会自动解析并注入这些依赖：

```php
<?php

namespace App\Mcp\Prompts;

use App\Repositories\WeatherRepository;
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Prompt;

class DescribeWeatherPrompt extends Prompt
{
    /**
     * 处理提示词请求。
     */
    public function handle(Request $request, WeatherRepository $weather): Response
    {
        $isAvailable = $weather->isServiceAvailable();

        // ...
    }
}
```

<a name="conditional-prompt-registration"></a>
### 有条件地注册提示词

你可以在提示词类中实现 `shouldRegister` 方法，在运行时有条件地注册提示词。此方法允许你根据应用状态、配置或请求参数，确定是否应提供某个提示词：

```php
<?php

namespace App\Mcp\Prompts;

use Laravel\Mcp\Request;
use Laravel\Mcp\Server\Prompt;

class CurrentWeatherPrompt extends Prompt
{
    /**
     * 确定是否应注册此提示词。
     */
    public function shouldRegister(Request $request): bool
    {
        return $request?->user()?->subscribed() ?? false;
    }
}
```

当提示词的 `shouldRegister` 方法返回 `false` 时，它不会出现在可用提示词列表中，AI 客户端也无法调用它。

<a name="prompt-responses"></a>
### 提示词响应

提示词可以返回单个 `Laravel\Mcp\Response`，也可以返回包含多个 `Laravel\Mcp\Response` 实例的可迭代对象。这些响应封装了将发送给 AI 客户端的内容：

```php
<?php

namespace App\Mcp\Prompts;

use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Prompt;

class DescribeWeatherPrompt extends Prompt
{
    /**
     * 处理提示词请求。
     *
     * @return array<int, \Laravel\Mcp\Response>
     */
    public function handle(Request $request): array
    {
        $tone = $request->string('tone');

        $systemMessage = "You are a helpful weather assistant. Please provide a weather description in a {$tone} tone.";

        $userMessage = "What is the current weather like in New York City?";

        return [
            Response::text($systemMessage)->asAssistant(),
            Response::text($userMessage),
        ];
    }
}
```

你可以使用 `asAssistant()` 方法，将响应消息标记为来自 AI 助手的消息；普通消息则被视为用户输入。

<a name="resources"></a>
## 资源

[资源](https://modelcontextprotocol.io/specification/2026-07-28/server/resources)使服务器能够开放数据和内容，供 AI 客户端在与语言模型交互时读取并用作上下文。它们可以共享文档、配置等静态或动态信息，以及任何有助于 AI 生成回答的数据。

<a name="creating-resources"></a>
## 创建资源

要创建资源，请运行 `make:mcp-resource` Artisan 命令：

```shell
php artisan make:mcp-resource WeatherGuidelinesResource
```

创建资源后，在服务器的 `$resources` 属性中注册它：

```php
<?php

namespace App\Mcp\Servers;

use App\Mcp\Resources\WeatherGuidelinesResource;
use Laravel\Mcp\Server;

class WeatherServer extends Server
{
    /**
     * 在此 MCP 服务器中注册的资源。
     *
     * @var array<int, class-string<\Laravel\Mcp\Server\Resource>>
     */
    protected array $resources = [
        WeatherGuidelinesResource::class,
    ];
}
```

<a name="resource-name-title-and-description"></a>
#### 资源名称、标题和描述

默认情况下，资源的名称和标题由类名派生而来。例如，`WeatherGuidelinesResource` 的名称为 `weather-guidelines`，标题为 `Weather Guidelines Resource`。你可以使用 `Name` 和 `Title` 特性自定义这些值：

```php
use Laravel\Mcp\Server\Attributes\Name;
use Laravel\Mcp\Server\Attributes\Title;

#[Name('weather-api-docs')]
#[Title('Weather API Documentation')]
class WeatherGuidelinesResource extends Resource
{
    // ...
}
```

资源描述不会自动生成。你应始终使用 `Description` 特性提供有意义的描述：

```php
use Laravel\Mcp\Server\Attributes\Description;

#[Description('Comprehensive guidelines for using the Weather API.')]
class WeatherGuidelinesResource extends Resource
{
    //
}
```

> [!NOTE]
> 描述是资源元数据的关键部分，它能帮助 AI 模型理解何时以及如何有效地使用资源。

<a name="resource-templates"></a>
### 资源模板

[资源模板](https://modelcontextprotocol.io/specification/2026-07-28/server/resources#resource-templates)使服务器能够开放与含变量的 URI 模式相匹配的动态资源。你无需为每个资源定义静态 URI，而是可以创建一个资源，根据模板模式处理多个 URI。

<a name="creating-resource-templates"></a>
#### 创建资源模板

要创建资源模板，请在资源类中实现 `HasUriTemplate` 接口，并定义一个返回 `UriTemplate` 实例的 `uriTemplate` 方法：

```php
<?php

namespace App\Mcp\Resources;

use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Attributes\Description;
use Laravel\Mcp\Server\Attributes\MimeType;
use Laravel\Mcp\Server\Contracts\HasUriTemplate;
use Laravel\Mcp\Server\Resource;
use Laravel\Mcp\Support\UriTemplate;

#[Description('Access user files by ID')]
#[MimeType('text/plain')]
class UserFileResource extends Resource implements HasUriTemplate
{
    /**
     * 获取此资源的 URI 模板。
     */
    public function uriTemplate(): UriTemplate
    {
        return new UriTemplate('file://users/{userId}/files/{fileId}');
    }

    /**
     * 处理资源请求。
     */
    public function handle(Request $request): Response
    {
        $userId = $request->get('userId');
        $fileId = $request->get('fileId');

        // 获取并返回文件内容……

        return Response::text($content);
    }
}
```

当资源实现 `HasUriTemplate` 接口时，它将注册为资源模板，而非静态资源。随后，AI 客户端可以使用匹配模板模式的 URI 请求资源；URI 中的变量会被自动提取，供资源的 `handle` 方法使用。

<a name="uri-template-syntax"></a>
#### URI 模板语法

URI 模板使用花括号包裹的占位符来定义 URI 中的可变部分：

```php
new UriTemplate('file://users/{userId}');
new UriTemplate('file://users/{userId}/files/{fileId}');
new UriTemplate('https://api.example.com/{version}/{resource}/{id}');
```

<a name="accessing-template-variables"></a>
#### 访问模板变量

当 URI 与资源模板匹配时，提取出的变量会自动合并到请求中，你可以使用 `get` 方法访问它们：

```php
<?php

namespace App\Mcp\Resources;

use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Contracts\HasUriTemplate;
use Laravel\Mcp\Server\Resource;
use Laravel\Mcp\Support\UriTemplate;

class UserProfileResource extends Resource implements HasUriTemplate
{
    public function uriTemplate(): UriTemplate
    {
        return new UriTemplate('file://users/{userId}/profile');
    }

    public function handle(Request $request): Response
    {
        // 访问提取出的变量
        $userId = $request->get('userId');

        // 按需访问完整 URI
        $uri = $request->uri();

        // 获取用户资料……

        return Response::text("Profile for user {$userId}");
    }
}
```

`Request` 对象同时提供提取出的变量和原始请求 URI，为处理资源请求提供完整的上下文。

<a name="resource-uri-and-mime-type"></a>
### 资源 URI 和 MIME 类型

每个资源都由唯一的 URI 标识，并具有相应的 MIME 类型，帮助 AI 客户端理解资源的格式。

默认情况下，资源的 URI 根据资源名称生成，因此 `WeatherGuidelinesResource` 的 URI 为 `weather://resources/weather-guidelines`。默认的 MIME 类型为 `text/plain`。

你可以使用 `Uri` 和 `MimeType` 特性自定义这些值：

```php
<?php

namespace App\Mcp\Resources;

use Laravel\Mcp\Server\Attributes\MimeType;
use Laravel\Mcp\Server\Attributes\Uri;
use Laravel\Mcp\Server\Resource;

#[Uri('weather://resources/guidelines')]
#[MimeType('application/pdf')]
class WeatherGuidelinesResource extends Resource
{
}
```

URI 和 MIME 类型有助于 AI 客户端确定如何恰当地处理和解读资源内容。

<a name="resource-request"></a>
### 资源请求

与工具和提示词不同，资源不能定义输入模式或参数。不过，你仍然可以在资源的 `handle` 方法中使用请求对象：

```php
<?php

namespace App\Mcp\Resources;

use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Resource;

class WeatherGuidelinesResource extends Resource
{
    /**
     * 处理资源请求。
     */
    public function handle(Request $request): Response
    {
        // ...
    }
}
```

<a name="resource-dependency-injection"></a>
### 资源依赖注入

Laravel [服务容器](/docs/{{version}}/container)负责解析所有资源。因此，你可以在资源的构造函数中通过类型提示声明所需的依赖。这些依赖会自动解析并注入资源实例：

```php
<?php

namespace App\Mcp\Resources;

use App\Repositories\WeatherRepository;
use Laravel\Mcp\Server\Resource;

class WeatherGuidelinesResource extends Resource
{
    /**
     * 创建一个新的资源实例。
     */
    public function __construct(
        protected WeatherRepository $weather,
    ) {}

    // ...
}
```

除了构造函数注入，你还可以在资源的 `handle` 方法中通过类型提示声明依赖。调用该方法时，服务容器会自动解析并注入这些依赖：

```php
<?php

namespace App\Mcp\Resources;

use App\Repositories\WeatherRepository;
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Resource;

class WeatherGuidelinesResource extends Resource
{
    /**
     * 处理资源请求。
     */
    public function handle(WeatherRepository $weather): Response
    {
        $guidelines = $weather->guidelines();

        return Response::text($guidelines);
    }
}
```

<a name="resource-annotations"></a>
### 资源注解

你可以为资源添加[注解](https://modelcontextprotocol.io/specification/2026-07-28/schema#annotations)，向 AI 客户端提供额外的元数据。注解通过特性添加到资源上：

```php
<?php

namespace App\Mcp\Resources;

use Laravel\Mcp\Enums\Role;
use Laravel\Mcp\Server\Annotations\Audience;
use Laravel\Mcp\Server\Annotations\LastModified;
use Laravel\Mcp\Server\Annotations\Priority;
use Laravel\Mcp\Server\Resource;

#[Audience(Role::User)]
#[LastModified('2025-01-12T15:00:58Z')]
#[Priority(0.9)]
class UserDashboardResource extends Resource
{
    //
}
```

可用的注解包括：

<div class="overflow-auto" markdown="1">

| 注解 | 类型 | 描述 |
| ----------------- | ------------- | --------------------------------------------------------------------------- |
| `#[Audience]` | Role 或数组 | 指定目标受众（`Role::User`、`Role::Assistant` 或两者）。 |
| `#[Priority]` | float | 介于 0.0 和 1.0 之间的数值，表示资源的重要程度。 |
| `#[LastModified]` | string | 表示资源最后更新时间的 ISO 8601 时间戳。 |

</div>

<a name="conditional-resource-registration"></a>
### 有条件地注册资源

你可以在资源类中实现 `shouldRegister` 方法，在运行时有条件地注册资源。此方法允许你根据应用状态、配置或请求参数，确定是否应提供某个资源：

```php
<?php

namespace App\Mcp\Resources;

use Laravel\Mcp\Request;
use Laravel\Mcp\Server\Resource;

class WeatherGuidelinesResource extends Resource
{
    /**
     * 确定是否应注册此资源。
     */
    public function shouldRegister(Request $request): bool
    {
        return $request?->user()?->subscribed() ?? false;
    }
}
```

当资源的 `shouldRegister` 方法返回 `false` 时，它不会出现在可用资源列表中，AI 客户端也无法访问它。

<a name="resource-responses"></a>
### 资源响应

资源必须返回 `Laravel\Mcp\Response` 实例。Response 类提供了多种便捷方法，用于创建不同类型的响应：

对于简单的文本内容，使用 `text` 方法：

```php
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;

/**
 * 处理资源请求。
 */
public function handle(Request $request): Response
{
    // ...

    return Response::text($weatherData);
}
```

<a name="resource-link-responses"></a>
#### 资源链接响应

要返回资源链接，使用 `resourceLink` 方法，并提供 URI 和名称。与内嵌资源不同，资源链接返回一个 URI 指针，由 AI 客户端独立获取对应内容：

```php
return Response::resourceLink(
    uri: 'file:///data/report.json',
    name: 'monthly-report',
    mimeType: 'application/json',
);
```

你也可以传入已注册的资源类或实例，这样会自动继承资源的 URI、名称、标题、描述和 MIME 类型：

```php
return Response::resourceLink(new WeatherForecastResource);
```

<a name="resource-blob-responses"></a>
#### Blob 响应

要返回 Blob 内容，使用 `blob` 方法并传入 Blob 内容：

```php
return Response::blob(file_get_contents(storage_path('weather/radar.png')));
```

返回 Blob 内容时，MIME 类型由资源所配置的 MIME 类型决定：

```php
<?php

namespace App\Mcp\Resources;

use Laravel\Mcp\Server\Attributes\MimeType;
use Laravel\Mcp\Server\Resource;

#[MimeType('image/png')]
class WeatherGuidelinesResource extends Resource
{
    //
}
```

<a name="resource-error-responses"></a>
#### 错误响应

要表示获取资源期间发生错误，使用 `error()` 方法：

```php
return Response::error('Unable to fetch weather data for the specified location.');
```

<a name="apps"></a>
## 应用

Laravel MCP 支持 [MCP Apps](https://modelcontextprotocol.io/extensions/apps/overview)。这是模型上下文协议的一项扩展，允许工具在受支持宿主的沙箱 iframe 中渲染交互式 HTML 应用。你可以借此构建仪表盘、表单、可视化界面等超越纯文本响应的丰富体验。

MCP 应用由相互配合的两部分组成：

- **应用资源**，返回应用所需的完整、自包含 HTML。
- **工具**，通过 `#[RendersApp]` 特性关联到应用资源。调用工具时，宿主会获取并渲染关联的资源。

<a name="creating-app-resources"></a>
### 创建应用资源

你可以使用 `make:mcp-app-resource` Artisan 命令创建应用资源：

```shell
php artisan make:mcp-app-resource WeatherDashboardApp
```

此命令会创建两个文件：`app/Mcp/Resources` 中的 PHP 类和 `resources/views/mcp` 中的 Blade 视图。视图名称根据类名自动推导。例如，`WeatherDashboardApp` 对应 `mcp.weather-dashboard-app`：

```php
<?php

namespace App\Mcp\Resources;

use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Attributes\AppMeta;
use Laravel\Mcp\Server\Attributes\Description;
use Laravel\Mcp\Server\AppResource;

#[Description('An interactive weather dashboard.')]
#[AppMeta]
class WeatherDashboardApp extends AppResource
{
    /**
     * 处理应用资源请求。
     */
    public function handle(Request $request): Response
    {
        return Response::view('mcp.weather-dashboard-app', [
            'title' => $this->title(),
        ]);
    }
}
```

`AppResource` 继承基类 `Resource`，并自动配置 MCP Apps 规范要求的 `ui://` URI 方案和 `text/html;profile=mcp-app` MIME 类型。与其他资源一样，你必须将其注册到服务器的 `$resources` 数组中。

生成的 Blade 视图使用 `<x-mcp::app>` 组件，该组件渲染完整的 HTML 文档，并内置可直接使用的客户端 MCP SDK：

```blade
<x-mcp::app :title="$title">
    <x-slot:head>
        <script type="module">
        createMcpApp(async (app) => {
            document.getElementById('run-btn').addEventListener('click', async () => {
                const result = await app.callServerTool('get-weather-data', {});
                document.getElementById('output').textContent = result.content[0]?.text ?? '';
            });
        });
        </script>
    </x-slot:head>

    <div id="app">
        <button id="run-btn">Refresh</button>
        <p id="output"></p>
    </div>
</x-mcp::app>
```

全局函数 `createMcpApp` 由内置 SDK 提供，负责将 iframe 连接到服务器、应用宿主主题，并提供 `callServerTool`、`sendMessage`、`openLink` 等辅助方法和事件回调。完整的客户端 API 请参阅 [MCP Apps 规范](https://modelcontextprotocol.io/extensions/apps/overview)。

<a name="rendering-apps-from-tools"></a>
### 通过工具渲染应用

要显示应用资源，请使用 `#[RendersApp]` 特性将工具关联到该资源。调用工具时，Laravel MCP 会在工具元数据中包含资源的 URI，以便宿主在沙箱 iframe 中渲染应用：

```php
<?php

namespace App\Mcp\Tools;

use App\Mcp\Resources\WeatherDashboardApp;
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\Server\Attributes\RendersApp;
use Laravel\Mcp\Server\Tool;

#[RendersApp(resource: WeatherDashboardApp::class)]
class ShowWeatherDashboard extends Tool
{
    /**
     * 处理工具请求。
     */
    public function handle(Request $request): Response
    {
        return Response::text('Weather dashboard loaded.');
    }
}
```

只要注册了任意 `AppResource`，Laravel MCP 就会在服务器的 `extensions` 能力中自动公布 `io.modelcontextprotocol/ui` 扩展，因此无需额外配置服务器。

<a name="app-tool-visibility"></a>
### 应用工具的可见性

每个带有 `#[RendersApp]` 特性的工具都可以通过 `visibility` 参数限制调用方。这适用于提供仅供应用使用的私有工具，让 UI 调用它们来加载或刷新数据，同时不向模型暴露这些工具：

```php
use Laravel\Mcp\Server\Attributes\RendersApp;
use Laravel\Mcp\Server\Ui\Enums\Visibility;

#[RendersApp(resource: WeatherDashboardApp::class, visibility: [Visibility::App])]
class GetWeatherData extends Tool
{
    // ...
}
```

`Visibility` 枚举包含 `Model` 和 `App` 两个枚举项，默认同时包含两者。对于 UI 直接调用的后端操作，使用 `[Visibility::App]`；若要禁止 UI 调用某个工具，则使用 `[Visibility::Model]`。

<a name="app-configuration"></a>
### 应用配置

应用资源上的 `#[AppMeta]` 特性用于配置 iframe 的内容安全策略、浏览器权限，以及应包含在视图 `<head>` 中的库脚本：

```php
use Laravel\Mcp\Server\Attributes\AppMeta;
use Laravel\Mcp\Server\Ui\Enums\Library;
use Laravel\Mcp\Server\Ui\Enums\Permission;

#[AppMeta(
    connectDomains: ['https://api.weather.com'],
    permissions: [Permission::Geolocation],
    libraries: [Library::Tailwind, Library::Alpine],
)]
class WeatherDashboardApp extends AppResource
{
    // ...
}
```

`Library` 枚举包含常用前端库的预配置 CDN 脚本，例如 `Library::Tailwind` 和 `Library::Alpine`，其 CDN 来源会自动合并到 CSP 中。`Permission` 枚举涵盖 `Camera`、`Microphone`、`Geolocation` 和 `ClipboardWrite` 等浏览器权限。

对于需要计算或动态生成的配置，请使用 `Laravel\Mcp\Server\Ui` 命名空间中的 `AppMeta`、`Csp` 和 `Permissions` 流畅构建器，重写资源的 `appMeta` 方法。

<a name="building-apps-with-boost"></a>
### 使用 Boost 构建应用

Laravel MCP 包含专门用于构建 MCP Apps 的 [Boost](/docs/{{version}}/boost) 技能参考。如果你安装了 [Laravel Boost](/docs/{{version}}/boost)，可以让 AI 编码智能体调用 `mcp-development` 技能，为你生成应用资源、Blade 视图和关联工具的基础代码。

完整的协议参考，包括全部客户端 API 和模式详情，请参阅官方 [MCP Apps 文档](https://modelcontextprotocol.io/extensions/apps/overview)。

<a name="metadata"></a>
## 元数据

Laravel MCP 还支持 [MCP 规范](https://modelcontextprotocol.io/specification/2026-07-28/basic#_meta)定义的 `_meta` 字段，某些 MCP 客户端或集成需要此字段。元数据可以应用于所有 MCP 基础组件，包括工具、资源、提示词及其响应。

你可以使用 `withMeta` 方法为单个响应内容附加元数据：

```php
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;

/**
 * 处理工具请求。
 */
public function handle(Request $request): Response
{
    return Response::text('The weather is sunny.')
        ->withMeta(['source' => 'weather-api', 'cached' => true]);
}
```

对于应用于整个响应封装的结果级元数据，请使用 `Response::make` 包装响应，并在返回的响应工厂实例上调用 `withMeta`：

```php
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;
use Laravel\Mcp\ResponseFactory;

/**
 * 处理工具请求。
 */
public function handle(Request $request): ResponseFactory
{
    return Response::make(
        Response::text('The weather is sunny.')
    )->withMeta(['request_id' => '12345']);
}
```

要为工具、资源或提示词本身附加元数据，请在类中定义 `$meta` 属性：

```php
use Laravel\Mcp\Server\Attributes\Description;
use Laravel\Mcp\Server\Tool;

#[Description('Fetches the current weather forecast.')]
class CurrentWeatherTool extends Tool
{
    protected ?array $meta = [
        'version' => '2.0',
        'author' => 'Weather Team',
    ];

    // ...
}
```

<a name="icons"></a>
## 图标

MCP 客户端可以显示服务器及其基础组件的图标。你可以使用 `Icon` 特性，在服务器、工具、资源或提示词上声明图标：

```php
use Laravel\Mcp\Enums\IconTheme;
use Laravel\Mcp\Server\Attributes\Icon;

#[Icon('mcp/server.png', mimeType: 'image/png', sizes: ['48x48'])]
#[Icon('mcp/server-dark.svg', theme: IconTheme::Dark)]
class WeatherServer extends Server
{
    // ...
}
```

`Icon` 特性可以重复使用，因此你可以声明多个图标，以提供不同尺寸或浅色、深色主题的变体。

你也可以重写 `icons` 方法，以编程方式定义图标。当图标取决于运行时条件时，这种方式非常实用：

```php
use Laravel\Mcp\Schema\Icon;

class CurrentWeatherTool extends Tool
{
    /**
     * 获取工具的图标。
     *
     * @return array<int, Icon>
     */
    public function icons(): array
    {
        return [
            Icon::from('mcp/tool.png', mimeType: 'image/png'),
        ];
    }
}
```

通过特性和 `icons` 方法定义的图标会自动合并。图标路径按以下规则解析：

<div class="content-list" markdown="1">

- 带有 `https:` 或 `data:` 等 URI 方案的路径按原样使用。
- 相对路径使用 Laravel 的 `asset` 辅助函数解析为 URL。

</div>

<a name="authentication"></a>
## 身份认证

与路由一样，你可以使用中间件对 Web MCP 服务器进行身份认证。为 MCP 服务器添加身份认证后，用户必须先通过认证才能使用服务器的任何功能。

本节介绍外部 AI 客户端访问**你的应用的 MCP 服务器**时的认证。如果要使用用户凭据将你的应用连接到其他服务的 MCP 服务器，请参阅[客户端身份认证](#client-authentication)。

你可以通过两种方式对 MCP 服务器的访问进行身份认证：使用 [Laravel Sanctum](/docs/{{version}}/sanctum)，或通过 `Authorization` HTTP 请求头传入任意令牌，进行简单的令牌认证；也可以使用 [Laravel Passport](/docs/{{version}}/passport) 进行 OAuth 认证。

<a name="oauth"></a>
### OAuth 2.1

保护 Web MCP 服务器最完善的方式，是通过 [Laravel Passport](/docs/{{version}}/passport) 使用 OAuth 认证。

通过 OAuth 对 MCP 服务器进行身份认证时，请在 `routes/ai.php` 文件中调用 `Mcp::oauthRoutes` 方法，注册所需的 OAuth2 发现路由和客户端注册路由。然后，在同一文件中为 `Mcp::web` 路由应用 Passport 的 `auth:api` 中间件：

```php
use App\Mcp\Servers\WeatherExample;
use Laravel\Mcp\Facades\Mcp;

Mcp::oauthRoutes();

Mcp::web('/mcp/weather', WeatherExample::class)
    ->middleware('auth:api');
```

<a name="new-passport-installation"></a>
#### 全新安装 Passport

如果你的应用尚未使用 Laravel Passport，请按照 Passport 的[安装和部署指南](/docs/{{version}}/passport#installation)将其添加到应用中。继续之前，你应准备好一个 `OAuthenticatable` 模型、新的认证看守器以及 Passport 密钥。

接下来，发布 Laravel MCP 提供的 Passport 授权视图：

```shell
php artisan vendor:publish --tag=mcp-views
```

然后，使用 `Passport::authorizationView` 方法让 Passport 使用该视图。通常应在应用的 `AppServiceProvider` 的 `boot` 方法中调用此方法：

```php
use Laravel\Passport\Passport;

/**
 * 引导应用服务。
 */
public function boot(): void
{
    Passport::authorizationView(function ($parameters) {
        return view('mcp.authorize', $parameters);
    });
}
```

在身份认证期间，此视图会显示给最终用户，让他们拒绝或批准 AI 智能体的认证请求。

![授权界面示例](https://cdn.learnku.com/uploads/images/202610/23/7400/eog2cyQ42f.png!large)

> [!NOTE]
> 在此场景中，我们只是将 OAuth 用作与底层可认证模型之间的转换层，并未处理 OAuth 的许多方面，例如作用域。

#### 使用现有的 Passport 安装

如果你的应用已使用 Laravel Passport，Laravel MCP 应能与现有的 Passport 安装无缝配合。不过，由于 OAuth 主要被用作与底层可认证模型之间的转换层，目前不支持自定义作用域。

Laravel MCP 通过上述 `Mcp::oauthRoutes` 方法，添加、公布并使用单一的 `mcp:use` 作用域。

#### Passport 与 Sanctum

OAuth2.1 是模型上下文协议规范中规定的身份认证机制，也是 MCP 客户端支持最广泛的机制。因此，我们建议尽可能使用 Passport。

如果你的应用已使用 [Sanctum](/docs/{{version}}/sanctum)，再添加 Passport 可能较为繁琐。在这种情况下，我们建议继续使用 Sanctum，直到明确需要使用仅支持 OAuth 的 MCP 客户端时，再添加 Passport。

<a name="rate-limiting-oauth-routes"></a>
#### 限制 OAuth 路由的请求频率

根据 MCP 规范和 RFC 7591 的要求，`Mcp::oauthRoutes` 注册的动态客户端注册路由可公开访问，允许任意 MCP 客户端无需身份认证即可注册。由于每次注册都会在数据库中创建新的 OAuth 客户端，你应根据应用的流量对这些路由进行频率限制。为此，可以在应用 Laravel `throttle` 中间件的路由组内注册这些路由：

```php
use Illuminate\Support\Facades\Route;
use Laravel\Mcp\Facades\Mcp;

Route::middleware('throttle:10,1')->group(function () {
    Mcp::oauthRoutes();
});
```

如果 MCP 客户端无需动态注册自身，你可以将 `registration` 参数设为 `false`，完全禁用客户端注册路由：

```php
Mcp::oauthRoutes(registration: false);
```

<a name="sanctum"></a>
### Sanctum

如果你想使用 [Sanctum](/docs/{{version}}/sanctum) 保护 MCP 服务器，只需在 `routes/ai.php` 文件中为服务器添加 Sanctum 的身份认证中间件。然后，确保 MCP 客户端提供 `Authorization: Bearer <token>` 请求头，以顺利通过身份认证：

```php
use App\Mcp\Servers\WeatherExample;
use Laravel\Mcp\Facades\Mcp;

Mcp::web('/mcp/demo', WeatherExample::class)
    ->middleware('auth:sanctum');
```

<a name="custom-mcp-authentication"></a>
#### 自定义 MCP 身份认证

如果你的应用签发自定义 API 令牌，你可以为 `Mcp::web` 路由分配任意中间件，对 MCP 服务器进行身份认证。自定义中间件可以手动检查 `Authorization` 请求头，以认证传入的 MCP 请求。

<a name="authorization"></a>
## 授权

你可以通过 `$request->user()` 方法访问当前已认证用户，从而在 MCP 工具和资源中执行[授权检查](/docs/{{version}}/authorization)：

```php
use Laravel\Mcp\Request;
use Laravel\Mcp\Response;

/**
 * 处理工具请求。
 */
public function handle(Request $request): Response
{
    if (! $request->user()->can('read-weather')) {
        return Response::error('Permission denied.');
    }

    // ...
}
```

<a name="client"></a>
## MCP 客户端

除了构建服务器，Laravel MCP 还包含一个客户端，可连接第一方或第三方的其他 MCP 服务器。客户端让应用能够发现并调用 MCP 服务器开放的工具，尤其适合让 [AI 智能体](/docs/{{version}}/ai-sdk#mcp-tools)使用外部 MCP 服务器提供的能力。

例如，聊天应用可以使用每个用户的 GitHub 令牌连接 GitHub 的 MCP 服务器，让智能体回答有关该用户仓库的问题。在此场景中，你的应用是 MCP 客户端，无需创建 MCP 服务器或注册 `Mcp::web` 路由。

<a name="client-connecting"></a>
### 连接服务器

你可以使用 `Client::web` 方法连接可通过 HTTP 访问的 MCP 服务器，并传入服务器的 URL：

```php
use Laravel\Mcp\Client;

$client = Client::web('https://api.githubcopilot.com/mcp/');
```

要连接以命令形式运行的本地 MCP 服务器，请使用 `Client::local` 方法，提供启动服务器所需的命令和参数：

```php
use Laravel\Mcp\Client;

$client = Client::local('php', ['artisan', 'mcp:start']);
```

客户端采用延迟连接，首次列出或调用工具时会自动建立连接。如果需要手动管理连接，可以使用 `connect`、`connected` 和 `disconnect` 方法：

```php
$client->connect();

if ($client->connected()) {
    $capabilities = $client->capabilities();
    $server = $client->serverInfo();
}

$client->disconnect();
```

你可以使用 `withTimeout` 方法自定义请求超时时间：

```php
$client = Client::web('https://api.githubcopilot.com/mcp/')->withTimeout(30);
```

<a name="named-clients"></a>
### 命名客户端

你可以选择注册可复用的命名客户端，而无需在每次使用时构建客户端。`registerClient` 方法为出站连接命名；它不会开放 MCP 服务器，也不会为用户授予权限。通常使用 `Mcp` 门面，在服务提供者的 `boot` 方法中完成注册：

```php
use Laravel\Mcp\Client;
use Laravel\Mcp\Facades\Mcp;

Mcp::registerClient('github', fn () => Client::web('https://api.githubcopilot.com/mcp/'));
```

注册后，你可以在应用中的任意位置按名称解析客户端：

```php
use Laravel\Mcp\Facades\Mcp;

$client = Mcp::client('github');
```

命名客户端在每个请求中只解析一次，并在请求生命周期结束时自动断开连接。

<a name="client-authentication"></a>
### 客户端身份认证

<a name="client-bearer-tokens"></a>
#### Bearer 令牌

要连接受 Bearer 令牌保护的 Web MCP 服务器，请使用 `withToken` 方法。你可以传入令牌字符串，也可以传入延迟解析令牌的闭包：

```php
use Illuminate\Support\Facades\Auth;
use Laravel\Mcp\Client;

$client = Client::web('https://api.githubcopilot.com/mcp/')->withToken(
    config('services.github_mcp.token'),
);

$client = Client::web('https://api.githubcopilot.com/mcp/')->withToken(
    fn () => Auth::user()->github_mcp_token,
);
```

如果你已通过 [Socialite](/docs/{{version}}/socialite) 或其他账户关联流程获得合适的令牌，将它传入 `withToken` 即可，无需注册 MCP OAuth 路由。

<a name="client-oauth"></a>
#### 使用 OAuth 关联用户账户

设想一个聊天应用：用户关联项目管理服务后，向智能体提问「我有哪些任务已逾期？」外部项目管理服务开放了一个受 OAuth 保护的 MCP 服务器。你的应用必须将每个用户重定向到该服务的授权同意页面，用其批准结果换取令牌，并保存令牌以供未来调用工具时使用。

Laravel MCP 使用 `withOAuth` 和 `Mcp::oAuthRoutesFor` 处理此账户关联流程。首先，在服务提供者中注册命名客户端。OAuth 客户端凭据用于向服务标识你的应用，而 `withToken` 则在调用工具时提供已关联用户所保存的访问令牌：

```php
use Illuminate\Support\Facades\Auth;
use Laravel\Mcp\Client;
use Laravel\Mcp\Facades\Mcp;

Mcp::registerClient('projects', fn () => Client::web('https://projects.example.com/mcp')
    ->withOAuth(
        clientId: config('services.projects.client_id'),
        clientSecret: config('services.projects.client_secret'),
    )
    ->withToken(fn () => Auth::user()->projects_token));
```

> [!NOTE]
> `clientId` 和 `clientSecret` 参数可以省略。如果授权服务器支持，Laravel 会使用[客户端 ID 元数据文档](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration#client-id-metadata-documents)；对于旧版服务器，则回退到[动态客户端注册](https://datatracker.ietf.org/doc/html/rfc7591)。

授权服务器必须在其授权服务器元数据中公布对 `S256` PKCE 代码质询方法的支持。如果未公布 PKCE 支持，Laravel 将拒绝授权尝试。

接下来，在 `routes/ai.php` 文件中注册账户关联路由。回调会接收客户端名称和生成的 `TokenSet`，以便为已登录用户保存令牌：

```php
use Illuminate\Support\Facades\Auth;
use Laravel\Mcp\Client\OAuth\TokenSet;
use Laravel\Mcp\Facades\Mcp;

Mcp::oAuthRoutesFor('projects', function (string $client, TokenSet $token) {
    Auth::user()->update([
        'projects_token' => $token->accessToken,
    ]);

    return redirect('/chat');
}, middleware: ['web', 'auth']);
```

`oAuthRoutesFor` 方法会注册三个命名路由：连接路由（`mcp.oauth.{client}.connect`）将用户重定向到授权服务器；回调路由（`mcp.oauth.{client}.callback`）交换授权码并调用你的处理程序；公开的客户端 ID 元数据文档路由为 `mcp.oauth.{client}.client-metadata`。

连接路由和回调路由默认使用 `web` 中间件组；上面的账户关联示例还添加了 `auth`，要求用户先登录。元数据路由不使用此中间件，因为授权服务器必须能够获取该文档。

「连接项目服务」按钮应将用户导向连接路由：

```php
return redirect()->route('mcp.oauth.projects.connect');
```

Laravel 会将用户重定向到服务以批准访问，在用户返回后交换授权码，并调用你的回调。在后续聊天请求中，命名客户端会使用保存的令牌。例如，[AI SDK 智能体](/docs/{{version}}/ai-sdk#mcp-tools)可以开放此服务的工具：

```php
public function tools(): iterable
{
    return [
        ...Mcp::client('projects')->tools(),
    ];
}
```

使用[加密类型转换](/docs/{{version}}/eloquent-mutators#encrypted-casting)保存令牌，并在模型序列化时隐藏它们。如果服务签发的令牌会过期，还应保存 `TokenSet` 中的刷新令牌和过期信息，并在调用工具之前处理续期。对于队列中的智能体，请从显式提供的用户解析凭据，而非使用 `Auth::user()`。

> [!NOTE]
> `Mcp::oAuthRoutesFor` 将你的用户关联到外部服务。相比之下，`Mcp::oauthRoutes` 允许外部 AI 客户端使用 Passport 认证并访问你自己的 MCP 服务器。上述账户关联流程无需使用 Passport 或 `Mcp::oauthRoutes`。

<a name="client-metadata"></a>
#### 客户端元数据

元数据文档将你的应用描述为公共 OAuth 客户端，并使用应用的 `APP_URL` 生成客户端 ID 和回调 URL。因此，你应确保生产环境中的 `APP_URL` 环境变量设置正确。你可以使用 `clientMetadataUri` 和 `clientMetadata` 参数自定义元数据路由，并提供额外的元数据：

```php
use Laravel\Mcp\Client\OAuth\TokenSet;
use Laravel\Mcp\Facades\Mcp;

Mcp::oAuthRoutesFor(
    'projects',
    function (string $client, TokenSet $token) {
        // 保存令牌……

        return redirect('/dashboard');
    },
    clientMetadataUri: 'oauth/projects/client.json',
    clientMetadata: [
        'client_name' => 'Acme Dashboard',
        'logo_uri' => 'https://acme.com/logo.png',
    ],
);
```

<a name="client-tools"></a>
### 工具

你可以使用 `tools` 方法获取 MCP 服务器开放的工具，该方法返回以名称为键的工具集合：

```php
use Laravel\Mcp\Facades\Mcp;

$tools = Mcp::client('github')->tools();

foreach ($tools as $tool) {
    $tool->name;
    $tool->title;
    $tool->description;
    $tool->inputSchema;
}
```

客户端会自动分页获取所有可用工具。你可以使用 `limit` 参数限制返回的工具数量：

```php
$tools = Mcp::client('github')->tools(limit: 10);
```

要调用工具，请使用 `callTool` 方法，传入工具名称和参数数组。返回的 `ToolResult` 实例提供对工具响应的访问：

```php
use Laravel\Mcp\Facades\Mcp;

$result = Mcp::client('github')->callTool('list_issues', [
    'owner' => 'laravel',
    'repo' => 'framework',
]);

$result->text(); // 响应的文本内容……
(string) $result; // 等同于调用 text()……
$result->isError; // 工具是否报告了错误……
$result->structuredContent;  // 结构化内容（如果有）……
```

你也可以直接从已列出的工具实例调用工具：

```php
$tools = Mcp::client('github')->tools();

$result = $tools['list_issues']->call([
    'owner' => 'laravel',
    'repo' => 'framework',
]);
```

如果你使用 [Laravel AI SDK](/docs/{{version}}/ai-sdk) 构建智能体，也可以将 MCP 客户端中的工具直接提供给智能体，让模型在响应提示词时调用它们。更多信息请参阅 AI SDK 文档的 [MCP 工具](/docs/{{version}}/ai-sdk#mcp-tools)一节。

<a name="client-prompts"></a>
### 提示词

你可以使用 `prompts` 方法获取 MCP 服务器开放的提示词，该方法返回以名称为键的提示词集合：

```php
use Laravel\Mcp\Facades\Mcp;

$prompts = Mcp::client('github')->prompts();

foreach ($prompts as $prompt) {
    $prompt->name;
    $prompt->title;
    $prompt->description;
    $prompt->arguments;
}
```

客户端会自动分页获取所有可用提示词。你可以使用 `limit` 参数限制返回的提示词数量：

```php
$prompts = Mcp::client('github')->prompts(limit: 10);
```

要获取提示词，请使用 `getPrompt` 方法，传入提示词名称和参数数组。返回的 `PromptResult` 实例提供对生成消息的访问：

```php
use Laravel\Mcp\Facades\Mcp;

$result = Mcp::client('github')->getPrompt('issue_to_fix_workflow', [
    'owner' => 'laravel',
    'repo' => 'framework',
    'title' => 'Fix typo in README',
    'description' => 'The installation section has a typo.',
]);

$result->text(); // 消息的文本内容……
(string) $result; // 等同于调用 text()……
$result->messages; // 提示词返回的原始消息……
$result->description; // 提示词描述（如果有）……
```

<a name="client-resources"></a>
### 资源

你可以使用 `resources` 方法获取 MCP 服务器开放的资源，该方法返回以 URI 为键的资源集合：

```php
use Laravel\Mcp\Facades\Mcp;

$resources = Mcp::client('github')->resources();

foreach ($resources as $resource) {
    $resource->uri;
    $resource->name;
    $resource->title;
    $resource->description;
    $resource->mimeType;
    $resource->size;
}
```

客户端会自动分页获取所有可用资源。你可以使用 `limit` 参数限制返回的资源数量：

```php
$resources = Mcp::client('github')->resources(limit: 10);
```

要读取资源，请使用 `readResource` 方法，并传入资源 URI。返回的 `ResourceReadResult` 实例提供对资源内容的访问：

```php
use Laravel\Mcp\Facades\Mcp;

$result = Mcp::client('github')->readResource('repo://laravel/framework/contents/README.md');

$result->content(); // 资源内容，按需解码 base64 Blob……
(string) $result; // 等同于调用 content()……
$result->mimeType(); // 资源的 MIME 类型（如果有）……
$result->contents; // 资源返回的原始内容……
```

<a name="testing-servers"></a>
## 测试服务器

你可以使用内置的 MCP Inspector 或编写单元测试来测试 MCP 服务器。

<a name="mcp-inspector"></a>
### MCP Inspector

交互式工具 [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) 用于测试和调试 MCP 服务器。你可以用它连接服务器、验证身份认证，并试用工具、资源和提示词。

你可以为任意已注册的服务器运行 Inspector：

```shell
# Web 服务器……
php artisan mcp:inspector mcp/weather

# 名为「weather」的本地服务器……
php artisan mcp:inspector weather
```

此命令会启动 MCP Inspector，并提供可复制到 MCP 客户端的客户端设置，以确保配置正确。如果 Web 服务器受身份认证中间件保护，请确保连接时包含所需的请求头，例如 `Authorization` Bearer 令牌。

<a name="unit-tests"></a>
### 单元测试

你可以为 MCP 服务器、工具、资源和提示词编写单元测试。

首先，创建一个新的测试用例，并在注册了目标基础组件的服务器上调用它。例如，要测试 `WeatherServer` 上的工具：

```php tab=Pest
test('tool', function () {
    $response = WeatherServer::tool(CurrentWeatherTool::class, [
        'location' => 'New York City',
        'units' => 'fahrenheit',
    ]);

    $response
        ->assertOk()
        ->assertSee('The current weather in New York City is 72°F and sunny.');
});
```

```php tab=PHPUnit
/**
 * 测试工具。
 */
public function test_tool(): void
{
    $response = WeatherServer::tool(CurrentWeatherTool::class, [
        'location' => 'New York City',
        'units' => 'fahrenheit',
    ]);

    $response
        ->assertOk()
        ->assertSee('The current weather in New York City is 72°F and sunny.');
}
```

同样，你也可以测试提示词和资源：

```php
$response = WeatherServer::prompt(...);
$response = WeatherServer::resource(...);
```

你还可以在调用基础组件之前链式调用 `actingAs` 方法，以已认证用户的身份进行操作：

```php
$response = WeatherServer::actingAs($user)->tool(...);
```

收到响应后，你可以使用各种断言方法验证响应的内容和状态。

你可以使用 `assertOk` 方法断言响应成功。此方法会检查响应是否没有任何错误：

```php
$response->assertOk();
```

你可以使用 `assertSee` 方法断言响应包含指定文本：

```php
$response->assertSee('The current weather in New York City is 72°F and sunny.');
```

你可以使用 `assertHasErrors` 方法断言响应包含错误：

```php
$response->assertHasErrors();

$response->assertHasErrors([
    'Something went wrong.',
]);
```

你可以使用 `assertHasNoErrors` 方法断言响应不包含错误：

```php
$response->assertHasNoErrors();
```

你可以使用 `assertName()`、`assertTitle()` 和 `assertDescription()` 方法断言响应包含指定的元数据：

```php
$response->assertName('current-weather');
$response->assertTitle('Current Weather Tool');
$response->assertDescription('Fetches the current weather forecast for a specified location.');
```

你可以使用 `assertSentNotification` 和 `assertNotificationCount` 方法断言通知已发送：

```php
$response->assertSentNotification('processing/progress', [
    'step' => 1,
    'total' => 5,
]);

$response->assertSentNotification('processing/progress', [
    'step' => 2,
    'total' => 5,
]);

$response->assertNotificationCount(5);
```

最后，如果你希望检查原始响应内容，可以使用 `dd` 或 `dump` 方法输出响应以进行调试：

```php
$response->dd();
$response->dump();
```
