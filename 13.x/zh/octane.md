# Laravel Octane

- [简介](#introduction)
- [安装](#installation)
- [服务器前置要求](#server-prerequisites)
    - [FrankenPHP](#frankenphp)
    - [RoadRunner](#roadrunner)
    - [Swoole](#swoole)
- [运行应用](#serving-your-application)
    - [通过 HTTPS 运行应用](#serving-your-application-via-https)
    - [通过 Nginx 运行应用](#serving-your-application-via-nginx)
    - [监视文件变化](#watching-for-file-changes)
    - [指定工作进程数量](#specifying-the-worker-count)
    - [指定最大请求数](#specifying-the-max-request-count)
    - [指定最大执行时间](#specifying-the-max-execution-time)
    - [重载工作进程](#reloading-the-workers)
    - [停止服务器](#stopping-the-server)
- [依赖注入与 Octane](#dependency-injection-and-octane)
    - [容器注入](#container-injection)
    - [请求注入](#request-injection)
    - [配置仓库注入](#configuration-repository-injection)
- [管理内存泄漏](#managing-memory-leaks)
- [并发任务](#concurrent-tasks)
- [定时任务与间隔](#ticks-and-intervals)
- [Octane 缓存](#the-octane-cache)
    - [间隔缓存](#cache-intervals)
- [数据表](#tables)

<a name="introduction"></a>
## 简介

[Laravel Octane](https://github.com/laravel/octane) 使用 [FrankenPHP](https://frankenphp.dev/)、[Open Swoole](https://openswoole.com/)、[Swoole](https://github.com/swoole/swoole-src) 和 [RoadRunner](https://roadrunner.dev) 等高性能应用服务器运行应用，大幅提升应用性能。Octane 只启动一次应用，使其常驻内存，然后以极快的速度将请求交给应用处理。

<a name="installation"></a>
## 安装

可以通过 Composer 包管理器安装 Octane：

```shell
composer require laravel/octane
```

安装 Octane 后，可以执行 `octane:install` Artisan 命令，将 Octane 的配置文件安装到应用中：

```shell
php artisan octane:install
```

<a name="server-prerequisites"></a>
## 服务器前置要求

<a name="frankenphp"></a>
### FrankenPHP

[FrankenPHP](https://frankenphp.dev) 是使用 Go 编写的 PHP 应用服务器，支持 Early Hints、Brotli 和 Zstandard 压缩等现代 Web 功能。安装 Octane 并选择 FrankenPHP 作为服务器时，Octane 会自动下载并安装 FrankenPHP 二进制文件。

> [!WARNING]
> FrankenPHP 静态二进制文件自带 PHP，因此更新系统安装的 PHP 不会更新 Octane 使用的 PHP 版本。可以使用 `./frankenphp version` 命令检查其内置 PHP 版本。要应用 PHP 安全更新，请删除项目根目录中的 `frankenphp` 二进制文件，运行 `php artisan octane:install --server=frankenphp` Artisan 命令下载最新版本，然后重启 Octane。如果 FrankenPHP 是全局安装的，请使用原来的安装方式更新它。

<a name="frankenphp-via-laravel-sail"></a>
#### 通过 Laravel Sail 使用 FrankenPHP

如果计划使用 [Laravel Sail](/docs/{{version}}/sail) 开发应用，请运行以下命令安装 Octane 和 FrankenPHP：

```shell
./vendor/bin/sail up

./vendor/bin/sail composer require laravel/octane
```

接下来，使用 `octane:install` Artisan 命令安装 FrankenPHP 二进制文件：

```shell
./vendor/bin/sail artisan octane:install --server=frankenphp
```

最后，在应用的 `docker-compose.yml` 文件中，为 `laravel.test` 服务定义添加 `SUPERVISOR_PHP_COMMAND` 环境变量。该变量包含 Sail 用于通过 Octane 而非 PHP 开发服务器运行应用的命令：

```yaml
services:
  laravel.test:
    environment:
      SUPERVISOR_PHP_COMMAND: "/usr/bin/php -d variables_order=EGPCS /var/www/html/artisan octane:start --server=frankenphp --host=0.0.0.0 --admin-port=2019 --port='${APP_PORT:-80}'" # [tl! add]
      XDG_CONFIG_HOME:  /var/www/html/config # [tl! add]
      XDG_DATA_HOME:  /var/www/html/data # [tl! add]
```

要启用 HTTPS、HTTP/2 和 HTTP/3，请改为进行以下修改：

```yaml
services:
  laravel.test:
    ports:
        - '${APP_PORT:-80}:80'
        - '${VITE_PORT:-5173}:${VITE_PORT:-5173}'
        - '443:443' # [tl! add]
        - '443:443/udp' # [tl! add]
    environment:
      SUPERVISOR_PHP_COMMAND: "/usr/bin/php -d variables_order=EGPCS /var/www/html/artisan octane:start --host=localhost --port=443 --admin-port=2019 --https" # [tl! add]
      XDG_CONFIG_HOME:  /var/www/html/config # [tl! add]
      XDG_DATA_HOME:  /var/www/html/data # [tl! add]
```

通常应通过 `https://localhost` 访问 FrankenPHP Sail 应用，因为使用 `https://127.0.0.1` 需要额外配置，且[不建议使用](https://frankenphp.dev/docs/known-issues/#using-https127001-with-docker)。

<a name="frankenphp-via-docker"></a>
#### 通过 Docker 使用 FrankenPHP

使用 FrankenPHP 官方 Docker 镜像可以提高性能，并使用 FrankenPHP 静态安装中未包含的额外扩展。此外，官方 Docker 镜像支持在 FrankenPHP 原生不支持的平台（例如 Windows）上运行 FrankenPHP。官方 Docker 镜像既适用于本地开发，也适用于生产环境。

你可以使用以下 Dockerfile 作为容器化 FrankenPHP 驱动的 Laravel 应用的起点：

```dockerfile
FROM dunglas/frankenphp

RUN install-php-extensions \
    pcntl
    # 在此添加其他 PHP 扩展...

COPY . /app

ENTRYPOINT ["php", "artisan", "octane:frankenphp"]
```

然后，在开发期间可以使用以下 Docker Compose 文件运行应用：

```yaml
# compose.yaml
services:
  frankenphp:
    build:
      context: .
    entrypoint: php artisan octane:frankenphp --workers=1 --max-requests=1
    ports:
      - "8000:8000"
    volumes:
      - .:/app
```

如果显式向 `php artisan octane:start` 命令传入 `--log-level` 选项，Octane 会使用 FrankenPHP 原生的日志记录器，并在未进行其他配置时生成结构化 JSON 日志。

有关通过 Docker 运行 FrankenPHP 的更多信息，请参阅 [FrankenPHP 官方文档](https://frankenphp.dev/docs/docker/)。

<a name="frankenphp-caddyfile"></a>
#### 自定义 Caddyfile 配置

使用 FrankenPHP 时，可以在启动 Octane 时通过 `--caddyfile` 选项指定自定义 Caddyfile：

```shell
php artisan octane:start --server=frankenphp --caddyfile=/path/to/your/Caddyfile
```

这让你可以在默认设置之外自定义 FrankenPHP 配置，例如添加自定义中间件、配置高级路由或设置自定义指令。有关 Caddyfile 语法和配置选项的更多信息，请参阅 [Caddy 官方文档](https://caddyserver.com/docs/caddyfile)。

<a name="roadrunner"></a>
### RoadRunner

[RoadRunner](https://roadrunner.dev) 由使用 Go 构建的 RoadRunner 二进制文件驱动。首次启动基于 RoadRunner 的 Octane 服务器时，Octane 会提示你下载并安装 RoadRunner 二进制文件。

<a name="roadrunner-via-laravel-sail"></a>
#### 通过 Laravel Sail 使用 RoadRunner

如果计划使用 [Laravel Sail](/docs/{{version}}/sail) 开发应用，请运行以下命令安装 Octane 和 RoadRunner：

```shell
./vendor/bin/sail up

./vendor/bin/sail composer require laravel/octane spiral/roadrunner-cli spiral/roadrunner-http
```

接下来，启动 Sail shell，并使用 `rr` 可执行文件获取最新的 Linux 版 RoadRunner 二进制文件：

```shell
./vendor/bin/sail shell

# 在 Sail shell 中...
./vendor/bin/rr get-binary
```

然后，在应用的 `docker-compose.yml` 文件中，为 `laravel.test` 服务定义添加 `SUPERVISOR_PHP_COMMAND` 环境变量。该变量包含 Sail 用于通过 Octane 而非 PHP 开发服务器运行应用的命令：

```yaml
services:
  laravel.test:
    environment:
      SUPERVISOR_PHP_COMMAND: "/usr/bin/php -d variables_order=EGPCS /var/www/html/artisan octane:start --server=roadrunner --host=0.0.0.0 --rpc-port=6001 --port='${APP_PORT:-80}'" # [tl! add]
```

最后，确保 `rr` 二进制文件可执行，并构建 Sail 镜像：

```shell
chmod +x ./rr

./vendor/bin/sail build --no-cache
```

<a name="swoole"></a>
### Swoole

如果计划使用 Swoole 应用服务器运行 Laravel Octane 应用，必须安装 Swoole PHP 扩展。通常可以通过 PECL 安装：

```shell
pecl install swoole
```

<a name="openswoole"></a>
#### Open Swoole

如果希望使用 Open Swoole 应用服务器运行 Laravel Octane 应用，必须安装 Open Swoole PHP 扩展。通常可以通过 PECL 安装：

```shell
pecl install openswoole
```

Laravel Octane 配合 Open Swoole 可提供与 Swoole 相同的功能，例如并发任务、定时任务和间隔任务。

<a name="swoole-via-laravel-sail"></a>
#### 通过 Laravel Sail 使用 Swoole

> [!WARNING]
> 通过 Sail 运行 Octane 应用之前，请确保使用最新版本的 Laravel Sail，并在应用根目录中执行 `./vendor/bin/sail build --no-cache`。

你也可以使用 Laravel 官方的 Docker 开发环境 [Laravel Sail](/docs/{{version}}/sail) 开发基于 Swoole 的 Octane 应用。Laravel Sail 默认包含 Swoole 扩展，但仍需调整 Sail 使用的 `docker-compose.yml` 文件。

首先，在应用的 `docker-compose.yml` 文件中，为 `laravel.test` 服务定义添加 `SUPERVISOR_PHP_COMMAND` 环境变量。该变量包含 Sail 用于通过 Octane 而非 PHP 开发服务器运行应用的命令：

```yaml
services:
  laravel.test:
    environment:
      SUPERVISOR_PHP_COMMAND: "/usr/bin/php -d variables_order=EGPCS /var/www/html/artisan octane:start --server=swoole --host=0.0.0.0 --port='${APP_PORT:-80}'" # [tl! add]
```

最后，构建 Sail 镜像：

```shell
./vendor/bin/sail build --no-cache
```

<a name="swoole-configuration"></a>
#### Swoole 配置

Swoole 支持一些额外配置选项，你可以在需要时将其添加到 `octane` 配置文件中。由于这些选项很少需要修改，因此默认配置文件中不包含它们：

```php
'swoole' => [
    'options' => [
        'log_file' => storage_path('logs/swoole_http.log'),
        'package_max_length' => 10 * 1024 * 1024,
    ],
],
```

<a name="serving-your-application"></a>
## 运行应用

可以通过 `octane:start` Artisan 命令启动 Octane 服务器。默认情况下，该命令使用应用的 `octane` 配置文件中 `server` 选项指定的服务器：

```shell
php artisan octane:start
```

默认情况下，Octane 在 8000 端口启动服务器，因此你可以通过浏览器访问 `http://localhost:8000` 来访问应用。

<a name="keeping-octane-running-in-production"></a>
#### 在生产环境中保持 Octane 运行

如果将 Octane 应用部署到生产环境，应使用 Supervisor 等进程监控器确保 Octane 服务器持续运行。Octane 的 Supervisor 配置文件示例如下：

```ini
[program:octane]
process_name=%(program_name)s_%(process_num)02d
command=php /home/forge/example.com/artisan octane:start --server=frankenphp --host=127.0.0.1 --port=8000
autostart=true
autorestart=true
user=forge
redirect_stderr=true
stdout_logfile=/home/forge/example.com/storage/logs/octane.log
stopwaitsecs=3600
```

<a name="serving-your-application-via-https"></a>
### 通过 HTTPS 运行应用

默认情况下，通过 Octane 运行的应用生成的链接以 `http://` 开头。通过 HTTPS 运行应用时，可以将应用的 `config/octane.php` 配置文件所使用的 `OCTANE_HTTPS` 环境变量设置为 `true`。该值为 `true` 时，Octane 会让 Laravel 为所有生成的链接添加 `https://` 前缀：

```php
'https' => env('OCTANE_HTTPS', false),
```

<a name="serving-your-application-via-nginx"></a>
### 通过 Nginx 运行应用

> [!NOTE]
> 如果你尚未准备好管理自己的服务器配置，或不熟悉运行可靠的 Laravel Octane 应用所需的各种服务配置，可以了解 [Laravel Cloud](https://cloud.laravel.com)，它提供完全托管的 Laravel Octane 支持。

在生产环境中，应将 Octane 应用部署在 Nginx 或 Apache 等传统 Web 服务器之后。这样，Web 服务器可以提供图片、样式表等静态资源，并管理 SSL 证书终止。

在下面的 Nginx 配置示例中，Nginx 将提供站点的静态资源，并将请求代理到运行在 8000 端口的 Octane 服务器：

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    listen [::]:80;
    server_name domain.com;
    server_tokens off;
    root /home/forge/domain.com/public;

    index index.php;

    charset utf-8;

    location /index.php {
        try_files /not_exists @octane;
    }

    location / {
        try_files $uri $uri/ @octane;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    access_log off;
    error_log  /var/log/nginx/domain.com-error.log error;

    error_page 404 /index.php;

    location @octane {
        set $suffix "";

        if ($uri = /index.php) {
            set $suffix ?$query_string;
        }

        proxy_http_version 1.1;
        proxy_set_header Host $http_host;
        proxy_set_header Scheme $scheme;
        proxy_set_header SERVER_PORT $server_port;
        proxy_set_header REMOTE_ADDR $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;

        proxy_pass http://127.0.0.1:8000$suffix;
    }
}
```

<a name="watching-for-file-changes"></a>
### 监视文件变化

由于 Octane 服务器启动时只将应用加载到内存一次，因此刷新浏览器时不会反映应用文件的变更。例如，添加到 `routes/web.php` 文件中的路由定义必须在服务器重启后才会生效。为方便起见，可以使用 `--watch` 标志，让 Octane 在应用文件发生任何变化时自动重启服务器：

```shell
php artisan octane:start --watch
```

使用此功能前，请确保本地开发环境已安装 [Node](https://nodejs.org)。此外，还应在项目中安装 [Chokidar](https://github.com/paulmillr/chokidar) 文件监视库：

```shell
npm install --save-dev chokidar
```

你可以使用应用的 `config/octane.php` 配置文件中的 `watch` 选项，配置要监视的目录和文件。

<a name="specifying-the-worker-count"></a>
### 指定工作进程数量

默认情况下，Octane 会为机器的每个 CPU 核心启动一个应用请求工作进程。这些工作进程随后用于处理进入应用的 HTTP 请求。调用 `octane:start` 命令时，可以使用 `--workers` 选项手动指定要启动的工作进程数：

```shell
php artisan octane:start --workers=4
```

如果使用 Swoole 应用服务器，还可以指定要启动的[「任务工作进程」](#concurrent-tasks)数量：

```shell
php artisan octane:start --workers=4 --task-workers=6
```

<a name="specifying-the-max-request-count"></a>
### 指定最大请求数

为帮助防止意外的内存泄漏，Octane 会在工作进程处理 500 个请求后优雅地重启该进程。可以使用 `--max-requests` 选项调整此数量：

```shell
php artisan octane:start --max-requests=250
```

<a name="specifying-the-max-execution-time"></a>
### 指定最大执行时间

默认情况下，Laravel Octane 通过应用的 `config/octane.php` 配置文件中的 `max_execution_time` 选项，将传入请求的最长执行时间设置为 30 秒：

```php
'max_execution_time' => 30,
```

该设置定义传入请求在被终止前允许执行的最长秒数。将此值设置为 `0` 会完全禁用执行时间限制。对于处理文件上传、数据处理或外部服务 API 调用等长时间运行请求的应用，此选项尤其有用。

> [!WARNING]
> 修改 `max_execution_time` 配置后，必须重启 Octane 服务器才能使更改生效。

<a name="reloading-the-workers"></a>
### 重载工作进程

你可以使用 `octane:reload` 命令优雅地重启 Octane 服务器的应用工作进程。通常应在部署后执行此操作，以便将新部署的代码加载到内存中，用于处理后续请求：

```shell
php artisan octane:reload
```

<a name="stopping-the-server"></a>
### 停止服务器

可以使用 `octane:stop` Artisan 命令停止 Octane 服务器：

```shell
php artisan octane:stop
```

<a name="checking-the-server-status"></a>
#### 检查服务器状态

可以使用 `octane:status` Artisan 命令检查 Octane 服务器的当前状态：

```shell
php artisan octane:status
```

<a name="dependency-injection-and-octane"></a>
## 依赖注入与 Octane

由于 Octane 只启动一次应用，并在处理请求期间将其保留在内存中，构建应用时需要注意一些事项。例如，应用服务提供者的 `register` 和 `boot` 方法只会在请求工作进程初次启动时执行一次，后续请求会复用同一个应用实例。

因此，将应用服务容器或请求注入任何对象的构造函数时，应特别小心。这样做可能使对象在后续请求中持有过时的容器或请求。

Octane 会在请求之间自动重置框架自身的状态。不过，Octane 并不总是知道如何重置应用创建的全局状态。因此，你应了解如何以兼容 Octane 的方式构建应用。下面将讨论使用 Octane 时最常见的潜在问题。

<a name="container-injection"></a>
### 容器注入

通常，应避免将应用服务容器或 HTTP 请求实例注入其他对象的构造函数。例如，以下绑定将整个应用服务容器注入一个以单例方式绑定的对象：

```php
use App\Service;
use Illuminate\Contracts\Foundation\Application;

/**
 * 注册应用服务。
 */
public function register(): void
{
    $this->app->singleton(Service::class, function (Application $app) {
        return new Service($app);
    });
}
```

在此示例中，如果 `Service` 实例在应用启动过程中被解析，容器就会注入该服务，而在后续请求中，`Service` 实例仍持有同一个容器。这对你的特定应用**可能**不是问题；但它可能导致容器意外缺少在启动周期后续阶段或后续请求中添加的绑定。

作为解决方法，你可以不再将该绑定注册为单例，也可以向服务注入一个容器解析器闭包，使其始终解析当前容器实例：

```php
use App\Service;
use Illuminate\Container\Container;
use Illuminate\Contracts\Foundation\Application;

$this->app->bind(Service::class, function (Application $app) {
    return new Service($app);
});

$this->app->singleton(Service::class, function () {
    return new Service(fn () => Container::getInstance());
});
```

全局 `app` 辅助函数和 `Container::getInstance()` 方法始终返回最新版本的应用容器。

<a name="request-injection"></a>
### 请求注入

通常，应避免将应用服务容器或 HTTP 请求实例注入其他对象的构造函数。例如，以下绑定将整个请求实例注入一个以单例方式绑定的对象：

```php
use App\Service;
use Illuminate\Contracts\Foundation\Application;

/**
 * 注册应用服务。
 */
public function register(): void
{
    $this->app->singleton(Service::class, function (Application $app) {
        return new Service($app['request']);
    });
}
```

在此示例中，如果 `Service` 实例在应用启动过程中被解析，HTTP 请求就会注入该服务，而在后续请求中，`Service` 实例仍持有同一个请求。因此，所有请求头、输入和查询字符串数据以及其他请求数据都会不正确。

作为解决方法，你可以不再将该绑定注册为单例，也可以向服务注入一个请求解析器闭包，使其始终解析当前请求实例。更推荐的方式是在运行时，直接将对象需要的具体请求信息传给对象的某个方法：

```php
use App\Service;
use Illuminate\Contracts\Foundation\Application;

$this->app->bind(Service::class, function (Application $app) {
    return new Service($app['request']);
});

$this->app->singleton(Service::class, function (Application $app) {
    return new Service(fn () => $app['request']);
});

// 或者...

$service->method($request->input('name'));
```

全局 `request` 辅助函数始终返回应用当前正在处理的请求，因此可以在应用中安全使用。

> [!WARNING]
> 在控制器方法和路由闭包中对 `Illuminate\Http\Request` 实例使用类型声明是可以的。

<a name="configuration-repository-injection"></a>
### 配置仓库注入

通常，应避免将配置仓库实例注入其他对象的构造函数。例如，以下绑定将配置仓库注入一个以单例方式绑定的对象：

```php
use App\Service;
use Illuminate\Contracts\Foundation\Application;

/**
 * 注册应用服务。
 */
public function register(): void
{
    $this->app->singleton(Service::class, function (Application $app) {
        return new Service($app->make('config'));
    });
}
```

在此示例中，如果配置值在请求之间发生变化，该服务将无法访问新值，因为它依赖的是原始仓库实例。

作为解决方法，你可以不再将该绑定注册为单例，也可以向该类注入一个配置仓库解析器闭包：

```php
use App\Service;
use Illuminate\Container\Container;
use Illuminate\Contracts\Foundation\Application;

$this->app->bind(Service::class, function (Application $app) {
    return new Service($app->make('config'));
});

$this->app->singleton(Service::class, function () {
    return new Service(fn () => Container::getInstance()->make('config'));
});
```

全局 `config` 始终返回最新版本的配置仓库，因此可以在应用中安全使用。

<a name="managing-memory-leaks"></a>
### 管理内存泄漏

请记住，Octane 在请求之间会将应用保留在内存中，因此向静态维护的数组添加数据会导致内存泄漏。例如，以下控制器存在内存泄漏，因为每次应用收到请求都会继续向静态 `$data` 数组添加数据：

```php
use App\Service;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

/**
 * 处理传入的请求。
 */
public function index(Request $request): array
{
    Service::$data[] = Str::random(10);

    return [
        // ...
    ];
}
```

构建应用时，应特别注意避免产生此类内存泄漏。建议在本地开发期间监控应用的内存使用情况，确保没有引入新的内存泄漏。

<a name="concurrent-tasks"></a>
## 并发任务

> [!WARNING]
> 此功能需要 [Swoole](#swoole)。

使用 Swoole 时，可以通过轻量级后台任务并发执行操作。你可以使用 Octane 的 `concurrently` 方法实现这一点，并结合 PHP 数组解构获取每项操作的结果：

```php
use App\Models\User;
use App\Models\Server;
use Laravel\Octane\Facades\Octane;

[$users, $servers] = Octane::concurrently([
    fn () => User::all(),
    fn () => Server::all(),
]);
```

Octane 处理的并发任务使用 Swoole 的「任务工作进程」，并在与传入请求完全不同的进程中执行。可用于处理并发任务的工作进程数量由 `octane:start` 命令的 `--task-workers` 指令决定：

```shell
php artisan octane:start --workers=4 --task-workers=6
```

由于 Swoole 任务系统的限制，调用 `concurrently` 方法时，提供的任务不能超过 1024 个。

<a name="ticks-and-intervals"></a>
## 定时任务与间隔

> [!WARNING]
> 此功能需要 [Swoole](#swoole)。

使用 Swoole 时，可以注册每隔指定秒数执行一次的「tick」操作。你可以通过 `tick` 方法注册「tick」回调。传给 `tick` 方法的第一个参数应是表示定时器名称的字符串，第二个参数应是在指定间隔调用的可调用对象。

在此示例中，我们将注册一个每 10 秒调用一次的闭包。通常应在应用某个服务提供者的 `boot` 方法中调用 `tick` 方法：

```php
Octane::tick('simple-ticker', fn () => ray('Ticking...'))
    ->seconds(10);
```

使用 `immediate` 方法，可以让 Octane 在服务器初次启动时立即调用 tick 回调，之后每隔 N 秒调用一次：

```php
Octane::tick('simple-ticker', fn () => ray('Ticking...'))
    ->seconds(10)
    ->immediate();
```

<a name="the-octane-cache"></a>
## Octane 缓存

> [!WARNING]
> 此功能需要 [Swoole](#swoole)。

使用 Swoole 时，可以使用 Octane 缓存驱动，其读写速度每秒可达 200 万次操作。因此，对于缓存层需要极高读写速度的应用，此缓存驱动是一个很好的选择。

该缓存驱动基于 [Swoole 数据表](https://www.swoole.co.uk/docs/modules/swoole-table)。存储在缓存中的所有数据都可供服务器上的所有工作进程访问，但服务器重启时缓存数据会被清空：

```php
Cache::store('octane')->put('framework', 'Laravel', 30);
```

> [!NOTE]
> 可以在应用的 `octane` 配置文件中定义 Octane 缓存允许的最大条目数。

<a name="cache-intervals"></a>
### 间隔缓存

除 Laravel 缓存系统提供的常规方法外，Octane 缓存驱动还支持基于间隔的缓存。这些缓存会按指定间隔自动刷新，应在应用某个服务提供者的 `boot` 方法中注册。例如，以下缓存每五秒刷新一次：

```php
use Illuminate\Support\Str;

Cache::store('octane')->interval('random', function () {
    return Str::random(10);
}, seconds: 5);
```

<a name="tables"></a>
## 数据表

> [!WARNING]
> 此功能需要 [Swoole](#swoole)。

使用 Swoole 时，可以定义并操作自己的任意 [Swoole 数据表](https://www.swoole.co.uk/docs/modules/swoole-table)。Swoole 数据表提供极高的吞吐性能，表中的数据可供服务器上的所有工作进程访问。但服务器重启时，表中数据会丢失。

应在应用的 `octane` 配置文件中的 `tables` 配置数组中定义数据表。系统已为你配置了一个最多允许 1000 行的示例表。如下所示，可以在列类型后指定列大小，配置字符串列的最大长度：

```php
'tables' => [
    'example:1000' => [
        'name' => 'string:1000',
        'votes' => 'int',
    ],
],
```

要访问数据表，可以使用 `Octane::table` 方法：

```php
use Laravel\Octane\Facades\Octane;

Octane::table('example')->set('uuid', [
    'name' => 'Nuno Maduro',
    'votes' => 1000,
]);

return Octane::table('example')->get('uuid');
```

> [!WARNING]
> Swoole 数据表支持的列类型为：`string`、`int` 和 `float`。
