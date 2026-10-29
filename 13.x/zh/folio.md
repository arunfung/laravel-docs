# Laravel Folio

- [简介](#introduction)
- [安装](#installation)
    - [页面路径 / URI](#page-paths-uris)
    - [子域名路由](#subdomain-routing)
- [创建路由](#creating-routes)
    - [嵌套路由](#nested-routes)
    - [索引路由](#index-routes)
- [路由参数](#route-parameters)
- [路由模型绑定](#route-model-binding)
    - [软删除模型](#soft-deleted-models)
- [渲染钩子](#render-hooks)
- [命名路由](#named-routes)
- [中间件](#middleware)
- [路由缓存](#route-caching)

<a name="introduction"></a>
## 简介

[Laravel Folio](https://github.com/laravel/folio) 是一个功能强大的基于页面的路由器，旨在简化 Laravel 应用的路由配置。使用 Laravel Folio，创建路由就像在应用的 `resources/views/pages` 目录中创建 Blade 模板一样简单。

例如，要创建一个可通过 `/greeting` URL 访问的页面，只需在应用的 `resources/views/pages` 目录中创建 `greeting.blade.php` 文件：

```blade
<div>
    Hello World
</div>
```

<a name="installation"></a>
## 安装

首先，使用 Composer 包管理器将 Folio 安装到项目中：

```shell
composer require laravel/folio
```

安装 Folio 后，可以执行 `folio:install` Artisan 命令，将 Folio 的服务提供者安装到应用中。该服务提供者会注册 Folio 搜索路由和页面的目录：

```shell
php artisan folio:install
```

<a name="page-paths-uris"></a>
### 页面路径 / URI

默认情况下，Folio 从应用的 `resources/views/pages` 目录提供页面，你可以在 Folio 服务提供者的 `boot` 方法中自定义这些目录。

例如，在同一个 Laravel 应用中指定多个 Folio 路径有时会很方便。你可能希望为应用的「管理」区域单独设置一个 Folio 页面目录，而将应用的其余页面放在另一个目录中。

你可以使用 `Folio::path` 和 `Folio::uri` 方法实现这一需求。`path` 方法注册一个目录，Folio 在处理传入的 HTTP 请求时会扫描该目录中的页面；`uri` 方法则指定该页面目录的「基础 URI」：

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

<a name="subdomain-routing"></a>
### 子域名路由

你也可以根据传入请求的子域名将请求路由到页面。例如，你可能希望将来自 `admin.example.com` 的请求路由到不同于其他 Folio 页面的目录。为此，可以在调用 `Folio::path` 方法之后调用 `domain` 方法：

```php
use Laravel\Folio\Folio;

Folio::domain('admin.example.com')
    ->path(resource_path('views/pages/admin'));
```

`domain` 方法还允许你将域名或子域名的一部分捕获为参数。这些参数将被注入页面模板：

```php
use Laravel\Folio\Folio;

Folio::domain('{account}.example.com')
    ->path(resource_path('views/pages/admin'));
```

<a name="creating-routes"></a>
## 创建路由

将 Blade 模板放入 Folio 挂载的任一目录，即可创建 Folio 路由。默认情况下，Folio 挂载 `resources/views/pages` 目录，你可以在 Folio 服务提供者的 `boot` 方法中自定义这些目录。

将 Blade 模板放入 Folio 挂载的目录后，就可以立即通过浏览器访问。例如，位于 `pages/schedule.blade.php` 的页面可以通过 `http://example.com/schedule` 访问。

要快速查看所有 Folio 页面和路由的列表，可以运行 `folio:list` Artisan 命令：

```shell
php artisan folio:list
```

<a name="nested-routes"></a>
### 嵌套路由

在 Folio 目录中创建一层或多层子目录，即可创建嵌套路由。例如，要创建可通过 `/user/profile` 访问的页面，可以在 `pages/user` 目录中创建 `profile.blade.php` 模板：

```shell
php artisan folio:page user/profile

# pages/user/profile.blade.php → /user/profile
```

<a name="index-routes"></a>
### 索引路由

有时，你可能希望将某个页面设为目录的「索引」。将 `index.blade.php` 模板放入 Folio 目录后，对该目录根路径的请求都会被路由到该页面：

```shell
php artisan folio:page index
# pages/index.blade.php → /

php artisan folio:page users/index
# pages/users/index.blade.php → /users
```

<a name="route-parameters"></a>
## 路由参数

你经常需要将传入请求 URL 的某些片段注入页面，以便在页面中使用。例如，可能需要获取正在显示其资料的用户的「ID」。为此，可以在页面文件名中用方括号括住相应片段：

```shell
php artisan folio:page "users/[id]"

# pages/users/[id].blade.php → /users/1
```

捕获的片段可以作为变量在 Blade 模板中访问：

```html
<div>
    User {{ $id }}
</div>
```

要捕获多个片段，可以在方括号内的名称前加上三个点 `...`：

```shell
php artisan folio:page "users/[...ids]"

# pages/users/[...ids].blade.php → /users/1/2/3
```

捕获多个片段时，这些片段将以数组形式注入页面：

```html
<ul>
    @foreach ($ids as $id)
        <li>User {{ $id }}</li>
    @endforeach
</ul>
```

<a name="route-model-binding"></a>
## 路由模型绑定

如果页面模板文件名中的通配符片段对应应用的某个 Eloquent 模型，Folio 会自动使用 Laravel 的路由模型绑定功能，尝试将解析出的模型实例注入页面：

```shell
php artisan folio:page "users/[User]"

# pages/users/[User].blade.php → /users/1
```

捕获的模型可以作为变量在 Blade 模板中访问。模型的变量名会转换为「驼峰命名」：

```html
<div>
    User {{ $user->id }}
</div>
```

#### 自定义键

有时，你可能希望使用 `id` 以外的列解析绑定的 Eloquent 模型。为此，可以在页面文件名中指定该列。例如，文件名为 `[Post:slug].blade.php` 的页面会尝试通过 `slug` 列而非 `id` 列解析绑定模型。

在 Windows 上，应使用 `-` 分隔模型名称和键：`[Post-slug].blade.php`。

#### 模型位置

默认情况下，Folio 会在应用的 `app/Models` 目录中查找模型。如有需要，你也可以在模板文件名中指定模型的完全限定类名：

```shell
php artisan folio:page "users/[.App.Models.User]"

# pages/users/[.App.Models.User].blade.php → /users/1
```

<a name="soft-deleted-models"></a>
### 软删除模型

默认情况下，解析隐式模型绑定时不会检索已软删除的模型。你可以在页面模板中调用 `withTrashed` 函数，指示 Folio 同时检索已软删除的模型：

```php
<?php

use function Laravel\Folio\{withTrashed};

withTrashed();

?>

<div>
    User {{ $user->id }}
</div>
```

<a name="render-hooks"></a>
## 渲染钩子

默认情况下，Folio 会将页面 Blade 模板的内容作为传入请求的响应。你也可以在页面模板中调用 `render` 函数来自定义响应。

`render` 函数接受一个闭包，该闭包会接收 Folio 正在渲染的 `View` 实例，让你可以向视图添加数据或自定义整个响应。除了 `View` 实例，其他路由参数或模型绑定也会传递给 `render` 闭包：

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

<a name="named-routes"></a>
## 命名路由

你可以使用 `name` 函数为页面路由指定名称：

```php
<?php

use function Laravel\Folio\name;

name('users.index');
```

与 Laravel 的命名路由一样，你可以使用 `route` 函数生成已命名 Folio 页面的 URL：

```blade
<a href="{{ route('users.index') }}">
    All Users
</a>
```

如果页面有参数，只需将参数值传递给 `route` 函数：

```php
route('users.show', ['user' => $user]);
```

<a name="middleware"></a>
## 中间件

你可以在页面模板中调用 `middleware` 函数，为特定页面应用中间件：

```php
<?php

use function Laravel\Folio\{middleware};

middleware(['auth', 'verified']);

?>

<div>
    Dashboard
</div>
```

或者，要为一组页面指定中间件，可以在调用 `Folio::path` 方法后链式调用 `middleware` 方法。

要指定中间件应用于哪些页面，可以使用对应页面的 URL 模式作为中间件数组的键。字符 `*` 可用作通配符：

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

<a name="route-caching"></a>
## 路由缓存

使用 Folio 时，应充分利用 [Laravel 的路由缓存功能](/docs/{{version}}/routing#route-caching)。Folio 会监听 `route:cache` Artisan 命令，确保 Folio 页面定义和路由名称被正确缓存，以获得最佳性能。
