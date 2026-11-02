
# Laravel Pennant

-   [简介](#introduction)
-   [安装](#installation)
-   [配置](#configuration)
-   [定义功能](#defining-features)
    -   [基于类的功能](#class-based-features)
-   [检查功能](#checking-features)
    -   [条件执行](#conditional-execution)
    -   [`HasFeatures` Trait](#the-has-features-trait)
    -   [Blade 指令](#blade-directive)
    -   [中间件](#middleware)
    -   [拦截功能检查](#intercepting-feature-checks)
    -   [内存缓存](#in-memory-cache)
-   [作用域](#scope)
    -   [指定作用域](#specifying-the-scope)
    -   [默认作用域](#default-scope)
    -   [可空作用域](#nullable-scope)
    -   [识别作用域](#identifying-scope)
    -   [序列化作用域](#serializing-scope)
-   [丰富的功能值](#rich-feature-values)
-   [检索多个功能](#retrieving-multiple-features)
-   [预加载](#eager-loading)
-   [更新值](#updating-values)
    -   [批量更新](#bulk-updates)
    -   [清除功能](#purging-features)
-   [测试](#testing)
-   [添加自定义 Pennant 驱动](#adding-custom-pennant-drivers)
    -   [实现驱动](#implementing-the-driver)
    -   [注册驱动](#registering-the-driver)
    -   [在外部定义功能](#defining-features-externally)
-   [事件](#events)

## 简介

[Laravel Pennant](https://github.com/laravel/pennant) 是一个简单且轻量的 **功能开关（feature flag）** 包 —— 没有多余的复杂性。
功能开关让你能够：

-   逐步发布新的应用功能；
-   自信地进行功能上线；
-   对新的界面设计进行 **A/B 测试**；
-   辅助 **主干式开发（trunk-based development）** 策略；
-   以及更多扩展用途。

## 安装

首先，使用 Composer 包管理器将 Pennant 安装到你的项目中：

```shell
composer require laravel/pennant
```

接下来，你需要通过 `vendor:publish` Artisan 命令发布 Pennant 的配置文件和迁移文件：

```shell
php artisan vendor:publish --provider="Laravel\Pennant\PennantServiceProvider"
```

最后，运行项目的数据库迁移。这会创建一个 `features` 表，Pennant 将使用该表来驱动其 `database` 驱动：

```shell
php artisan migrate
```


## 配置（Configuration）

在发布 Pennant 的资源之后，其配置文件将位于 `config/pennant.php`。
该配置文件允许你指定 **默认的存储机制**，用于存储 Pennant 已解析的功能开关值。

Pennant 支持以下存储方式：

-   通过 `array` 驱动将已解析的功能开关值存储在 **内存数组** 中；
-   或通过 `database` 驱动将已解析的功能开关值 **持久化存储** 到关系型数据库中。
    其中，`database` 驱动是 Pennant 默认使用的存储机制。

## 定义功能（Defining Features）

要定义一个功能开关，可以使用 `Feature` facade 提供的 `define` 方法。
你需要为功能指定一个名称，并提供一个闭包（closure），该闭包将在解析功能的初始值时被调用。

通常，功能会在 **服务提供者（service provider）** 中使用 `Feature` facade 定义。
闭包将接收功能检查的 “作用域（scope）”，最常见的作用域是当前已认证的用户。

下面的示例展示了如何为应用的用户 **逐步推出一个新的 API** 功能：

```php
<?php

namespace App\Providers;

use App\Models\User;
use Illuminate\Support\Lottery;
use Illuminate\Support\ServiceProvider;
use Laravel\Pennant\Feature;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 引导应用服务。
     */
    public function boot(): void
    {
        Feature::define('new-api', fn (User $user) => match (true) {
            $user->isInternalTeamMember() => true,
            $user->isHighTrafficCustomer() => false,
            default => Lottery::odds(1 / 100),
        });
    }
}
```

如上示例中，我们为该功能定义了以下规则：

-   所有内部团队成员应该使用新的 API；
-   高流量客户不应该使用新的 API；
-   其他用户将 **以 1/100 的概率随机启用该功能**。



当某个用户第一次检查 `new-api` 功能时，闭包的执行结果会被存储驱动保存。
下次针对同一用户再次检查该功能时，系统会从存储中直接获取该值，而不会再次执行闭包。

为方便起见，如果一个功能定义仅返回一个 **Lottery（随机分配概率）**，你可以完全省略闭包：

    Feature::define('site-redesign', Lottery::odds(1, 1000));

### 基于类的功能（Class Based Features）

Pennant 还支持定义**基于类的功能**。
与基于闭包的功能定义不同，基于类的功能无需在服务提供者中注册。

要创建一个基于类的功能，可以运行以下 Artisan 命令。
默认情况下，功能类会被放置在应用程序的 `app/Features` 目录中：

```shell
php artisan pennant:feature NewApi
```

当编写一个功能类时，只需要定义一个 `resolve` 方法。
该方法会被调用，用于解析给定作用域（scope）的功能初始值。
通常，这个作用域就是当前已登录的用户：

```php
<?php

namespace App\Features;

use App\Models\User;
use Illuminate\Support\Lottery;

class NewApi
{
    /**
     * 解析功能的初始值。
     */
    public function resolve(User $user): mixed
    {
        return match (true) {
            $user->isInternalTeamMember() => true,
            $user->isHighTrafficCustomer() => false,
            default => Lottery::odds(1 / 100),
        };
    }
}
```

如果你希望手动解析一个基于类的功能实例，可以通过 `Feature` facade 调用 `instance` 方法：

```php
use Illuminate\Support\Facades\Feature;

$instance = Feature::instance(NewApi::class);
```

> [!注意]
> 功能类是通过 [Laravel 容器](/docs/laravel/12.x/container) 解析的，
因此你可以在功能类的构造函数中注入所需的依赖。


#### 自定义存储的功能名称（Customizing the Stored Feature Name）

默认情况下，Pennant 会将功能类的**完整命名空间类名**作为存储标识。
如果你希望将存储的功能名称与应用程序的内部结构解耦，可以在功能类中定义一个 `$name` 属性。
此属性的值将会替代类名被保存：

```php
<?php

namespace App\Features;

class NewApi
{
    /**
     * 功能在存储中使用的名称。
     *
     * @var string
     */
    public $name = 'new-api';

    // ...
}
```

## 检查功能状态（Checking Features）

要判断某个功能是否处于启用状态，可以使用 `Feature` facade 的 `active` 方法。
默认情况下，Pennant 会针对**当前已认证的用户**检查功能状态：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Laravel\Pennant\Feature;

class PodcastController
{
    /**
     * 显示资源列表。
     */
    public function index(Request $request): Response
    {
        return Feature::active('new-api')
            ? $this->resolveNewApiResponse($request)
            : $this->resolveLegacyApiResponse($request);
    }

    // ...
}
```

虽然默认是针对当前登录用户进行检查，但你也可以轻松地针对**其他用户或作用域（scope）**进行检查。
要实现这一点，可以使用 `Feature` facade 提供的 `for` 方法：

```php
return Feature::for($user)->active('new-api')
    ? $this->resolveNewApiResponse($request)
    : $this->resolveLegacyApiResponse($request);
```

Pennant 还提供了一些额外的便捷方法，用于判断功能是否处于激活或未激活状态：

```php
// 判断给定的所有功能是否都已激活...
Feature::allAreActive(['new-api', 'site-redesign']);

// 判断给定的任意一个功能是否已激活...
Feature::someAreActive(['new-api', 'site-redesign']);

// 判断某个功能是否未激活...
Feature::inactive('new-api');

// 判断给定的所有功能是否都未激活...
Feature::allAreInactive(['new-api', 'site-redesign']);

// 判断给定的任意一个功能是否未激活...
Feature::someAreInactive(['new-api', 'site-redesign']);
```

> [!注意]
> 当在 **HTTP 上下文之外** 使用 Pennant（例如在 Artisan 命令或队列任务中）时，
通常应**显式指定功能的作用域**（scope）。
或者，你也可以定义一个**默认作用域（default scope）**，
以同时兼容已认证与未认证的上下文环境。




#### 检查基于类的功能（Class Based Features）

对于基于类的功能，在检查功能时，你应当提供类名：

```php
<?php

namespace App\Http\Controllers;

use App\Features\NewApi;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Laravel\Pennant\Feature;

class PodcastController
{
    /**
     * 显示资源列表。
     */
    public function index(Request $request): Response
    {
        return Feature::active(NewApi::class)
            ? $this->resolveNewApiResponse($request)
            : $this->resolveLegacyApiResponse($request);
    }

    // ...
}
```

### 条件执行（Conditional Execution）

`when` 方法可以用于在某个功能处于激活状态时，流畅地执行指定的闭包。此外，还可以提供第二个闭包，当功能未激活时将执行该闭包：

```php
<?php

namespace App\Http\Controllers;

use App\Features\NewApi;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Laravel\Pennant\Feature;

class PodcastController
{
    /**
     * 显示资源列表。
     */
    public function index(Request $request): Response
    {
        return Feature::when(NewApi::class,
            fn () => $this->resolveNewApiResponse($request),
            fn () => $this->resolveLegacyApiResponse($request),
        );
    }

    // ...
}
```

`unless` 方法与 `when` 方法相反：当功能未激活时执行第一个闭包：

```php
return Feature::unless(NewApi::class,
    fn () => $this->resolveLegacyApiResponse($request),
    fn () => $this->resolveNewApiResponse($request),
);
```

### `HasFeatures` Trait

Pennant 的 `HasFeatures` trait 可以添加到你应用程序的 `User` 模型（或任何具有功能的模型）中，从而提供一种流畅且方便的方式，直接从模型上检查功能：

```php
<?php

namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Laravel\Pennant\Concerns\HasFeatures;

class User extends Authenticatable
{
    use HasFeatures;

    // ...
}
```



一旦将该 trait 添加到模型中，你就可以通过调用 `features` 方法轻松检查功能状态：

```php
if ($user->features()->active('new-api')) {
    // ...
}
```

当然，`features` 方法还提供了许多其他便捷的方法，用于与功能进行交互：

```php
// 获取值...
$value = $user->features()->value('purchase-button');
$values = $user->features()->values(['new-api', 'purchase-button']);

// 状态判断...
$user->features()->active('new-api');
$user->features()->allAreActive(['new-api', 'server-api']);
$user->features()->someAreActive(['new-api', 'server-api']);

$user->features()->inactive('new-api');
$user->features()->allAreInactive(['new-api', 'server-api']);
$user->features()->someAreInactive(['new-api', 'server-api']);

// 条件执行...
$user->features()->when('new-api',
    fn () => /* ... */,
    fn () => /* ... */,
);

$user->features()->unless('new-api',
    fn () => /* ... */,
    fn () => /* ... */,
);
```

### Blade 指令（Blade Directive）

为了让在 Blade 模板中检查功能更加方便，Pennant 提供了 `@feature` 和 `@featureany` 指令：

```blade
@feature('site-redesign')
    <!-- “site-redesign” 功能处于激活状态 -->
@else
    <!-- “site-redesign” 功能未激活 -->
@endfeature

@featureany(['site-redesign', 'beta'])
    <!-- “site-redesign” 或 “beta” 功能处于激活状态 -->
@endfeatureany
```

### 中间件（Middleware）

Pennant 还包含一个 [中间件](/docs/laravel/12.x/middleware)，可在调用路由之前验证当前已认证用户是否具有访问某个功能的权限。
你可以将此中间件分配给路由，并指定访问该路由所需的功能。
如果当前认证用户的任一指定功能未激活，则该路由将返回 `400 Bad Request` HTTP 响应。
可以通过静态方法 `using` 传入多个功能名称：

```php
use Illuminate\Support\Facades\Route;
use Laravel\Pennant\Middleware\EnsureFeaturesAreActive;

Route::get('/api/servers', function () {
    // ...
})->middleware(EnsureFeaturesAreActive::using('new-api', 'servers-api'));
```



#### 自定义响应（Customizing the Response）

如果你希望在中间件检测到某个指定功能未激活时自定义返回的响应，可以使用 `EnsureFeaturesAreActive` 中间件提供的 `whenInactive` 方法。
通常，这个方法应在应用的某个服务提供者（Service Provider）的 `boot` 方法中调用：

```php
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Laravel\Pennant\Middleware\EnsureFeaturesAreActive;

/**
 * 启动应用服务。
 */
public function boot(): void
{
    EnsureFeaturesAreActive::whenInactive(
        function (Request $request, array $features) {
            return new Response(status: 403);
        }
    );

    // ...
}
```

### 拦截功能检查（Intercepting Feature Checks）

有时，在获取某个功能的存储值之前执行一些内存检查会非常有用。
想象一下，你正在开发一个通过功能标志控制的新 API，并且希望在不丢失任何已解析的功能值的情况下，能够暂时禁用这个新 API。
例如，当你在新 API 中发现了一个 Bug 时，可以轻松地为除内部团队成员外的所有用户禁用该功能，修复 Bug 后，再重新启用该功能给原先有访问权限的用户。

你可以通过 [基于类的功能（class-based feature）](#class-based-features) 的 `before` 方法实现这一点。
当存在 `before` 方法时，它会在检索存储值之前始终在内存中运行。
如果该方法返回了一个非 `null` 的值，那么此值将在本次请求期间替代存储中的功能值：

```php
<?php

namespace App\Features;

use App\Models\User;
use Illuminate\Support\Facades\Config;
use Illuminate\Support\Lottery;

class NewApi
{
    /**
     * 在检索存储值之前，运行始终驻留于内存中的检查。
     */
    public function before(User $user): mixed
    {
        if (Config::get('features.new-api.disabled')) {
            return $user->isInternalTeamMember();
        }
    }

    /**
     * 解析功能的初始值。
     */
    public function resolve(User $user): mixed
    {
        return match (true) {
            $user->isInternalTeamMember() => true,
            $user->isHighTrafficCustomer() => false,
            default => Lottery::odds(1 / 100),
        };
    }
}
```



你也可以利用这个功能来**安排一个此前受功能标志（feature flag）控制的功能的全局发布**：

```php
<?php

namespace App\Features;

use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\Config;

class NewApi
{
    /**
     * 在检索存储值之前运行始终驻留于内存中的检查。
     */
    public function before(User $user): mixed
    {
        if (Config::get('features.new-api.disabled')) {
            return $user->isInternalTeamMember();
        }

        if (Carbon::parse(Config::get('features.new-api.rollout-date'))->isPast()) {
            return true;
        }
    }

    // ...
}
```

### 内存缓存（In-Memory Cache）

在检查某个功能时，Pennant 会创建一个**内存缓存**来保存结果。
如果你使用的是 `database` 驱动，那么在同一个请求中重复检查相同的功能标志，将**不会触发额外的数据库查询**。
这同时也确保了该功能在整个请求周期内返回的结果保持一致。

如果你需要手动清空内存缓存，可以使用 `Feature` facade 提供的 `flushCache` 方法：

```php
Feature::flushCache();
```

## 范围（Scope）

### 指定范围（Specifying the Scope）

如前所述，功能通常是针对**当前已认证的用户**进行检查的。
然而，这并不总是符合你的需求。
因此，你可以通过 `Feature` facade 的 `for` 方法，指定要检查功能的作用范围（scope）：

```php
return Feature::for($user)->active('new-api')
    ? $this->resolveNewApiResponse($request)
    : $this->resolveLegacyApiResponse($request);
```

当然，功能的作用范围不仅限于“用户”。
想象一下，你构建了一个**新的账单系统体验**，并且希望按团队（team）而不是按用户进行逐步发布。
也许你希望**创建时间较早的团队**比**新团队**获得更新的速度更慢。
你的功能解析闭包（resolution closure）可以像这样编写：

```php
use App\Models\Team;
use Carbon\Carbon;
use Illuminate\Support\Lottery;
use Laravel\Pennant\Feature;

Feature::define('billing-v2', function (Team $team) {
    if ($team->created_at->isAfter(new Carbon('1st Jan, 2023'))) {
        return true;
    }

    if ($team->created_at->isAfter(new Carbon('1st Jan, 2019'))) {
        return Lottery::odds(1 / 100);
    }

    return Lottery::odds(1 / 1000);
});
```



你会注意到，我们定义的闭包参数并不是 `User`，而是一个 `Team` 模型。
要判断某个功能对用户所属团队是否启用，你应该将团队对象传递给 `Feature` facade 提供的 `for` 方法：

```php
if (Feature::for($user->team)->active('billing-v2')) {
    return redirect('/billing/v2');
}

// ...
```

### 默认作用域（Default Scope）

你还可以自定义 Pennant 在检查功能时使用的**默认作用域（scope）**。
例如，假设你希望所有功能都基于当前已认证用户所属的团队进行检查，而不是用户本身。
与其每次都调用 `Feature::for($user->team)`，你可以直接将团队指定为默认作用域。
通常，这应在应用程序的某个 **服务提供者（Service Provider）** 中完成：

```php
<?php

namespace App\Providers;

use Illuminate\Support\Facades\Auth;
use Illuminate\Support\ServiceProvider;
use Laravel\Pennant\Feature;

class AppServiceProvider extends ServiceProvider
{
   /**
     * 启动任何应用服务。
     */
    public function boot(): void
    {
        Feature::resolveScopeUsing(fn ($driver) => Auth::user()?->team);

        // ...
    }
}
```

如果在检查功能时没有通过 `for` 方法显式指定作用域，
那么现在功能检查将默认使用“当前已认证用户的团队”作为作用域：

```php
Feature::active('billing-v2');

// 等价于：

Feature::for($user->team)->active('billing-v2');
```

### 可空作用域（Nullable Scope）

如果在检查功能时你传入的作用域是 `null`，
并且该功能的定义中**没有通过可空类型（nullable type）**或**联合类型中包含 `null`** 来支持 `null` 值，
那么 Pennant 会自动返回 `false` 作为该功能的结果值。



因此，如果你传递给某个功能的作用域（scope）**可能为 `null`**，并且你希望功能值解析器仍然能够被调用，那么你需要在功能定义中考虑这种情况。

当在 **Artisan 命令**、**队列任务（queued job）** 或 **未认证路由** 中检查功能时，作用域可能会为 `null`，
因为在这些上下文中通常没有已认证用户，所以默认作用域会是 `null`。

如果你并不总是会[显式指定功能作用域](#specifying-the-scope)，
那么你应确保作用域的类型是 **可空的（nullable）**，
并在功能定义逻辑中处理 `null` 作用域的情况：

```php
use App\Models\User;
use Illuminate\Support\Lottery;
use Laravel\Pennant\Feature;

// 原本：
// Feature::define('new-api', fn (User $user) => match (true) {

// 修改后：
Feature::define('new-api', fn (User|null $user) => match (true) {
    $user === null => true,
    $user->isInternalTeamMember() => true,
    $user->isHighTrafficCustomer() => false,
    default => Lottery::odds(1 / 100),
});
```

### 标识作用域（Identifying Scope）

Pennant 内置的 `array` 和 `database` 存储驱动，
能够正确地为所有 PHP 数据类型以及 Eloquent 模型存储作用域标识符（scope identifier）。

然而，如果你的应用使用了第三方的 Pennant 驱动，那么该驱动可能**不知道如何正确存储 Eloquent 模型或其他自定义类型**的标识符。

因此，Pennant 允许你通过在应用中作为作用域使用的对象上实现 `FeatureScopeable` 接口，
来自定义这些作用域值的存储格式。

例如，假设你在同一个应用中同时使用了两个不同的功能驱动：
内置的 `database` 驱动，以及一个名为 “Flag Rocket” 的第三方驱动。

“Flag Rocket” 驱动不知道如何存储 Eloquent 模型，
而是需要一个 `FlagRocketUser` 实例。

通过实现 `FeatureScopeable` 接口中定义的 `toFeatureIdentifier` 方法，
我们可以为应用中使用的每个驱动自定义可存储的作用域值：

```php
<?php

namespace App\Models;

use FlagRocket\FlagRocketUser;
use Illuminate\Database\Eloquent\Model;
use Laravel\Pennant\Contracts\FeatureScopeable;

class User extends Model implements FeatureScopeable
{
    /**
     * 将对象转换为给定驱动可存储的功能作用域标识符。
     */
    public function toFeatureIdentifier(string $driver): mixed
    {
        return match($driver) {
            'database' => $this,
            'flag-rocket' => FlagRocketUser::fromId($this->flag_rocket_id),
        };
    }
}
```



### 序列化作用域（Serializing Scope）

默认情况下，Pennant 在存储与 Eloquent 模型关联的功能时，会使用模型的完整类名。如果你已经使用了 [Eloquent morph map](/docs/laravel/12.x/eloquent-relationships#custom-polymorphic-types)，你可以让 Pennant 也使用 morph map，以便将存储的功能与应用结构解耦。

实现方法是在服务提供者中定义 Eloquent morph map 后，调用 `Feature` facade 的 `useMorphMap` 方法：

```php
use Illuminate\Database\Eloquent\Relations\Relation;
use Laravel\Pennant\Feature;

Relation::enforceMorphMap([
    'post' => 'App\Models\Post',
    'video' => 'App\Models\Video',
]);

Feature::useMorphMap();
```

## 丰富功能值（Rich Feature Values）

到目前为止，我们展示的功能主要是二元状态，即“激活”或“未激活”。然而，Pennant 也允许存储**丰富的功能值**。

例如，假设你正在测试应用中“立即购买”按钮的三种新颜色。你可以在功能定义中返回一个字符串，而不是 `true` 或 `false`：

```php
use Illuminate\Support\Arr;
use Laravel\Pennant\Feature;

Feature::define('purchase-button', fn (User $user) => Arr::random([
    'blue-sapphire',
    'seafoam-green',
    'tart-orange',
]));
```

你可以使用 `value` 方法获取 `purchase-button` 功能的值：

```php
$color = Feature::value('purchase-button');
```

Pennant 提供的 Blade 指令也可以方便地根据当前功能值条件渲染内容：

```blade
@feature('purchase-button', 'blue-sapphire')
    <!-- 'blue-sapphire' 被激活 -->
@elsefeature('purchase-button', 'seafoam-green')
    <!-- 'seafoam-green' 被激活 -->
@elsefeature('purchase-button', 'tart-orange')
    <!-- 'tart-orange' 被激活 -->
@endfeature
```

> [!注意]
> 使用丰富功能值时，需要注意：当功能值不是 `false` 时，该功能被视为“激活”。



当调用条件方法 [`when`](#conditional-execution) 时，功能（feature）的**完整值（rich value）** 会被传递给第一个闭包参数：

```php
Feature::when('purchase-button',
    fn ($color) => /* ... */,
    fn () => /* ... */,
);
```

同样地，当调用条件方法 `unless` 时，功能的完整值会被传递给**第二个可选闭包**：

```php
Feature::unless('purchase-button',
    fn () => /* ... */,
    fn ($color) => /* ... */,
);
```

## 获取多个功能（Retrieving Multiple Features）

`values` 方法允许你为某个作用域（scope）一次性获取多个功能的值：

```php
Feature::values(['billing-v2', 'purchase-button']);

// [
//     'billing-v2' => false,
//     'purchase-button' => 'blue-sapphire',
// ]
```

或者，你可以使用 `all` 方法，获取当前作用域下**所有已定义功能**的值：

```php
Feature::all();

// [
//     'billing-v2' => false,
//     'purchase-button' => 'blue-sapphire',
//     'site-redesign' => true,
// ]
```

不过，需要注意的是：**基于类（class-based）的功能** 是动态注册的。
Pennant 在功能被**首次检查（checked）** 之前，并不知道这些功能的存在。
因此，如果某个类功能在当前请求中尚未被检查过，它可能不会出现在 `all` 方法的返回结果中。

如果你希望在调用 `all` 方法时始终包含这些类功能（无论它们是否被检查过），
可以启用 **Pennant 的功能自动发现（feature discovery）** 能力。

要启用自动发现，请在应用的某个服务提供者（Service Provider）中调用 `discover` 方法：

```php
<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Laravel\Pennant\Feature;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 启动任何应用服务。
     */
    public function boot(): void
    {
        Feature::discover();

        // ...
    }
}
```

`discover` 方法会自动注册应用中 `app/Features` 目录下的所有功能类。
此后，即使这些类功能在当前请求中尚未被检查过，
`all` 方法的返回结果中也会包含它们：

```php
Feature::all();

// [
//     'App\Features\NewApi' => true,
//     'billing-v2' => false,
//     'purchase-button' => 'blue-sapphire',
//     'site-redesign' => true,
// ]
```



## 预加载（Eager Loading）

尽管 Pennant 会在单次请求中对所有解析过的功能保持内存缓存，但在某些情况下仍可能出现性能问题。为了解决这个问题，Pennant 提供了**预加载（eager load）**功能值的能力。

例如，假设我们在循环中检查某个功能是否激活：

```php
use Laravel\Pennant\Feature;

foreach ($users as $user) {
    if (Feature::for($user)->active('notifications-beta')) {
        $user->notify(new RegistrationSuccess);
    }
}
```

如果使用的是数据库驱动，上述代码会对每个用户执行一次数据库查询——可能执行上百次查询。
然而，使用 Pennant 的 `load` 方法，可以通过为用户或作用域集合预加载功能值来消除这一潜在的性能瓶颈：

```php
Feature::for($users)->load(['notifications-beta']);

foreach ($users as $user) {
    if (Feature::for($user)->active('notifications-beta')) {
        $user->notify(new RegistrationSuccess);
    }
}
```

如果你只想加载尚未加载过的功能值，可以使用 `loadMissing` 方法：

```php
Feature::for($users)->loadMissing([
    'new-api',
    'purchase-button',
    'notifications-beta',
]);
```

你也可以使用 `loadAll` 方法加载所有已定义的功能：

```php
Feature::for($users)->loadAll();
```

## 更新功能值（Updating Values）

当功能值首次被解析时，底层驱动会将结果存储到存储器中。
这通常是为了确保用户在多次请求中的体验一致。不过，有时你可能希望手动更新功能的存储值。

为此，你可以使用 `activate` 和 `deactivate` 方法，将功能“开启”或“关闭”：

```php
use Laravel\Pennant\Feature;

// 为默认作用域激活功能...
Feature::activate('new-api');

// 为指定作用域（如用户团队）禁用功能...
Feature::for($user->team)->deactivate('billing-v2');
```



你也可以通过向 `activate` 方法提供第二个参数来手动设置功能的丰富值：

```php
Feature::activate('purchase-button', 'seafoam-green');
```

如果你希望 Pennant 忘记某个功能的存储值，可以使用 `forget` 方法。当该功能再次被检查时，Pennant 会根据功能定义重新解析其值：

```php
Feature::forget('purchase-button');
```

### 批量更新（Bulk Updates）

要批量更新存储的功能值，可以使用 `activateForEveryone` 和 `deactivateForEveryone` 方法。

例如，假设你已经确认 `new-api` 功能的稳定性，并确定了结账流程中 `'purchase-button'` 的最佳颜色，你可以相应地为所有用户更新存储值：

```php
use Laravel\Pennant\Feature;

Feature::activateForEveryone('new-api');

Feature::activateForEveryone('purchase-button', 'seafoam-green');
```

或者，你也可以为所有用户停用该功能：

```php
Feature::deactivateForEveryone('new-api');
```

> [!注意]
> 这只会更新由 Pennant 的存储驱动存储的已解析功能值。你还需要在应用中更新功能定义。

### 清除功能（Purging Features）

有时，将整个功能从存储中清除是有用的。通常在以下情况下需要这样做：

-   你已经从应用中移除了该功能

-   或者你修改了功能定义，并希望将新的定义应用到所有用户

可以使用 `purge` 方法移除某个功能的所有存储值：

```php
// 清除单个功能...
Feature::purge('new-api');

// 清除多个功能...
Feature::purge(['new-api', 'purchase-button']);
```



如果你想清除存储中的**所有**功能，可以在不传递任何参数的情况下调用 `purge` 方法

```php
Feature::purge();
```

由于在应用部署流水线中清除功能可能很有用，Pennant 提供了一个 `pennant:purge` Artisan 命令，用于从存储中清除指定的功能：

```shell
php artisan pennant:purge new-api

php artisan pennant:purge new-api purchase-button
```

你也可以清除除指定功能之外的所有功能。例如，如果你想清除所有功能，但保留 `"new-api"` 和 `"purchase-button"` 的值，可以使用 `--except` 选项：

```shell
php artisan pennant:purge --except=new-api --except=purchase-button
```

为了方便，`pennant:purge` 命令还支持 `--except-registered` 标志。此标志表示应清除所有功能，**除了那些在服务提供者中明确注册的功能**：

```shell
php artisan pennant:purge --except-registered
```

## 测试（Testing）

在测试与功能标志交互的代码时，控制功能标志返回值最简单的方法是重新定义该功能。例如，假设你在应用的某个服务提供者中定义了如下功能：

```php
use Illuminate\Support\Arr;
use Laravel\Pennant\Feature;

Feature::define('purchase-button', fn () => Arr::random([
    'blue-sapphire',
    'seafoam-green',
    'tart-orange',
]));
```

为了在测试中修改功能的返回值，可以在测试开始时重新定义该功能。即使服务提供者中仍使用 `Arr::random()` 实现，以下测试也会始终通过：

```php tab=Pest
use Laravel\Pennant\Feature;

test('it can control feature values', function () {
    Feature::define('purchase-button', 'seafoam-green');

    expect(Feature::value('purchase-button'))->toBe('seafoam-green');
});
```

```php tab=PHPUnit
use Laravel\Pennant\Feature;

public function test_it_can_control_feature_values()
{
    Feature::define('purchase-button', 'seafoam-green');

    $this->assertSame('seafoam-green', Feature::value('purchase-button'));
}
```



同样的方法也可用于基于类的功能（class based features）：

```php tab=Pest
use Laravel\Pennant\Feature;

test('它可以控制功能值', function () {
    Feature::define(NewApi::class, true);

    expect(Feature::value(NewApi::class))->toBeTrue();
});
```

```php tab=PHPUnit
use App\Features\NewApi;
use Laravel\Pennant\Feature;

public function test_it_can_control_feature_values()
{
    Feature::define(NewApi::class, true);

    $this->assertTrue(Feature::value(NewApi::class));
}
```

如果你的功能（feature）返回一个 `Lottery` 实例，那么有一些有用的[测试辅助函数](/docs/laravel/12.x/helpers#testing-lotteries)可供使用。

#### 存储配置（Store Configuration）

你可以在应用的 `phpunit.xml` 文件中定义 `PENNANT_STORE` 环境变量，以配置 Pennant 在测试期间使用的存储方式：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<phpunit colors="true">
    <!-- ... -->
    <php>
        <env name="PENNANT_STORE" value="array"/>
        <!-- ... -->
    </php>
</phpunit>
```

## 添加自定义 Pennant 驱动（Adding Custom Pennant Drivers）

#### 实现驱动（Implementing the Driver）

如果 Pennant 现有的存储驱动都不适合你的应用需求，你可以编写自己的存储驱动。
你的自定义驱动应实现 `Laravel\Pennant\Contracts\Driver` 接口：

```php
<?php

namespace App\Extensions;

use Laravel\Pennant\Contracts\Driver;

class RedisFeatureDriver implements Driver
{
    public function define(string $feature, callable $resolver): void {}
    public function defined(): array {}
    public function getAll(array $features): array {}
    public function get(string $feature, mixed $scope): mixed {}
    public function set(string $feature, mixed $scope, mixed $value): void {}
    public function setForAllScopes(string $feature, mixed $value): void {}
    public function delete(string $feature, mixed $scope): void {}
    public function purge(array|null $features): void {}
}
```



现在，我们只需要使用 Redis 连接来实现这些方法即可。
关于如何实现这些方法的示例，你可以查看 [Pennant 源码中的 `Laravel\Pennant\Drivers\DatabaseDriver`](https://github.com/laravel/pennant/blob/1.x/src/Drivers/DatabaseDriver.php)。

> [!注意]
> Laravel 默认不会附带一个专门用于存放扩展（extensions）的目录。
> 你可以将它们放在任意位置。
> 在本示例中，我们创建了一个 `Extensions` 目录来存放 `RedisFeatureDriver`。

#### 注册驱动（Registering the Driver）

当你的驱动实现完成后，你就可以将它注册到 Laravel 中了。
要为 Pennant 添加额外的驱动，可以使用 `Feature` facade 提供的 `extend` 方法。
你应当在应用程序的某个[服务提供者](/docs/laravel/12.x/providers)的 `boot` 方法中调用该方法：

```php
<?php

namespace App\Providers;

use App\Extensions\RedisFeatureDriver;
use Illuminate\Contracts\Foundation\Application;
use Illuminate\Support\ServiceProvider;
use Laravel\Pennant\Feature;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 注册应用的所有服务。
     */
    public function register(): void
    {
        // ...
    }

    /**
     * 启动应用的所有服务。
     */
    public function boot(): void
    {
        Feature::extend('redis', function (Application $app) {
            return new RedisFeatureDriver($app->make('redis'), $app->make('events'), []);
        });
    }
}
```

当驱动注册完成后，你就可以在应用的 `config/pennant.php` 配置文件中使用 `redis` 驱动：

```php
'stores' => [

    'redis' => [
        'driver' => 'redis',
        'connection' => null,
    ],

    // ...

],
```

### 外部定义功能（Defining Features Externally）

如果你的驱动是某个第三方功能开关平台的封装，那么你可能会在该平台上定义功能（features），而不是通过 Pennant 的 `Feature::define` 方法来定义。
如果是这种情况，你的自定义驱动还应实现 `Laravel\Pennant\Contracts\DefinesFeaturesExternally` 接口：

```php
<?php

namespace App\Extensions;

use Laravel\Pennant\Contracts\Driver;
use Laravel\Pennant\Contracts\DefinesFeaturesExternally;

class FeatureFlagServiceDriver implements Driver, DefinesFeaturesExternally
{
    /**
     * 获取给定作用域下定义的功能。
     */
    public function definedFeaturesForScope(mixed $scope): array {}

    /* ... */
}
```



`definedFeaturesForScope` 方法应返回为指定作用域定义的功能名称列表。

## 事件（Events）

Pennant 会分发多种事件，这些事件在跟踪应用程序中的功能开关（feature flags）时非常有用。

### `Laravel\Pennant\Events\FeatureRetrieved`

每当[检查功能](#checking-features)时，都会触发此事件。
该事件可用于创建并跟踪某个功能开关在应用中的使用指标。

### `Laravel\Pennant\Events\FeatureResolved`

当某个功能在特定作用域中第一次解析其值时，会触发此事件。

### `Laravel\Pennant\Events\UnknownFeatureResolved`

当某个未知功能在特定作用域中第一次被解析时，会触发此事件。
监听该事件在以下情况下特别有用：当你本打算移除某个功能开关，但在应用程序的某些地方仍然遗留了对此功能的引用。

```php
<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Facades\Event;
use Illuminate\Support\Facades\Log;
use Laravel\Pennant\Events\UnknownFeatureResolved;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 启动任何应用服务。
     */
    public function boot(): void
    {
        Event::listen(function (UnknownFeatureResolved $event) {
            Log::error("正在解析未知功能 [{$event->feature}]。");
        });
    }
}
```

### `Laravel\Pennant\Events\DynamicallyRegisteringFeatureClass`

当某个[基于类的功能](#class-based-features)在请求期间首次被动态检查时，会触发此事件。

### `Laravel\Pennant\Events\UnexpectedNullScopeEncountered`

当一个 `null` 作用域被传递给一个[不支持 null 的功能定义](#nullable-scope)时，会触发此事件。

这种情况会被优雅地处理，功能将返回 `false`。
然而，如果你希望禁用这种默认的优雅行为，可以在应用的 `AppServiceProvider` 的 `boot` 方法中为该事件注册监听器：

```php
use Illuminate\Support\Facades\Log;
use Laravel\Pennant\Events\UnexpectedNullScopeEncountered;

/**
 * 启动任何应用服务。
 */
public function boot(): void
{
    Event::listen(UnexpectedNullScopeEncountered::class, fn () => abort(500));
}
```



### `Laravel\Pennant\Events\FeatureUpdated`

当为某个作用域更新功能时会触发此事件，通常通过调用 `activate` 或 `deactivate` 方法实现。

### `Laravel\Pennant\Events\FeatureUpdatedForAllScopes`

当为所有作用域更新功能时会触发此事件，通常通过调用 `activateForEveryone` 或 `deactivateForEveryone` 方法实现。

### `Laravel\Pennant\Events\FeatureDeleted`

当为某个作用域删除功能时会触发此事件，通常通过调用 `forget` 方法实现。

### `Laravel\Pennant\Events\FeaturesPurged`

当清除（purge）特定功能时会触发此事件。

### `Laravel\Pennant\Events\AllFeaturesPurged`

当清除所有功能时会触发此事件。
