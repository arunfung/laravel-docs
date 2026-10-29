
# Laravel Folio

-   [简介](#introduction)
-   [安装](#installation)
    -   [页面路径 / URI](#page-paths-uris)
    -   [子域名路由](#subdomain-routing)
-   [创建路由](#creating-routes)
    -   [嵌套路由](#nested-routes)
    -   [索引路由](#index-routes)
-   [路由参数](#route-parameters)
-   [路由模型绑定](#route-model-binding)
    -   [软删除模型](#soft-deleted-models)
-   [渲染钩子](#render-hooks)
-   [命名路由](#named-routes)
-   [中间件](#middleware)
-   [路由缓存](#route-caching)

## 简介

[Laravel Folio](https://github.com/laravel/folio?utm_source=chatgpt.com) 是一个强大的基于页面的路由器，旨在简化 Laravel 应用中的路由处理。使用 Laravel Folio，生成路由就像在应用的 `resources/views/pages` 目录中创建一个 Blade 模板一样简单。

例如，要创建一个可以通过 `/greeting` URL 访问的页面，只需在应用的 `resources/views/pages` 目录中创建一个 `greeting.blade.php` 文件：

```php
<div>
    Hello World
</div>
```

## 安装

首先，使用 Composer 包管理器将 Folio 安装到你的项目中：

```shell
composer require laravel/folio
```

安装完成后，你可以执行 `folio:install` Artisan 命令，它会将 Folio 的服务提供者安装到你的应用中。该服务提供者会注册 Folio 搜索路由 / 页面所使用的目录：

```shell
php artisan folio:install
```

### 页面路径 / URI

默认情况下，Folio 会从应用的 `resources/views/pages` 目录中提供页面，但你也可以在 Folio 服务提供者的 `boot` 方法中自定义这些目录。

例如，有时在同一个 Laravel 应用中指定多个 Folio 路径会很方便。你可能希望为应用的“管理后台”使用一个单独的 Folio 页面目录，而为应用的其他部分使用另一个目录。



你可以使用 `Folio::path` 和 `Folio::uri` 方法来实现这一点。
`path` 方法会注册一个目录，Folio 在路由传入的 HTTP 请求时会扫描该目录中的页面，而 `uri` 方法则指定该目录下页面的“基础 URI”：

```php
use Laravel\Folio\Folio;

Folio::path(resource_path('views/pages/guest'))->uri('/');

Folio::path(resource_path('views/pages/admin'))
    ->uri('/admin')
    ->middleware([
        '*' => [
            'auth',
            'verified',

            // ...
        ],
    ]);
```

### 子域名路由

你也可以基于传入请求的子域名来路由到不同的页面。
例如，你可能希望将来自 `admin.example.com` 的请求路由到一个与其他 Folio 页面不同的页面目录。你可以在调用 `Folio::path` 方法后调用 `domain` 方法来实现这一点：

```php
use Laravel\Folio\Folio;

Folio::domain('admin.example.com')
    ->path(resource_path('views/pages/admin'));
```

`domain` 方法还允许你将域名或子域名的一部分捕获为参数。这些参数将被注入到你的页面模板中：

```php
use Laravel\Folio\Folio;

Folio::domain('{account}.example.com')
    ->path(resource_path('views/pages/admin'));
```

## 创建路由

你可以通过在任意一个 Folio 挂载的目录中放置一个 Blade 模板来创建 Folio 路由。默认情况下，Folio 会挂载 `resources/views/pages` 目录，但你也可以在 Folio 服务提供者的 `boot` 方法中自定义这些目录。

一旦 Blade 模板被放置到 Folio 挂载的目录中，你就可以立即通过浏览器访问它。例如，放在 `pages/schedule.blade.php` 中的页面，可以通过浏览器访问：
`http://example.com/schedule`。



要快速查看你所有的 Folio 页面 / 路由列表，可以调用 `folio:list` Artisan 命令：

```shell
php artisan folio:list
```

### 嵌套路由

你可以通过在 Folio 的某个目录内创建一个或多个子目录来创建嵌套路由。
例如，要创建一个可以通过 `/user/profile` 访问的页面，可以在 `pages/user` 目录下创建一个 `profile.blade.php` 模板：

```shell
php artisan folio:page user/profile

# pages/user/profile.blade.php → /user/profile
```

### 索引路由

有时候，你可能希望将某个页面设为某个目录的“索引页”。
只需在 Folio 目录中放置一个 `index.blade.php` 模板，对该目录根路径的任何请求都会被路由到该页面：

```shell
php artisan folio:page index
# pages/index.blade.php → /

php artisan folio:page users/index
# pages/users/index.blade.php → /users
```

## 路由参数

通常，你需要将传入请求 URL 的某些片段注入到你的页面中，以便与之交互。
例如，你可能需要访问正在展示的用户的 “ID”。
要实现这一点，你可以将页面文件名的一部分用方括号括起来：

```shell
php artisan folio:page "users/[id]"

# pages/users/[id].blade.php → /users/1
```

捕获的片段可以作为变量在 Blade 模板中使用：

```html
<div>
    User {{ $id }}
</div>
```

要捕获多个片段，可以在方括号中的名称前加上三个点 `...`：

```shell
php artisan folio:page "users/[...ids]"

# pages/users/[...ids].blade.php → /users/1/2/3
```



当捕获多个片段时，这些捕获的片段会作为数组被注入到页面中：

```html
<ul>
    @foreach ($ids as $id)
        <li>User {{ $id }}</li>
    @endforeach
</ul>
```

## 路由模型绑定

如果页面模板文件名中的某个通配符片段对应于你应用中的某个 Eloquent 模型，Folio 会自动利用 Laravel 的路由模型绑定功能，并尝试将解析后的模型实例注入到页面中：

```shell
php artisan folio:page "users/[User]"

# pages/users/[User].blade.php → /users/1
```

捕获的模型可以作为变量在 Blade 模板中访问。模型的变量名会被转换为“小驼峰”形式：

```html
<div>
    User {{ $user->id }}
</div>
```

#### 自定义键

有时你可能希望通过除 `id` 以外的列来解析绑定的 Eloquent 模型。
要做到这一点，你可以在页面文件名中指定列名。
例如，文件名为 `[Post:slug].blade.php` 的页面会尝试通过 `slug` 列来解析模型，而不是 `id` 列。

在 Windows 上，你应该使用 `-` 来分隔模型名称和键名：`[Post-slug].blade.php`。

#### 模型位置

默认情况下，Folio 会在应用的 `app/Models` 目录中搜索模型。
但是，如果需要，你可以在模板的文件名中指定模型的完整类名：

```shell
php artisan folio:page "users/[.App.Models.User]"

# pages/users/[.App.Models.User].blade.php → /users/1
```

### 软删除模型

默认情况下，在解析隐式模型绑定时，不会检索已软删除的模型。
但是，如果你希望这样做，可以在页面模板中调用 `withTrashed` 函数来指示 Folio 检索已软删除的模型：

```php
<?php

use function Laravel\Folio\{withTrashed};

withTrashed();

?>

<div>
    User {{ $user->id }}
</div>
```



## 渲染钩子（Render Hooks）

默认情况下，Folio 会将页面 Blade 模板的内容作为传入请求的响应返回。
但是，你可以通过在页面模板中调用 `render` 函数来自定义响应。

`render` 函数接受一个闭包，该闭包会接收 Folio 正在渲染的 `View` 实例，你可以借此向视图添加额外数据，或者自定义整个响应。
除了接收 `View` 实例外，任何额外的路由参数或模型绑定也会被传递给 `render` 闭包：

```php
<?php

use App\Models\Post;
use Illuminate\Support\Facades\Auth;
use Illuminate\View\View;

use function Laravel\Folio\render;

render(function (View $view, Post $post) {
    if (! Auth::user()->can('view', $post)) {
        return response('Unauthorized', 403);
    }

    return $view->with('photos', $post->author->photos);
}); ?>

<div>
    {{ $post->content }}
</div>

<div>
    This author has also taken {{ count($photos) }} photos.
</div>
```

## 命名路由（Named Routes）

你可以通过在页面模板中调用 `name` 函数，为某个页面的路由指定名称：

```php
<?php

use function Laravel\Folio\name;

name('users.index');
```

就像 Laravel 的命名路由一样，你可以使用 `route` 函数来生成指向已分配名称的 Folio 页面 URL：

```php
<a href="{{ route('users.index') }}">
    All Users
</a>
```

如果页面有参数，你只需将参数值传递给 `route` 函数即可：

```php
route('users.show', ['user' => $user]);
```

## 中间件（Middleware）

你可以通过在页面模板中调用 `middleware` 函数，为某个特定页面应用中间件：

```php
<?php

use function Laravel\Folio\{middleware};

middleware(['auth', 'verified']);

?>

<div>
    Dashboard
</div>
```



或者，要为一组页面分配中间件，你可以在调用 `Folio::path` 方法后链式调用 `middleware` 方法。

要指定中间件应用到哪些页面，可以在中间件数组中使用相应页面的 URL 模式作为键。`*` 字符可以用作通配符：

```php
use Laravel\Folio\Folio;

Folio::path(resource_path('views/pages'))->middleware([
    'admin/*' => [
        'auth',
        'verified',

        // ...
    ],
]);
```

你可以在中间件数组中包含闭包，以定义内联的匿名中间件：

```php
use Closure;
use Illuminate\Http\Request;
use Laravel\Folio\Folio;

Folio::path(resource_path('views/pages'))->middleware([
    'admin/*' => [
        'auth',
        'verified',

        function (Request $request, Closure $next) {
            // ...

            return $next($request);
        },
    ],
]);
```

## 路由缓存

在使用 Folio 时，你应该始终利用 [Laravel 的路由缓存功能](/docs/laravel/12.x/routing#route-caching)。
Folio 会监听 `route:cache` Artisan 命令，以确保 Folio 页面定义和路由名称被正确缓存，从而获得最佳性能。
