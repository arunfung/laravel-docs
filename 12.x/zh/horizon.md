
# Laravel Horizon

-   [简介](#introduction)
-   [安装](#installation)
    -   [配置](#configuration)
    -   [负载均衡策略](#balancing-strategies)
    -   [仪表盘授权](#dashboard-authorization)
    -   [静默任务](#silenced-jobs)
-   [升级 Horizon](#upgrading-horizon)
-   [运行 Horizon](#running-horizon)
    -   [部署 Horizon](#deploying-horizon)
-   [标签](#tags)
-   [通知](#notifications)
-   [指标](#metrics)
-   [删除失败的任务](#deleting-failed-jobs)
-   [清空队列中的任务](#clearing-jobs-from-queues)

## 简介

> [!注意]
> 在深入了解 Laravel Horizon 之前，你应该先熟悉 Laravel 的基础 [队列服务](/docs/laravel/12.x/queues)。
> Horizon 在 Laravel 队列的基础上提供了额外功能，如果你对 Laravel 提供的基础队列功能还不熟悉，这些可能会让你感到困惑。

[Laravel Horizon](https://github.com/laravel/horizon?utm_source=chatgpt.com) 为你的 Laravel 驱动的 [Redis 队列](/docs/laravel/12.x/queues) 提供了一个优雅的仪表盘和代码驱动的配置。
Horizon 允许你轻松监控队列系统的关键指标，例如任务吞吐量、运行时长以及任务失败情况。

使用 Horizon 时，你的所有队列 worker 配置都会存储在一个简单的配置文件中。
通过在版本控制文件中定义应用的 worker 配置，你可以在部署应用时轻松扩展或修改队列 worker。

<img src="https://laravel.com/img/docs/horizon-example.png">

## 安装

> [!警告]
> Laravel Horizon 要求你使用 [Redis](https://redis.io?utm_source=chatgpt.com) 来驱动队列。
> 因此，你应当确保在应用的 `config/queue.php` 配置文件中，将队列连接设置为 `redis`。

你可以使用 Composer 包管理器将 Horizon 安装到项目中：

```shell
composer require laravel/horizon
```



在安装 Horizon 之后，使用 `horizon:install` Artisan 命令发布它的资源：

```shell
php artisan horizon:install
```

### 配置

发布 Horizon 的资源后，它的主要配置文件将位于 `config/horizon.php`。
该配置文件允许你为应用配置队列 worker 的选项。
每个配置选项都包含了它的用途说明，因此请务必仔细阅读这个文件。

> [!警告]
> Horizon 在内部使用一个名为 `horizon` 的 Redis 连接。
> 这个 Redis 连接名称是保留的，不应在 `database.php` 配置文件中分配给其他 Redis 连接，也不应作为 `horizon.php` 配置文件中 `use` 选项的值。

#### 环境

安装完成后，你需要熟悉的主要 Horizon 配置项是 `environments`。
这个配置项是一个数组，定义了应用运行的环境，以及每个环境的 worker 进程选项。
默认情况下，该项包含 `production` 和 `local` 环境。
当然，你可以根据需要自由添加更多环境：

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

你还可以定义一个通配符环境（`*`），当找不到其他匹配环境时将使用它：

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

当你启动 Horizon 时，它会使用应用当前运行环境对应的 worker 进程配置选项。
通常，运行环境由 `APP_ENV` [环境变量](/docs/laravel/12.x/configuration#determining-the-current-environment) 的值决定。
例如，默认的 `local` Horizon 环境被配置为启动 3 个 worker 进程，并自动平衡分配到每个队列的 worker 进程数量。
而默认的 `production` 环境则被配置为最多启动 10 个 worker 进程，并自动平衡分配到每个队列的 worker 进程数量。

> [!警告]
> 你需要确保 `horizon` 配置文件中的 `environments` 部分包含你计划运行 Horizon 的每个 [环境](/docs/laravel/12.x/configuration#environment-configuration) 的条目。



#### 监督器（Supervisors）

正如你在 Horizon 的默认配置文件中所看到的，每个环境可以包含一个或多个“监督器”。
默认情况下，配置文件将这个监督器定义为 `supervisor-1`；不过，你可以自由地为监督器命名。
每个监督器本质上负责“监督”一组 worker 进程，并负责在队列之间平衡 worker 进程。

如果你希望在某个环境中定义一组新的 worker 进程，可以为该环境添加额外的监督器。
当你希望为应用使用的某个队列定义不同的负载均衡策略或不同的 worker 进程数量时，这样做是有意义的。

#### 维护模式（Maintenance Mode）

当你的应用处于 [维护模式](/docs/laravel/12.x/configuration#maintenance-mode) 时，Horizon 不会处理队列任务，
除非你在 Horizon 配置文件中将监督器的 `force` 选项定义为 `true`：

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

#### 默认值（Default Values）

在 Horizon 的默认配置文件中，你会注意到一个 `defaults` 配置项。
该配置项指定了应用 [监督器](#supervisors) 的默认值。
监督器的默认配置值会被合并到各环境的监督器配置中，从而避免你在定义监督器时出现不必要的重复。

### 负载均衡策略（Balancing Strategies）

与 Laravel 的默认队列系统不同，Horizon 允许你从三种 worker 负载均衡策略中进行选择：`simple`、`auto` 和 `false`。
其中，`simple` 策略会将传入的任务均匀分配给 worker 进程：

    'balance' => 'simple',



`auto` 策略是配置文件中的默认值，它会根据队列当前的工作负载来调整每个队列的 worker 进程数量。
例如，如果你的 `notifications` 队列有 1,000 个待处理任务，而 `render` 队列为空，Horizon 会分配更多的 worker 到 `notifications` 队列，直到该队列被清空。

当使用 `auto` 策略时，你可以定义 `minProcesses` 和 `maxProcesses` 配置项，用于控制每个队列的最小进程数，以及 Horizon 在扩缩容时所允许的最大进程数：

```php
'environments' => [
    'production' => [
        'supervisor-1' => [
            'connection' => 'redis',
            'queue' => ['default'],
            'balance' => 'auto',
            'autoScalingStrategy' => 'time',
            'minProcesses' => 1,
            'maxProcesses' => 10,
            'balanceMaxShift' => 1,
            'balanceCooldown' => 3,
            'tries' => 3,
        ],
    ],
],
```

`autoScalingStrategy` 配置项决定 Horizon 在为队列分配更多 worker 进程时，依据的标准是队列清空所需的总时间（`time` 策略），还是依据队列中的任务总数（`size` 策略）。

`balanceMaxShift` 和 `balanceCooldown` 配置项决定 Horizon 扩缩容的速度。
在上面的示例中，最多每三秒会创建或销毁一个新的进程。
你可以根据应用的需求自由调整这些值。

当 `balance` 选项被设置为 `false` 时，将使用 Laravel 的默认行为，队列会按照你在配置中列出的顺序依次处理。

### 仪表盘授权（Dashboard Authorization）

Horizon 仪表盘可以通过 `/horizon` 路径访问。
默认情况下，你只能在 `local` 环境中访问该仪表盘。

不过，在你的 `app/Providers/HorizonServiceProvider.php` 文件中，有一个 [授权 gate](/docs/laravel/12.x/authorization#gates) 的定义。
这个授权 gate 用来控制在 **非本地环境** 中访问 Horizon 的权限。
你可以根据需要修改这个 gate，以限制对 Horizon 的访问：

```php
/**
 * 注册 Horizon gate。
 *
 * 这个 gate 决定了谁可以在非本地环境中访问 Horizon。
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



#### 替代认证策略（Alternative Authentication Strategies）

请记住，Laravel 会自动将已认证的用户注入到 gate 闭包中。
如果你的应用通过其他方式提供 Horizon 的安全性，例如 IP 限制，那么你的 Horizon 用户可能不需要“登录”。
因此，你需要将上面闭包的签名 `function (User $user)` 改为 `function (User $user = null)`，以强制 Laravel 不要求认证。

### 静默任务（Silenced Jobs）

有时，你可能不希望查看应用或第三方包派发的某些任务。
与其让这些任务占用“已完成任务”列表中的空间，你可以将它们静默。
要开始操作，请在应用的 `horizon` 配置文件中，将任务的类名添加到 `silenced` 配置项中：

```php
'silenced' => [
    App\Jobs\ProcessPodcast::class,
],
```

或者，你希望静默的任务可以实现 `Laravel\Horizon\Contracts\Silenced` 接口。
如果任务实现了该接口，即使它不在 `silenced` 配置数组中，也会自动被静默：

```php
use Laravel\Horizon\Contracts\Silenced;

class ProcessPodcast implements ShouldQueue, Silenced
{
    use Queueable;

    // ...
}
```

## 升级 Horizon（Upgrading Horizon）

当升级到 Horizon 的新主版本时，务必仔细查看 [升级指南](https://github.com/laravel/horizon/blob/master/UPGRADE.md?utm_source=chatgpt.com)。

## 运行 Horizon（Running Horizon）

一旦你在应用的 `config/horizon.php` 配置文件中配置了监督器和 worker，就可以使用 `horizon` Artisan 命令启动 Horizon。
这一条命令会启动当前环境下所有已配置的 worker 进程：

```shell
php artisan horizon
```



你可以使用 `horizon:pause` 和 `horizon:continue` Artisan 命令暂停 Horizon 进程并指示它继续处理任务：

```shell
php artisan horizon:pause

php artisan horizon:continue
```

你还可以使用 `horizon:pause-supervisor` 和 `horizon:continue-supervisor` Artisan 命令暂停或继续特定的 Horizon [监督器](#supervisors)：

```shell
php artisan horizon:pause-supervisor supervisor-1

php artisan horizon:continue-supervisor supervisor-1
```

你可以使用 `horizon:status` Artisan 命令检查 Horizon 进程的当前状态：

```shell
php artisan horizon:status
```

你可以使用 `horizon:supervisor-status` Artisan 命令检查特定 Horizon [监督器](#supervisors) 的当前状态：

```shell
php artisan horizon:supervisor-status supervisor-1
```

你可以使用 `horizon:terminate` Artisan 命令优雅地终止 Horizon 进程。
任何正在处理的任务会被完成，然后 Horizon 才会停止执行：

```shell
php artisan horizon:terminate
```

### 部署 Horizon（Deploying Horizon）

当你准备将 Horizon 部署到应用的实际服务器时，应配置一个进程监控器来监控 `php artisan horizon` 命令，并在它意外退出时重新启动它。
不用担心，我们将在下面讨论如何安装进程监控器。

在应用的部署过程中，你应指示 Horizon 进程终止，以便你的进程监控器重新启动它，并应用你的代码更改：

```shell
php artisan horizon:terminate
```

#### 安装 Supervisor

Supervisor 是 Linux 操作系统的进程监控器，如果你的 `horizon` 进程停止执行，它会自动重新启动。
在 Ubuntu 上安装 Supervisor，可以使用以下命令。如果你不是使用 Ubuntu，也可以通过操作系统的包管理器安装 Supervisor：

```shell
sudo apt-get install supervisor
```

> [!注意]
> 如果自己配置 Supervisor 感到繁琐，可以考虑使用 [Laravel Cloud](https://cloud.laravel.com?utm_source=chatgpt.com)，它可以管理 Laravel 应用的后台进程。



#### 监督器配置（Supervisor Configuration）

Supervisor 配置文件通常存储在服务器的 `/etc/supervisor/conf.d` 目录下。
在该目录中，你可以创建任意数量的配置文件，指示 Supervisor 如何监控你的进程。
例如，我们创建一个 `horizon.conf` 文件，用于启动并监控一个 `horizon` 进程：

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

在定义 Supervisor 配置时，应确保 `stopwaitsecs` 的值大于你最长运行任务所需的秒数。
否则，Supervisor 可能会在任务完成前就将其终止。

> [!警告]
> 上述示例适用于基于 Ubuntu 的服务器，但其他操作系统的 Supervisor 配置文件的位置和文件扩展名可能有所不同。
> 请查阅你的服务器文档以获取更多信息。

#### 启动 Supervisor（Starting Supervisor）

创建配置文件后，你可以使用以下命令更新 Supervisor 配置并启动被监控的进程：

```shell
sudo supervisorctl reread

sudo supervisorctl update

sudo supervisorctl start horizon
```

> [!注意]
> 有关运行 Supervisor 的更多信息，请查阅 [Supervisor 文档](http://supervisord.org/index.html?utm_source=chatgpt.com)。

## 标签

Horizon 允许你为任务分配“标签”，包括可邮件任务（mailables）、广播事件（broadcast events）、通知（notifications）和队列事件监听器（queued event listeners）。
事实上，Horizon 会根据附加到任务的 Eloquent 模型，智能且自动地为大多数任务打标签。
例如，看看下面这个任务：

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
     * 创建新的任务实例
     */
    public function __construct(
        public Video $video,
    ) {}

    /**
     * 执行任务
     */
    public function handle(): void
    {
        // ...
    }
}
```



如果该任务在队列中附带了一个 `id` 属性为 `1` 的 `App\Models\Video` 实例，它将自动获得标签 `App\Models\Video:1`。
这是因为 Horizon 会在任务的属性中搜索任何 Eloquent 模型。
如果找到 Eloquent 模型，Horizon 会智能地使用模型的类名和主键为任务打标签：

```php
use App\Jobs\RenderVideo;
use App\Models\Video;

$video = Video::find(1);

RenderVideo::dispatch($video);
```

#### 手动为任务打标签（Manually Tagging Jobs）

如果你希望手动定义某个可队列对象的标签，可以在类中定义一个 `tags` 方法：

```php
class RenderVideo implements ShouldQueue
{
    /**
     * 获取应分配给任务的标签
     *
     * @return array<int, string>
     */
    public function tags(): array
    {
        return ['render', 'video:'.$this->video->id];
    }
}
```

#### 手动为事件监听器打标签（Manually Tagging Event Listeners）

在获取队列事件监听器的标签时，Horizon 会自动将事件实例传递给 `tags` 方法，
从而允许你将事件数据添加到标签中：

```php
class SendRenderNotifications implements ShouldQueue
{
    /**
     * 获取应分配给监听器的标签
     *
     * @return array<int, string>
     */
    public function tags(VideoRendered $event): array
    {
        return ['video:'.$event->video->id];
    }
}
```

## 通知

> [!警告]
> 在配置 Horizon 发送 Slack 或 SMS 通知时，你应当查看相关通知渠道的 [前置条件](/docs/laravel/12.x/notifications)。

如果你希望在队列等待时间过长时收到通知，可以使用以下方法：
`Horizon::routeMailNotificationsTo`、`Horizon::routeSlackNotificationsTo` 和 `Horizon::routeSmsNotificationsTo`。
你可以在应用的 `App\Providers\HorizonServiceProvider` 的 `boot` 方法中调用这些方法：

```php
/**
 * 启动应用服务
 */
public function boot(): void
{
    parent::boot();

    Horizon::routeSmsNotificationsTo('15556667777');
    Horizon::routeMailNotificationsTo('example@example.com');
    Horizon::routeSlackNotificationsTo('slack-webhook-url', '#channel');
}
```



#### 配置通知等待时间阈值

你可以在应用的 `config/horizon.php` 配置文件中配置多少秒被视为“长时间等待”。
该文件中的 `waits` 配置项允许你为每个连接 / 队列组合控制长等待阈值。
任何未定义的连接 / 队列组合将默认为长等待阈值 60 秒：

```php
'waits' => [
    'redis:critical' => 30,
    'redis:default' => 60,
    'redis:batch' => 120,
],
```

## 指标

Horizon 包含一个指标仪表盘，用于提供有关任务和队列等待时间及吞吐量的信息。
为了填充该仪表盘，你应在应用的 `routes/console.php` 文件中配置 Horizon 的 `snapshot` Artisan 命令每五分钟运行一次：

```php
use Illuminate\Support\Facades\Schedule;

Schedule::command('horizon:snapshot')->everyFiveMinutes();
```

## 删除失败任务

如果你希望删除一个失败任务，可以使用 `horizon:forget` 命令。
`horizon:forget` 命令接受失败任务的 ID 或 UUID 作为唯一参数：

```shell
php artisan horizon:forget 5
```

如果你希望删除所有失败任务，可以为 `horizon:forget` 命令提供 `--all` 选项：

```shell
php artisan horizon:forget --all
```

## 清空队列中的任务

如果你希望删除应用默认队列中的所有任务，可以使用 `horizon:clear` Artisan 命令：

```shell
php artisan horizon:clear
```

你也可以提供 `queue` 选项，从特定队列中删除任务：

```shell
php artisan horizon:clear --queue=emails
```
