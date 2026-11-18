
# Laravel Telescope

- [介绍](#introduction)
- [安装](#installation)
    - [仅限本地环境安装](#local-only-installation)
    - [配置](#configuration)
    - [数据修剪](#data-pruning)
    - [仪表盘授权](#dashboard-authorization)
- [升级 Telescope](#upgrading-telescope)
- [过滤](#filtering)
    - [条目](#filtering-entries)
    - [批次](#filtering-batches)
- [标签](#tagging)
- [可用的监视器](#available-watchers)
    - [批处理监视器](#batch-watcher)
    - [缓存监视器](#cache-watcher)
    - [命令监视器](#command-watcher)
    - [变量转储监视器](#dump-watcher)
    - [事件监视器](#event-watcher)
    - [异常监视器](#exception-watcher)
    - [门面（Gate）监视器](#gate-watcher)
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

[Laravel Telescope](https://github.com/laravel/telescope) 是您本地 Laravel 开发环境的绝佳调试伴侣。它能深入洞察进入应用的请求、异常、日志条目、数据库查询、队列任务、邮件、通知、缓存操作、定时任务、变量转储等核心运行信息。

<img src="https://laravel.com/img/docs/telescope-example.png" alt="Telescope 仪表盘界面示例">

<a name="installation"></a>
## 安装

通过 Composer 包管理器安装 Telescope：

```shell
composer require laravel/telescope
```

安装 Telescope 后，使用 Artisan 命令 `telescope:install` 发布其资源文件和迁移文件。安装完成后，还需运行 `migrate` 命令来创建存储 Telescope 数据所需的表：

```shell
php artisan telescope:install

php artisan migrate
```

最后，您可以通过 /telescope 路由访问 Telescope 仪表盘。



<a name="local-only-installation"></a>
### 仅限本地环境安装

若您仅需在本地开发环境使用 Telescope，可通过 `--dev` 参数进行安装：

```shell
composer require laravel/telescope --dev

php artisan telescope:install

php artisan migrate
```

执行 `telescope:install` 后，需从 `bootstrap/providers.php` 配置文件中移除 `TelescopeServiceProvider` 服务提供者注册。改为在 `App\Providers\AppServiceProvider` 类的 `register` 方法中手动注册 Telescope 服务提供者，我们将确保当前环境为 `local` 时才进行注册：

```php
/**
 * 注册应用服务
 */
public function register(): void
{
    if ($this->app->environment('local') && class_exists(\Laravel\Telescope\TelescopeServiceProvider::class)) {
        $this->app->register(\Laravel\Telescope\TelescopeServiceProvider::class);
        $this->app->register(TelescopeServiceProvider::class);
    }
}
```

最后，您还需在 `composer.json` 中添加以下配置，防止 Telescope 被[自动发现](/docs/laravel/12.x/packages#package-discovery)：

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

发布 Telescope 资源后，主配置文件位于 `config/telescope.php`。该文件允许您配置[监视器选项](#available-watchers)。每个配置选项都包含用途说明，请仔细查阅此文件。

如需完全禁用 Telescope 数据收集，可通过 `enabled` 配置项实现：

```php
'enabled' => env('TELESCOPE_ENABLED', true),
```

<a name="data-pruning"></a>
### 数据修剪

若不进行修剪，`telescope_entries` 表会快速累积记录。建议通过[任务调度](/docs/laravel/12.x/scheduling)每天运行 `telescope:prune` 命令：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('telescope:prune')->daily();
```

默认情况下，超过24小时的所有记录将被清除。您可以在调用命令时使用 `hours` 选项来指定数据保留时长。例如，以下命令将删除48小时前的所有记录：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('telescope:prune --hours=48')->daily();
```

<a name="dashboard-authorization"></a>
### 仪表盘访问控制

Telescope 仪表盘可通过 `/telescope` 路由访问。默认情况下，仅在 `local` 环境中可访问。在 `app/Providers/TelescopeServiceProvider.php` 文件中定义了[授权门面](/docs/laravel/12.x/authorization#gates)，用于控制**非本地**环境下的访问权限。您可以根据需要修改此门面以限制访问：

```php
use App\Models\User;

/**
 * 注册 Telescope 访问门面
 *
 * 此门面决定谁能在非本地环境中访问 Telescope
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

> [!警告]
> 请确保在生产环境中将 `APP_ENV` 变量设置为 `production`，否则 Telescope 安装将对公众开放。

<a name="upgrading-telescope"></a>
## 升级 Telescope

升级到新主版本时，请务必仔细阅读[升级指南](https://github.com/laravel/telescope/blob/master/UPGRADE.md)。

此外，升级任何新版本时都应重新发布资源文件：

```shell
php artisan telescope:publish
```

为保持资源文件最新并避免未来更新问题，可在 `composer.json` 的 `post-update-cmd` 脚本中添加发布命令：

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
## 数据过滤

<a name="filtering-entries"></a>
### 条目过滤

您可以通过 `App\Providers\TelescopeServiceProvider` 类中定义的 `filter` 闭包来过滤 Telescope 记录的数据。默认情况下，该闭包在 `local` 环境中记录所有数据，在其他环境中仅记录异常、失败任务、计划任务和带有监控标签的数据：

```php
use Laravel\Telescope\IncomingEntry;
use Laravel\Telescope\Telescope;

/**
 * 注册应用服务
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
### 批量过滤

`filter` 闭包用于过滤单个条目，而 `filterBatch` 方法可以过滤整个请求或控制台命令的所有数据。当闭包返回 `true` 时，Telescope 会记录所有条目：

```php
use Illuminate\Support\Collection;
use Laravel\Telescope\IncomingEntry;
use Laravel\Telescope\Telescope;

/**
 * 注册应用服务
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
## 标签功能

Telescope 允许通过「标签」搜索条目。通常标签是 Eloquent 模型类名或认证用户ID，Telescope 会自动添加到条目中。您也可以使用 `Telescope::tag` 方法添加自定义标签。该方法接受返回标签数组的闭包，返回的标签将与 Telescope 自动添加的标签合并。通常应在 `App\Providers\TelescopeServiceProvider` 的 `register` 方法中调用：

```php
use Laravel\Telescope\IncomingEntry;
use Laravel\Telescope\Telescope;

/**
 * 注册应用服务
 */
public function register(): void
{
    $this->hideSensitiveRequestDetails();

    Telescope::tag(function (IncomingEntry $entry) {
        return $entry->type === 'request'
            ? ['status:'.$entry->content['response_status']]
            : [];
    });
}
```

<a name="available-watchers"></a>
## 可用监视器

Telescope 的「观察者」会在执行请求或控制台命令时收集应用程序数据。您可以在 `config/telescope.php` 配置文件中自定义要启用的监视器列表：

```php
'watchers' => [
    Watchers\CacheWatcher::class => true,
    Watchers\CommandWatcher::class => true,
    // ...
],
```

部分监视器还支持提供额外的自定义选项：

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
### 批量任务监视器

记录有关队列[批量任务](/docs/laravel/12.x/queues#job-batching)的信息，包括作业和连接详情。

<a name="cache-watcher"></a>
### 缓存监视器

当缓存键被命中、未命中、更新或删除时记录数据。

<a name="command-watcher"></a>
### 命令监视器

记录 Artisan 命令执行时的参数、选项、退出码和输出。如需排除特定命令，可在 `config/telescope.php` 中配置：

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

记录并显示通过全局 `dump` 函数输出的变量内容。注意：必须在浏览器中打开 dump 监视器标签页才会记录转储内容。

<a name="event-watcher"></a>
### 事件监视器

记录应用程序分发的任何[事件](/docs/laravel/12.x/events)的有效载荷、监听器和广播数据（Laravel 框架内部事件会被自动忽略）。

<a name="exception-watcher"></a>
### 异常监视器

异常监视器会记录应用程序抛出的所有可报告异常的数据和堆栈追踪信息。

<a name="gate-watcher"></a>
### 权限门监视器

权限门监视器记录应用程序执行的[权限门和策略](/docs/laravel/12.x/authorization)检查的数据和结果。如需排除特定权限检查不被记录，可以在`config/telescope.php`文件中指定`ignore_abilities`选项：

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
### HTTP客户端监视器

HTTP客户端监视器记录应用程序发出的[HTTP客户端请求](/docs/laravel/12.x/http-client)。

<a name="job-watcher"></a>
### 任务监视器

任务监视器记录应用程序分发的所有[队列任务](/docs/laravel/12.x/queues)的数据和状态。

<a name="log-watcher"></a>
### 日志监视器

日志监视器记录应用程序写入的[日志数据](/docs/laravel/12.x/logging)。

默认情况下，Telescope只记录`error`级别及以上的日志。您可以通过修改`config/telescope.php`配置文件中的`level`选项来调整此行为：

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

邮件监视器允许您在浏览器中预览应用程序发送的[邮件](/docs/laravel/12.x/mail)内容及其相关数据，还可以将邮件下载为`.eml`文件。

<a name="model-watcher"></a>


### 模型监视器

模型监视器会在Eloquent[模型事件](/docs/laravel/12.x/eloquent#events)触发时记录模型变更。您可以通过`events`选项指定要记录哪些模型事件：

```php
'watchers' => [
    Watchers\ModelWatcher::class => [
        'enabled' => env('TELESCOPE_MODEL_WATCHER', true),
        'events' => ['eloquent.created*', 'eloquent.updated*'],
    ],
    // ...
],
```

如果你想记录在给定请求期间加载的模型数量，可启用`hydrations`选项：

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

通知监视器记录应用程序发送的所有[通知](/docs/laravel/12.x/notifications)。如果通知触发了邮件发送且邮件监视器已启用，邮件内容也可在邮件监视器界面预览。

<a name="query-watcher"></a>
### 查询监视器

查询监视器记录应用程序执行的所有SQL查询的原始语句、绑定参数和执行时间。执行时间超过100毫秒的查询会被标记为`slow`。可通过`slow`选项自定义慢查询阈值：

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
### Redis监视器

Redis监视器记录应用程序执行的所有[Redis](/docs/laravel/12.x/redis)命令。如果将Redis用作缓存，缓存命令也会被记录。

<a name="request-watcher"></a>
### 请求监视器

请求监视器记录应用程序处理的请求相关的请求数据、头信息、会话和响应数据。可通过`size_limit`选项(单位KB)限制记录的响应数据大小：

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

计划任务监视器记录应用程序运行的[计划任务](/docs/laravel/12.x/scheduling)的命令和输出内容。

<a name="view-watcher"></a>
### 视图监视器

视图监视器记录[视图](/docs/laravel/12.x/views)渲染时使用的视图名称、路径、数据以及「composers」信息。

<a name="displaying-user-avatars"></a>
## 显示用户头像

Telescope仪表盘会显示记录条目时已认证用户的头像。默认情况下，Telescope使用Gravatar网络服务获取头像。您可以通过在`App\Providers\TelescopeServiceProvider`类中注册回调函数来自定义头像URL。该回调接收用户ID和邮箱地址，应返回用户头像图片URL：

```php
use App\Models\User;
use Laravel\Telescope\Telescope;

/**
 * 注册应用服务
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
