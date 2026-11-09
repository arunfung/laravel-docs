# Laravel Reverb

- [介绍](#introduction)
- [安装](#installation)
- [配置](#configuration)
    - [应用凭证](#application-credentials)
    - [允许的来源](#allowed-origins)
    - [多应用](#additional-applications)
    - [SSL](#ssl)
- [运行服务](#running-server)
    - [调试](#debugging)
    - [重启](#restarting)
- [监控](#monitoring)
- [在生产环境中运行 Reverb](#production)
    - [打开的文件](#open-files)
    - [事件循环](#event-loop)
    - [Web 服务](#web-server)
    - [端口](#ports)
    - [进程管理](#process-management)
    - [扩展](#scaling)
- [事件](#events)

<a name="introduction"></a>
## 介绍

[Laravel Reverb](https://github.com/laravel/reverb) 为你的 Laravel 应用带来了快速的、可扩展的实时 WebSocket 通信，并提供与 Laravel 现有[事件广播工具套件](/docs/{{version}}/broadcasting)的无缝集成。

<a name="installation"></a>
## 安装

你可以使用 `install:broadcasting` Artisan 命令安装 Reverb：

```shell
php artisan install:broadcasting
```

<a name="configuration"></a>
## 配置

在底层，`install:broadcasting` Artisan 命令会运行 `reverb:install` 命令，它会使用一系列合理的默认配置选项来安装 Reverb。如果你想要更改任何配置选项，可以通过更新 Reverb 的环境变量或者更新 `config/reverb.php` 配置文件来进行。

<a name="application-credentials"></a>
### 应用凭证

为了建立与 Reverb 的连接，必须在客户端和服务器之间交换一组 Reverb 「应用程序」凭据。这些凭据在服务器上配置，用于验证来自客户端的请求。你可以使用以下环境变量定义这些凭据:

```ini
REVERB_APP_ID=my-app-id
REVERB_APP_KEY=my-app-key
REVERB_APP_SECRET=my-app-secret
```

<a name="allowed-origins"></a>
### 允许的来源

你也可以通过更新 `config/reverb.php` 配置文件中 `apps` 部分的 `allowed_origins` 配置值来定义客户端请求可以来源的域。任何不在允许来源列表中的请求都会被拒绝。你可以使用 `*` 来允许所有来源：

```php
'apps' => [
    [
        'app_id' => 'my-app-id',
        'allowed_origins' => ['laravel.com'],
        // ...
    ]
]
```

<a name="additional-applications"></a>
### 额外应用

通常情况下，Reverb 会为安装它的应用提供一个 WebSocket 服务器。然而，也可以使用单个 Reverb 安装为多个应用提供服务。

例如，你可能希望维护一个单一的 Laravel 应用，通过 Reverb 为多个应用提供 WebSocket 连接。这可以通过在应用的 `config/reverb.php` 配置文件中定义多个 `apps` 来实现：

```php
'apps' => [
    [
        'app_id' => 'my-app-one',
        // ...
    ],
    [
        'app_id' => 'my-app-two',
        // ...
    ],
],
```

<a name="ssl"></a>
### SSL

在大多数情况下，安全的 WebSocket 连接由上游 Web 服务器（如 Nginx）处理，然后再将请求代理到你的 Reverb 服务器。

但是，有时在本地开发期间，让 Reverb 服务器直接处理安全连接会很有用。如果你使用 [Laravel Herd](https://herd.laravel.com) 的安全站点功能，或者使用 [Laravel Valet](/docs/{{version}}/valet) 并对你的应用运行了 [secure 命令](/docs/{{version}}/valet#securing-sites)，你可以使用为你的网站生成的 Herd / Valet 证书来保护 Reverb 连接。为此，将 `REVERB_HOST` 环境变量设置为你站点的主机名，或者在启动 Reverb 服务器时显式传递 `hostname` 选项：

```shell
php artisan reverb:start --host="0.0.0.0" --port=8080 --hostname="laravel.test"
```

由于 Herd 和 Valet 域名解析到 `localhost`，运行上述命令将使你的 Reverb 服务器可以通过安全 WebSocket 协议（`wss`）访问，地址为 `wss://laravel.test:8080`。

你也可以通过在应用的 `config/reverb.php` 配置文件中定义 `tls` 选项手动选择证书。在 `tls` 选项数组中，你可以提供 [PHP SSL 上下文选项](https://www.php.net/manual/en/context.ssl.php) 支持的任何选项：

```php
'options' => [
    'tls' => [
        'local_cert' => '/path/to/cert.pem'
    ],
],
```

<a name="running-server"></a>
## 启动服务器

Reverb 服务器可以通过 `reverb:start` Artisan 命令启动：

```shell
php artisan reverb:start
```

默认情况下，Reverb 服务器会启动在 `0.0.0.0:8080`，使其可从所有网络接口访问。

如果需要指定自定义主机或端口，可以在启动服务器时通过 `--host` 和 `--port` 选项实现：

```shell
php artisan reverb:start --host=127.0.0.1 --port=9000
```

或者，你也可以在应用的 `.env` 配置文件中定义 `REVERB_SERVER_HOST` 和 `REVERB_SERVER_PORT` 环境变量。

需要注意的是，`REVERB_SERVER_HOST` 和 `REVERB_SERVER_PORT` 环境变量不要与 `REVERB_HOST` 和 `REVERB_PORT` 混淆。前者指定 Reverb 服务器自身运行的主机和端口，而后者用于告诉 Laravel 向哪里发送广播消息。例如，在生产环境中，你可以将公共 Reverb 主机名的 443 端口请求路由到运行在 `0.0.0.0:8080` 的 Reverb 服务器。在这种情况下，你的环境变量可以这样定义：

```ini
REVERB_SERVER_HOST=0.0.0.0
REVERB_SERVER_PORT=8080

REVERB_HOST=ws.laravel.com
REVERB_PORT=443
```

<a name="debugging"></a>
### 调试

为了提升性能，Reverb 默认不会输出任何调试信息。如果你希望查看通过 Reverb 服务器传输的数据流，可以在运行 `reverb:start` 命令时添加 `--debug` 选项：

```shell
php artisan reverb:start --debug
```

<a name="restarting"></a>
### 重启

由于 Reverb 是一个长时间运行的进程，对代码的修改在不重启服务器的情况下不会生效。你需要通过 `reverb:restart` Artisan 命令来重启服务器。

`reverb:restart` 命令会在停止服务器之前，确保所有连接被优雅地终止。如果你使用 Supervisor 等进程管理器运行 Reverb，所有连接终止后，进程管理器会自动重启服务器：

```shell
php artisan reverb:restart
```

<a name="monitoring"></a>
## 监控

Reverb 可以通过与 [Laravel Pulse](/docs/{{version}}/pulse) 的集成进行监控。启用 Reverb 的 Pulse 集成后，你可以跟踪服务器处理的连接数和消息数量。

要启用该集成，首先需要确保你已经 [安装 Pulse](/docs/{{version}}/pulse#installation)。然后，将 Reverb 的任意记录器添加到应用的 `config/pulse.php` 配置文件中：

```php
use Laravel\Reverb\Pulse\Recorders\ReverbConnections;
use Laravel\Reverb\Pulse\Recorders\ReverbMessages;

'recorders' => [
    ReverbConnections::class => [
        'sample_rate' => 1,
    ],

    ReverbMessages::class => [
        'sample_rate' => 1,
    ],

    // ...
],
```

接下来，将每个记录器的 Pulse 卡片添加到你的 [Pulse 仪表盘](/docs/{{version}}/pulse#dashboard-customization)：

```blade
<x-pulse>
    <livewire:reverb.connections cols="full" />
    <livewire:reverb.messages cols="full" />
    ...
</x-pulse>
```

连接活动通过定期轮询新更新进行记录。为了确保这些信息在 Pulse 仪表盘上正确显示，你必须在 Reverb 服务器上运行 `pulse:check` 守护进程。如果你在 [水平扩展](#scaling) 配置中运行 Reverb，该守护进程只需要在其中一台服务器上运行即可。

<a name="production"></a>
## 在生产环境中运行 Reverb

由于 WebSocket 服务器是长时间运行的，你可能需要对服务器和托管环境进行一些优化，以确保你的 Reverb 服务器能够根据服务器可用资源有效处理最佳数量的连接。

> [!NOTE]
> [Laravel Cloud](https://cloud.laravel.com) 提供由 Laravel Reverb 集群驱动的全托管 WebSocket 基础设施，让你无需管理基础设施即可扩展和发布使用 Reverb 的应用。

<a name="open-files"></a>
### 打开的文件

每个 WebSocket 连接会保存在内存中，直到客户端或服务器断开连接。在 Unix 和类 Unix 系统中，每个连接都对应一个文件。然而，操作系统和应用程序级别通常对允许打开的文件数量有限制。

<a name="operating-system"></a>
#### 操作系统

在基于 Unix 的操作系统中，你可以使用 `ulimit` 命令查看允许打开的文件数量：

```shell
ulimit -n
```

此命令会显示不同用户允许的打开文件限制。你可以通过编辑 `/etc/security/limits.conf` 文件来更新这些值。例如，将 `forge` 用户的最大打开文件数更新为 10,000，可以这样设置：

```ini
# /etc/security/limits.conf
forge        soft  nofile  10000
forge        hard  nofile  10000
```

<a name="event-loop"></a>
### 事件循环

在底层，Reverb 使用 ReactPHP 事件循环来管理服务器上的 WebSocket 连接。默认情况下，该事件循环由 `stream_select` 提供支持，它不需要额外的扩展。然而，`stream_select` 通常限制在 1,024 个打开文件。因此，如果你计划处理超过 1,000 个并发连接，你需要使用不受同样限制的替代事件循环。

Reverb 在可用时会自动切换到由 `ext-uv` 提供支持的事件循环。这个 PHP 扩展可以通过 PECL 安装：

```shell
pecl install uv
```

<a name="web-server"></a>
### Web 服务器

在大多数情况下，Reverb 在服务器上运行于非面向 Web 的端口。因此，为了将流量路由到 Reverb，你应配置反向代理。假设 Reverb 运行在主机 `0.0.0.0` 和端口 `8080` 上，并且你的服务器使用 Nginx Web 服务器，可以通过以下 Nginx 站点配置为 Reverb 服务器定义反向代理：

```nginx
server {
    ...

    location / {
        proxy_http_version 1.1;
        proxy_set_header Host $http_host;
        proxy_set_header Scheme $scheme;
        proxy_set_header SERVER_PORT $server_port;
        proxy_set_header REMOTE_ADDR $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";

        proxy_pass http://0.0.0.0:8080;
    }

    ...
}
```

> [!WARNING]
> Reverb 在 `/app` 监听 WebSocket 连接，并在 `/apps` 处理 API 请求。你应确保处理 Reverb 请求的 Web 服务器可以提供这两个 URI。如果你使用 [Laravel Forge](https://forge.laravel.com) 管理服务器，Reverb 服务器默认会被正确配置。

通常，Web 服务器会限制允许的连接数量，以防止服务器过载。要将 Nginx Web 服务器允许的连接数增加到 10,000，需要更新 `nginx.conf` 文件中的 `worker_rlimit_nofile` 和 `worker_connections` 值：

```nginx
user forge;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;
worker_rlimit_nofile 10000;

events {
  worker_connections 10000;
  multi_accept on;
}
```

上述配置将允许每个 Nginx 进程生成最多 10,000 个工作进程。此外，该配置将 Nginx 的打开文件限制设置为 10,000。

<a name="ports"></a>
### 端口

基于 Unix 的操作系统通常会限制服务器上可打开的端口数量。你可以通过以下命令查看当前允许的端口范围：

```shell
cat /proc/sys/net/ipv4/ip_local_port_range
# 32768	60999
```

上面的输出显示服务器最多可以处理 28,231（60,999 - 32,768）个连接，因为每个连接都需要一个可用端口。虽然我们推荐使用[水平扩展](#scaling)来增加允许的连接数，你也可以通过更新服务器 `/etc/sysctl.conf` 配置文件中的允许端口范围来增加可用的开放端口数量。

<a name="process-management"></a>
### 进程管理

在大多数情况下，你应使用进程管理器（如 Supervisor）来确保 Reverb 服务器持续运行。如果你使用 Supervisor 来运行 Reverb，应更新服务器 `supervisor.conf` 文件中的 `minfds` 设置，以确保 Supervisor 能够打开处理 Reverb 服务器连接所需的文件：

```ini
[supervisord]
...
minfds=10000
```

<a name="scaling"></a>
### 扩展

如果你需要处理的连接数量超过单台服务器允许的数量，可以通过水平扩展 Reverb 服务器来实现。利用 Redis 的发布/订阅功能，Reverb 能够在多台服务器间管理连接。当你的应用某台 Reverb 服务器接收到消息时，该服务器将使用 Redis 将收到的消息发布给其他所有服务器。

要启用水平扩展，你应在应用的 `.env` 配置文件中将 `REVERB_SCALING_ENABLED` 环境变量设置为 `true`：

```env
REVERB_SCALING_ENABLED=true
```

接下来，你需要一台专用的中央 Redis 服务器，所有 Reverb 服务器将与其通信。Reverb 会使用[为你的应用配置的默认 Redis 连接](/docs/{{version}}/redis#configuration)将消息发布到所有 Reverb 服务器。

一旦启用了 Reverb 的扩展选项并配置了 Redis 服务器，你只需在能够与 Redis 服务器通信的多台服务器上执行 `reverb:start` 命令。这些 Reverb 服务器应放置在负载均衡器后面，以便将传入请求均匀分配到各个服务器。

<a name="events"></a>
## 事件

Reverb 在连接生命周期和消息处理过程中会分发内部事件。你可以[监听这些事件](/docs/{{version}}/events)，以便在管理连接或交换消息时执行相应操作。

Reverb 会分发以下事件：

#### `Laravel\Reverb\Events\ChannelCreated`

创建频道时分发，通常发生在第一个连接订阅特定频道时。该事件接收 `Laravel\Reverb\Protocols\Pusher\Channel` 实例。

#### `Laravel\Reverb\Events\ChannelRemoved`

移除频道时分发，通常发生在最后一个连接取消订阅频道时。该事件接收 `Laravel\Reverb\Protocols\Pusher\Channel` 实例。

#### `Laravel\Reverb\Events\ConnectionPruned`

服务器清理失效连接时分发。该事件接收 `Laravel\Reverb\Contracts\Connection` 实例。

#### `Laravel\Reverb\Events\MessageReceived`

从客户端连接收到消息时分发。该事件接收 `Laravel\Reverb\Contracts\Connection` 实例和原始字符串 `$message`。

#### `Laravel\Reverb\Events\MessageSent`

向客户端连接发送消息时分发。该事件接收 `Laravel\Reverb\Contracts\Connection` 实例和原始字符串 `$message`。
