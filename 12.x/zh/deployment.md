# Deployment

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
- [调试模式](#debug-mode)
- [健康检查路由](#the-health-route)
- [使用 Forge / Vapor 轻松部署](#deploying-with-cloud-or-forge)

<a name="introduction"></a>
## 简介

当你准备将 Laravel 应用程序部署到生产环境时，有一些重要的步骤可以确保你的应用程序运行得尽可能高效。在本文档中，我们将涵盖一些确保 Laravel 应用程序正确部署的良好起点。

<a name="server-requirements"></a>
## 服务器要求

Laravel 框架有一些建议的系统要求。你应确保你的 Web 服务器至少具备以下 PHP 版本和扩展：

<div class="content-list" markdown="1">

- PHP >= 8.2
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

如果你正在将应用程序部署到运行 Nginx 的服务器上，你可以使用以下配置文件作为配置 Web 服务器的起点。根据你的服务器配置，此文件很可能需要进行定制。**如果你需要协助管理服务器，可以考虑使用 Laravel 官方提供的服务器管理和部署服务，如 [Laravel Cloud](https://cloud.laravel.com).**



请确保，像下面的配置一样，你的 Web 服务器将所有请求指向应用程序的 `public/index.php` 文件。绝不能把 `index.php` 文件移动到项目根目录，因为从项目根目录提供应用程序将会使许多敏感的配置文件暴露在公共互联网上：

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
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
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

[FrankenPHP](https://frankenphp.dev/) 也可以用来服务 Laravel 应用程序。FrankenPHP 是用 Go 编写的现代 PHP 应用服务器。要使用 FrankenPHP 为 Laravel PHP 应用提供服务，您可以简单地调用其 `php-server` 命令：

```shell
frankenphp php-server -r public/
```

要利用 FrankenPHP 支持的更强大功能，例如其 [Laravel Octane](/docs/laravel/12.x/octane) 集成、HTTP/3、现代压缩技术或将 Laravel 应用打包为独立的二进制文件，请参阅 FrankenPHP 的 [Laravel 文档](https://frankenphp.dev/docs/laravel/).

<a name="directory-permissions"></a>
### D目录权限

Laravel 需要写入 `bootstrap/cache` 和 `storage` 目录，因此你应确保 Web 服务器进程所有者有权限写入这些目录。



<a name="optimization"></a>
## 优化

在将应用程序部署到生产环境时，有多种文件应该被缓存，包括配置、事件、路由和视图。Laravel 提供了一个方便的单一 `optimize` Artisan 命令，可以缓存所有这些文件。这个命令通常应该作为应用程序部署过程的一部分被调用：

```shell
php artisan optimize
```

`optimize:clear` 方法可以用来删除由 `optimize` 命令生成的所有缓存文件：

```shell
php artisan optimize:clear
```

在接下来的文档中，我们将讨论由 `optimize` 命令执行的每个细粒度优化命令。

<a name="optimizing-configuration-loading"></a>
### 缓存配置

在将应用程序部署到生产环境时，应确保在部署过程中运行 `config:cache` Artisan 命令：

```shell
php artisan config:cache
```

这个命令会将 Laravel 的所有配置文件合并成一个缓存文件，这大大减少了框架在加载配置值时对文件系统进行的访问次数。

> [!注意]
> 如果您在部署过程中执行 `config:cache` 命令，您应确保只在配置文件中调用 `env` 函数。一旦配置被缓存，`.env` 文件将不会被加载，对 `env` 变量的所有调用 `.env` 函数将返回 `null`。

<a name="caching-events"></a>
### 缓存事件

在部署过程中，应该缓存应用程序的自动发现的事件到监听器映射。这可以通过在部署期间调用 `event:cache` Artisan 命令来完成：

```shell
php artisan event:cache
```



<a name="optimizing-route-loading"></a>
### 缓存路由
如果你正在构建一个包含许多路由的大型应用程序，应该确保在部署过程中运行 `route:cache` Artisan 命令：

```shell
php artisan route:cache
```

这个命令将所有的路由注册减少到缓存文件中的单个方法调用，当注册数百个路由时，可以提高路由注册的性能。

<a name="optimizing-view-loading"></a>
### 缓存视图

当将应用程序部署到生产环境时，你应该确保在部署过程中运行 `view:cache` Artisan 命令：

```shell
php artisan view:cache
```
这个命令预编译所有的 Blade 视图，因此它们不会在需求时编译，从而提高了返回视图的每个请求的性能。

<a name="debug-mode"></a>
## 调试模式

`config/app.php` 配置文件中的调试选项决定了向用户显示的错误信息量。默认情况下，此选项设置为 `APP_DEBUG` 环境变量的值，该变量存储在应用程序的 `.env` 文件中。

> **注意**
> **在生产环境中，此值应始终为「false」。如果在生产中将 `APP_DEBUG` 变量设置为「true」，可能会向应用程序的最终用户暴露敏感配置值。**


<a name="the-health-route"></a>
## 健康路由

Laravel 包括一个内置的健康检查路由，可用于监控应用程序的状态。在生产中，此路由可用于向运行时间监控器、负载均衡器或诸如 Kubernetes 之类的编排系统报告应用程序的状态。




默认情况下，健康检查路由在 `/up` 地址提供服务，并且如果应用程序无异常启动，将返回 200 HTTP 响应。否则，将返回 500 HTTP 响应。可以在应用程序的 `bootstrap/app` 文件中配置此路由的 URI：

```php
->withRouting(
    web: __DIR__.'/../routes/web.php',
    commands: __DIR__.'/../routes/console.php',
    health: '/up', // [删除这一行]
    health: '/status', // [[添加这一行]
)
```
当对此路由发出 HTTP 请求时，Laravel 还将触发  `Illuminate\Foundation\Events\DiagnosingHealth` 事件，允许执行与应用程序相关的额外健康检查。在此事件的 [监听器](/docs/laravel/12.x/events) 中，可以检查应用程序的数据库或缓存状态。如果检测到应用程序存在问题，可以直接从监听器中抛出异常。

<a name="deploying-with-cloud-or-forge"></a>
## 使用 Laravel Cloud 或 Forge 部署

<a name="laravel-cloud"></a>
#### Laravel Cloud
如果你希望使用专为 Laravel 调优的完全托管、自动扩展部署平台，请查看 [Laravel Cloud](https://cloud.laravel.com/)。Laravel Cloud 是为 Laravel 提供强大部署的平台，支持托管计算、数据库、缓存和对象存储。

在 Cloud 上启动你的 Laravel 应用程序，体验可扩展的简约之美。Laravel Cloud 由 Laravel 的创造者精心调优，与框架无缝协作，让你可以继续按照习惯的方式编写 Laravel 应用程序。

<a name="laravel-forge"></a>
#### Laravel Forge
如果你更喜欢管理自己的服务器，但对配置运行健壮 Laravel 应用程序所需的各种服务感到不适，可使用 [Laravel Forge](https://forge.laravel.com/)，这是一个专为 Laravel 应用程序设计的 VPS 服务器管理平台。

Laravel Forge 可在 DigitalOcean、Linode、AWS 等多种基础设施提供商上创建服务器。此外，Forge 还会安装并管理构建健壮 Laravel 应用程序所需的所有工具，如 Nginx、MySQL、Redis、Memcached、Beanstalk 等。
