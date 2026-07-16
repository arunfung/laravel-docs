# 上下文（Context）

- [介绍](#introduction)
    - [工作原理](#how-it-works)
- [捕获上下文](#capturing-context)
    - [栈](#stacks)
- [检索上下文](#retrieving-context)
    - [判断条目是否存在](#determining-item-existence)
- [移除上下文](#removing-context)
- [隐藏上下文](#hidden-context)
- [事件](#events)
    - [去水化](#dehydrating)
    - [水化完成](#hydrated)

<a name="introduction"></a>
## 介绍

Laravel 的“上下文（context）”功能使你能够在应用程序执行的请求、任务和命令中捕获、检索并共享信息。这些捕获到的信息也会包含在应用程序写入的日志中，让你能够更深入地了解日志条目写入前的相关代码执行历史，并跟踪分布式系统中的执行流程。

<a name="how-it-works"></a>
### 工作原理

理解 Laravel 上下文功能的最好方法，是通过内置的日志功能查看其实际运作方式。首先，可以使用 `Context` 门面向上下文中[添加信息](#capturing-context)。在本例中，我们将使用[中间件](/docs/{{version}}/middleware)，在每个传入请求中将请求 URL 和唯一的追踪 ID 添加到上下文：

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

添加到上下文的信息会自动作为元数据附加到整个请求期间写入的所有[日志条目](/docs/{{version}}/logging)中。将上下文作为元数据附加，可以把传递给单个日志条目的信息与通过 `Context` 共享的信息区分开来。例如，假设我们写入以下日志条目：

```php
Log::info('User authenticated.', ['auth_id' => Auth::id()]);
```

写入的日志将包含传递给日志条目的 `auth_id`，同时也会将上下文中的 `url` 和 `trace_id` 作为元数据包含在内：

```text
User authenticated. {"auth_id":27} {"url":"https://example.com/login","trace_id":"e04e1a11-e75c-4db3-b5b5-cfef4ef56697"}
```

添加到上下文中的信息也可以在派发到队列的任务中使用。例如，假设我们在向上下文添加一些信息后，将 `ProcessPodcast` 任务派发到队列：

```php
// 在中间件中...
Context::add('url', $request->url());
Context::add('trace_id', Str::uuid()->toString());

// 在控制器中...
ProcessPodcast::dispatch($podcast);
```

当任务被派发时，当前存储在上下文中的所有信息都会被捕获并共享给该任务。捕获的信息会在任务执行时重新注入当前上下文。因此，如果任务的 `handle` 方法写入日志：

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

尽管我们主要介绍了 Laravel 上下文内置的日志相关功能，接下来的文档将说明如何通过上下文跨越 HTTP 请求与队列任务的边界共享信息，以及如何添加不会写入日志条目的[隐藏上下文数据](#hidden-context)。

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

`add` 方法会覆盖具有相同键名的任何现有值。如果只希望在键尚不存在时向上下文添加信息，可以使用 `addIf` 方法：

```php
Context::add('key', 'first');

Context::get('key');
// "first"

Context::addIf('key', 'second');

Context::get('key');
// "first"
```

上下文还提供了用于递增或递减指定键的便捷方法。这两个方法都至少接受一个参数：要跟踪的键。还可以提供第二个参数，指定该键递增或递减的数值：

```php
Context::increment('records_added');
Context::increment('records_added', 5);

Context::decrement('records_added');
Context::decrement('records_added', 5);
```

<a name="conditional-context"></a>
#### 条件上下文

`when` 方法可根据给定条件向上下文添加数据。如果给定条件求值为 `true`，则调用传给 `when` 方法的第一个闭包；如果求值为 `false`，则调用第二个闭包：

```php
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Context;

Context::when(
    Auth::user()->isAdmin(),
    fn ($context) => $context->add('permissions', Auth::user()->permissions),
    fn ($context) => $context->add('permissions', []),
);
```

<a name="scoped-context"></a>
#### 作用域上下文（Scoped Context）

`scope` 方法可以在执行给定回调期间临时修改上下文，并在回调执行完毕后将上下文恢复到原始状态。此外，还可以通过第二个和第三个参数传入额外数据，在闭包执行期间将其合并到上下文中。

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

> [!WARNING]
> 如果在作用域闭包内部修改了上下文中的对象，该修改也会反映到作用域外。

<a name="stacks"></a>
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

栈可用于捕获请求的历史信息，例如应用程序中发生的事件。举例来说，可以创建一个事件监听器，在每次执行查询时将数据推入栈中，以元组形式捕获查询 SQL 和执行时长：

```php
use Illuminate\Support\Facades\Context;
use Illuminate\Support\Facades\DB;

// 在 AppServiceProvider.php 中...
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

<a name="retrieving-context"></a>
## 获取上下文信息（Retrieving Context）

可以使用 `Context` 门面的 `get` 方法从上下文中获取信息：

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

如果上下文数据存储在[栈](#stacks)中，可以使用 `pop` 方法从栈中弹出元素：

```php
Context::push('breadcrumbs', 'first_value', 'second_value');

Context::pop('breadcrumbs');
// second_value

Context::get('breadcrumbs');
// ['first_value']
```

`remember` 和 `rememberHidden` 方法可用于从上下文中检索信息。如果请求的信息不存在，则会将给定闭包的返回值设置为上下文值：

```php
$permissions = Context::remember(
    'user-permissions',
    fn () => $user->permissions,
);
```

如果你想获取上下文中存储的所有信息，可以调用 `all` 方法：

```php
$data = Context::all();
```

<a name="determining-item-existence"></a>
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

无论存储的值是什么，`has` 方法都会返回 `true`。例如，即使键对应的值为 `null`，该键仍会被视为存在：

```php
Context::add('key', null);

Context::has('key');
// true
```

<a name="removing-context"></a>
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

<a name="hidden-context"></a>
## 隐藏上下文

上下文还可以存储“隐藏”数据。隐藏数据不会附加到日志中，也无法通过上述常规数据检索方法访问。`Context` 提供了另一组方法来操作隐藏的上下文信息：

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

<a name="events"></a>
## 事件

上下文会分派两个事件，让你可以在上下文的“水化”（hydration）和“去水化”（dehydration）过程中执行相应操作。

为了说明这些事件的用法，假设应用程序的中间件根据传入 HTTP 请求的 `Accept-Language` 标头设置了 `app.locale` 配置值。上下文事件允许你在请求期间捕获该值，并在队列中恢复它，从而确保队列发送的通知使用正确的 `app.locale` 值。我们可以结合上下文事件和[隐藏](#hidden-context)数据来实现这一点，下面的文档将对此进行说明。

<a name="dehydrating"></a>
### 去水化（Dehydrating）

每当任务被分派到队列时，上下文中的数据都会被“去水化”（dehydrated），并与任务负载一起被捕获。`Context::dehydrating` 方法允许你注册一个在去水化过程中调用的闭包。在该闭包中，可以修改将与队列任务共享的数据。

通常，你应该在应用程序的 `AppServiceProvider` 类的 `boot` 方法中注册 `dehydrating` 回调：

```php
use Illuminate\Log\Context\Repository;
use Illuminate\Support\Facades\Config;
use Illuminate\Support\Facades\Context;

/**
 * 引导任何应用程序服务。
 */
public function boot(): void
{
    Context::dehydrating(function (Repository $context) {
        $context->addHidden('locale', Config::get('app.locale'));
    });
}
```

> [!NOTE]
> 不应在 `dehydrating` 回调中使用 `Context` 门面，因为这会改变当前进程的上下文。请确保只修改传给回调的上下文仓库。

<a name="hydrated"></a>
### 水化完成

每当队列任务开始执行时，之前与任务共享的上下文都会被“水化”（hydrated）回当前上下文。`Context::hydrated` 方法允许你注册一个在水化过程中调用的闭包。

通常，你应该在应用程序的 `AppServiceProvider` 类的 `boot` 方法中注册 `hydrated` 回调：

```php
use Illuminate\Log\Context\Repository;
use Illuminate\Support\Facades\Config;
use Illuminate\Support\Facades\Context;

/**
 * 引导任何应用程序服务。
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

> [!NOTE]
> 不应在 `hydrated` 回调中使用 `Context` 门面。请确保只修改传给回调的上下文仓库。
