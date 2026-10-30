# Laravel Horizon

- [简介](#introduction)
- [安装](#installation)
    - [配置](#configuration)
    - [仪表盘授权](#dashboard-authorization)
    - [任务最大尝试次数](#max-job-attempts)
    - [任务超时](#job-timeout)
    - [任务重试退避](#job-backoff)
    - [其他工作进程选项](#other-worker-options)
    - [静默任务](#silenced-jobs)
- [平衡策略](#balancing-strategies)
    - [自动平衡](#auto-balancing)
    - [简单平衡](#simple-balancing)
    - [不平衡](#no-balancing)
- [升级 Horizon](#upgrading-horizon)
- [运行 Horizon](#running-horizon)
    - [部署 Horizon](#deploying-horizon)
- [标签](#tags)
- [通知](#notifications)
- [指标](#metrics)
- [删除失败任务](#deleting-failed-jobs)
- [清除队列中的任务](#clearing-jobs-from-queues)

<a name="introduction"></a>
## 简介

> [!NOTE]
> 在深入了解 Laravel Horizon 之前，你应该先熟悉 Laravel 的基础[队列服务](/docs/{{version}}/queues)。Horizon 为 Laravel 队列增加了额外功能，如果你尚不熟悉 Laravel 提供的基础队列功能，可能会对这些功能感到困惑。

[Laravel Horizon](https://github.com/laravel/horizon) 为 Laravel 应用的 [Redis 队列](/docs/{{version}}/queues)提供了美观的仪表盘和代码驱动的配置。通过 Horizon，你可以轻松监控队列系统的关键指标，例如任务吞吐量、运行时间和失败情况。

使用 Horizon 时，所有队列工作进程配置都存储在一个简单的配置文件中。通过在受版本控制的文件中定义应用的工作进程配置，你可以在部署应用时轻松扩展或修改队列工作进程。

<img src="https://laravel.com/img/docs/horizon-example.png">

<a name="installation"></a>
## 安装

> [!WARNING]
> Laravel Horizon 要求使用 [Redis](https://redis.io) 驱动队列。因此，请确保应用的 `config/queue.php` 配置文件中将队列连接设置为 `redis`。Horizon 目前不兼容 Redis Cluster。

你可以使用 Composer 包管理器将 Horizon 安装到项目中：

```shell
composer require laravel/horizon
```

安装 Horizon 后，使用 `horizon:install` Artisan 命令发布其资源：

```shell
php artisan horizon:install
```

<a name="configuration"></a>
### 配置

发布 Horizon 资源后，其主配置文件位于 `config/horizon.php`。该文件允许你配置应用的队列工作进程选项。每个配置选项都包含用途说明，请务必仔细了解此文件。

> [!WARNING]
> Horizon 内部使用名为 `horizon` 的 Redis 连接。这个 Redis 连接名称是保留名称，不应在 `database.php` 配置文件中分配给其他 Redis 连接，也不应作为 `horizon.php` 配置文件中 `use` 选项的值。

<a name="content-security-policy-csp-nonce"></a>
#### 内容安全策略（CSP）Nonce

如果你希望在 Horizon 视图使用的 script 和 style 标签上使用 [nonce 属性](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Global_attributes/nonce)，作为[内容安全策略](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)的一部分，可以使用 `Horizon::cspNonce` 方法指定要使用的 nonce。通常应在中间件中调用此方法，以便为每次请求分配新的 nonce：

```php
use Closure;
use Illuminate\Http\Request;
use Laravel\Horizon\Horizon;
use Symfony\Component\HttpFoundation\Response;

public function handle(Request $request, Closure $next): Response
{
    Horizon::cspNonce('csp-nonce');

    return $next($request);
}
```

你可以将此中间件添加到应用的 `config/horizon.php` 配置文件中的 `middleware` 选项：

```php
'middleware' => [
    'web',
    App\Http\Middleware\AddHorizonCspNonce::class,
],
```

<a name="environments"></a>
#### 环境

安装后，你首先应熟悉 Horizon 的 `environments` 配置选项。该选项是应用运行环境的数组，并为每个环境定义工作进程选项。默认包含 `production` 和 `local` 两个环境，你也可以根据需要添加更多环境：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            'maxProcesses' => 10,
            'balanceMaxShift' => 1,
            'balanceCooldown' => 3,
        ],
    ],

    'local' => [
        'supervisor-1' => [
            'maxProcesses' => 3,
        ],
    ],
],
```

你也可以定义通配符环境（`*`），当没有其他匹配环境时使用：

```php
'environments' => [
    // ...

    '*' => [
        'supervisor-1' => [
            'maxProcesses' => 3,
        ],
    ],
],
```

启动 Horizon 时，它会使用应用当前运行环境对应的工作进程配置选项。通常，环境由 `APP_ENV` [环境变量](/docs/{{version}}/configuration#determining-the-current-environment)的值决定。例如，默认的 Horizon `local` 环境配置为启动三个工作进程，并自动平衡分配给各个队列的工作进程数量。默认的 `production` 环境配置为最多启动 10 个工作进程，并自动平衡分配给各个队列的工作进程数量。

> [!WARNING]
> 请确保 `horizon` 配置文件的 `environments` 部分包含你计划运行 Horizon 的每个[环境](/docs/{{version}}/configuration#environment-configuration)对应的配置项。

<a name="supervisors"></a>
#### 监督器

如 Horizon 的默认配置文件所示，每个环境可以包含一个或多个「监督器」。默认情况下，配置文件将该监督器命名为 `supervisor-1`，但你可以自行命名。每个监督器主要负责监督一组工作进程，并在各队列之间平衡这些进程。

如果希望在某个环境中定义另一组运行的工作进程，可以为该环境添加监督器。例如，你可能希望为应用使用的某个队列定义不同的平衡策略或工作进程数量。

<a name="maintenance-mode"></a>
#### 维护模式

当应用处于[维护模式](/docs/{{version}}/configuration#maintenance-mode)时，Horizon 不会处理队列任务，除非在 Horizon 配置文件中将监督器的 `force` 选项设置为 `true`：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            // ...
            'force' => true,
        ],
    ],
],
```

<a name="default-values"></a>
#### 默认值

在 Horizon 的默认配置文件中，你会看到一个 `defaults` 配置选项。该选项指定应用[监督器](#supervisors)的默认值。监督器的默认配置值会合并到每个环境的监督器配置中，避免你在定义监督器时不必要地重复配置。

<a name="dashboard-authorization"></a>
### 仪表盘授权

可以通过 `/horizon` 路由访问 Horizon 仪表盘。默认情况下，你只能在 `local` 环境中访问该仪表盘。不过，`app/Providers/HorizonServiceProvider.php` 文件中定义了一个[授权门](/docs/{{version}}/authorization#gates)，用于控制 **非 local** 环境中对 Horizon 的访问。你可以按需修改此授权门，限制对 Horizon 的访问：

```php
/**
 * 注册 Horizon 授权门。
 *
 * 此授权门决定谁可以在非 local 环境中访问 Horizon。
 */
protected function gate(): void
{
    Gate::define('viewHorizon', function (User $user) {
        return in_array($user->email, [
            'taylor@laravel.com',
        ]);
    });
}
```

<a name="alternative-authentication-strategies"></a>
#### 其他认证策略

请注意，Laravel 会自动将已认证用户注入授权门闭包。如果你的应用通过其他方式（例如 IP 限制）保护 Horizon，Horizon 用户可能无需「登录」。因此，你需要将上面的闭包签名 `function (User $user)` 改为 `function (User $user = null)`，让 Laravel 不再要求用户通过认证。

<a name="max-job-attempts"></a>
### 任务最大尝试次数

> [!NOTE]
> 调整这些选项之前，请确保你已熟悉 Laravel 的默认[队列服务](/docs/{{version}}/queues#max-job-attempts-and-timeout)和「尝试次数」的概念。

你可以在监督器配置中定义任务允许消耗的最大尝试次数：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            // ...
            'tries' => 10,
        ],
    ],
],
```

> [!NOTE]
> 此选项与使用 Artisan 命令处理队列时的 `--tries` 选项类似。

使用 `WithoutOverlapping` 或 `RateLimited` 等中间件时，调整 `tries` 选项至关重要，因为这些中间件会消耗尝试次数。可以在监督器级别调整 `tries` 配置值，也可以在任务类上定义 `$tries` 属性。

如果没有设置 `tries` 选项，Horizon 默认只尝试一次，除非任务类定义了 `$tries`；任务类的设置优先于 Horizon 配置。

将 `tries` 或 `$tries` 设置为 0 可允许无限次尝试，适用于尝试次数不确定的情况。为避免无限失败，可以通过设置任务类的 `$maxExceptions` 属性限制允许的异常次数。

<a name="job-timeout"></a>
### 任务超时

类似地，你可以在监督器级别设置 `timeout` 值，指定工作进程运行任务多少秒后会被强制终止。终止后，任务会根据队列配置被重试或标记为失败：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            // ...
            'timeout' => 60,
        ],
    ],
],
```

> [!WARNING]
> 使用 `auto` 平衡策略时，在缩减进程数量期间，Horizon 会将超过 Horizon 超时时间、仍在运行的工作进程视为「挂起」并强制终止。务必确保 Horizon 的超时时间大于任何任务级别的超时时间，否则任务可能在执行过程中被终止。此外，`timeout` 值始终应比 `config/queue.php` 配置文件中定义的 `retry_after` 值至少短几秒，否则任务可能被处理两次。

<a name="job-backoff"></a>
### 任务重试退避

你可以在监督器级别定义 `backoff` 值，指定任务遇到未处理异常后，Horizon 在重试前应等待多久：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            // ...
            'backoff' => 10,
        ],
    ],
],
```

你也可以使用数组作为 `backoff` 值，配置「指数」退避。在此示例中，第一次重试延迟 1 秒，第二次延迟 5 秒，第三次延迟 10 秒；如果还有剩余尝试次数，此后的每次重试都延迟 10 秒：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            // ...
            'backoff' => [1, 5, 10],
        ],
    ],
],
```

<a name="other-worker-options"></a>
### 其他工作进程选项

除了 `tries`、`timeout` 和 `backoff`，每个监督器还接受其他几个选项，用于控制工作进程的行为及其自动重启时机。定期重启工作进程是处理长期运行进程的良好实践，有助于防范内存泄漏：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            // ...
            'memory' => 128,
            'maxJobs' => 1000,
            'maxTime' => 3600,
            'sleep' => 3,
            'rest' => 0,
            'nice' => 0,
        ],
    ],
],
```

<div class="content-list" markdown="1">

- `memory` 定义单个工作进程在重启前最多可消耗的内存量，单位为 MB。默认值为 `128`。
- `maxJobs` 定义工作进程重启前应处理的任务数量。值为 `0` 表示不根据已处理任务数量重启工作进程。默认值为 `0`。
- `maxTime` 定义工作进程重启前应运行的秒数。值为 `0` 表示不根据运行时间重启工作进程。默认值为 `0`。
- `sleep` 定义没有可用任务时，工作进程再次轮询队列之前应等待的秒数。默认值为 `3`。
- `rest` 定义处理每个任务之间暂停的秒数。默认值为 `0`。
- `nice` 定义工作进程的「nice 值」（调度优先级）。值越高，进程优先级越低。默认值为 `0`。

</div>

<a name="silenced-jobs"></a>
### 静默任务

有时，你可能不希望查看应用或第三方包分发的某些任务。你可以将这些任务静默，而不让它们占据「已完成任务」列表的空间。首先，将任务类名添加到应用的 `horizon` 配置文件中的 `silenced` 选项：

```php
'silenced' => [
    App\Jobs\ProcessPodcast::class,
],
```

除了静默单个任务类，Horizon 还支持根据[标签](#tags)静默任务。如果你希望隐藏共享某个标签的多个任务，这会很有用：

```php
'silenced_tags' => [
    'notifications'
],
```

或者，想要静默的任务也可以实现 `Laravel\Horizon\Contracts\Silenced` 接口。实现该接口的任务即使不在 `silenced` 配置数组中，也会自动被静默：

```php
use Laravel\Horizon\Contracts\Silenced;

class ProcessPodcast implements ShouldQueue, Silenced
{
    use Queueable;

    // ...
}
```

<a name="balancing-strategies"></a>
## 平衡策略

每个监督器可以处理一个或多个队列。与 Laravel 默认的队列系统不同，Horizon 允许你从三种工作进程平衡策略中选择：`auto`、`simple` 和 `false`。

<a name="auto-balancing"></a>
### 自动平衡

`auto` 是默认策略，它会根据队列当前的工作负载调整每个队列的工作进程数量。例如，如果 `notifications` 队列有 1,000 个待处理任务，而 `default` 队列为空，Horizon 会为 `notifications` 队列分配更多工作进程，直到该队列清空。

使用 `auto` 策略时，你还可以配置 `minProcesses` 和 `maxProcesses` 选项：

<div class="content-list" markdown="1">

- `minProcesses` 定义每个队列的最少工作进程数。该值必须大于或等于 1。
- `maxProcesses` 定义 Horizon 在所有队列中可扩展到的最大工作进程总数。该值通常应大于队列数量与 `minProcesses` 值的乘积。要阻止监督器创建任何进程，可以将此值设为 0。

</div>

例如，你可以配置 Horizon 为每个队列至少保留一个进程，并最多扩展到 10 个工作进程：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            'connection' => 'redis',
            'queue' => ['default', 'notifications'],
            'balance' => 'auto',
            'autoScalingStrategy' => 'time',
            'minProcesses' => 1,
            'maxProcesses' => 10,
            'balanceMaxShift' => 1,
            'balanceCooldown' => 3,
        ],
    ],
],
```

`autoScalingStrategy` 配置选项决定 Horizon 如何向队列分配更多工作进程。你可以选择以下三种策略：

<div class="content-list" markdown="1">

- `time` 策略根据清空队列预计所需的总时间分配工作进程。
- `size` 策略根据队列中的任务总数分配工作进程。
- `log` 策略根据队列中任务数量的对数分配工作进程，避免明显更大的队列获得不成比例的大量工作进程。

</div>

`balanceMaxShift` 和 `balanceCooldown` 配置值决定 Horizon 为满足工作进程需求而进行扩缩的速度。在上面的示例中，每三秒最多创建或销毁一个进程。你可以根据应用需要调整这些值。

<a name="auto-queue-priorities"></a>
#### 队列优先级与自动平衡

使用 `auto` 平衡策略时，Horizon 不会严格执行队列之间的优先级。监督器配置中的队列顺序不会影响工作进程的分配；Horizon 会根据所选的 `autoScalingStrategy`，按队列负载动态分配工作进程。

例如，在以下配置中，虽然 high 队列在列表中排在前面，但它的优先级并不高于 default 队列：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            // ...
            'queue' => ['high', 'default'],
            'minProcesses' => 1,
            'maxProcesses' => 10,
        ],
    ],
],
```

如果需要在队列之间实行相对优先级，可以定义多个监督器并明确分配处理资源：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            // ...
            'queue' => ['default'],
            'minProcesses' => 1,
            'maxProcesses' => 10,
        ],
        'supervisor-2' => [
            // ...
            'queue' => ['images'],
            'minProcesses' => 1,
            'maxProcesses' => 1,
        ],
    ],
],
```

在此示例中，默认 `queue` 最多可扩展到 10 个进程，而 `images` 队列仅限一个进程。该配置确保队列能够独立扩缩。

> [!NOTE]
> 分发资源密集型任务时，有时最好将其分配到专用队列，并限制其 `maxProcesses` 值。否则，这些任务可能消耗过多 CPU 资源，使系统过载。

<a name="simple-balancing"></a>
### 简单平衡

`simple` 策略将工作进程均匀分配给指定队列。使用该策略时，Horizon 不会自动扩缩工作进程数量，而是使用固定数量的进程：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            // ...
            'queue' => ['default', 'notifications'],
            'balance' => 'simple',
            'processes' => 10,
        ],
    ],
],
```

在上面的示例中，Horizon 会将总共 10 个进程平均分配给两个队列，每个队列分配 5 个进程。

如果希望分别控制分配给每个队列的工作进程数量，可以定义多个监督器：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            // ...
            'queue' => ['default'],
            'balance' => 'simple',
            'processes' => 10,
        ],
        'supervisor-notifications' => [
            // ...
            'queue' => ['notifications'],
            'balance' => 'simple',
            'processes' => 2,
        ],
    ],
],
```

使用此配置时，Horizon 会为 `default` 队列分配 10 个进程，为 `notifications` 队列分配 2 个进程。

<a name="no-balancing"></a>
### 不平衡

当 `balance` 选项设为 `false` 时，Horizon 会严格按列出的顺序处理队列，类似于 Laravel 的默认队列系统。不过，如果任务开始积压，它仍会扩缩工作进程数量：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            // ...
            'queue' => ['default', 'notifications'],
            'balance' => false,
            'minProcesses' => 1,
            'maxProcesses' => 10,
        ],
    ],
],
```

在上面的示例中，`default` 队列中的任务始终优先于 `notifications` 队列中的任务。例如，如果 `default` 中有 1,000 个任务，而 `notifications` 中只有 10 个，Horizon 会先处理完所有 `default` 任务，再处理 `notifications` 中的任务。

你可以使用 `minProcesses` 和 `maxProcesses` 选项控制 Horizon 扩缩工作进程的能力：

<div class="content-list" markdown="1">

- `minProcesses` 定义最少工作进程总数。该值必须大于或等于 1。
- `maxProcesses` 定义 Horizon 可扩展到的最大工作进程总数。

</div>

<a name="upgrading-horizon"></a>
## 升级 Horizon

将 Horizon 升级到新的主要版本时，请务必仔细阅读[升级指南](https://github.com/laravel/horizon/blob/master/UPGRADE.md)。

<a name="running-horizon"></a>
## 运行 Horizon

在应用的 `config/horizon.php` 配置文件中配置监督器和工作进程后，可以使用 `horizon` Artisan 命令启动 Horizon。该命令会启动当前环境中配置的所有工作进程：

```shell
php artisan horizon
```

你可以使用 `horizon:pause` 和 `horizon:continue` Artisan 命令暂停 Horizon 进程，并让它继续处理任务：

```shell
php artisan horizon:pause

php artisan horizon:continue
```

你也可以使用 `horizon:pause-supervisor` 和 `horizon:continue-supervisor` Artisan 命令暂停和继续指定的 Horizon [监督器](#supervisors)：

```shell
php artisan horizon:pause-supervisor supervisor-1

php artisan horizon:continue-supervisor supervisor-1
```

你可以使用 `horizon:status` Artisan 命令检查 Horizon 进程的当前状态：

```shell
php artisan horizon:status
```

你可以使用 `horizon:supervisor-status` Artisan 命令检查指定 Horizon [监督器](#supervisors)的当前状态：

```shell
php artisan horizon:supervisor-status supervisor-1
```

你可以使用 `horizon:terminate` Artisan 命令优雅地终止 Horizon 进程。当前正在处理的所有任务会先完成，然后 Horizon 才会停止执行：

```shell
php artisan horizon:terminate
```

<a name="automatically-restarting-horizon"></a>
#### 自动重启 Horizon

在本地开发期间，你可以运行 `horizon:listen` 命令。使用该命令时，想要重新加载更新后的代码，无需手动重启 Horizon。使用此功能前，请确保本地开发环境已安装 [Node](https://nodejs.org)。此外，还应在项目中安装 [Chokidar](https://github.com/paulmillr/chokidar) 文件监视库：

```shell
npm install --save-dev chokidar
```

安装 Chokidar 后，可以使用 `horizon:listen` 命令启动 Horizon：

```shell
php artisan horizon:listen
```

在 Docker 或 Vagrant 中运行时，应使用 `--poll` 选项：

```shell
php artisan horizon:listen --poll
```

你可以使用应用的 `config/horizon.php` 配置文件中的 `watch` 选项，配置需要监视的目录和文件：

```php
'watch' => [
    'app',
    'bootstrap',
    'config',
    'database',
    'public/**/*.php',
    'resources/**/*.php',
    'routes',
    'composer.lock',
    '.env',
],
```

<a name="deploying-horizon"></a>
### 部署 Horizon

准备将 Horizon 部署到应用的实际服务器时，应配置进程监控器来监控 `php artisan horizon` 命令，并在其意外退出时重启它。下面将介绍如何安装进程监控器。

在应用部署过程中，应让 Horizon 进程终止，以便进程监控器重启它并加载代码变更：

```shell
php artisan horizon:terminate
```

<a name="installing-supervisor"></a>
#### 安装 Supervisor

Supervisor 是 Linux 操作系统的进程监控器。当 `horizon` 进程停止执行时，它会自动重启该进程。在 Ubuntu 上，可以使用以下命令安装 Supervisor。如果不使用 Ubuntu，通常可以通过操作系统的包管理器安装 Supervisor：

```shell
sudo apt-get install supervisor
```

> [!NOTE]
> 如果自行配置 Supervisor 比较困难，可以考虑使用 [Laravel Cloud](https://cloud.laravel.com)，它能够管理 Laravel 应用的后台进程。

<a name="supervisor-configuration"></a>
#### Supervisor 配置

Supervisor 配置文件通常存储在服务器的 `/etc/supervisor/conf.d` 目录中。你可以在该目录中创建任意数量的配置文件，指示 Supervisor 如何监控进程。例如，创建一个 `horizon.conf` 文件来启动并监控 `horizon` 进程：

```ini
[program:horizon]
process_name=%(program_name)s
command=php /home/forge/example.com/artisan horizon
autostart=true
autorestart=true
user=forge
redirect_stderr=true
stdout_logfile=/home/forge/example.com/horizon.log
stopwaitsecs=3600
```

定义 Supervisor 配置时，应确保 `stopwaitsecs` 的值大于运行时间最长的任务所需的秒数。否则，Supervisor 可能在任务完成处理前将其终止。

> [!WARNING]
> 虽然以上示例适用于基于 Ubuntu 的服务器，但其他服务器操作系统可能要求不同的 Supervisor 配置文件位置和扩展名。详情请参阅服务器文档。

<a name="starting-supervisor"></a>
#### 启动 Supervisor

创建配置文件后，可以使用以下命令更新 Supervisor 配置并启动受监控的进程：

```shell
sudo supervisorctl reread

sudo supervisorctl update

sudo supervisorctl start horizon
```

> [!NOTE]
> 有关运行 Supervisor 的更多信息，请参阅 [Supervisor 文档](http://supervisord.org/index.html)。

<a name="tags"></a>
## 标签

Horizon 允许你为任务分配「标签」，包括可发送邮件、广播事件、通知和排队事件监听器。事实上，Horizon 会根据附加到任务的 Eloquent 模型，智能地为大多数任务自动添加标签。例如，看看以下任务：

```php
<?php

namespace App\Jobs;

use App\Models\Video;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class RenderVideo implements ShouldQueue
{
    use Queueable;

    /**
     * 创建新的任务实例。
     */
    public function __construct(
        public Video $video,
    ) {}

    /**
     * 执行任务。
     */
    public function handle(): void
    {
        // ...
    }
}
```

如果此任务入队时传入一个 `id` 属性为 `1` 的 `App\Models\Video` 实例，它会自动获得 `App\Models\Video:1` 标签。这是因为 Horizon 会在任务属性中查找 Eloquent 模型。如果找到 Eloquent 模型，Horizon 会使用模型的类名和主键智能地为任务添加标签：

```php
use App\Jobs\RenderVideo;
use App\Models\Video;

$video = Video::find(1);

RenderVideo::dispatch($video);
```

<a name="manually-tagging-jobs"></a>
#### 手动为任务添加标签

如果希望为某个可入队对象手动定义标签，可以在类上定义 `tags` 方法：

```php
class RenderVideo implements ShouldQueue
{
    /**
     * 获取应分配给任务的标签。
     *
     * @return array<int, string>
     */
    public function tags(): array
    {
        return ['render', 'video:'.$this->video->id];
    }
}
```

<a name="manually-tagging-event-listeners"></a>
#### 手动为事件监听器添加标签

获取排队事件监听器的标签时，Horizon 会自动将事件实例传给 `tags` 方法，让你能够将事件数据添加到标签中：

```php
class SendRenderNotifications implements ShouldQueue
{
    /**
     * 获取应分配给监听器的标签。
     *
     * @return array<int, string>
     */
    public function tags(VideoRendered $event): array
    {
        return ['video:'.$event->video->id];
    }
}
```

<a name="notifications"></a>
## 通知

> [!WARNING]
> 配置 Horizon 发送 Slack 或短信通知时，应查看[相关通知渠道的前提条件](/docs/{{version}}/notifications)。

如果希望在某个队列等待时间过长时收到通知，可以使用 `Horizon::routeMailNotificationsTo`、`Horizon::routeSlackNotificationsTo` 和 `Horizon::routeSmsNotificationsTo` 方法。你可以在应用的 `App\Providers\HorizonServiceProvider` 的 `boot` 方法中调用这些方法：

```php
/**
 * 启动所有应用服务。
 */
public function boot(): void
{
    parent::boot();

    Horizon::routeSmsNotificationsTo('15556667777');
    Horizon::routeMailNotificationsTo('example@example.com');
    Horizon::routeSlackNotificationsTo('slack-webhook-url', '#channel');
}
```

<a name="configuring-notification-wait-time-thresholds"></a>
#### 配置通知等待时间阈值

你可以在应用的 `config/horizon.php` 配置文件中配置多少秒被视为「长时间等待」。该文件中的 `waits` 配置选项允许你控制每个连接与队列组合的长等待阈值。未定义的连接与队列组合默认使用 60 秒的长等待阈值：

```php
'waits' => [
    'redis:critical' => 30,
    'redis:default' => 60,
    'redis:batch' => 120,
],
```

将队列的阈值设置为 `0` 会禁用该队列的长等待通知。

<a name="metrics"></a>
## 指标

Horizon 包含一个指标仪表盘，提供任务与队列的等待时间和吞吐量信息。要填充此仪表盘，应在应用的 `routes/console.php` 文件中配置 Horizon 的 `snapshot` Artisan 命令每五分钟运行一次：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('horizon:snapshot')->everyFiveMinutes();
```

你可以使用应用的 `config/horizon.php` 配置文件中的 `metrics.trim_snapshots` 选项配置 Horizon 为指标图表保留多少个快照。由于此选项限制的是快照数量而非快照的存留时间，保留时长取决于 `horizon:snapshot` 命令运行的频率：

```php
'metrics' => [
    'trim_snapshots' => [
        'job' => 24,
        'queue' => 24,
    ],
],
```

如果希望删除所有指标数据，可以调用 `horizon:clear-metrics` Artisan 命令：

```shell
php artisan horizon:clear-metrics
```

<a name="deleting-failed-jobs"></a>
## 删除失败任务

如果希望删除失败任务，可以使用 `horizon:forget` 命令。该命令只接受一个参数，即失败任务的 ID 或 UUID：

```shell
php artisan horizon:forget 5
```

如果希望删除所有失败任务，可以为 `horizon:forget` 命令提供 `--all` 选项：

```shell
php artisan horizon:forget --all
```

<a name="clearing-jobs-from-queues"></a>
## 清除队列中的任务

如果希望删除应用默认队列中的所有任务，可以使用 `horizon:clear` Artisan 命令：

```shell
php artisan horizon:clear
```

你可以提供 `queue` 选项，删除指定队列中的任务：

```shell
php artisan horizon:clear --queue=emails
```
