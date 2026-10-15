
# 授权

-   [简介](#introduction)
-   [Gates（权限门）](#gates)
    -   [编写 Gates](#writing-gates)
    -   [通过 Gates 授权操作](#authorizing-actions-via-gates)
    -   [Gate 响应](#gate-responses)
    -   [拦截 Gate 检查](#intercepting-gate-checks)
    -   [内联授权](#inline-authorization)
-   [创建 Policies（策略）](#creating-policies)
    -   [生成策略](#generating-policies)
    -   [注册策略](#registering-policies)
-   [编写策略](#writing-policies)
    -   [策略方法](#policy-methods)
    -   [策略响应](#policy-responses)
    -   [无模型方法](#methods-without-models)
    -   [访客用户](#guest-users)
    -   [策略过滤器](#policy-filters)
-   [使用策略授权操作](#authorizing-actions-using-policies)
    -   [通过用户模型](#via-the-user-model)
    -   [通过 Gate 门 Facade](#via-the-gate-facade)
    -   [通过中间件](#via-middleware)
    -   [通过 Blade 模板](#via-blade-templates)
    -   [提供额外上下文](#supplying-additional-context)
-   [授权与 Inertia](#authorization-and-inertia)

## 简介

除了提供内置的 [认证](/docs/laravel/12.x/authentication) 服务外，Laravel 还提供了一种简单的方式，用于授权用户对给定资源执行操作。
例如，即使用户已经通过认证，他们可能仍未被授权更新或删除应用管理的某些 Eloquent 模型或数据库记录。
Laravel 的授权功能提供了一种易于管理、组织良好的方式来处理这类授权检查。

Laravel 提供了两种主要的授权方式：[Gates](#gates) 和 [Policies](#creating-policies)。
可以把 gates 和 policies 想象成路由和控制器的关系。
Gates 提供了一个简单的基于闭包的授权方法，而 policies 则像控制器一样，将逻辑围绕特定模型或资源进行分组。
在本篇文档中，我们将先探索 gates，然后再研究 policies。

在构建应用时，你不必仅限于使用 gates 或仅限于使用 policies。
大多数应用很可能会包含 gates 和 policies 的混合使用，这是完全可以的！
Gates 最适用于不依赖任何模型或资源的操作，例如查看管理员仪表盘。
相反，当你希望授权某个特定模型或资源的操作时，应使用 policies。


<a name="gates"></a>
## 拦截器 (Gates)

<a name="writing-gates"></a>
### 编写拦截器（Gates）

> [! 注意]
> 拦截器（Gates）是学习 Laravel 授权特性基础知识的好方法，但在构建健壮的 Laravel 应用时，应该考虑结合使用策略 [policies](#creating-policies) 来组织授权规则。

拦截器（Gates）是用来确定用户是否有权执行给定操作的闭包函数。通常，拦截器（Gates）通过 `Gate` 门面在 `App\Providers\AppServiceProvider` 类中的 `boot` 函数里定义。拦截器（Gates）始终接收一个用户实例作为第一个参数，可以选择性的接收额外参数，例如相关的 Eloquent 模型。

在下面的例子中，我们将定义一个拦截器（Gates) 来确定用户是否可以更新给定的 `App\Models\Post` 模型。拦截器（Gates）将通过比较用户的 `id` 与创建帖子的用户的 `user_id` 来实现该判断：

```php
use App\Models\Post;
use App\Models\User;
use Illuminate\Support\Facades\Gate;

/**
 * 启动任何应用程序服务.
 */
public function boot(): void
{
    Gate::define('update-post', function (User $user, Post $post) {
        return $user->id === $post->user_id;
    });
}
```

与控制器一样，拦截器（Gates）也可以使用类回调数组来定义：

```php
use App\Policies\PostPolicy;
use Illuminate\Support\Facades\Gate;

/**
 * 启动任何应用程序服务.
 */
public function boot(): void
{
    Gate::define('update-post', [PostPolicy::class, 'update']);
}
```

<a name="authorizing-actions-via-gates"></a>
### 授权操作

要使用拦截器（Gates）授权操作，你应该使用 `Gate` 门面提供的 `allows` 或 `denies` 方法。注意，你不需要将当前认证的用户传递给这些方法，Laravel 会自动处理将用户传递给拦截器（gate）闭包。通常，在应用程序的控制器中，需要授权操作之前调用门面授权方法：

```php
<?php

namespace App\Http\Controllers;

use App\Models\Post;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;

class PostController extends Controller
{
    /**
     * 更新给定的帖子。
     */
    public function update(Request $request, Post $post): RedirectResponse
    {
        if (! Gate::allows('update-post', $post)) {
            abort(403);
        }

        // 更新帖子...

        return redirect('/posts');
    }
}
```



如果你希望判断 **非当前认证用户** 是否被授权执行某个操作，可以在 `Gate` Facade 上使用 `forUser` 方法：

```php
if (Gate::forUser($user)->allows('update-post', $post)) {
    // 该用户可以更新这篇文章...
}

if (Gate::forUser($user)->denies('update-post', $post)) {
    // 该用户无法更新这篇文章...
}
```

你也可以使用 `any` 或 `none` 方法一次授权多个操作：

```php
if (Gate::any(['update-post', 'delete-post'], $post)) {
    // 该用户可以更新或删除这篇文章...
}

if (Gate::none(['update-post', 'delete-post'], $post)) {
    // 该用户无法更新或删除这篇文章...
}
```

#### 授权或抛出异常

如果你希望尝试授权某个操作，并在用户未被允许执行该操作时自动抛出 `Illuminate\Auth\Access\AuthorizationException`，可以使用 `Gate` Facade 的 `authorize` 方法。
Laravel 会自动将 `AuthorizationException` 实例转换为 403 HTTP 响应：

```php
Gate::authorize('update-post', $post);

// 操作已授权...
```

#### 提供额外上下文

用于授权能力的 gate 方法（`allows`、`denies`、`check`、`any`、`none`、`authorize`、`can`、`cannot`）以及授权 [Blade 指令](#via-blade-templates)（`@can`、`@cannot`、`@canany`）都可以接收数组作为第二个参数。
这些数组元素会作为参数传递给 gate 闭包，可用于在做授权决策时提供额外的上下文：

```php
use App\Models\Category;
use App\Models\User;
use Illuminate\Support\Facades\Gate;

Gate::define('create-post', function (User $user, Category $category, bool $pinned) {
    if (! $user->canPublishToGroup($category->group)) {
        return false;
    } elseif ($pinned && ! $user->canPinPosts()) {
        return false;
    }

    return true;
});

if (Gate::check('create-post', [$category, $pinned])) {
      // 该用户可以创建这篇文章...
}
```



### Gate 响应

到目前为止，我们只研究了返回简单布尔值的 Gate。
然而，有时候你可能希望返回更详细的响应，包括错误消息。
为此，你可以从 Gate 中返回一个 `Illuminate\Auth\Access\Response` 实例：

```php
use App\Models\User;
use Illuminate\Auth\Access\Response;
use Illuminate\Support\Facades\Gate;

Gate::define('edit-settings', function (User $user) {
    return $user->isAdmin
        ? Response::allow()
        : Response::deny('You must be an administrator.');
});
```

即使你从 Gate 返回了一个授权响应，`Gate::allows` 方法仍然只会返回一个简单的布尔值；
然而，你可以使用 `Gate::inspect` 方法来获取 Gate 返回的完整授权响应：

```php
$response = Gate::inspect('edit-settings');

if ($response->allowed()) {
    // 动作已被授权...
} else {
    echo $response->message();
}
```

当使用 `Gate::authorize` 方法时，如果动作未被授权，会抛出一个 `AuthorizationException`；
在这种情况下，授权响应中提供的错误消息会被传递到 HTTP 响应中：

```php
Gate::authorize('edit-settings');

// The action is authorized...
```

#### 自定义 HTTP 响应状态码

当一个动作被 Gate 拒绝时，默认会返回一个 `403` HTTP 响应；
但是，有时返回其他 HTTP 状态码会更有用。
你可以使用 `Illuminate\Auth\Access\Response` 类中的 `denyWithStatus` 静态构造方法，
来自定义失败授权检查时返回的 HTTP 状态码：

```php
use App\Models\User;
use Illuminate\Auth\Access\Response;
use Illuminate\Support\Facades\Gate;

Gate::define('edit-settings', function (User $user) {
    return $user->isAdmin
        ? Response::allow()
        : Response::denyWithStatus(404);
});
```



因为通过 `404` 响应隐藏资源是 Web 应用程序中非常常见的模式，所以 Laravel 提供了一个便捷方法 `denyAsNotFound`：

```php
use App\Models\User;
use Illuminate\Auth\Access\Response;
use Illuminate\Support\Facades\Gate;

Gate::define('edit-settings', function (User $user) {
    return $user->isAdmin
        ? Response::allow()
        : Response::denyAsNotFound();
});
```

### 拦截 Gate 检查

有时，你可能希望为特定用户授予所有权限。你可以使用 `before` 方法定义一个闭包，它会在所有其他授权检查之前运行：

```php
use App\Models\User;
use Illuminate\Support\Facades\Gate;

Gate::before(function (User $user, string $ability) {
    if ($user->isAdministrator()) {
        return true;
    }
});
```

如果 `before` 闭包返回一个非 null 的结果，那么该结果将被视为授权检查的最终结果。

你也可以使用 `after` 方法定义一个闭包，它会在所有其他授权检查之后执行：

```php
use App\Models\User;

Gate::after(function (User $user, string $ability, bool|null $result, mixed $arguments) {
    if ($user->isAdministrator()) {
        return true;
    }
});
```

由 `after` 闭包返回的值不会覆盖授权检查的结果，除非 gate 或 policy 返回了 `null`。

### 内联授权

有时，你可能希望确定当前认证用户是否被授权执行某个操作，而不必专门为该操作编写一个 Gate。Laravel 允许你通过 `Gate::allowIf` 和 `Gate::denyIf` 方法执行这种“内联”的授权检查。

内联授权不会执行任何已定义的 [“before” 或 “after” 授权钩子](#intercepting-gate-checks)：

```php
use App\Models\User;
use Illuminate\Support\Facades\Gate;

Gate::allowIf(fn (User $user) => $user->isAdministrator());

Gate::denyIf(fn (User $user) => $user->banned());
```



如果某个操作未被授权，或者当前没有用户通过认证，Laravel 会自动抛出 `Illuminate\Auth\Access\AuthorizationException` 异常。
`AuthorizationException` 实例会被 Laravel 的异常处理器自动转换为 `403` HTTP 响应。

## 创建策略（Policies）

### 生成策略

策略是围绕某个特定模型或资源组织授权逻辑的类。
例如，如果你的应用是一个博客，你可能会有一个 `App\Models\Post` 模型，以及对应的 `App\Policies\PostPolicy`，用于授权用户执行诸如创建或更新文章的操作。

你可以使用 `make:policy` Artisan 命令生成策略。生成的策略类将被放置在 `app/Policies` 目录下。如果该目录在你的应用中不存在，Laravel 会自动为你创建：

```shell
php artisan make:policy PostPolicy
```

`make:policy` 命令默认会生成一个空的策略类。
如果你希望生成一个包含示例策略方法（如查看、创建、更新和删除资源）的类，可以在执行命令时添加 `--model` 选项：

```shell
php artisan make:policy PostPolicy --model=Post
```

### 注册策略

#### 策略自动发现（Policy Discovery）

默认情况下，只要模型和策略遵循 Laravel 的标准命名约定，Laravel 会自动发现策略。

具体来说，策略类必须放在一个 `Policies` 目录下，该目录位置可以在模型目录同级或更上层。

例如，模型可以放在 `app/Models` 目录，而策略可以放在 `app/Policies` 目录。在这种情况下，Laravel 会先检查 `app/Models/Policies`，然后再检查 `app/Policies`。

此外，策略类的命名必须与模型名匹配，并加上 `Policy` 后缀。
所以，一个 `User` 模型将会对应一个 `UserPolicy` 策略类。



如果你希望定义自己的策略发现逻辑，你可以通过 `Gate::guessPolicyNamesUsing` 方法注册一个自定义的策略发现回调。
通常，这个方法应该在应用的 `AppServiceProvider` 的 `boot` 方法中调用：

```php
use Illuminate\Support\Facades\Gate;

Gate::guessPolicyNamesUsing(function (string $modelClass) {
       // 返回给定模型所对应的策略类名...
});
```

#### 手动注册策略

使用 `Gate` facade，你可以在应用的 `AppServiceProvider` 的 `boot` 方法中手动注册策略及其对应的模型：

```php
use App\Models\Order;
use App\Policies\OrderPolicy;
use Illuminate\Support\Facades\Gate;

/**
 * 初始化应用服务
 */
public function boot(): void
{
    Gate::policy(Order::class, OrderPolicy::class);
}
```

## 编写策略

### 策略方法（Policy Methods）

一旦策略类被注册，你就可以为它添加对应的授权方法。
例如，我们来在 `PostPolicy` 中定义一个 `update` 方法，用来判断某个 `App\Models\User` 是否能够更新某个 `App\Models\Post` 实例。

`update` 方法会接收一个 `User` 和一个 `Post` 实例作为参数，并且应返回 `true` 或 `false`，以指示该用户是否被授权更新该 `Post`。
在本例中，我们将验证用户的 `id` 是否与文章的 `user_id` 相匹配：

```php
<?php

namespace App\Policies;

use App\Models\Post;
use App\Models\User;

class PostPolicy
{
    /**
     * 判断用户是否可以更新指定的文章
     */
    public function update(User $user, Post $post): bool
    {
        return $user->id === $post->user_id;
    }
}
```



你可以继续在策略（policy）中定义其他方法，以满足对各种操作的授权需求。
例如，你可以定义 `view` 或 `delete` 方法来授权与 `Post` 相关的操作。
但请记住，你可以自由地为策略方法命名。

如果在通过 Artisan 控制台生成策略时使用了 `--model` 选项，那么生成的策略类将已经包含以下方法：
-   `viewAny`
-   `view`
-   `create`
-   `update`
-   `delete`
-   `restore`
-   `forceDelete`

> [!注意]
> 所有策略都是通过 Laravel 的 [服务容器](/docs/laravel/12.x/container) 解析的。
> 因此，你可以在策略的构造函数中使用类型提示声明所需的依赖，它们会被自动注入。

### 策略响应（Policy Responses）

到目前为止，我们只研究了返回简单布尔值的策略方法。
然而，有时你可能希望返回更详细的响应，包括错误消息。
为此，你可以从策略方法中返回一个 `Illuminate\Auth\Access\Response` 实例：

```php
use App\Models\Post;
use App\Models\User;
use Illuminate\Auth\Access\Response;

/**
 * 判断用户是否可以更新指定文章
 */
public function update(User $user, Post $post): Response
{
    return $user->id === $post->user_id
        ? Response::allow()
        : Response::deny('You do not own this post.');
}
```

当你从策略方法返回一个授权响应时，`Gate::allows` 方法依旧只会返回一个简单的布尔值；
但是，你可以使用 `Gate::inspect` 方法来获取 gate 返回的完整授权响应：

```php
use Illuminate\Support\Facades\Gate;

$response = Gate::inspect('update', $post);

if ($response->allowed()) {
    // 动作已被授权...
} else {
    echo $response->message();
}
```



当使用 `Gate::authorize` 方法时，如果操作未被授权，将会抛出一个 `AuthorizationException`。
在这种情况下，授权响应中提供的错误消息会被传递到 HTTP 响应中：

```php
Gate::authorize('update', $post);

// 操作已被授权...
```

#### 自定义 HTTP 响应状态码

当某个操作通过策略方法被拒绝时，默认会返回一个 `403` HTTP 响应；
然而，有时返回一个其他的 HTTP 状态码会更有用。
你可以通过 `Illuminate\Auth\Access\Response` 类的 `denyWithStatus` 静态构造方法，
来自定义授权检查失败时返回的 HTTP 状态码：

```php
use App\Models\Post;
use App\Models\User;
use Illuminate\Auth\Access\Response;

/**
 * 判断用户是否可以更新指定文章
 */
public function update(User $user, Post $post): Response
{
    return $user->id === $post->user_id
        ? Response::allow()
        : Response::denyWithStatus(404);
}
```

因为通过 `404` 响应隐藏资源是 Web 应用程序中非常常见的模式，
所以 Laravel 提供了一个便捷方法 `denyAsNotFound`：

```php
use App\Models\Post;
use App\Models\User;
use Illuminate\Auth\Access\Response;

/**
 * 判断用户是否可以更新指定文章
 */
public function update(User $user, Post $post): Response
{
    return $user->id === $post->user_id
        ? Response::allow()
        : Response::denyAsNotFound();
}
```

### 无模型的方法（Methods Without Models）

有些策略方法只会接收当前已认证用户的实例。
这种情况最常见于授权 `create` 操作时。
例如，如果你在构建一个博客，你可能希望判断用户是否有权限创建任何文章。
在这种情况下，你的策略方法只需要接收一个用户实例：

```php
/**
 * 判断指定用户是否可以创建文章
 */
public function create(User $user): bool
{
    return $user->role == 'writer';
}
```



### 游客用户（Guest Users）

默认情况下，如果传入的 HTTP 请求不是由已认证用户发起的，那么所有的 Gate 和 Policy 都会自动返回 `false`。
不过，你也可以通过在用户参数的定义中声明“可选”类型提示（`?User`）或提供一个 `null` 默认值，
来允许这些授权检查继续传递到 Gate 和 Policy：

```php
<?php

namespace App\Policies;

use App\Models\Post;
use App\Models\User;

class PostPolicy
{
    /**
     * 判断给定的文章是否可以被用户更新
     */
    public function update(?User $user, Post $post): bool
    {
        return $user?->id === $post->user_id;
    }
}
```

### 策略过滤器（Policy Filters）

对于某些用户，你可能希望在某个策略中授权他们执行所有操作。
要实现这一点，可以在策略中定义一个 `before` 方法。
`before` 方法会在策略中的任何其他方法之前执行，
这让你有机会在实际调用目标策略方法之前完成授权。
这个功能最常见的用途是允许应用管理员执行任意操作：

```php
use App\Models\User;

/**
 * 执行预授权检查
 */
public function before(User $user, string $ability): bool|null
{
    if ($user->isAdministrator()) {
        return true;
    }

    return null;
}
```
如果你希望拒绝某类用户的所有授权检查，可以从 `before` 方法返回 `false`。
如果返回 `null`，则授权检查会继续传递到策略方法。

> [!警告]
> 如果策略类中没有定义与正在检查的能力（ability）同名的方法，
> 那么该类的 `before` 方法将不会被调用。




## 使用策略授权操作（Authorizing Actions Using Policies）

### 通过 User 模型

Laravel 应用中自带的 `App\Models\User` 模型包含两个用于授权操作的便捷方法：`can` 和 `cannot`。
`can` 和 `cannot` 方法接收你希望授权的操作名称以及相关模型。

例如，我们来判断一个用户是否被授权去更新一个指定的 `App\Models\Post` 模型。
通常，这会在控制器方法中完成：

```php
<?php

namespace App\Http\Controllers;

use App\Models\Post;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class PostController extends Controller
{
    /**
     * 更新指定文章
     */
    public function update(Request $request, Post $post): RedirectResponse
    {
        if ($request->user()->cannot('update', $post)) {
            abort(403);
        }

        // 更新文章...

        return redirect('/posts');
    }
}
```

如果给定模型已经 [注册了策略](#registering-policies)，
`can` 方法会自动调用对应的策略并返回布尔结果。
如果该模型没有注册策略，`can` 方法会尝试调用与操作名相匹配的基于闭包的 Gate。

#### 不需要模型实例的操作

请记住，有些操作可能对应于策略方法（例如 `create`），它们不需要模型实例。
在这种情况下，你可以将类名传递给 `can` 方法。
类名将用于确定在授权操作时使用哪个策略：

```php
<?php

namespace App\Http\Controllers;

use App\Models\Post;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class PostController extends Controller
{
     /**
     * 创建文章
     */
    public function store(Request $request): RedirectResponse
    {
        if ($request->user()->cannot('create', Post::class)) {
            abort(403);
        }

        // 创建文章...

        return redirect('/posts');
    }
}
```



### 通过 `Gate` Facade

除了 `App\Models\User` 模型提供的便捷方法外，你也可以始终通过 `Gate` facade 的 `authorize` 方法来进行操作授权。

与 `can` 方法类似，该方法接收你想要授权的操作名称以及相关模型。
如果操作未被授权，`authorize` 方法会抛出一个 `Illuminate\Auth\Access\AuthorizationException` 异常，
而 Laravel 的异常处理器会自动将其转换为带有 **403 状态码** 的 HTTP 响应：

```php
<?php

namespace App\Http\Controllers;

use App\Models\Post;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;

class PostController extends Controller
{
    /**
     * 更新指定的博客文章
     *
     * @throws \Illuminate\Auth\Access\AuthorizationException
     */
    public function update(Request $request, Post $post): RedirectResponse
    {
        Gate::authorize('update', $post);

        // 当前用户可以更新该博客文章...

        return redirect('/posts');
    }
}
```

#### 不需要模型实例的操作

如前所述，有些策略方法（例如 `create`）并不需要一个模型实例。
在这种情况下，你应当将类名传递给 `authorize` 方法。
类名会被用来确定在授权操作时应该使用哪个策略：

```php
use App\Models\Post;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;

/**
 * 创建新的博客文章
 *
 * @throws \Illuminate\Auth\Access\AuthorizationException
 */
public function create(Request $request): RedirectResponse
{
    Gate::authorize('create', Post::class);

    // 当前用户可以创建博客文章...

    return redirect('/posts');
}
```


### 通过中间件（Via Middleware）

Laravel 提供了一个中间件，可以在传入请求到达路由或控制器之前进行操作授权。
默认情况下，`Illuminate\Auth\Middleware\Authorize` 中间件可以通过 `can` [中间件别名](/docs/laravel/12.x/middleware#middleware-aliases) 附加到路由上，
该别名由 Laravel 自动注册。

下面是一个使用 `can` 中间件授权用户更新文章的示例：

```php
use App\Models\Post;

Route::put('/post/{post}', function (Post $post) {
    // 当前用户可以更新文章...
})->middleware('can:update,post');
```
在这个示例中，我们向 `can` 中间件传递了两个参数：
1.  要授权的操作名称
2.  路由参数，该参数将传递给策略方法
在这里，由于我们使用了 [隐式模型绑定](/docs/laravel/12.x/routing#implicit-binding)，
一个 `App\Models\Post` 模型实例会被传递给策略方法。
如果用户未被授权执行该操作，中间件将返回 **HTTP 403 状态码** 的响应。

为了方便，你也可以使用 `can` 方法将中间件附加到路由上：

```php
use App\Models\Post;

Route::put('/post/{post}', function (Post $post) {
    // The current user may update the post...
})->can('update', 'post');
```

#### 不需要模型实例的操作

同样，有些策略方法（例如 `create`）不需要模型实例。
在这种情况下，你可以将类名传递给中间件。
类名将用于确定在授权操作时使用哪个策略：

```php
Route::post('/post', function () {
    // 当前用户可以创建文章...
})->middleware('can:create,App\Models\Post');
```



在字符串中指定完整类名来定义中间件可能会比较繁琐。
因此，你也可以使用 `can` 方法将中间件附加到路由上：

```php
use App\Models\Post;

Route::post('/post', function () {
    // 当前用户可以创建文章...
})->can('create', Post::class);
```

### 通过 Blade 模板（Via Blade Templates）

在编写 Blade 模板时，你可能希望仅在用户被授权执行某个操作时显示页面的一部分。
例如，你可能希望仅当用户可以更新博客文章时才显示更新表单。
在这种情况下，你可以使用 `@can` 和 `@cannot` 指令：

```blade
@can('update', $post)
    <!-- 当前用户可以更新文章... -->
@elsecan('create', App\Models\Post::class)
    <!-- 当前用户可以创建新文章... -->
@else
    <!-- ... -->
@endcan

@cannot('update', $post)
    <!-- 当前用户不能更新文章... -->
@elsecannot('create', App\Models\Post::class)
    <!-- 当前用户不能创建新文章... -->
@endcannot
```

这些指令是编写 `@if` 和 `@unless` 语句的便捷方式。
上面的 `@can` 和 `@cannot` 语句等价于以下写法：

```blade
@if (Auth::user()->can('update', $post))
    <!-- 当前用户可以更新文章... -->
@endif

@unless (Auth::user()->can('update', $post))
    <!-- 当前用户不能更新文章... -->
@endunless
```

你还可以判断用户是否被授权执行给定操作数组中的任意一个操作。
为此，可以使用 `@canany` 指令：

```blade
@canany(['update', 'view', 'delete'], $post)
    <!-- 当前用户可以更新、查看或删除文章... -->
@elsecanany(['create'], \App\Models\Post::class)
    <!-- 当前用户可以创建文章... -->
@endcanany
```



#### 不需要模型实例的操作

与大多数其他授权方法一样，如果操作不需要模型实例，你可以将类名传递给 `@can` 和 `@cannot` 指令：

```blade
@can('create', App\Models\Post::class)
    <!-- 当前用户可以创建文章... -->
@endcan

@cannot('create', App\Models\Post::class)
    <!-- 当前用户不能创建文章... -->
@endcannot
```

### 提供额外上下文（Supplying Additional Context）

在使用策略（policies）授权操作时，你可以将数组作为第二个参数传递给各种授权函数和辅助方法。

数组的第一个元素用于确定应该调用哪个策略，而数组的其余元素会作为参数传递给策略方法，
可以在做授权判断时提供额外上下文。

例如，考虑以下 `PostPolicy` 方法定义，其中包含额外的 `$category` 参数：

```php
/**
 * 判断用户是否可以更新指定文章
 */
public function update(User $user, Post $post, int $category): bool
{
    return $user->id === $post->user_id &&
           $user->canUpdateCategory($category);
}
```

在尝试判断已认证用户是否可以更新某篇文章时，可以这样调用策略方法：

```php
/**
 * 更新指定博客文章
 *
 * @throws \Illuminate\Auth\Access\AuthorizationException
 */
public function update(Request $request, Post $post): RedirectResponse
{
    Gate::authorize('update', [$post, $request->category]);

    // 当前用户可以更新该博客文章...

    return redirect('/posts');
}
```

## 授权与 Inertia（Authorization & Inertia）

虽然授权必须始终在服务器端处理，但通常将授权数据提供给前端应用可以更方便地渲染应用的 UI。
Laravel 并没有规定向基于 Inertia 的前端暴露授权信息的标准约定。



不过，如果你使用的是 Laravel 基于 Inertia 的 [入门套件（starter kits）](/docs/laravel/12.x/starter-kits)，
你的应用已经包含了一个 `HandleInertiaRequests` 中间件。

在这个中间件的 `share` 方法中，你可以返回共享数据，这些数据会被提供给应用中所有的 Inertia 页面。
这个共享数据是定义用户授权信息的一个便捷位置：

```php
<?php

namespace App\Http\Middleware;

use App\Models\Post;
use Illuminate\Http\Request;
use Inertia\Middleware;

class HandleInertiaRequests extends Middleware
{
    // ...

    /**
     * 定义默认共享的属性（props）
     *
     * @return array<string, mixed>
     */
    public function share(Request $request)
    {
        return [
            ...parent::share($request),
            'auth' => [
                'user' => $request->user(),
                'permissions' => [
                    'post' => [
                        'create' => $request->user()->can('create', Post::class),
                    ],
                ],
            ],
        ];
    }
}
```
