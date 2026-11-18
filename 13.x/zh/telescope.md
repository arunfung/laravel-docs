# Laravel Telescope

- [介绍](#introduction)
- [安装](#installation)
    - [仅在本地安装](#local-only-installation)
    - [配置](#configuration)
    - [数据清理](#data-pruning)
    - [仪表盘授权](#dashboard-authorization)
- [升级 Telescope](#upgrading-telescope)
- [过滤](#filtering)
    - [条目](#filtering-entries)
    - [批次](#filtering-batches)
- [标签](#tagging)
- [可用监视器](#available-watchers)
    - [批次监视器](#batch-watcher)
    - [缓存监视器](#cache-watcher)
    - [命令监视器](#command-watcher)
    - [变量转储监视器](#dump-watcher)
    - [事件监视器](#event-watcher)
    - [异常监视器](#exception-watcher)
    - [Gate 监视器](#gate-watcher)
    - [HTTP 客户端监视器](#http-client-watcher)
    - [任务监视器](#job-watcher)
    - [日志监视器](#log-watcher)
    - [邮件监视器](#mail-watcher)
    - [模型监视器](#model-watcher)
    - [通知监视器](#notification-watcher)
    - [查询监视器](#query-watcher)
    - [Redis 监视器](#redis-watcher)
    - [请求监视器](#request-watcher)
    - [计划任务监视器](#schedule-watcher)
    - [视图监视器](#view-watcher)
- [显示用户头像](#displaying-user-avatars)

<a name="introduction"></a>
## 介绍

[Laravel Telescope](https://github.com/laravel/telescope) 是本地 Laravel 开发环境的得力助手。Telescope 可以帮助你深入了解应用收到的请求、异常、日志条目、数据库查询、队列任务、邮件、通知、缓存操作、计划任务、变量转储等信息。

<img src="https://laravel.com/img/docs/telescope-example.png">

<a name="installation"></a>
## 安装

你可以通过 Composer 包管理器将 Telescope 安装到 Laravel 项目中：

```shell
composer require laravel/telescope
```

安装 Telescope 后，使用 `telescope:install` Artisan 命令发布其资源和迁移文件。之后还应运行 `migrate` 命令，创建存储 Telescope 数据所需的表：

```shell
php artisan telescope:install

php artisan migrate
```

最后，可以通过 `/telescope` 路由访问 Telescope 仪表盘。

<a name="local-only-installation"></a>
### 仅在本地安装

如果你只打算使用 Telescope 辅助本地开发，可以使用 `--dev` 标志安装 Telescope：

```shell
composer require laravel/telescope --dev

php artisan telescope:install

php artisan migrate
```

运行 `telescope:install` 后，应从应用的 `bootstrap/providers.php` 配置文件中移除 `TelescopeServiceProvider` 服务提供者的注册。改为在 `App\Providers\AppServiceProvider` 类的 `register` 方法中手动注册 Telescope 的服务提供者。注册之前，我们会确保当前环境为 `local`：

```php
/**
 * 注册应用服务。
 */
public function register(): void
{
    if ($this->app->environment('local') && class_exists(\Laravel\Telescope\TelescopeServiceProvider::class)) {
        $this->app->register(\Laravel\Telescope\TelescopeServiceProvider::class);
        $this->app->register(TelescopeServiceProvider::class);
    }
}
```

最后，还应在 `composer.json` 文件中添加以下内容，防止 Telescope 扩展包被 [自动发现](/docs/{{version}}/packages#package-discovery)：

```json
"extra": {
    "laravel": {
        "dont-discover": [
            "laravel/telescope"
        ]
    }
},
```

<a name="configuration"></a>
### 配置

发布 Telescope 资源后，其主要配置文件位于 `config/telescope.php`。该配置文件允许你配置 [监视器选项](#available-watchers)。每个配置选项都包含用途说明，请仔细阅读此文件。

如有需要，可以使用 `enabled` 配置选项完全禁用 Telescope 的数据收集：

```php
'enabled' => env('TELESCOPE_ENABLED', true),
```

<a name="content-security-policy-csp-nonce"></a>
#### 内容安全策略（CSP）Nonce

如果你希望为 Telescope 视图使用的 script 和 style 标签添加 [nonce 属性](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/nonce)，作为 [内容安全策略](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) 的一部分，可以使用 `Telescope::cspNonce` 方法指定 nonce。通常应在中间件中调用该方法，以便为每个请求分配新的 nonce：

```php
use Closure;
use Illuminate\Http\Request;
use Laravel\Telescope\Telescope;
use Symfony\Component\HttpFoundation\Response;

public function handle(Request $request, Closure $next): Response
{
    Telescope::cspNonce('csp-nonce');

    return $next($request);
}
```

可以将此中间件添加到应用的 `config/telescope.php` 配置文件中的 `middleware` 选项：

```php
'middleware' => [
    'web',
    App\Http\Middleware\AddTelescopeCspNonce::class,
    Authorize::class,
],
```

<a name="data-pruning"></a>
### 数据清理

如果不清理，`telescope_entries` 表中的记录可能会迅速累积。为缓解这一问题，应 [调度](/docs/{{version}}/scheduling) `telescope:prune` Artisan 命令每天运行：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('telescope:prune')->daily();
```

默认情况下，所有超过 24 小时的条目都会被清理。调用命令时，可以使用 `hours` 选项指定 Telescope 数据的保留时长。例如，以下命令会删除所有在 48 小时之前创建的记录：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('telescope:prune --hours=48')->daily();
```

<a name="dashboard-authorization"></a>
### 仪表盘授权

可以通过 `/telescope` 路由访问 Telescope 仪表盘。默认情况下，只有在 `local` 环境中才能访问该仪表盘。`app/Providers/TelescopeServiceProvider.php` 文件中定义了一个 [授权 Gate](/docs/{{version}}/authorization#gates)，用于控制在 **非本地** 环境中对 Telescope 的访问。你可以根据需要修改该 Gate，以限制对 Telescope 的访问：

```php
use App\Models\User;

/**
 * 注册 Telescope 授权 Gate。
 *
 * 此 Gate 决定谁可以在非本地环境中访问 Telescope。
 */
protected function gate(): void
{
    Gate::define('viewTelescope', function (User $user) {
        return in_array($user->email, [
            'taylor@laravel.com',
        ]);
    });
}
```

> [!WARNING]
> 请确保在生产环境中将 `APP_ENV` 环境变量设为 `production`。否则，安装的 Telescope 将对公众开放。

<a name="upgrading-telescope"></a>
## 升级 Telescope

升级到 Telescope 的新主版本时，请务必仔细阅读 [升级指南](https://github.com/laravel/telescope/blob/master/UPGRADE.md)。

此外，升级到任何新的 Telescope 版本时，都应重新发布 Telescope 的资源：

```shell
php artisan telescope:publish
```

为了保持资源最新并避免后续更新出现问题，可以将 `vendor:publish --tag=laravel-assets` 命令添加到应用的 `composer.json` 文件中的 `post-update-cmd` 脚本：

```json
{
    "scripts": {
        "post-update-cmd": [
            "@php artisan vendor:publish --tag=laravel-assets --ansi --force"
        ]
    }
}
```

<a name="filtering"></a>
## 过滤

<a name="filtering-entries"></a>
### 条目

可以通过 `App\Providers\TelescopeServiceProvider` 类中定义的 `filter` 闭包过滤 Telescope 记录的数据。默认情况下，该闭包在 `local` 环境中记录所有数据；在其他所有环境中记录异常、失败的任务、计划任务以及带有受监控标签的数据：

```php
use Laravel\Telescope\IncomingEntry;
use Laravel\Telescope\Telescope;

/**
 * 注册应用服务。
 */
public function register(): void
{
    $this->hideSensitiveRequestDetails();

    Telescope::filter(function (IncomingEntry $entry) {
        if ($this->app->environment('local')) {
            return true;
        }

        return $entry->isReportableException() ||
            $entry->isFailedJob() ||
            $entry->isScheduledTask() ||
            $entry->isSlowQuery() ||
            $entry->hasMonitoredTag();
    });
}
```

<a name="filtering-batches"></a>
### 批次

`filter` 闭包过滤单个条目的数据，而 `filterBatch` 方法允许你注册一个闭包，过滤给定请求或控制台命令的所有数据。如果闭包返回 `true`，Telescope 就会记录所有条目：

```php
use Illuminate\Support\Collection;
use Laravel\Telescope\IncomingEntry;
use Laravel\Telescope\Telescope;

/**
 * 注册应用服务。
 */
public function register(): void
{
    $this->hideSensitiveRequestDetails();

    Telescope::filterBatch(function (Collection $entries) {
        if ($this->app->environment('local')) {
            return true;
        }

        return $entries->contains(function (IncomingEntry $entry) {
            return $entry->isReportableException() ||
                $entry->isFailedJob() ||
                $entry->isScheduledTask() ||
                $entry->isSlowQuery() ||
                $entry->hasMonitoredTag();
            });
    });
}
```

<a name="tagging"></a>
## 标签

Telescope 允许通过「标签」搜索条目。标签通常是 Telescope 自动添加到条目的 Eloquent 模型类名或已认证用户 ID。有时你可能希望为条目添加自定义标签，为此可以使用 `Telescope::tag` 方法。`tag` 方法接受一个应返回标签数组的闭包，其返回的标签会与 Telescope 自动添加到条目的标签合并。通常应在 `App\Providers\TelescopeServiceProvider` 类的 `register` 方法中调用 `tag` 方法：

```php
use Laravel\Telescope\EntryType;
use Laravel\Telescope\IncomingEntry;
use Laravel\Telescope\Telescope;

/**
 * 注册应用服务。
 */
public function register(): void
{
    $this->hideSensitiveRequestDetails();

    Telescope::tag(function (IncomingEntry $entry) {
        return $entry->type === EntryType::REQUEST
            ? ['status:'.$entry->content['response_status']]
            : [];
    });
}
```

<a name="available-watchers"></a>
## 可用监视器

Telescope 的「监视器」会在执行请求或控制台命令时收集应用数据。可以在 `config/telescope.php` 配置文件中自定义要启用的监视器列表：

```php
'watchers' => [
    Watchers\CacheWatcher::class => true,
    Watchers\CommandWatcher::class => true,
    // ...
],
```

有些监视器还允许你提供额外的自定义选项：

```php
'watchers' => [
    Watchers\QueryWatcher::class => [
        'enabled' => env('TELESCOPE_QUERY_WATCHER', true),
        'slow' => 100,
    ],
    // ...
],
```

<a name="batch-watcher"></a>
### 批次监视器

批次监视器记录队列 [批次](/docs/{{version}}/queues#job-batching) 的信息，包括任务和连接信息。

<a name="cache-watcher"></a>
### 缓存监视器

缓存监视器在缓存键命中、未命中、更新或删除时记录数据。

<a name="command-watcher"></a>
### 命令监视器

每当执行 Artisan 命令时，命令监视器会记录参数、选项、退出码和输出。如果希望监视器不记录某些命令，可以在 `config/telescope.php` 文件的 `ignore` 选项中指定这些命令：

```php
'watchers' => [
    Watchers\CommandWatcher::class => [
        'enabled' => env('TELESCOPE_COMMAND_WATCHER', true),
        'ignore' => ['key:generate'],
    ],
    // ...
],
```

<a name="dump-watcher"></a>
### 变量转储监视器

变量转储监视器在 Telescope 中记录并显示变量转储内容。在 Laravel 中，可以使用全局 `dump` 函数转储变量。必须在浏览器中打开变量转储监视器标签页，转储内容才会被记录；否则，监视器会忽略这些内容。

<a name="event-watcher"></a>
### 事件监视器

事件监视器记录应用分派的任何 [事件](/docs/{{version}}/events) 的载荷、监听器和广播数据。事件监视器会忽略 Laravel 框架的内部事件。

<a name="exception-watcher"></a>
### 异常监视器

异常监视器记录应用抛出的任何可报告异常的数据和堆栈跟踪。

<a name="gate-watcher"></a>
### Gate 监视器

Gate 监视器记录应用执行的 [Gate 和策略](/docs/{{version}}/authorization) 检查的数据及结果。如果希望监视器不记录某些能力，可以在 `config/telescope.php` 文件的 `ignore_abilities` 选项中指定：

```php
'watchers' => [
    Watchers\GateWatcher::class => [
        'enabled' => env('TELESCOPE_GATE_WATCHER', true),
        'ignore_abilities' => ['viewNova'],
    ],
    // ...
],
```

<a name="http-client-watcher"></a>
### HTTP 客户端监视器

HTTP 客户端监视器记录应用发出的 [HTTP 客户端请求](/docs/{{version}}/http-client)。

<a name="job-watcher"></a>
### 任务监视器

任务监视器记录应用分派的所有 [任务](/docs/{{version}}/queues) 的数据和状态。

<a name="log-watcher"></a>
### 日志监视器

日志监视器记录应用写入的所有日志的 [日志数据](/docs/{{version}}/logging)。

默认情况下，Telescope 只记录 `error` 级别及以上的日志。不过，可以修改应用的 `config/telescope.php` 配置文件中的 `level` 选项来更改此行为：

```php
'watchers' => [
    Watchers\LogWatcher::class => [
        'enabled' => env('TELESCOPE_LOG_WATCHER', true),
        'level' => 'debug',
    ],

    // ...
],
```

<a name="mail-watcher"></a>
### 邮件监视器

邮件监视器允许你在浏览器中预览应用发送的 [邮件](/docs/{{version}}/mail) 及其相关数据。你还可以将邮件下载为 `.eml` 文件。

<a name="model-watcher"></a>
### 模型监视器

每当分派 Eloquent [模型事件](/docs/{{version}}/eloquent#events) 时，模型监视器都会记录模型变更。可以通过监视器的 `events` 选项指定应记录哪些模型事件：

```php
'watchers' => [
    Watchers\ModelWatcher::class => [
        'enabled' => env('TELESCOPE_MODEL_WATCHER', true),
        'events' => ['eloquent.created*', 'eloquent.updated*'],
    ],
    // ...
],
```

如果希望记录某个请求期间填充的模型数量，请启用 `hydrations` 选项：

```php
'watchers' => [
    Watchers\ModelWatcher::class => [
        'enabled' => env('TELESCOPE_MODEL_WATCHER', true),
        'events' => ['eloquent.created*', 'eloquent.updated*'],
        'hydrations' => true,
    ],
    // ...
],
```

<a name="notification-watcher"></a>
### 通知监视器

通知监视器记录应用发送的所有 [通知](/docs/{{version}}/notifications)。如果通知触发了邮件，并且启用了邮件监视器，也可以在邮件监视器页面预览该邮件。

<a name="query-watcher"></a>
### 查询监视器

查询监视器记录应用执行的所有查询的原始 SQL、绑定参数和执行时间。监视器还会将超过 100 毫秒的查询标记为 `slow`。可以使用监视器的 `slow` 选项自定义慢查询阈值：

```php
'watchers' => [
    Watchers\QueryWatcher::class => [
        'enabled' => env('TELESCOPE_QUERY_WATCHER', true),
        'slow' => 50,
    ],
    // ...
],
```

<a name="redis-watcher"></a>
### Redis 监视器

Redis 监视器记录应用执行的所有 [Redis](/docs/{{version}}/redis) 命令。如果使用 Redis 进行缓存，缓存命令也会由 Redis 监视器记录。

<a name="request-watcher"></a>
### 请求监视器

请求监视器记录与应用处理的任何请求相关的请求、请求头、会话和响应数据。可以通过 `size_limit` 选项（单位为千字节）限制记录的响应数据：

```php
'watchers' => [
    Watchers\RequestWatcher::class => [
        'enabled' => env('TELESCOPE_REQUEST_WATCHER', true),
        'size_limit' => env('TELESCOPE_RESPONSE_SIZE_LIMIT', 64),
    ],
    // ...
],
```

<a name="schedule-watcher"></a>
### 计划任务监视器

计划任务监视器记录应用运行的所有 [计划任务](/docs/{{version}}/scheduling) 的命令和输出。

<a name="view-watcher"></a>
### 视图监视器

视图监视器记录渲染视图时使用的 [视图](/docs/{{version}}/views) 名称、路径、数据和「composer」。

<a name="displaying-user-avatars"></a>
## 显示用户头像

Telescope 仪表盘会显示保存某个条目时已认证用户的头像。默认情况下，Telescope 使用 Gravatar 网络服务获取头像。不过，你可以在 `App\Providers\TelescopeServiceProvider` 类中注册回调来自定义头像 URL。该回调接收用户 ID 和电子邮件地址，并应返回用户的头像图片 URL：

```php
use App\Models\User;
use Laravel\Telescope\Telescope;

/**
 * 注册应用服务。
 */
public function register(): void
{
    // ...

    Telescope::avatar(function (?string $id, ?string $email) {
        return ! is_null($id)
            ? '/avatars/'.User::find($id)->avatar_path
            : '/generic-avatar.jpg';
    });
}
```
