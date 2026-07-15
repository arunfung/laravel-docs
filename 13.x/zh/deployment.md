# 部署

- [简介](#introduction)
- [服务器要求](#server-requirements)
- [服务器配置](#server-configuration)
    - [Nginx](#nginx)
    - [FrankenPHP](#frankenphp)
    - [目录权限](#directory-permissions)
- [优化](#optimization)
    - [缓存配置](#optimizing-configuration-loading)
    - [缓存事件](#caching-events)
    - [缓存路由](#optimizing-route-loading)
    - [缓存视图](#optimizing-view-loading)
- [重新加载服务](#reloading-services)
- [调试模式](#debug-mode)
- [健康检查路由](#the-health-route)
- [使用 Laravel Cloud 或 Forge 部署](#deploying-with-cloud-or-forge)

<a name="introduction"></a>
## 简介

当你准备将 Laravel 应用部署到生产环境时，可以采取一些重要措施来确保应用尽可能高效地运行。本文档将介绍一些良好的起点，帮助你正确部署 Laravel 应用。

<a name="server-requirements"></a>
## 服务器要求

Laravel 框架有一些系统要求。你应确保 Web 服务器至少具备以下 PHP 版本和扩展：

<div class="content-list" markdown="1">

- PHP >= 8.3
- Ctype PHP 扩展
- cURL PHP 扩展
- DOM PHP 扩展
- Fileinfo PHP 扩展
- Filter PHP 扩展
- Hash PHP 扩展
- Mbstring PHP 扩展
- OpenSSL PHP 扩展
- PCRE PHP 扩展
- PDO PHP 扩展
- Session PHP 扩展
- Tokenizer PHP 扩展
- XML PHP 扩展

</div>

<a name="server-configuration"></a>
## 服务器配置

<a name="nginx"></a>
### Nginx

如果要将应用部署到运行 Nginx 的服务器，可以使用以下配置文件作为配置 Web 服务器的起点。你很可能需要根据服务器配置自定义此文件。**如果需要协助管理服务器，可以考虑使用 [Laravel Cloud](https://cloud.laravel.com) 这样的全托管 Laravel 平台。**

请确保 Web 服务器像以下配置一样，将所有请求转发到应用的 `public/index.php` 文件。绝不要尝试将 `index.php` 文件移动到项目根目录，因为从项目根目录提供应用服务会将许多敏感配置文件暴露在公共互联网上：

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com;
    root /srv/example.com/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    index index.php;

    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ ^/index\.php(/|$) {
        fastcgi_pass unix:/var/run/php/php8.3-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_hide_header X-Powered-By;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

<a name="frankenphp"></a>
### FrankenPHP

[FrankenPHP](https://frankenphp.dev/) 也可以用来提供 Laravel 应用服务。FrankenPHP 是一个使用 Go 编写的现代 PHP 应用服务器。若要使用 FrankenPHP 提供 Laravel PHP 应用服务，只需调用其 `php-server` 命令：

```shell
frankenphp php-server -r public/
```

若要使用 FrankenPHP 支持的更强大功能，例如 [Laravel Octane](/docs/{{version}}/octane) 集成、HTTP/3、现代压缩技术，或将 Laravel 应用打包为独立二进制文件的能力，请参阅 FrankenPHP 的 [Laravel 文档](https://frankenphp.dev/docs/laravel/)。

<a name="directory-permissions"></a>
### 目录权限

Laravel 需要写入 `bootstrap/cache` 和 `storage` 目录，因此应确保 Web 服务器进程的所有者拥有这些目录的写入权限。

<a name="optimization"></a>
## 优化

将应用部署到生产环境时，应缓存多种文件，包括配置、事件、路由和视图。Laravel 提供了一个便捷的 `optimize` Artisan 命令，可缓存所有这些文件。通常应在应用部署过程中调用此命令：

```shell
php artisan optimize
```

可以使用 `optimize:clear` 命令删除 `optimize` 命令生成的所有缓存文件，以及默认缓存驱动中的所有键：

```shell
php artisan optimize:clear
```

在以下文档中，我们将分别介绍 `optimize` 命令所执行的各项细粒度优化命令。

<a name="optimizing-configuration-loading"></a>
### 缓存配置

将应用部署到生产环境时，应确保在部署过程中运行 `config:cache` Artisan 命令：

```shell
php artisan config:cache
```

此命令会将 Laravel 的所有配置文件合并为一个缓存文件，从而大幅减少框架加载配置值时访问文件系统的次数。

> [!WARNING]
> 如果在部署过程中执行 `config:cache` 命令，请确保只在配置文件中调用 `env` 函数。配置被缓存后，将不会加载 `.env` 文件；对于 `.env` 变量，在配置文件之外调用 `env` 函数都将返回 `null`。

<a name="caching-events"></a>
### 缓存事件

部署过程中，应缓存应用自动发现的事件与监听器映射。可以在部署时调用 `event:cache` Artisan 命令来完成此操作：

```shell
php artisan event:cache
```

<a name="optimizing-route-loading"></a>
### 缓存路由

如果正在构建一个包含大量路由的大型应用，应确保在部署过程中运行 `route:cache` Artisan 命令：

```shell
php artisan route:cache
```

此命令会将所有路由注册压缩为缓存文件中的一次方法调用，从而提升注册数百条路由时的路由注册性能。

<a name="optimizing-view-loading"></a>
### 缓存视图

将应用部署到生产环境时，应确保在部署过程中运行 `view:cache` Artisan 命令：

```shell
php artisan view:cache
```

此命令会预编译所有 Blade 视图，使其无须按需编译，从而提升每个返回视图的请求的性能。

<a name="reloading-services"></a>
## 重新加载服务

> [!NOTE]
> 部署到 [Laravel Cloud](https://cloud.laravel.com) 时，无须使用 `reload` 命令，因为系统会自动平滑地重新加载所有服务。

部署新版本的应用后，应重新加载或重启队列工作进程、Laravel Reverb 或 Laravel Octane 等所有长期运行的服务，以使用新代码。Laravel 提供了一个 `reload` Artisan 命令来终止这些服务：

```shell
php artisan reload
```

如果不使用 [Laravel Cloud](https://cloud.laravel.com)，应手动配置进程监控器，使其能够检测可重新加载的进程何时退出，并自动重启这些进程。

<a name="debug-mode"></a>
## 调试模式

`config/app.php` 配置文件中的调试选项决定了实际向用户显示多少错误信息。默认情况下，此选项会遵循 `APP_DEBUG` 环境变量的值，该变量存储在应用的 `.env` 文件中。

> [!WARNING]
> **在生产环境中，此值应始终为 `false`。如果在生产环境中将 `APP_DEBUG` 变量设置为 `true`，可能会向应用的最终用户暴露敏感配置值。**

<a name="the-health-route"></a>
## 健康检查路由

Laravel 内置了一个健康检查路由，可用于监控应用状态。在生产环境中，可以使用此路由将应用状态报告给可用性监控器、负载均衡器或 Kubernetes 等编排系统。

默认情况下，健康检查路由通过 `/up` 提供服务。如果应用启动时未出现异常，该路由将返回 HTTP 200 响应；否则将返回 HTTP 500 响应。可以在应用的 `bootstrap/app` 文件中配置此路由的 URI：

```php
->withRouting(
    web: __DIR__.'/../routes/web.php',
    commands: __DIR__.'/../routes/console.php',
    health: '/up', // [tl! remove]
    health: '/status', // [tl! add]
)
```

当 HTTP 请求访问此路由时，Laravel 还会分发 `Illuminate\Foundation\Events\DiagnosingHealth` 事件，使你能够执行与应用相关的其他健康检查。在此事件的[监听器](/docs/{{version}}/events)中，可以检查应用的数据库或缓存状态。如果检测到应用存在问题，只需在监听器中抛出异常即可。

<a name="deploying-with-cloud-or-forge"></a>
## 使用 Laravel Cloud 或 Forge 部署

<a name="laravel-cloud"></a>
#### Laravel Cloud

如果需要一个专为 Laravel 调优、完全托管且可自动扩缩的部署平台，可以试试 [Laravel Cloud](https://cloud.laravel.com)。Laravel Cloud 是一个功能强大的 Laravel 部署平台，提供托管的计算、数据库、缓存和对象存储服务。

在 Cloud 上启动 Laravel 应用，体验可扩展的简约之美。Laravel Cloud 由 Laravel 的创造者精心调优，可与框架无缝协作，让你能够继续以熟悉的方式编写 Laravel 应用。

<a name="laravel-forge"></a>
#### Laravel Forge

如果更愿意自己管理服务器，但不熟悉如何配置运行可靠 Laravel 应用所需的各种服务，可以使用 [Laravel Forge](https://forge.laravel.com)。它是一个面向 Laravel 应用的 VPS 服务器管理平台。

Laravel Forge 可以在 DigitalOcean、Linode、AWS 等各种基础设施提供商上创建服务器。此外，Forge 还会安装并管理构建可靠 Laravel 应用所需的所有工具，例如 Nginx、MySQL、Redis、Memcached 和 Beanstalk 等。
