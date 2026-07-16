# 上下文（Context）

-   [介绍](#introduction)
  -   [工作原理](#how-it-works)
-   [捕获上下文](#capturing-context)
  -   [上下文栈（Stacks）](#stacks)
-   [检索上下文](#retrieving-context)
  -   [判断条目是否存在](#determining-item-existence)
-   [移除上下文](#removing-context)
-   [隐藏上下文](#hidden-context)
-   [事件](#events)
  -   [反序列化（Dehydrating）](#dehydrating)
  -   [序列化完成（Hydrated）](#hydrated)

## 介绍

Laravel 的“上下文（context）”功能使你能够在应用程序中执行的请求、任务（jobs）和命令中捕获、检索并共享信息。
这些捕获到的信息也会包含在你的应用程序写入的日志中，这让你能够更深入地了解在日志条目被写入之前发生的周边代码执行历史，并允许你跟踪分布式系统中的执行流程。


### 工作原理

理解 Laravel 上下文功能的最好方法是通过内置的日志功能来实际演示。要开始，你可以使用 `Context` facade 向上下文中[添加信息](#capturing-context)。在这个示例中，我们将使用一个 [middleware](/docs/laravel/12.x/middleware) 在每个传入请求时向上下文中添加请求 URL 和一个唯一的 trace ID：


```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Context;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

class AddContext
{
    /**
     * 处理一个传入请求。
     */
    public function handle(Request $request, Closure $next): Response
    {
        Context::add('url', $request->url());
        Context::add('trace_id', Str::uuid()->toString());

        return $next($request);
    }
}
```

添加到上下文的信息会自动作为元数据附加到在整个请求过程中写入的任何[日志条目](/docs/laravel/12.x/logging)上。将上下文作为元数据附加允许传递给单个日志条目的信息与通过 `Context` 共享的信息区分开。例如，假设我们写下以下日志条目：

```php
Log::info('User authenticated.', ['auth_id' => Auth::id()]);
```



写入的日志将包含传递给日志条目的 `auth_id`，但它也会将上下文中的 `url` 和 `trace_id` 作为元数据包含在内：

```text
User authenticated. {"auth_id":27} {"url":"https://example.com/login","trace_id":"e04e1a11-e75c-4db3-b5b5-cfef4ef56697"}
```

添加到上下文中的信息也可以在派发到队列的任务中使用。例如，假设我们在向上下文添加一些信息后，将 `ProcessPodcast` 任务派发到队列：

```php
// 在我们的 middleware 中...
Context::add('url', $request->url());
Context::add('trace_id', Str::uuid()->toString());

// 在我们的控制器中...
ProcessPodcast::dispatch($podcast);
```

当任务被派发时，当前存储在上下文中的任何信息都会被捕获并共享给该任务。捕获的信息在任务执行时会被重新注入到当前上下文中。因此，如果我们的任务的 handle 方法写入日志：

```php
class ProcessPodcast implements ShouldQueue
{
    use Queueable;

    // ...

    /**
     * 执行任务。
     */
    public function handle(): void
    {
        Log::info('Processing podcast.', [
            'podcast_id' => $this->podcast->id,
        ]);

        // ...
    }
}
```

生成的日志条目将包含在最初派发任务的请求期间添加到上下文中的信息：

```text
Processing podcast. {"podcast_id":95} {"url":"https://example.com/login","trace_id":"e04e1a11-e75c-4db3-b5b5-cfef4ef56697"}
```

尽管我们主要关注了 Laravel 上下文的内置日志相关功能，以下文档将演示上下文如何允许你在 HTTP 请求与队列任务之间共享信息，甚至如何添加[隐藏上下文数据](#hidden-context)，这些数据不会与日志条目一起写入。



<a name="capturing-context"></a>
## 捕获上下文

使用 `Context` 门面的 `add` 方法，你可以在当前上下文中存储信息：

```php
use Illuminate\Support\Facades\Context;

Context::add('key', 'value');
```

要一次添加多个项目，你可以将关联数组传递给 `add` 方法：

```php
Context::add([
    'first_key' => 'value',
    'second_key' => 'value',
]);
```

该 `add` 方法将覆盖共享同一个键名的现有值。如果你只想将还不存在键名的信息添加到上下文中，你可以使用 `addIf` 方法：

```php
Context::add('key', 'first');

Context::get('key');
// "first"

Context::addIf('key', 'second');

Context::get('key');
// "first"
```

上下文还提供了递增或递减的方法。这两种方法都至少接受一个参数：要跟踪的键。可以提供第二个参数来指定该键应递增或递减的量：

```php
Context::increment('records_added');
Context::increment('records_added', 5);

Context::decrement('records_added');
Context::decrement('records_added', 5);
```

<a name="conditional-context"></a>
#### 条件上下文

`when` 方法可以用于基于给定条件将数据添加到上下文中。如果给定的条件等于 `true`，`when` 方法中的第一个闭包将被调用；而如果给定的条件等于 `false`，则会调用第二个闭包：

```php
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Context;

Context::when(
    Auth::user()->isAdmin(),
    fn ($context) => $context->add('permissions', Auth::user()->permissions),
    fn ($context) => $context->add('permissions', []),
);
```



#### 作用域上下文（Scoped Context）

`scope` 方法提供了一种在执行给定回调期间临时修改上下文的方法，并在回调执行完毕后将上下文恢复到原始状态。此外，你可以在闭包执行期间传入应合并到上下文中的额外数据（作为第二和第三个参数）。

```php
use Illuminate\Support\Facades\Context;
use Illuminate\Support\Facades\Log;

Context::add('trace_id', 'abc-999');
Context::addHidden('user_id', 123);

Context::scope(
    function () {
        Context::add('action', 'adding_friend');

        $userId = Context::getHidden('user_id');

        Log::debug("Adding user [{$userId}] to friends list.");
        // Adding user [987] to friends list.  {"trace_id":"abc-999","user_name":"taylor_otwell","action":"adding_friend"}
    },
    data: ['user_name' => 'taylor_otwell'],
    hidden: ['user_id' => 987],
);

Context::all();
// [
//     'trace_id' => 'abc-999',
// ]

Context::allHidden();
// [
//     'user_id' => 123,
// ]
```

> [!注意]
> 如果上下文中的对象在作用域闭包内部被修改，该修改也会反映到作用域外。

### 栈（Stacks）

上下文提供了创建“栈”的能力，即按添加顺序存储的数据列表。你可以通过调用 `push` 方法向栈中添加信息：

```php
use Illuminate\Support\Facades\Context;

Context::push('breadcrumbs', 'first_value');

Context::push('breadcrumbs', 'second_value', 'third_value');

Context::get('breadcrumbs');
// [
//     'first_value',
//     'second_value',
//     'third_value',
// ]
```

栈可以用于捕获请求的历史信息，例如应用程序中发生的事件。举例来说，你可以创建一个事件监听器，每次执行查询时向栈中推送数据，捕获查询的 SQL 和执行时间：

```php
use Illuminate\Support\Facades\Context;
use Illuminate\Support\Facades\DB;

// In AppServiceProvider.php...
DB::listen(function ($event) {
    Context::push('queries', [$event->time, $event->sql]);
});
```



你可以使用 `stackContains` 和 `hiddenStackContains` 方法来判断某个值是否存在于栈中：

```php
if (Context::stackContains('breadcrumbs', 'first_value')) {
    //
}

if (Context::hiddenStackContains('secrets', 'first_value')) {
    //
}
```

`stackContains` 和 `hiddenStackContains` 方法也可以接受一个闭包作为第二个参数，从而更灵活地控制值的比较操作：

```php
use Illuminate\Support\Facades\Context;
use Illuminate\Support\Str;

return Context::stackContains('breadcrumbs', function ($value) {
    return Str::startsWith($value, 'query_');
});
```

## 获取上下文信息（Retrieving Context）

你可以使用 `Context` facade 的 `get` 方法从上下文中获取信息：

```php
use Illuminate\Support\Facades\Context;

$value = Context::get('key');
```

`only` 和 `except` 方法可用于获取上下文中的部分信息：

```php
$data = Context::only(['first_key', 'second_key']);

$data = Context::except(['first_key']);
```

`pull` 方法可用于从上下文中获取信息的同时，将其立即移除：

```php
$value = Context::pull('key');
```

如果上下文数据存储在 [栈](#stacks) 中，你可以使用 `pop` 方法从栈中弹出元素：

```php
Context::push('breadcrumbs', 'first_value', 'second_value');

Context::pop('breadcrumbs');
// second_value

Context::get('breadcrumbs');
// ['first_value']
```

如果你想获取上下文中存储的所有信息，可以调用 `all` 方法：

```php
$data = Context::all();
```

### 判断键是否存在（Determining Item Existence）

你可以使用 `has` 和 `missing` 方法来判断上下文中是否存在指定键的值：

```php
use Illuminate\Support\Facades\Context;

if (Context::has('key')) {
    // ...
}

if (Context::missing('key')) {
    // ...
}
```



`has` 方法会返回 `true`，无论存储的值是什么。例如，即使键对应的值为 `null`，它仍然会被认为存在：

```php
Context::add('key', null);

Context::has('key');
// true
```

## 删除上下文


`forget` 方法可用于从当前上下文中移除指定键及其对应的值：

```php
use Illuminate\Support\Facades\Context;

Context::add(['first_key' => 1, 'second_key' => 2]);

Context::forget('first_key');

Context::all();

// ['second_key' => 2]
```

如果需要一次删除多个键，可以传入一个数组：

```php
Context::forget(['first_key', 'second_key']);
```

## 隐藏上下文

Context 提供存储“隐藏”数据的功能。隐藏数据不会被附加到日志中，也无法通过常规的数据检索方法访问。你可以使用 Context 提供的专用方法来操作隐藏数据：

```php
use Illuminate\Support\Facades\Context;

Context::addHidden('key', 'value');

Context::getHidden('key');
// 'value'

Context::get('key');
// null
```

隐藏方法的功能与常规方法类似：

```php
Context::addHidden(/* ... */);
Context::addHiddenIf(/* ... */);
Context::pushHidden(/* ... */);
Context::getHidden(/* ... */);
Context::pullHidden(/* ... */);
Context::popHidden(/* ... */);
Context::onlyHidden(/* ... */);
Context::exceptHidden(/* ... */);
Context::allHidden(/* ... */);
Context::hasHidden(/* ... */);
Context::missingHidden(/* ... */);
Context::forgetHidden(/* ... */);
```

## 事件

Context 会触发两个事件，这允许你在上下文的“水化”（hydration）和“去水化”（dehydration）过程中进行钩子操作。

为了说明这些事件的用法，假设在你的应用程序的中间件中，你根据传入 HTTP 请求的 `Accept-Language` 头设置了 `app.locale` 配置值。Context 的事件允许你在请求期间捕获这个值，并在队列中恢复它，从而确保队列发送的通知具有正确的 `app.locale` 值。我们可以使用 Context 的事件和[隐藏](#hidden-context)数据来实现这一点，下面的文档会对此进行说明。




### 去水化（Dehydrating）

每当一个任务被派发到队列时，上下文中的数据会被“去水化”（dehydrated），并与任务的负载一起捕获。`Context::dehydrating` 方法允许你注册一个闭包，该闭包会在去水化过程中被调用。在这个闭包中，你可以对将与队列任务共享的数据进行修改。

通常，你应该在应用程序的 `AppServiceProvider` 类的 `boot` 方法中注册 `dehydrating` 回调：

```php
use Illuminate\Log\Context\Repository;
use Illuminate\Support\Facades\Config;
use Illuminate\Support\Facades\Context;

/**
 * 启动任何应用服务
 */
public function boot(): void
{
    Context::dehydrating(function (Repository $context) {
        $context->addHidden('locale', Config::get('app.locale'));
    });
}
```

> [!注意]
> 不应在 `dehydrating` 回调中使用 `Context` 门面（facade），因为那会改变当前进程的上下文。确保只修改传入回调的仓库（repository）。

### 水化

每当队列任务开始在队列中执行时，之前共享给任务的上下文会被“水化”（hydrated）回当前上下文。`Context::hydrated` 方法允许你注册一个闭包，该闭包会在水化过程中被调用。

通常，你应该在应用程序的 `AppServiceProvider` 类的 `boot` 方法中注册 `hydrated` 回调：

```php
use Illuminate\Log\Context\Repository;
use Illuminate\Support\Facades\Config;
use Illuminate\Support\Facades\Context;

/**
 * Bootstrap any application services.
 */
public function boot(): void
{
    Context::hydrated(function (Repository $context) {
        if ($context->hasHidden('locale')) {
            Config::set('app.locale', $context->getHidden('locale'));
        }
    });
}
```

> [!注意]
> 不应在 `hydrated` 回调中使用 `Context` 门面，而应确保只修改传入回调的仓库（repository）。
