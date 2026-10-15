# 用户授权

- [简介](#introduction)
- [Gates（权限门）](#gates)
    - [编写权限门](#writing-gates)
    - [授权操作](#authorizing-actions-via-gates)
    - [权限门响应](#gate-responses)
    - [拦截权限门检查](#intercepting-gate-checks)
    - [内联授权](#inline-authorization)
- [创建策略](#creating-policies)
    - [生成策略](#generating-policies)
    - [注册策略](#registering-policies)
- [编写策略](#writing-policies)
    - [策略方法](#policy-methods)
    - [策略响应](#policy-responses)
    - [不接收模型的方法](#methods-without-models)
    - [访客用户](#guest-users)
    - [策略过滤器](#policy-filters)
- [使用策略授权操作](#authorizing-actions-using-policies)
    - [通过用户模型](#via-the-user-model)
    - [通过 Gate 门面](#via-the-gate-facade)
    - [通过中间件](#via-middleware)
    - [通过 Blade 模板](#via-blade-templates)
    - [提供额外上下文](#supplying-additional-context)
- [授权与 Inertia](#authorization-and-inertia)

<a name="introduction"></a>
## 简介

除了提供内置的 [身份认证](/docs/{{version}}/authentication) 服务，Laravel 还提供了简单的方式来判断用户是否有权对给定资源执行操作。例如，即使用户已经通过身份认证，也不一定有权更新或删除应用管理的某些 Eloquent 模型或数据库记录。Laravel 的授权功能让你能够方便、有序地管理这类授权检查。

Laravel 提供了两种主要的操作授权方式：[权限门（Gates）](#gates) 和 [策略（Policies）](#creating-policies)。权限门与策略的关系类似于路由与控制器：权限门通过简单的闭包进行授权，而策略则像控制器一样，将特定模型或资源的授权逻辑组织在一起。本文会先介绍权限门，再介绍策略。

构建应用时，你不必在权限门和策略之间二选一。大多数应用都会同时使用它们，这完全没有问题。权限门最适合不涉及模型或资源的操作，例如查看管理员仪表盘；而当你需要授权针对特定模型或资源的操作时，应使用策略。

<a name="gates"></a>
## Gates（权限门）

<a name="writing-gates"></a>
### 编写权限门

> [!WARNING]
> 权限门有助于你学习 Laravel 授权功能的基础知识。不过，在构建健壮的 Laravel 应用时，应考虑使用 [策略](#creating-policies) 来组织授权规则。

权限门本质上是判断用户是否有权执行某个操作的闭包。通常，你会使用 `Gate` 门面在 `App\Providers\AppServiceProvider` 类的 `boot` 方法中定义权限门。权限门始终接收用户实例作为第一个参数，也可以接收额外参数，例如相关的 Eloquent 模型。

在下面的示例中，我们将定义一个权限门，判断用户能否更新给定的 `App\Models\Post` 模型。这个权限门会比较用户的 `id` 与文章记录中表示创建者的 `user_id`：

```php
use App\Models\Post;
use App\Models\User;
use Illuminate\Support\Facades\Gate;

/**
 * 初始化应用服务。
 */
public function boot(): void
{
    Gate::define('update-post', function (User $user, Post $post) {
        return $user->id === $post->user_id;
    });
}
```

与控制器一样，权限门也可以使用类回调数组来定义：

```php
use App\Policies\PostPolicy;
use Illuminate\Support\Facades\Gate;

/**
 * 初始化应用服务。
 */
public function boot(): void
{
    Gate::define('update-post', [PostPolicy::class, 'update']);
}
```

<a name="authorizing-actions-via-gates"></a>
### 授权操作

要使用权限门授权操作，可以调用 `Gate` 门面提供的 `allows` 或 `denies` 方法。你不需要将当前已认证的用户传入这些方法，Laravel 会自动将用户传给权限门闭包。通常，你会在控制器中执行需要授权的操作之前调用这些方法：

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
     * 更新给定的文章。
     */
    public function update(Request $request, Post $post): RedirectResponse
    {
        if (! Gate::allows('update-post', $post)) {
            abort(403);
        }

        // 更新文章……

        return redirect('/posts');
    }
}
```

如果想判断当前已认证用户以外的其他用户是否有权执行某个操作，可以使用 `Gate` 门面的 `forUser` 方法：

```php
if (Gate::forUser($user)->allows('update-post', $post)) {
    // 该用户可以更新文章……
}

if (Gate::forUser($user)->denies('update-post', $post)) {
    // 该用户无权更新文章……
}
```

你可以使用 `any` 或 `none` 方法一次检查多个操作的权限：

```php
if (Gate::any(['update-post', 'delete-post'], $post)) {
    // 该用户可以更新或删除文章……
}

if (Gate::none(['update-post', 'delete-post'], $post)) {
    // 该用户既不能更新也不能删除文章……
}
```

<a name="authorizing-or-throwing-exceptions"></a>
#### 授权或抛出异常

如果想检查某个操作是否获得授权，并在用户无权执行时自动抛出 `Illuminate\Auth\Access\AuthorizationException` 异常，可以使用 `Gate` 门面的 `authorize` 方法。Laravel 会自动将 `AuthorizationException` 实例转换为 HTTP 403 响应：

```php
Gate::authorize('update-post', $post);

// 操作已获授权……
```

<a name="gates-supplying-additional-context"></a>
#### 提供额外上下文

用于检查权限的 Gate 方法（`allows`、`denies`、`check`、`any`、`none`、`authorize`、`can`、`cannot`）以及授权 [Blade 指令](#via-blade-templates)（`@can`、`@cannot`、`@canany`）都可以接收数组作为第二个参数。数组中的元素会作为参数传给权限门闭包，在作出授权判断时提供额外的上下文：

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
    // 该用户可以创建文章……
}
```

<a name="gate-responses"></a>
### 权限门响应

到目前为止，我们只介绍了返回简单布尔值的权限门。有时你可能希望返回包含错误信息的详细响应。为此，可以从权限门中返回一个 `Illuminate\Auth\Access\Response` 实例：

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

即使权限门返回授权响应，`Gate::allows` 方法仍然只返回布尔值。不过，你可以使用 `Gate::inspect` 方法获取权限门返回的完整授权响应：

```php
$response = Gate::inspect('edit-settings');

if ($response->allowed()) {
    // 操作已获授权……
} else {
    echo $response->message();
}
```

使用 `Gate::authorize` 方法时，如果操作未获授权，会抛出 `AuthorizationException` 异常，授权响应提供的错误信息也会传递到 HTTP 响应中：

```php
Gate::authorize('edit-settings');

// 操作已获授权……
```

<a name="customizing-gate-response-status"></a>
#### 自定义 HTTP 响应状态码

当权限门拒绝某个操作时，默认返回 HTTP `403` 响应。不过，有时返回其他 HTTP 状态码更合适。你可以使用 `Illuminate\Auth\Access\Response` 类的 `denyWithStatus` 静态构造方法，自定义授权检查失败时返回的 HTTP 状态码：

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

在 Web 应用中，通过 `404` 响应隐藏资源十分常见，因此 Laravel 提供了便捷的 `denyAsNotFound` 方法：

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

<a name="intercepting-gate-checks"></a>
### 拦截权限门检查

有时，你可能希望授予特定用户所有权限。你可以使用 `before` 方法定义一个闭包，使其在所有其他授权检查之前运行：

```php
use App\Models\User;
use Illuminate\Support\Facades\Gate;

Gate::before(function (User $user, string $ability) {
    if ($user->isAdministrator()) {
        return true;
    }
});
```

如果 `before` 闭包返回非 null 的结果，该结果就会作为授权检查的结果。

你可以使用 `after` 方法定义一个闭包，使其在所有其他授权检查之后执行：

```php
use App\Models\User;

Gate::after(function (User $user, string $ability, bool|null $result, mixed $arguments) {
    if ($user->isAdministrator()) {
        return true;
    }
});
```

`after` 闭包的返回值不会覆盖授权检查的结果，除非权限门或策略返回了 `null`。

<a name="inline-authorization"></a>
### 内联授权

有时，你可能只想判断当前已认证用户是否有权执行某个操作，而不希望为此专门定义一个权限门。Laravel 允许你通过 `Gate::allowIf` 和 `Gate::denyIf` 方法执行这种「内联」授权检查。内联授权不会执行任何已定义的 [「before」或「after」授权钩子](#intercepting-gate-checks)：

```php
use App\Models\User;
use Illuminate\Support\Facades\Gate;

Gate::allowIf(fn (User $user) => $user->isAdministrator());

Gate::denyIf(fn (User $user) => $user->banned());
```

如果操作未获授权，或当前没有已认证用户，Laravel 会自动抛出 `Illuminate\Auth\Access\AuthorizationException` 异常。Laravel 的异常处理器会自动将 `AuthorizationException` 实例转换为 HTTP 403 响应。

<a name="creating-policies"></a>
## 创建策略

<a name="generating-policies"></a>
### 生成策略

策略是围绕特定模型或资源组织授权逻辑的类。例如，在博客应用中，你可能会有一个 `App\Models\Post` 模型，以及对应的 `App\Policies\PostPolicy` 策略，用于授权用户创建或更新文章等操作。

你可以使用 `make:policy` Artisan 命令生成策略。生成的策略会放在 `app/Policies` 目录中。如果应用中不存在此目录，Laravel 会自动创建：

```shell
php artisan make:policy PostPolicy
```

`make:policy` 命令会生成一个空的策略类。如果希望生成的类包含查看、创建、更新和删除资源的示例策略方法，可以在执行命令时传入 `--model` 选项：

```shell
php artisan make:policy PostPolicy --model=Post
```

<a name="registering-policies"></a>
### 注册策略

<a name="policy-discovery"></a>
#### 策略自动发现

默认情况下，只要模型和策略遵循 Laravel 的标准命名约定，Laravel 就会自动发现策略。具体来说，策略必须位于 `Policies` 目录中，该目录应放在模型所在目录内或其上级目录中。例如，模型可以位于 `app/Models` 目录，策略则位于 `app/Policies` 目录。此时，Laravel 会先在 `app/Models/Policies` 中查找策略，再查找 `app/Policies`。此外，策略名称必须与模型名称匹配，并以 `Policy` 结尾。因此，`User` 模型对应的策略类应为 `UserPolicy`。

如果希望自定义策略发现逻辑，可以通过 `Gate::guessPolicyNamesUsing` 方法注册自定义的策略发现回调。通常，应在应用的 `AppServiceProvider` 的 `boot` 方法中调用此方法：

```php
use Illuminate\Support\Facades\Gate;

Gate::guessPolicyNamesUsing(function (string $modelClass) {
    // 返回给定模型对应的策略类名……
});
```

<a name="manually-registering-policies"></a>
#### 手动注册策略

你可以使用 `Gate` 门面，在应用的 `AppServiceProvider` 的 `boot` 方法中手动注册策略及其对应的模型：

```php
use App\Models\Order;
use App\Policies\OrderPolicy;
use Illuminate\Support\Facades\Gate;

/**
 * 初始化应用服务。
 */
public function boot(): void
{
    Gate::policy(Order::class, OrderPolicy::class);
}
```

你也可以在模型类上添加 `UsePolicy` 属性，告知 Laravel 该模型对应的策略：

```php
<?php

namespace App\Models;

use App\Policies\OrderPolicy;
use Illuminate\Database\Eloquent\Attributes\UsePolicy;
use Illuminate\Database\Eloquent\Model;

#[UsePolicy(OrderPolicy::class)]
class Order extends Model
{
    //
}
```

<a name="writing-policies"></a>
## 编写策略

<a name="policy-methods"></a>
### 策略方法

注册策略类后，就可以为它要授权的每个操作添加方法。例如，我们在 `PostPolicy` 中定义一个 `update` 方法，用来判断给定的 `App\Models\User` 能否更新给定的 `App\Models\Post` 实例。

`update` 方法接收 `User` 和 `Post` 实例作为参数，并应返回 `true` 或 `false`，表示用户是否有权更新给定的 `Post`。因此，在此示例中，我们会检查用户的 `id` 是否与文章的 `user_id` 相同：

```php
<?php

namespace App\Policies;

use App\Models\Post;
use App\Models\User;

class PostPolicy
{
    /**
     * 判断用户是否可以更新给定的文章。
     */
    public function update(User $user, Post $post): bool
    {
        return $user->id === $post->user_id;
    }
}
```

你可以根据授权需求，继续在策略中定义其他方法。例如，定义 `view` 或 `delete` 方法来授权与 `Post` 相关的不同操作。不过，策略方法可以自由命名。

如果通过 Artisan 控制台生成策略时使用了 `--model` 选项，生成的策略类就已经包含 `viewAny`、`view`、`create`、`update`、`delete`、`restore` 和 `forceDelete` 操作对应的方法。

> [!NOTE]
> 所有策略都通过 Laravel 的 [服务容器](/docs/{{version}}/container) 解析，因此你可以在策略构造函数中使用类型提示声明所需的依赖，让它们自动注入。

<a name="policy-responses"></a>
### 策略响应

到目前为止，我们只介绍了返回简单布尔值的策略方法。有时你可能希望返回包含错误信息的详细响应。为此，可以从策略方法中返回一个 `Illuminate\Auth\Access\Response` 实例：

```php
use App\Models\Post;
use App\Models\User;
use Illuminate\Auth\Access\Response;

/**
 * 判断用户是否可以更新给定的文章。
 */
public function update(User $user, Post $post): Response
{
    return $user->id === $post->user_id
        ? Response::allow()
        : Response::deny('You do not own this post.');
}
```

即使策略返回授权响应，`Gate::allows` 方法仍然只返回布尔值。不过，你可以使用 `Gate::inspect` 方法获取权限门返回的完整授权响应：

```php
use Illuminate\Support\Facades\Gate;

$response = Gate::inspect('update', $post);

if ($response->allowed()) {
    // 操作已获授权……
} else {
    echo $response->message();
}
```

使用 `Gate::authorize` 方法时，如果操作未获授权，会抛出 `AuthorizationException` 异常，授权响应提供的错误信息也会传递到 HTTP 响应中：

```php
Gate::authorize('update', $post);

// 操作已获授权……
```

<a name="customizing-policy-response-status"></a>
#### 自定义 HTTP 响应状态码

当策略方法拒绝某个操作时，默认返回 HTTP `403` 响应。不过，有时返回其他 HTTP 状态码更合适。你可以使用 `Illuminate\Auth\Access\Response` 类的 `denyWithStatus` 静态构造方法，自定义授权检查失败时返回的 HTTP 状态码：

```php
use App\Models\Post;
use App\Models\User;
use Illuminate\Auth\Access\Response;

/**
 * 判断用户是否可以更新给定的文章。
 */
public function update(User $user, Post $post): Response
{
    return $user->id === $post->user_id
        ? Response::allow()
        : Response::denyWithStatus(404);
}
```

在 Web 应用中，通过 `404` 响应隐藏资源十分常见，因此 Laravel 提供了便捷的 `denyAsNotFound` 方法：

```php
use App\Models\Post;
use App\Models\User;
use Illuminate\Auth\Access\Response;

/**
 * 判断用户是否可以更新给定的文章。
 */
public function update(User $user, Post $post): Response
{
    return $user->id === $post->user_id
        ? Response::allow()
        : Response::denyAsNotFound();
}
```

<a name="methods-without-models"></a>
### 不接收模型的方法

有些策略方法只接收当前已认证用户的实例，这在授权 `create` 操作时最为常见。例如，构建博客应用时，你可能希望判断某个用户是否有权创建文章。此时，策略方法只需要接收用户实例：

```php
/**
 * 判断给定用户是否可以创建文章。
 */
public function create(User $user): bool
{
    return $user->role == 'writer';
}
```

<a name="guest-users"></a>
### 访客用户

默认情况下，如果传入的 HTTP 请求不是由已认证用户发起的，所有权限门和策略都会自动返回 `false`。不过，你可以为用户参数声明可空类型提示，或提供 `null` 默认值，让这些授权检查继续交给权限门和策略处理：

```php
<?php

namespace App\Policies;

use App\Models\Post;
use App\Models\User;

class PostPolicy
{
    /**
     * 判断用户是否可以更新给定的文章。
     */
    public function update(?User $user, Post $post): bool
    {
        return $user?->id === $post->user_id;
    }
}
```

<a name="policy-filters"></a>
### 策略过滤器

对于某些用户，你可能希望允许他们执行某个策略中的所有操作。为此，可以在策略中定义 `before` 方法。该方法会在策略的其他方法之前执行，让你在目标策略方法真正被调用前授权操作。这通常用于允许应用管理员执行任何操作：

```php
use App\Models\User;

/**
 * 执行授权前的检查。
 */
public function before(User $user, string $ability): bool|null
{
    if ($user->isAdministrator()) {
        return true;
    }

    return null;
}
```

如果希望对某类用户拒绝所有授权检查，可以让 `before` 方法返回 `false`。如果返回 `null`，授权检查则会继续交给相应的策略方法处理。

> [!WARNING]
> 如果策略类中没有与待检查权限同名的方法，该类的 `before` 方法就不会被调用。

<a name="authorizing-actions-using-policies"></a>
## 使用策略授权操作

<a name="via-the-user-model"></a>
### 通过用户模型

Laravel 应用自带的 `App\Models\User` 模型提供了两个实用的操作授权方法：`can` 和 `cannot`。这两个方法接收要授权的操作名称和相关模型。例如，下面判断用户是否有权更新给定的 `App\Models\Post` 模型。通常，这会在控制器方法中进行：

```php
<?php

namespace App\Http\Controllers;

use App\Models\Post;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class PostController extends Controller
{
    /**
     * 更新给定的文章。
     */
    public function update(Request $request, Post $post): RedirectResponse
    {
        if ($request->user()->cannot('update', $post)) {
            abort(403);
        }

        // 更新文章……

        return redirect('/posts');
    }
}
```

如果给定模型已 [注册策略](#registering-policies)，`can` 方法会自动调用相应策略并返回布尔结果。如果该模型没有注册策略，`can` 方法会尝试调用与给定操作名称匹配的闭包权限门。

<a name="user-model-actions-that-dont-require-models"></a>
#### 不需要模型实例的操作

请记住，某些操作可能对应 `create` 这类不需要模型实例的策略方法。此时，你可以将类名传给 `can` 方法。这个类名将用于确定授权操作时应使用哪个策略：

```php
<?php

namespace App\Http\Controllers;

use App\Models\Post;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class PostController extends Controller
{
    /**
     * 创建文章。
     */
    public function store(Request $request): RedirectResponse
    {
        if ($request->user()->cannot('create', Post::class)) {
            abort(403);
        }

        // 创建文章……

        return redirect('/posts');
    }
}
```

<a name="via-the-gate-facade"></a>
### 通过 `Gate` 门面

除了 `App\Models\User` 模型提供的实用方法，你还可以随时通过 `Gate` 门面的 `authorize` 方法授权操作。

与 `can` 方法一样，此方法接收要授权的操作名称和相关模型。如果操作未获授权，`authorize` 方法会抛出 `Illuminate\Auth\Access\AuthorizationException` 异常，Laravel 的异常处理器会自动将其转换为状态码为 403 的 HTTP 响应：

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
     * 更新给定的博客文章。
     *
     * @throws \Illuminate\Auth\Access\AuthorizationException
     */
    public function update(Request $request, Post $post): RedirectResponse
    {
        Gate::authorize('update', $post);

        // 当前用户可以更新博客文章……

        return redirect('/posts');
    }
}
```

<a name="controller-actions-that-dont-require-models"></a>
#### 不需要模型实例的操作

如前所述，`create` 这类策略方法不需要模型实例。此时，应将类名传给 `authorize` 方法。这个类名将用于确定授权操作时应使用哪个策略：

```php
use App\Models\Post;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;

/**
 * 创建新的博客文章。
 *
 * @throws \Illuminate\Auth\Access\AuthorizationException
 */
public function create(Request $request): RedirectResponse
{
    Gate::authorize('create', Post::class);

    // 当前用户可以创建博客文章……

    return redirect('/posts');
}
```

<a name="via-middleware"></a>
### 通过中间件

Laravel 提供了一个中间件，可以在传入请求到达路由或控制器之前授权操作。默认情况下，你可以通过 Laravel 自动注册的 `can` [中间件别名](/docs/{{version}}/middleware#middleware-aliases)，将 `Illuminate\Auth\Middleware\Authorize` 中间件附加到路由上。下面使用 `can` 中间件授权用户更新文章：

```php
use App\Models\Post;

Route::put('/post/{post}', function (Post $post) {
    // 当前用户可以更新文章……
})->middleware('can:update,post');
```

在此示例中，我们向 `can` 中间件传入两个参数：第一个是要授权的操作名称，第二个是要传给策略方法的路由参数。由于这里使用了 [隐式模型绑定](/docs/{{version}}/routing#implicit-binding)，传给策略方法的会是一个 `App\Models\Post` 模型。如果用户无权执行给定操作，中间件就会返回状态码为 403 的 HTTP 响应。

为了方便，你也可以使用 `can` 方法将 `can` 中间件附加到路由上：

```php
use App\Models\Post;

Route::put('/post/{post}', function (Post $post) {
    // 当前用户可以更新文章……
})->can('update', 'post');
```

如果使用 [控制器中间件属性](/docs/{{version}}/controllers#middleware-attributes)，可以通过 `Authorize` 属性应用 `can` 中间件：

```php
use Illuminate\Routing\Attributes\Controllers\Authorize;

#[Authorize('update', 'post')]
public function update(Post $post)
{
    // 当前用户可以更新文章……
}
```

<a name="middleware-actions-that-dont-require-models"></a>
#### 不需要模型实例的操作

同样，`create` 这类策略方法不需要模型实例。此时，可以将类名传给中间件。这个类名将用于确定授权操作时应使用哪个策略：

```php
Route::post('/post', function () {
    // 当前用户可以创建文章……
})->middleware('can:create,App\Models\Post');
```

在字符串形式的中间件定义中写出完整类名可能比较繁琐，因此你也可以使用 `can` 方法将 `can` 中间件附加到路由上：

```php
use App\Models\Post;

Route::post('/post', function () {
    // 当前用户可以创建文章……
})->can('create', Post::class);
```

<a name="via-blade-templates"></a>
### 通过 Blade 模板

编写 Blade 模板时，你可能希望仅在用户有权执行某个操作时显示页面的某个部分。例如，只有当用户能更新博客文章时，才显示更新表单。此时，可以使用 `@can` 和 `@cannot` 指令：

```blade
@can('update', $post)
    <!-- 当前用户可以更新文章…… -->
@elsecan('create', App\Models\Post::class)
    <!-- 当前用户可以创建新文章…… -->
@else
    <!-- ... -->
@endcan

@cannot('update', $post)
    <!-- 当前用户无权更新文章…… -->
@elsecannot('create', App\Models\Post::class)
    <!-- 当前用户无权创建新文章…… -->
@endcannot
```

这些指令是编写 `@if` 和 `@unless` 语句的便捷方式。上面的 `@can` 和 `@cannot` 语句等价于以下写法：

```blade
@if (Auth::user()->can('update', $post))
    <!-- 当前用户可以更新文章…… -->
@endif

@unless (Auth::user()->can('update', $post))
    <!-- 当前用户无权更新文章…… -->
@endunless
```

你也可以判断用户是否有权执行给定操作数组中的任意一个操作。为此，可以使用 `@canany` 指令：

```blade
@canany(['update', 'view', 'delete'], $post)
    <!-- 当前用户可以更新、查看或删除文章…… -->
@elsecanany(['create'], \App\Models\Post::class)
    <!-- 当前用户可以创建文章…… -->
@endcanany
```

<a name="blade-actions-that-dont-require-models"></a>
#### 不需要模型实例的操作

与大多数其他授权方法一样，如果操作不需要模型实例，可以将类名传给 `@can` 和 `@cannot` 指令：

```blade
@can('create', App\Models\Post::class)
    <!-- 当前用户可以创建文章…… -->
@endcan

@cannot('create', App\Models\Post::class)
    <!-- 当前用户无权创建文章…… -->
@endcannot
```

<a name="supplying-additional-context"></a>
### 提供额外上下文

使用策略授权操作时，你可以将数组作为第二个参数传给各种授权函数和辅助函数。数组的第一个元素用于确定应调用哪个策略，其余元素则作为参数传给策略方法，在作出授权判断时提供额外的上下文。例如，下面的 `PostPolicy` 方法定义包含一个额外的 `$category` 参数：

```php
/**
 * 判断用户是否可以更新给定的文章。
 */
public function update(User $user, Post $post, int $category): bool
{
    return $user->id === $post->user_id &&
           $user->canUpdateCategory($category);
}
```

判断已认证用户能否更新给定文章时，可以这样调用该策略方法：

```php
/**
 * 更新给定的博客文章。
 *
 * @throws \Illuminate\Auth\Access\AuthorizationException
 */
public function update(Request $request, Post $post): RedirectResponse
{
    Gate::authorize('update', [$post, $request->category]);

    // 当前用户可以更新博客文章……

    return redirect('/posts');
}
```

<a name="authorization-and-inertia"></a>
## 授权与 Inertia

授权必须始终在服务器端处理。不过，将授权数据提供给前端应用，通常有助于前端正确渲染应用界面。Laravel 没有规定向基于 Inertia 的前端提供授权信息必须遵循的约定。

如果你使用的是 Laravel 基于 Inertia 的 [入门套件](/docs/{{version}}/starter-kits)，应用中已经包含 `HandleInertiaRequests` 中间件。在该中间件的 `share` 方法中，你可以返回共享数据，供应用中的所有 Inertia 页面使用。这些共享数据很适合用来定义用户的授权信息：

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
     * 定义默认共享的属性（props）。
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
