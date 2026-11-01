
# Laravel 辛烷值

- [简介](#introduction)
- [安装指南](#installation)
- [服务器环境要求](#server-prerequisites)
    - [FrankenPHP 集成](#frankenphp)
    - [RoadRunner 集成](#roadrunner)
    - [Swoole 集成](#swoole)
- [应用服务部署](#serving-your-application)
    - [HTTPS 服务部署](#serving-your-application-via-https)
    - [Nginx 代理部署](#serving-your-application-via-nginx)
    - [文件变更监听](#watching-for-file-changes)
    - [工作进程数配置](#specifying-the-worker-count)
    - [最大请求数设置](#specifying-the-max-request-count)
    - [工作进程重启](#reloading-the-workers)
    - [服务停止操作](#stopping-the-server)
- [依赖注入与 Octane](#dependency-injection-and-octane)
    - [容器注入](#container-injection)
    - [请求注入](#request-injection)
    - [配置仓库注入](#configuration-repository-injection)
- [内存泄漏管理](#managing-memory-leaks)
- [并发任务处理](#concurrent-tasks)
- [定时器与间隔任务](#ticks-and-intervals)
- [Octane 缓存系统](#the-octane-cache)
- [数据表操作](#tables)

<a name="introduction"></a>
## 简介

[Laravel 辛烷值](https://github.com/laravel/octane) 通过高性能应用服务器（如 [FrankenPHP](https://frankenphp.dev/), [Open Swoole](https://openswoole.com/), [Swoole](https://github.com/swoole/swoole-src), 和 [RoadRunner](https://roadrunner.dev)）来运行您的应用，从而大幅提升性能。Octane 会在启动时一次性加载您的应用并常驻内存，随后以超高速处理请求。

<a name="installation"></a>
## 安装指南

可以通过 Composer 包管理器安装 Octane：

```shell
composer require laravel/octane
```

安装完成后，可以执行 `octane:install` Artisan 命令，该命令会在您的应用中安装 Octane 的配置文件：

```shell
php artisan octane:install
```

<a name="server-prerequisites"></a>
## 服务器环境要求

> [!警告]
> Laravel 辛烷值 需要 [PHP 8.1+](https://php.net/releases/).

<a name="frankenphp"></a>
### FrankenPHP

[FrankenPHP](https://frankenphp.dev) 是一款基于 Go 语言开发的 PHP 应用服务器，支持早期提示（early hints）、Brotli 和 Zstandard 压缩等现代 Web 特性。当您安装 Octane 并选择 FrankenPHP 作为服务器时，Octane 将自动为您下载并安装 FrankenPHP 二进制文件。



<a name="frankenphp-via-laravel-sail"></a>
#### 通过 Laravel Sail 使用 FrankenPHP

如果您计划使用 [Laravel Sail](https://docs/laravel/12.x/sail) 进行开发，请运行以下命令安装 Octane 和 FrankenPHP：

```shell
./vendor/bin/sail up

./vendor/bin/sail composer require laravel/octane
```

接着使用 `octane:install` Artisan 命令安装 FrankenPHP 二进制文件：

```shell
./vendor/bin/sail artisan octane:install --server=frankenphp
```

最后，在您应用的 `docker-compose.yml` 文件中，为 `laravel.test` 服务添加 `SUPERVISOR_PHP_COMMAND` 环境变量。该变量将指定 Sail 使用 Octane 而非 PHP 开发服务器来运行应用：

```yaml
services:
  laravel.test:
    environment:
      SUPERVISOR_PHP_COMMAND: "/usr/bin/php -d variables_order=EGPCS /var/www/html/artisan octane:start --server=frankenphp --host=0.0.0.0 --admin-port=2019 --port='${APP_PORT:-80}'"
      XDG_CONFIG_HOME:  /var/www/html/config
      XDG_DATA_HOME:  /var/www/html/data
```

如需启用 HTTPS、HTTP/2 和 HTTP/3，请改用以下配置：

```yaml
services:
  laravel.test:
    ports:
        - '${APP_PORT:-80}:80'
        - '${VITE_PORT:-5173}:${VITE_PORT:-5173}'
        - '443:443'
        - '443:443/udp'
    environment:
      SUPERVISOR_PHP_COMMAND: "/usr/bin/php -d variables_order=EGPCS /var/www/html/artisan octane:start --host=localhost --port=443 --admin-port=2019 --https"
      XDG_CONFIG_HOME:  /var/www/html/config
      XDG_DATA_HOME:  /var/www/html/data
```

建议通过 `https://localhost` 访问 FrankenPHP Sail 应用。使用 `https://127.0.0.1` 需要额外配置，且[不推荐](https://frankenphp.dev/docs/known-issues/#using-https127001-with-docker)使用该方式。


<a name="frankenphp-via-docker"></a>
#### 通过 Docker 使用 FrankenPHP

FrankenPHP 官方 Docker 镜像能提供更优性能，并支持静态安装版未包含的额外扩展。此外，这些镜像还支持在 Windows 等原生不支持 FrankenPHP 的平台上运行，既适用于本地开发也适用于生产环境。

以下 Dockerfile 可作为构建 FrankenPHP 驱动的 Laravel 应用容器的基础模板：

```dockerfile
FROM dunglas/frankenphp

RUN install-php-extensions \
    pcntl
    # Add other PHP extensions here...

COPY . /app

ENTRYPOINT ["php", "artisan", "octane:frankenphp"]
```

开发阶段可使用以下 Docker Compose 配置文件运行应用：

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

若向 `php artisan octane:start` 命令显式传递 `--log-level` 参数，Octane 将启用 FrankenPHP 原生日志记录器，默认生成结构化 JSON 日志（除非另行配置）。

更多 Docker 运行 FrankenPHP 的细节，请参阅[官方 FrankenPHP 文档](https://frankenphp.dev/docs/docker/)。


<a name="roadrunner"></a>
### RoadRunner

[RoadRunner](https://roadrunner.dev) 由 Go 语言编写的 RoadRunner 二进制驱动。首次启动基于 RoadRunner 的 Octane 服务时，Octane 将自动提示下载并安装 RoadRunner 二进制文件。

<a name="roadrunner-via-laravel-sail"></a>
#### 通过 Laravel Sail 使用 RoadRunner

若计划使用 [Laravel Sail](https://docs/laravel/12.x/sail) 开发，请执行以下命令安装 Octane 和 RoadRunner：

```shell
./vendor/bin/sail up

./vendor/bin/sail composer require laravel/octane spiral/roadrunner-cli spiral/roadrunner-http
```



接下来，你应该启动一个 Sail shell，并使用 `rr` 可执行文件来获取最新的基于 Linux 构建的 RoadRunner 二进制文件：

```shell
./vendor/bin/sail shell

# 在 Sail shell 中...
./vendor/bin/rr get-binary
```
然后，在你的应用程序的`docker-compose.yml`文件中的 `laravel.test`服务定义中添加一个 `SUPERVISOR_PHP_COMMAND` 环境变量。这个环境变量将包含 Sail 用来使用 Octane 为你的应用提供服务的命令，而不是使用 PHP 开发服务器：

```yaml
services:
  laravel.test:
    environment:
      SUPERVISOR_PHP_COMMAND: "/usr/bin/php -d variables_order=EGPCS /var/www/html/artisan octane:start --server=roadrunner --host=0.0.0.0 --rpc-port=6001 --port='${APP_PORT:-80}'" # [tl! add]
```

最后，确保 `rr` 可执行并构建你的 Sail 镜像：

```shell
chmod +x ./rr

./vendor/bin/sail build --no-cache
```

<a name="swoole"></a>
### Swoole

如果你计划使用 Swoole 应用服务器为你的 Laravel Octane 应用提供服务，你必须安装 Swoole PHP 扩展。通常情况下，可以通过 PECL 完成：

```shell
pecl install swoole
```

<a name="openswoole"></a>
#### Open Swoole

如果你想使用 Open Swoole 应用服务器为你的 Laravel Octane 应用提供服务，你必须安装 Open Swoole PHP 扩展。通常情况下，可以通过 PECL 完成：

```shell
pecl install openswoole
```

使用 Laravel Octane 与 Open Swoole 提供了与 Swoole 相同的功能，如并发任务、时钟周期和间隔。

<a name="swoole-via-laravel-sail"></a>
#### 通过 Laravel Sail 使用 Swoole

> [!警告]
> 在通过 Sail 提供 Octane 应用服务之前，请确保你有最新版本的 Laravel Sail，并在应用程序的根目录中执行 `./vendor/bin/sail build --no-cache`。



或者，你可以使用 [Laravel Sail](/docs/laravel/12.x/sail) 来开发基于 Swoole 的 Octane 应用程序，这是 Laravel 的官方基于 Docker 的开发环境。Laravel Sail 默认包含 Swoole 扩展。然而，你仍需要调整 Sail 使用的 `docker-compose.yml` 文件。

要开始，向你应用程序的 `docker-compose.yml` 文件中的 `laravel.test` 服务定义中添加一个 `SUPERVISOR_PHP_COMMAND` 环境变量。这个环境变量将包含 Sail 用来使用 Octane 为你的应用提供服务的命令，而不是使用 PHP 开发服务器：

```yaml
services:
  laravel.test:
    environment:
      SUPERVISOR_PHP_COMMAND: "/usr/bin/php -d variables_order=EGPCS /var/www/html/artisan octane:start --server=swoole --host=0.0.0.0 --port='${APP_PORT:-80}'" # [tl! add]
```

最后，构建你的 Sail 镜像：

```shell
./vendor/bin/sail build --no-cache
```

<a name="swoole-configuration"></a>
#### Swoole 配置

Swoole 支持一些额外的配置选项，如果需要，你可以将它们添加到你的 `octane` 配置文件中。由于它们很少需要被修改，这些选项没有包含在默认配置文件中：

```php
'swoole' => [
    'options' => [
        'log_file' => storage_path('logs/swoole_http.log'),
        'package_max_length' => 10 * 1024 * 1024,
    ],
],
```

<a name="serving-your-application"></a>
## 为你的应用提供服务

Octane 服务器可以通过 `octane:start` Artisan 命令启动。默认情况下，此命令将使用你应用程序的 `octane` 配置文件的 `server` 指定的服务器：

```shell
php artisan octane:start
```

默认情况下，Octane 将在端口 8000 上启动服务器，所以你可以通过 `http://localhost:8000` 在 Web 浏览器中访问你的应用程序。



<a name="serving-your-application-via-https"></a>
### 通过 HTTPS 提供你的应用程序

默认情况下，通过Octane运行的应用程序会生成前缀为 `http://`的链接。 当通过HTTPS为应用程序提供服务时，可以将应用程序的`config/octane.php`配置文件中使用的`OCTANE_HTTPS`环境变量设置为`true`。 当此配置值设置为`true`时，Octane将指示Laravel在所有生成的链接前加上`https://`：

```php
'https' => env('OCTANE_HTTPS', false),
```

<a name="serving-your-application-via-nginx"></a>
### 通过 Nginx 为你的应用提供服务

> [注意]
> 如果你还没有准备好管理自己的服务器配置，或者不熟悉配置运行一个强大的Laravel Octane应用程序所需的所有各种服务，请查看[Laravel Cloud](https://cloud.laravel.com)，它提供完全托管的Laravel Octane支持。

在生产环境中，您应该在Nginx或Apache等传统web服务器后面为Octane应用程序提供服务。这样做将允许web服务器为您的静态资产（如图像和样式表）提供服务，并管理您的SSL证书终止。

在下面的Nginx配置示例中，Nginx将向运行在端口8000上的Octane服务器提供站点的静态资产和代理请求：

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
### 监视文件更改

由于您的应用程序在Octane服务器启动时仅加载一次到内存中，因此当您刷新浏览器时，对应用程序文件所做的任何更改都不会立即生效。例如，添加到`routes/web.php`文件中的路由定义只有在服务器重新启动后才会生效。为了方便起见，您可以使用`--watch`标志来指示Octane在应用程序中的任何文件发生更改时自动重新启动服务器：

```shell
php artisan octane:start --watch
```

在使用此功能之前，您应确保在本地开发环境中已安装[Node](https://nodejs.org)。此外，您还应在项目中安装[Chokidar](https://github.com/paulmillr/chokidar)文件监视库：

```shell
npm install --save-dev chokidar
```

您可以在应用程序的`config/octane.php`配置文件中，使用`watch`配置选项来配置应监视的目录和文件。

<a name="specifying-the-worker-count"></a>
### 指定工作进程数量

默认情况下，Octane会为你的机器提供的每个CPU核心启动一个应用程序请求工作进程。当HTTP请求进入你的应用程序时，这些工作进程将用于处理这些请求。在调用`octane:start`命令时，你可以使用`--workers`选项手动指定要启动的工作进程数量：

```shell
php artisan octane:start --workers=4
```

如果你正在使用Swoole应用服务器，您还可以指定希望启动多少个[任务工作进程](#concurrent-tasks)：

```shell
php artisan octane:start --workers=4 --task-workers=6
```

<a name="specifying-the-max-request-count"></a>


### 指定最大请求数

为了帮助防止偶发的内存泄漏，Octane 会在任意 Worker 处理完 **500 个请求后**，优雅地重启该 Worker。
如果要调整该数量，可以使用 `--max-requests` 选项：

```shell
php artisan octane:start --max-requests=250
```

### 重新加载 Workers

你可以使用 `octane:reload` 命令优雅地重启 Octane 服务器的应用程序 Workers。
通常，这个操作应该在 **部署（deployment）之后执行**，以便你新部署的代码被加载到内存中，并用于处理后续的请求：
You may gracefully restart the Octane server's application workers using the `octane:reload` command. Typically, this should be done after deployment so that your newly deployed code is loaded into memory and is used to serve to subsequent requests:

```shell
php artisan octane:reload
```

### 停止服务器

你可以使用 `octane:stop` Artisan 命令停止 Octane 服务器：

```shell
php artisan octane:stop
```

#### 检查服务器状态

你可以使用 `octane:status` Artisan 命令检查 Octane 服务器的当前状态：

```shell
php artisan octane:status
```

## 依赖注入与 Octane

由于 Octane 只会 **启动（boot）你的应用一次**，并在处理请求时保持它驻留在内存中，因此在构建应用时你需要考虑一些注意事项（caveats）。
例如，应用的 Service Providers 中的 `register` 和 `boot` 方法 **只会在 Worker 首次启动时执行一次**。在后续请求中，将会复用同一个应用实例。

基于这一点，当在任意对象的构造函数中注入 **应用服务容器（Service Container）或 Request** 时，你应该格外小心。
如果这样做，在后续请求中，该对象可能会持有 **过期（stale）的 Container 或 Request 版本**。

Octane 会在每次请求之间 **自动重置（reset）框架的第一方状态（first-party framework state）**。
但是，Octane 并不总是能够知道如何重置 **由你的应用创建的全局状态（global state）**。
因此，你应该了解如何以 **对 Octane 友好的方式** 构建你的应用。
下面，我们将讨论在使用 Octane 时可能引发问题的最常见场景。



### 容器注入（Container Injection）

通常情况下，你应该避免在其他对象的构造函数中注入应用服务容器（Service Container）或 HTTP Request 实例。
例如，下面的绑定将整个应用服务容器注入到一个被绑定为 Singleton（单例）的对象中：

```php
use App\Service;
use Illuminate\Contracts\Foundation\Application;

/**
 * 注册任何应用服务
 */
public function register(): void
{
    $this->app->singleton(Service::class, function (Application $app) {
        return new Service($app);
    });
}
```

在这个例子中，如果 `Service` 实例是在应用启动（boot）过程中被解析（resolved）的，容器将会被注入到该 Service 中，并且在后续请求中，`Service` 实例会继续持有（hold）同一个容器实例。
这 **可能不会** 对你的应用造成问题；但是，它可能会导致该容器 **意外缺失（missing）那些在 boot 周期后阶段，或由后续请求中才被添加的绑定（bindings）**。

作为一种变通方案（work-around），你可以停止将该绑定注册为 Singleton（单例），或者你可以向 Service 注入一个 **容器解析器闭包（container resolver closure）**，该闭包始终解析当前的容器实例：

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

全局的 `app` Helper（辅助函数）以及 `Container::getInstance()` 方法 **始终会返回最新版本的应用容器**。

### 请求注入（Request Injection）

通常情况下，你应该避免在其他对象的构造函数中注入应用服务容器（Service Container）或 HTTP Request 实例。
例如，下面的绑定将整个 Request 实例注入到一个被绑定为 Singleton（单例）的对象中：

```php
use App\Service;
use Illuminate\Contracts\Foundation\Application;

/**
 * 注册任何应用服务
 */
public function register(): void
{
    $this->app->singleton(Service::class, function (Application $app) {
        return new Service($app['request']);
    });
}
```



在这个例子中，如果 `Service` 实例是在应用启动（boot）过程中被解析（resolved）的，HTTP Request 将会被注入到该 Service 中，并且在后续请求中，`Service` 实例会继续持有（hold）同一个 Request 实例。
因此，所有 Header（请求头）、Input（输入数据）、Query String（查询字符串）数据以及其他所有 Request 相关数据都将是错误的。

作为一种变通方案（work-around），你可以停止将该绑定注册为 Singleton（单例），或者你可以向 Service 注入一个 **Request 解析器闭包（request resolver closure）**，该闭包始终解析当前的 Request 实例。
或者，最推荐的做法（recommended approach）是：**在运行时（runtime）将对象所需的特定 Request 信息传递给对象的某个方法，而不是在构造函数中注入 Request**：

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

全局 `request` Helper（辅助函数）**始终会返回应用当前正在处理的 Request 实例**，因此在应用内部使用它是安全的。

> [!警告]
> 在 Controller 方法和 Route（路由）闭包中声明 `Illuminate\Http\Request` 实例的类型提示（type-hint）是可以接受的。

### 配置仓库注入（Configuration Repository Injection）

通常情况下，你应该避免在其他对象的构造函数中注入配置仓库（Configuration Repository）实例。
例如，下面的绑定将配置仓库注入到一个被绑定为 Singleton（单例）的对象中：

```php
use App\Service;
use Illuminate\Contracts\Foundation\Application;

/**
 * 注册任何应用服务。
 */
public function register(): void
{
    $this->app->singleton(Service::class, function (Application $app) {
        return new Service($app->make('config'));
    });
}
```



在这个例子中，如果配置值（configuration values）在请求之间发生改变，该 Service 将无法访问新值，因为它依赖的是最初（original）的 Repository（配置仓库）实例。

作为一种变通方案（work-around），你可以停止将该绑定注册为 Singleton（单例），或者你可以向该类注入一个 **配置仓库解析器闭包（configuration repository resolver closure）**：

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

全局 `config` Helper **始终会返回最新版本的配置仓库（configuration repository）**，因此在你的应用中使用它是安全的。

### 管理内存泄漏（Managing Memory Leaks）

请记住，Octane 会在请求之间将你的应用保持在内存中；因此，如果你向一个静态维护（statically maintained）的数组中添加数据，就会导致内存泄漏（memory leak）。
例如，下面的 Controller 存在内存泄漏，因为每次请求都会持续向静态 `$data` 数组添加数据：

```php
use App\Service;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

/**
 * 处理传入请求
 */
public function index(Request $request): array
{
    Service::$data[] = Str::random(10);

    return [
        // ...
    ];
}
```

在构建应用时，你应该格外小心，避免创建这类内存泄漏。
建议在本地开发（local development）期间 **监控应用的内存使用情况**，以确保你没有在应用中引入新的内存泄漏。

## 并发任务（Concurrent Tasks）

> [!警告]
> 该功能需要 Swoole。



当使用 Swoole 时，你可以通过轻量级（light-weight）的后台任务（background tasks）并发执行操作。你可以使用 Octane 的 `concurrently` 方法来实现这一点。你可以结合 PHP 数组解构（array destructuring）来获取每个操作的结果：

```php
use App\Models\User;
use App\Models\Server;
use Laravel\Octane\Facades\Octane;

[$users, $servers] = Octane::concurrently([
    fn () => User::all(),
    fn () => Server::all(),
]);
```

Octane 处理的并发任务会使用 Swoole 的 **“Task Workers（任务 Worker）”**，并且会在一个与传入请求（incoming request）**完全不同的进程（process）中执行**。可用于处理并发任务的 Worker 数量由 `octane:start` 命令中的 `--task-workers` 指令决定：

```shell
php artisan octane:start --workers=4 --task-workers=6
```

在调用 `concurrently` 方法时，由于 Swoole 任务系统的限制，你不应该提供超过 1024 个任务（tasks）。

## Ticks（定时执行）与 Intervals（时间间隔）

> [!警告]
> 该功能需要 Swoole。

当使用 Swoole 时，你可以注册 **“Tick（定时）操作”**，这些操作会按照指定的秒数间隔重复执行。你可以通过 `tick` 方法注册 **Tick 回调（callbacks）**。
传递给 `tick` 方法的第一个参数应该是一个字符串，用来表示 Ticker（定时器）的名称。第二个参数应该是一个可调用对象（callable），它会在指定的时间间隔（interval）被调用（invoked）。

在这个例子中，我们将注册一个 Closure（闭包），让它每 10 秒被调用一次。通常，`tick` 方法应该在你应用中某个 Service Provider 的 `boot` 方法中调用：

```php
Octane::tick('simple-ticker', fn () => ray('Ticking...'))
    ->seconds(10);
```

使用 `immediate` 方法，你可以指示（instruct）Octane 在服务器首次启动（initially boots）时 **立即调用（immediately invoke）** Tick 回调，并在之后每 N 秒再次调用：

```php
Octane::tick('simple-ticker', fn () => ray('Ticking...'))
    ->seconds(10)
    ->immediate();
```



## Octane 缓存（The Octane Cache）

> [!警告]
> 该功能需要 [Swoole](#swoole)。

当使用 Swoole 时，你可以使用 Octane 缓存驱动，它提供**每秒最多 200 万次操作**的读写速度。
因此，对于需要在缓存层获得**极端读/写速度**的应用来说，该缓存驱动是一个非常优秀的选择。

该缓存驱动由 [Swoole tables](https://www.swoole.co.uk/docs/modules/swoole-table) 提供支持。
存入缓存的所有数据**可被服务器上的所有 Worker 访问**。
但是，**当服务器重启时，缓存的数据将会被清空**：

```php
Cache::store('octane')->put('framework', 'Laravel', 30);
```
> [!注意]
> Octane 缓存允许的**最大条目数量**可以在你应用的 `octane` 配置文件中定义。

### 缓存间隔（Cache Intervals）

除了 Laravel 缓存系统提供的常规方法外，Octane 缓存驱动还具有**基于间隔（interval）的缓存**。
这些缓存会在指定的时间间隔**自动刷新**，并且应当在你某个 Service Provider 的 `boot` 方法中注册。
例如，下面的缓存将**每 5 秒刷新一次**：

```php
use Illuminate\Support\Str;

Cache::store('octane')->interval('random', function () {
    return Str::random(10);
}, seconds: 5);
```

## Swoole 表（Tables）

> [!警告]
> 该功能需要 [Swoole](#swoole)。

当使用 Swoole 时，你可以定义并操作你自己的任意 [Swoole tables](https://www.swoole.co.uk/docs/modules/swoole-table)。
Swoole 表提供**极端的性能吞吐量**，并且这些表中的数据**可以被服务器上的所有 Worker 访问**。
但是，其中的数据**会在服务器重启时丢失**。



Swoole 表应在你应用的 `octane` 配置文件中的 `tables` 配置数组内定义。
一个允许**最多 1000 行（rows）**的示例表（example table）已经默认为你配置好。
字符串（string）类型列的最大长度可以通过在列类型后指定大小来进行配置，如下所示：

```php
'tables' => [
    'example:1000' => [
        'name' => 'string:1000',
        'votes' => 'int',
    ],
],
```

要访问一个表，你可以使用 `Octane::table` 方法：

```php
use Laravel\Octane\Facades\Octane;

Octane::table('example')->set('uuid', [
    'name' => 'Nuno Maduro',
    'votes' => 1000,
]);

return Octane::table('example')->get('uuid');
```
> [!警告]
> Swoole 表支持的列类型（column types）是：`string`、`int` 和 `float`。
