
# Laravel Pulse

-   [简介](#introduction)
-   [安装](#installation)
    -   [配置](#configuration)
-   [仪表盘](#dashboard)
    -   [授权](#dashboard-authorization)
    -   [自定义](#dashboard-customization)
    -   [解析用户](#dashboard-resolving-users)
    -   [卡片](#dashboard-cards)
-   [捕获条目](#capturing-entries)
    -   [记录器](#recorders)
    -   [过滤](#filtering)
-   [性能](#performance)
    -   [使用不同的数据库](#using-a-different-database)
    -   [Redis 写入](#ingest)
    -   [采样](#sampling)
    -   [修剪](#trimming)
    -   [处理 Pulse 异常](#pulse-exceptions)
-   [自定义卡片](#custom-cards)
    -   [卡片组件](#custom-card-components)
    -   [样式](#custom-card-styling)
    -   [数据捕获与聚合](#custom-card-data)
## 简介

[Laravel Pulse](https://github.com/laravel/pulse) 可让你一目了然地洞察应用的性能与使用情况。通过 Pulse，你可以追踪性能瓶颈（如慢任务和慢接口）、找到最活跃的用户等。

如果需要对单个事件进行深入调试，请查看 [Laravel Telescope](/docs/laravel/12.x/telescope)。

## 安装

> [!警告]
> Pulse 的官方存储实现目前需要 MySQL、MariaDB 或 PostgreSQL 数据库。如果你正在使用其他数据库引擎，则需要单独准备一个 MySQL、MariaDB 或 PostgreSQL 数据库来存储 Pulse 数据。

你可以使用 Composer 包管理器安装 Pulse：

```shell
composer require laravel/pulse
```

接着，你需要使用 `vendor:publish` Artisan 命令发布 Pulse 的配置文件和迁移文件：

```shell
php artisan vendor:publish --provider="Laravel\Pulse\PulseServiceProvider"
```

最后，你需要运行 `migrate` 命令来创建存储 Pulse 数据所需的数据表：

```shell
php artisan migrate
```

当 Pulse 的数据库迁移执行完毕后，你就可以通过 `/pulse` 路由访问 Pulse 仪表盘了。

> [!注意]
> 如果你不想将 Pulse 数据存储在应用的主数据库中，可以 [指定一个独立的数据库连接](#using-a-different-database)。



### 配置

Pulse 的许多配置选项都可以通过环境变量来控制。若要查看可用选项、注册新的记录器或配置高级选项，你可以发布 `config/pulse.php` 配置文件：

```shell
php artisan vendor:publish --tag=pulse-config
```

## 仪表盘

### 授权

Pulse 仪表盘可以通过 `/pulse` 路由访问。默认情况下，你只能在 `local` 环境中访问此仪表盘，因此在生产环境中，你需要通过自定义 `'viewPulse'` 授权 Gate 来配置访问权限。你可以在应用的 `app/Providers/AppServiceProvider.php` 文件中完成此操作：

```php
use App\Models\User;
use Illuminate\Support\Facades\Gate;

/**
 * 启动任何应用服务
 */
public function boot(): void
{
    Gate::define('viewPulse', function (User $user) {
        return $user->isAdmin();
    });

    // ...
}
```

### 自定义

Pulse 仪表盘的卡片和布局可以通过发布仪表盘视图来进行配置。该视图会被发布到 `resources/views/vendor/pulse/dashboard.blade.php`：

```shell
php artisan vendor:publish --tag=pulse-dashboard
```

仪表盘由 [Livewire](https://livewire.laravel.com/) 驱动，你可以自定义卡片和布局，而无需重新构建任何 JavaScript 资源。

在此文件中，`<x-pulse>` 组件负责渲染仪表盘，并为卡片提供网格布局。如果你希望仪表盘占据整个屏幕宽度，可以为该组件提供 `full-width` 属性：

```blade
<x-pulse full-width>
    ...
</x-pulse>
```

默认情况下，`<x-pulse>` 组件会创建一个 12 列的网格，但你可以通过 `cols` 属性进行自定义：

```blade
<x-pulse cols="16">
    ...
</x-pulse>
```



每个卡片都可以接受 `cols` 和 `rows` 属性，用于控制空间与位置：

```blade
<livewire:pulse.usage cols="4" rows="2" />
```

大多数卡片还可以接受一个 `expand` 属性，用于显示完整卡片而不是滚动：

```blade
<livewire:pulse.slow-queries expand />
```

### 解析用户

对于显示用户信息的卡片（例如 **应用使用情况** 卡片），Pulse 只会记录用户的 ID。在渲染仪表盘时，Pulse 会从默认的 `Authenticatable` 模型中解析 `name` 和 `email` 字段，并使用 Gravatar 网络服务来显示头像。

你可以在应用的 `App\Providers\AppServiceProvider` 类中调用 `Pulse::user` 方法来自定义这些字段和头像。

`user` 方法接受一个闭包，该闭包会接收要展示的 `Authenticatable` 模型，并应返回一个包含 `name`、`extra` 和 `avatar` 信息的数组：

```php
use Laravel\Pulse\Facades\Pulse;

/**
 * 启动任何应用服务
 */
public function boot(): void
{
    Pulse::user(fn ($user) => [
        'name' => $user->name,
        'extra' => $user->email,
        'avatar' => $user->avatar_url,
    ]);

    // ...
}
```

> [!笔记]
> 你可以通过实现 `Laravel\Pulse\Contracts\ResolvesUsers` 合约并将其绑定到 Laravel 的 [服务容器](/docs/laravel/12.x/container#binding-a-singleton)，来完全自定义已认证用户的捕获与解析方式。

### 卡片

#### 服务器

`<livewire:pulse.servers />` 卡片会显示运行 `pulse:check` 命令的所有服务器的系统资源使用情况。请参考有关 [服务器记录器](#servers-recorder) 的文档以获取更多系统资源报告的信息。

如果你在基础设施中替换了一台服务器，你可能希望在一段时间后停止在 Pulse 仪表盘中显示这台不再活跃的服务器。你可以使用 `ignore-after` 属性来实现，它接受一个秒数，超过该秒数后不活跃的服务器会从 Pulse 仪表盘中移除。或者，你也可以提供一个相对时间格式的字符串，例如 `1 hour` 或 `3 days and 1 hour`：

```blade
<livewire:pulse.servers ignore-after="3 hours" />
```



#### 应用使用情况

`<livewire:pulse.usage />` 卡片会显示向你的应用发出请求、分发任务以及遇到慢请求的 **前 10 位用户**。

如果你希望在屏幕上同时查看所有使用情况指标，可以多次引入该卡片，并通过 `type` 属性来指定类型：

```blade
<livewire:pulse.usage type="requests" />
<livewire:pulse.usage type="slow_requests" />
<livewire:pulse.usage type="jobs" />
```
要了解如何自定义 Pulse 获取和显示用户信息的方式，请参阅我们关于 [解析用户](#dashboard-resolving-users) 的文档。

> [!注意]
> 如果你的应用接收了大量请求或分发了大量任务，你可能需要启用 [采样](#sampling)。更多信息请参阅 [用户请求记录器](#user-requests-recorder)、[用户任务记录器](#user-jobs-recorder) 以及 [慢任务记录器](#slow-jobs-recorder) 文档。

#### 异常

`<livewire:pulse.exceptions />` 卡片会显示应用中发生的异常的频率和最近情况。默认情况下，异常会根据 **异常类** 和 **发生位置** 进行分组。更多信息请参阅 [异常记录器](#exceptions-recorder) 文档。

#### 队列

`<livewire:pulse.queues />` 卡片会显示应用中队列的吞吐量，包括 **排队中、正在处理、已处理、已释放和失败的任务数量**。更多信息请参阅 [队列记录器](#queues-recorder) 文档。

#### 慢请求

`<livewire:pulse.slow-requests />` 卡片会显示进入应用的 **超过配置阈值的请求**，默认阈值为 **1000ms**。更多信息请参阅 [慢请求记录器](#slow-requests-recorder) 文档。




#### 慢任务

`<livewire:pulse.slow-jobs />` 卡片会显示应用中 **超过配置阈值的队列任务**，默认阈值为 **1000ms**。更多信息请参阅 [慢任务记录器](#slow-jobs-recorder) 文档。

#### 慢查询

`<livewire:pulse.slow-queries />` 卡片会显示应用中 **超过配置阈值的数据库查询**，默认阈值为 **1000ms**。

默认情况下，慢查询会根据 **SQL 语句（不含绑定参数）** 以及 **发生位置** 进行分组，但如果你希望只按 SQL 语句分组，也可以选择不捕获位置。

如果由于 **非常大的 SQL 查询在进行语法高亮时** 导致渲染性能问题，你可以通过添加 `without-highlighting` 属性来禁用高亮：

```blade
<livewire:pulse.slow-queries without-highlighting />
```

更多信息请参阅 [慢查询记录器](#slow-queries-recorder) 文档。

#### 慢出站请求

`<livewire:pulse.slow-outgoing-requests />` 卡片会显示通过 Laravel 的 [HTTP 客户端](/docs/laravel/12.x/http-client) 发出的 **超过配置阈值的出站请求**，默认阈值为 **1000ms**。

默认情况下，条目会根据完整 URL 进行分组。但如果你希望对类似的出站请求进行归一化或使用正则表达式进行分组，也可以实现。更多信息请参阅 [慢出站请求记录器](#slow-outgoing-requests-recorder) 文档。

#### 缓存

`<livewire:pulse.cache />` 卡片会显示应用的 **缓存命中率和未命中统计信息**，包括全局和单个 key 的数据。

默认情况下，条目会按 key 分组。但如果你希望对类似的 key 进行归一化或使用正则表达式分组，也可以实现。更多信息请参阅 [缓存交互记录器](#cache-interactions-recorder) 文档。



## 捕获条目

大多数 Pulse 记录器会基于 Laravel 派发的框架事件自动捕获条目。然而，[服务器记录器](#servers-recorder) 和一些第三方卡片必须定期轮询信息。要使用这些卡片，你必须在每台应用服务器上运行 `pulse:check` 守护进程：

```php
php artisan pulse:check
```

> [!注意]
> 为了让 `pulse:check` 进程在后台永久运行，你应使用像 Supervisor 这样的进程监控工具，以确保该命令不会停止运行。

由于 `pulse:check` 命令是一个长时间运行的进程，它不会自动看到代码库的更改，因此在部署时需要重启。你应在应用部署过程中通过调用 `pulse:restart` 命令优雅地重启该进程：

```shell
php artisan pulse:restart
```

> [!注意]
> Pulse 使用 [缓存](/docs/laravel/12.x/cache) 来存储重启信号，因此在使用此功能前，应确保你的应用正确配置了缓存驱动。

### 记录器

记录器负责从应用中捕获条目，并将其记录到 Pulse 数据库中。记录器在 [Pulse 配置文件](#configuration) 的 `recorders` 部分进行注册和配置。

#### 缓存交互

`CacheInteractions` 记录器会捕获应用中发生的 [缓存](/docs/laravel/12.x/cache) 命中与未命中信息，并在 [缓存卡片](#cache-card) 上显示。

你可以选择性地调整 [采样率](#sampling) 和忽略的 key 模式。

你还可以配置 key 分组，以便将类似的 key 归为单个条目。例如，你可能希望从缓存相同类型信息的 key 中去掉唯一 ID。分组通过正则表达式来 “查找并替换” key 的部分内容。配置文件中包含了一个示例：

```php
Recorders\CacheInteractions::class => [
    // ...
    'groups' => [
        // '/:\d+/' => ':*',
    ],
],
```



第一个匹配的模式将被使用。如果没有任何模式匹配，则该 key 会按原样捕获。

#### 异常

`Exceptions` 记录器会捕获应用中可报告的异常信息，并在 [异常卡片](#exceptions-card) 上显示。

你可以选择性地调整 [采样率](#sampling) 和忽略的异常模式。你还可以配置是否捕获异常的来源位置。捕获的位置会显示在 Pulse 仪表盘上，有助于追踪异常的来源；不过，如果同一异常发生在多个位置，它将在每个唯一位置上分别显示多次。

#### 队列

`Queues` 记录器会捕获应用中队列的相关信息，并在 [队列卡片](#queues-card) 上显示。

你可以选择性地调整 [采样率](#sampling) 和忽略的任务模式。

#### 慢任务

`SlowJobs` 记录器会捕获应用中执行缓慢的任务信息，并在 [慢任务卡片](#slow-jobs-recorder) 上显示。

你可以选择性地调整慢任务阈值、[采样率](#sampling) 以及忽略的任务模式。

对于一些你预期执行时间较长的任务，你可以为每个任务单独配置阈值：

```php
Recorders\SlowJobs::class => [
    // ...
    'threshold' => [
        '#^App\\Jobs\\GenerateYearlyReports$#' => 5000,
        'default' => env('PULSE_SLOW_JOBS_THRESHOLD', 1000),
    ],
],
```

如果没有任何正则表达式模式匹配任务的类名，则会使用 `'default'` 的值。

#### 慢出站请求

`SlowOutgoingRequests` 记录器会捕获通过 Laravel [HTTP 客户端](/docs/laravel/12.x/http-client) 发出的 **超过配置阈值的出站 HTTP 请求**，并在 [慢出站请求卡片](#slow-outgoing-requests-card) 上显示。



你可以选择性地调整慢出站请求的阈值、[采样率](#sampling) 以及忽略的 URL 模式。

对于一些你预期执行时间较长的出站请求，你可以为每个请求单独配置阈值：

```php
Recorders\SlowOutgoingRequests::class => [
    // ...
    'threshold' => [
        '#backup.zip$#' => 5000,
        'default' => env('PULSE_SLOW_OUTGOING_REQUESTS_THRESHOLD', 1000),
    ],
],
```

如果没有任何正则表达式模式匹配请求的 URL，则会使用 `'default'` 的值。

你还可以配置 URL 分组，以便将类似的 URL 归为单个条目。例如，你可能希望从 URL 路径中去掉唯一 ID，或者仅按域名进行分组。分组通过正则表达式来 “查找并替换” URL 的部分内容。配置文件中包含一些示例：

```php
Recorders\SlowOutgoingRequests::class => [
    // ...
    'groups' => [
        // '#^https://api\.github\.com/repos/.*$#' => 'api.github.com/repos/*',
        // '#^https?://([^/]*).*$#' => '\1',
        // '#/\d+#' => '/*',
    ],
],
```

第一个匹配的模式将被使用。如果没有任何模式匹配，则 URL 会按原样捕获。

#### 慢查询

`SlowQueries` 记录器会捕获应用中 **超过配置阈值的数据库查询**，并在 [慢查询卡片](#slow-queries-card) 上显示。

你可以选择性地调整慢查询阈值、[采样率](#sampling) 以及忽略的查询模式。你还可以配置是否捕获查询发生的位置。捕获的位置会显示在 Pulse 仪表盘上，有助于追踪查询来源；不过，如果同一查询在多个位置执行，它将在每个唯一位置分别显示多次。




对于一些你预期执行时间较长的查询，你可以为每个查询单独配置阈值：

```php
Recorders\SlowQueries::class => [
    // ...
    'threshold' => [
        '#^insert into `yearly_reports`#' => 5000,
        'default' => env('PULSE_SLOW_QUERIES_THRESHOLD', 1000),
    ],
],
```

如果没有任何正则表达式模式匹配查询的 SQL，则会使用 `'default'` 的值。

#### 慢请求

`Requests` 记录器会捕获对应用发起的请求信息，并显示在 [慢请求卡片](#slow-requests-card) 和 [应用使用情况卡片](#application-usage-card) 上。

你可以选择性地调整慢路由阈值、[采样率](#sampling) 以及忽略的路径。

对于一些你预期执行时间较长的请求，你可以为每个请求单独配置阈值：

```php
Recorders\SlowRequests::class => [
    // ...
    'threshold' => [
        '#^/admin/#' => 5000,
        'default' => env('PULSE_SLOW_REQUESTS_THRESHOLD', 1000),
    ],
],
```

如果没有任何正则表达式模式匹配请求的 URL，则会使用 `'default'` 的值。

#### 服务器

`Servers` 记录器会捕获支撑应用的服务器的 CPU、内存和存储使用情况，并显示在 [服务器卡片](#servers-card) 上。此记录器要求在每台你希望监控的服务器上运行 [pulse:check 命令](#capturing-entries)。

每台上报的服务器必须有唯一名称。默认情况下，Pulse 会使用 PHP 的 `gethostname` 函数返回的值。如果你希望自定义名称，可以设置 `PULSE_SERVER_NAME` 环境变量：

```env
PULSE_SERVER_NAME=load-balancer
```

Pulse 配置文件还允许你自定义被监控的目录。



#### 用户任务

`UserJobs` 记录器会捕获应用中 **用户分发任务** 的信息，并在 [应用使用情况卡片](#application-usage-card) 上显示。

你可以选择性地调整 [采样率](#sampling) 和忽略的任务模式。

#### 用户请求

`UserRequests` 记录器会捕获应用中 **用户发起请求** 的信息，并在 [应用使用情况卡片](#application-usage-card) 上显示。

你可以选择性地调整 [采样率](#sampling) 和忽略的 URL 模式。

### 过滤

如前所述，许多 [记录器](#recorders) 通过配置提供了根据条目值（例如请求的 URL）“忽略”输入条目的能力。但有时，你可能希望基于其他因素过滤记录，例如当前认证的用户。要过滤这些记录，你可以向 Pulse 的 `filter` 方法传入一个闭包。通常，应在应用的 `AppServiceProvider` 的 `boot` 方法中调用 `filter` 方法：

```php
use Illuminate\Support\Facades\Auth;
use Laravel\Pulse\Entry;
use Laravel\Pulse\Facades\Pulse;
use Laravel\Pulse\Value;

/**
 * 启动任何应用服务
 */
public function boot(): void
{
    Pulse::filter(function (Entry|Value $entry) {
        return Auth::user()->isNotAdmin();
    });

    // ...
}
```

## 性能

Pulse 的设计目标是能够无缝集成到现有应用中，而无需额外基础设施。然而，对于高流量应用，有几种方式可以降低 Pulse 对应用性能的影响。

### 使用独立数据库

对于高流量应用，你可能希望为 Pulse 使用独立的数据库连接，以避免影响应用的主数据库。



你可以通过设置 `PULSE_DB_CONNECTION` 环境变量来自定义 Pulse 使用的 [数据库连接](/docs/laravel/12.x/database#configuration)：

```env
PULSE_DB_CONNECTION=pulse
```

### Redis 写入（Redis Ingest）

> [!警告]
> Redis 写入要求 Redis 版本 6.2 或更高，并且应用配置的 Redis 客户端驱动为 `phpredis` 或 `predis`。

默认情况下，Pulse 会在 HTTP 响应发送给客户端或任务处理完成后，将条目直接存储到 [配置的数据库连接](#using-a-different-database)；然而，你可以使用 Pulse 的 Redis 写入驱动，将条目发送到 Redis 流中。启用方法是配置 `PULSE_INGEST_DRIVER` 环境变量：

```ini
PULSE_INGEST_DRIVER=redis
```

Pulse 默认会使用应用的 [Redis 默认连接](/docs/laravel/12.x/redis#configuration)，但你也可以通过 `PULSE_REDIS_CONNECTION` 环境变量自定义：

```ini
PULSE_REDIS_CONNECTION=pulse
```

使用 Redis 写入时，你需要运行 `pulse:work` 命令来监控 Redis 流，并将条目从 Redis 移动到 Pulse 的数据库表中：

```php
php artisan pulse:work
```

> [!注意]
> 为了让 `pulse:work` 进程在后台永久运行，你应使用像 Supervisor 这样的进程监控工具，以确保 Pulse worker 不会停止运行。

由于 `pulse:work` 是一个长时间运行的进程，它不会自动看到代码库的更改，因此在部署时需要重启。你应在应用部署过程中通过调用 `pulse:restart` 命令优雅地重启该进程：

```shell
php artisan pulse:restart
```

> [!注意]
> Pulse 使用 [缓存](/docs/laravel/12.x/cache) 来存储重启信号，因此在使用此功能前，应确保你的应用正确配置了缓存驱动。



### 采样

默认情况下，Pulse 会捕获应用中发生的每一个相关事件。对于高流量应用，这可能导致在仪表盘中需要聚合数百万条数据库记录，尤其是在较长时间范围内。

你可以选择在某些 Pulse 数据记录器上启用“采样”。例如，在 [用户请求](#user-requests-recorder) 记录器上将采样率设置为 `0.1`，意味着你只会记录大约 10% 的请求。在仪表盘中，这些值会按比例放大，并以 `~` 前缀标记，表示这是一个近似值。

一般而言，对于某个指标的条目越多，你就可以安全地将采样率设置得越低，而不会牺牲太多准确性。

### 修剪

Pulse 会在存储的条目超出仪表盘窗口时自动进行修剪。修剪在数据写入时通过抽奖系统（lottery system）进行，你可以在 Pulse 的 [配置文件](#configuration) 中自定义该系统。

### 处理 Pulse 异常

如果在捕获 Pulse 数据时发生异常，例如无法连接到存储数据库，Pulse 会静默失败，以避免影响你的应用。

如果你希望自定义这些异常的处理方式，可以向 `handleExceptionsUsing` 方法提供一个闭包：

```php
use Laravel\Pulse\Facades\Pulse;
use Illuminate\Support\Facades\Log;

Pulse::handleExceptionsUsing(function ($e) {
    Log::debug('An exception happened in Pulse', [
        'message' => $e->getMessage(),
        'stack' => $e->getTraceAsString(),
    ]);
});
```

## 自定义卡片

Pulse 允许你构建自定义卡片，以显示与你的应用特定需求相关的数据。Pulse 使用 [Livewire](https://livewire.laravel.com)，因此在构建第一个自定义卡片之前，你可能希望先 [查看其文档](https://livewire.laravel.com/docs)。



### 卡片组件

在 Laravel Pulse 中创建自定义卡片，首先需要扩展基础的 `Card` Livewire 组件，并定义对应的视图：

```php
namespace App\Livewire\Pulse;

use Laravel\Pulse\Livewire\Card;
use Livewire\Attributes\Lazy;

#[Lazy]
class TopSellers extends Card
{
    public function render()
    {
        return view('livewire.pulse.top-sellers');
    }
}
```

使用 Livewire 的 [懒加载](https://livewire.laravel.com/docs/lazy) 功能时，`Card` 组件会自动提供一个占位符，该占位符会遵循传入组件的 `cols` 和 `rows` 属性。

在编写 Pulse 卡片的对应视图时，你可以使用 Pulse 的 Blade 组件，以保持统一的外观和风格：

```blade
<x-pulse::card :cols="$cols" :rows="$rows" :class="$class" wire:poll.5s="">
    <x-pulse::card-header name="Top Sellers">
        <x-slot:icon>
            ...
        </x-slot:icon>
    </x-pulse::card-header>

    <x-pulse::scroll :expand="$expand">
        ...
    </x-pulse::scroll>
</x-pulse::card>
```

`$cols`、`$rows`、`$class` 和 `$expand` 变量应传递给相应的 Blade 组件，以便在仪表盘视图中自定义卡片布局。你也可以在视图中包含 `wire:poll.5s=""` 属性，让卡片自动更新。

定义好 Livewire 组件和模板后，可以在你的 [仪表盘视图](#dashboard-customization) 中引入卡片：

```blade
<x-pulse>
    ...

    <livewire:pulse.top-sellers cols="4" />
</x-pulse>
```

> [!注意]
> 如果你的卡片包含在一个包中，需要使用 `Livewire::component` 方法将组件注册到 Livewire。

### 样式

如果你的卡片需要超出 Pulse 自带类和组件的额外样式，有几种方式可以为卡片引入自定义 CSS。



#### Laravel Vite 集成

如果你的自定义卡片位于应用程序代码中，并且你正在使用 Laravel 的 [Vite 集成](/docs/laravel/12.x/vite)，你可以更新 `vite.config.js` 文件，为你的卡片添加专用的 CSS 入口点：

```js
laravel({
    input: [
        'resources/css/pulse/top-sellers.css',
        // ...
    ],
}),
```

然后，你可以在 [仪表盘视图](#dashboard-customization) 中使用 `@vite` Blade 指令，指定卡片的 CSS 入口文件：

```blade
<x-pulse>
    @vite('resources/css/pulse/top-sellers.css')

    ...
</x-pulse>
```

#### CSS 文件

对于其他用例，包括包含在包中的 Pulse 卡片，你可以在 Livewire 组件中定义一个 `css` 方法，返回 CSS 文件路径，来指示 Pulse 加载额外样式表：

```php
class TopSellers extends Card
{
    // ...

    protected function css()
    {
        return __DIR__.'/../../dist/top-sellers.css';
    }
}
```

当该卡片被包含在仪表盘中时，Pulse 会自动将该文件内容包含在 `<style>` 标签中，无需发布到 `public` 目录。

#### Tailwind CSS

使用 Tailwind CSS 时，应创建专用的 Tailwind 配置文件，以避免加载不必要的 CSS 或与 Pulse 的 Tailwind 类冲突：

```js
export default {
    darkMode: 'class',
    important: '#top-sellers',
    content: [
        './resources/views/livewire/pulse/top-sellers.blade.php',
    ],
    corePlugins: {
        preflight: false,
    },
};
```

然后，在 CSS 入口文件中指定该配置文件：

```css
@config "../../tailwind.top-sellers.config.js";
@tailwind base;
@tailwind components;
@tailwind utilities;
```

此外，你需要在卡片视图中添加一个 `id` 或 `class` 属性，该属性应与 Tailwind 的 [important selector strategy](https://tailwindcss.com/docs/configuration#selector-strategy) 中指定的选择器匹配：

```blade
<x-pulse::card id="top-sellers" :cols="$cols" :rows="$rows" class="$class">
    ...
</x-pulse::card>
```



### 数据捕获与聚合

自定义卡片可以从任何地方获取和显示数据；不过，你可能希望利用 Pulse 高效的数据记录和聚合系统。

#### 捕获条目

Pulse 允许你使用 `Pulse::record` 方法记录“条目（entries）”：

```php
use Laravel\Pulse\Facades\Pulse;

Pulse::record('user_sale', $user->id, $sale->amount)
    ->sum()
    ->count();
```

`record` 方法的第一个参数是你要记录条目的 `type`，第二个参数是用于确定如何分组聚合数据的 `key`。对于大多数聚合方法，你还需要提供一个要聚合的 `value`。上例中，要聚合的值是 `$sale->amount`。你可以调用一个或多个聚合方法（如 `sum`），以便 Pulse 将预聚合的值捕获到“桶”中，从而实现高效检索。

可用的聚合方法有：

* `avg`
* `count`
* `max`
* `min`
* `sum`

> [!注意]
> 当构建捕获当前认证用户 ID 的卡片包时，应使用 `Pulse::resolveAuthenticatedUserId()` 方法，它会遵循应用中对 [用户解析器](#dashboard-resolving-users) 的任何自定义配置。

#### 获取聚合数据

在扩展 Pulse 的 `Card` Livewire 组件时，可以使用 `aggregate` 方法获取仪表盘中所查看期间的聚合数据：

```php
class TopSellers extends Card
{
    public function render()
    {
        return view('livewire.pulse.top-sellers', [
            'topSellers' => $this->aggregate('user_sale', ['sum', 'count'])
        ]);
    }
}
```

`aggregate` 方法返回一个 PHP `stdClass` 对象集合。每个对象都包含之前捕获的 `key` 属性，以及每个请求聚合方法对应的键：

```blade
@foreach ($topSellers as $seller)
    {{ $seller->key }}
    {{ $seller->sum }}
    {{ $seller->count }}
@endforeach
```



Pulse 主要从预先聚合的“桶”中获取数据；因此，指定的聚合必须事先通过 `Pulse::record` 方法捕获。最旧的桶通常部分落在所查看的期间之外，因此 Pulse 会对最旧的条目进行聚合以填补空缺，从而为整个期间提供准确的值，而无需在每次轮询请求时对整个期间进行聚合。

你还可以使用 `aggregateTotal` 方法获取某个类型的总值。例如，下面的方法会获取所有用户销售的总和，而不是按用户分组：

```php
$total = $this->aggregateTotal('user_sale', 'sum');
```

#### 显示用户

当处理以用户 ID 作为键的聚合时，可以使用 `Pulse::resolveUsers` 方法将键解析为用户记录：

```php
$aggregates = $this->aggregate('user_sale', ['sum', 'count']);

$users = Pulse::resolveUsers($aggregates->pluck('key'));

return view('livewire.pulse.top-sellers', [
    'sellers' => $aggregates->map(fn ($aggregate) => (object) [
        'user' => $users->find($aggregate->key),
        'sum' => $aggregate->sum,
        'count' => $aggregate->count,
    ])
]);
```

`find` 方法返回一个包含 `name`、`extra` 和 `avatar` 键的对象，你可以将其直接传递给 `<x-pulse::user-card>` Blade 组件：

```blade
<x-pulse::user-card :user="{{ $seller->user }}" :stats="{{ $seller->sum }}" />
```

#### 自定义记录器

包作者可能希望提供记录器类，以便用户配置数据捕获。

记录器在应用的 `config/pulse.php` 配置文件的 `recorders` 部分注册：

```php
[
    // ...
    'recorders' => [
        Acme\Recorders\Deployments::class => [
            // ...
        ],

        // ...
    ],
]
```

记录器可通过指定 `$listen` 属性来监听事件。Pulse 会自动注册监听器并调用记录器的 `record` 方法：

```php
<?php

namespace Acme\Recorders;

use Acme\Events\Deployment;
use Illuminate\Support\Facades\Config;
use Laravel\Pulse\Facades\Pulse;

class Deployments
{
    /**
     * 要监听的事件
     *
     * @var array<int, class-string>
     */
    public array $listen = [
        Deployment::class,
    ];

    /**
     * 记录部署事件
     */
    public function record(Deployment $event): void
    {
        $config = Config::get('pulse.recorders.'.static::class);

        Pulse::record(
            // ...
        );
    }
}
```
