
# Mocking

- [简介](#introduction)
- [模拟对象](#mocking-objects)
- [模拟 Facade](#mocking-facades)
    - [Facade 监视器](#facade-spies)
- [与时间交互](#interacting-with-time)

## 简介

在测试 Laravel 应用时，你可能希望「模拟（mock）」应用的某些部分，防止它们在测试过程中实际执行。例如，当你测试某个会分发事件的控制器时，你可能并不希望事件监听器在测试中真正运行。这样做的好处是，你可以专注于测试控制器的 HTTP 响应，而把事件监听器的行为放在独立的测试用例中验证。

Laravel 提供了便捷的辅助方法，用于模拟事件、任务（job）、以及其他 Facade。底层这些功能仍依赖 Mockery，只不过 Laravel 对其进行了包装，简化了原本复杂的模拟调用。

## 模拟对象

当你需要模拟一个对象，并通过 Laravel 的 [服务容器](/docs/laravel/12.x/container) 注入到应用中时，必须将模拟对象**绑定为容器实例（`instance`）**。这样，Laravel 在依赖注入时就会使用你提供的模拟对象，而不是自动构造新的对象：

```php tab=Pest
use App\Service;
use Mockery;
use Mockery\MockInterface;

test('something can be mocked', function () {
    $this->instance(
        Service::class,
        Mockery::mock(Service::class, function (MockInterface $mock) {
            $mock->expects('process');
        })
    );
});
```

```php tab=PHPUnit
use App\Service;
use Mockery;
use Mockery\MockInterface;

public function test_something_can_be_mocked(): void
{
    $this->instance(
        Service::class,
        Mockery::mock(Service::class, function (MockInterface $mock) {
            $mock->expects('process');
        })
    );
}
```



为了进一步简化模拟操作，Laravel 的基础测试类提供了一个 `mock` 方法，可以更方便地创建模拟对象。下面这个例子与前面的绑定 `instance` 的示例效果相同：

```php
use App\Service;
use Mockery\MockInterface;

$mock = $this->mock(Service::class, function (MockInterface $mock) {
    $mock->expects('process');
});
```

如果你只需要模拟某个对象的部分方法，而希望其他方法在调用时照常执行，则可以使用 `partialMock` 方法：

```php
use App\Service;
use Mockery\MockInterface;

$mock = $this->partialMock(Service::class, function (MockInterface $mock) {
    $mock->expects('process');
});
```

此外，如果你希望对一个对象进行 [监视（spy）](http://docs.mockery.io/en/latest/reference/spies.html)，Laravel 的基础测试类也提供了便捷的 `spy` 方法，它是 `Mockery::spy` 的封装。Spy 与 Mock 类似，不同之处在于它**会记录对象在测试过程中的调用信息**，从而让你可以在代码执行完毕后再进行断言：

```php
use App\Service;

$spy = $this->spy(Service::class);

// ...

$spy->shouldHaveReceived('process');
```

## 模拟 Facade

与传统的静态方法调用不同，[Facade](/docs/laravel/12.x/facades)（包括 [实时 Facade](/docs/laravel/12.x/facades#real-time-facades)）是可以被模拟的。相较于传统的静态调用方式，这种做法带来了极大的测试优势，你可以像使用依赖注入一样灵活地进行测试。

在编写测试时，你可能会希望模拟控制器中调用的某个 Laravel Facade。例如，假设你有如下控制器动作：
```php
<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Cache;

class UserController extends Controller
{
    /**
     * 获取应用中的所有用户列表。
     */
    public function index(): array
    {
        $value = Cache::get('key');

        return [
            // ...
        ];
    }
}
```



我们可以使用 `expects` 方法来模拟对 `Cache` Facade 的调用。该方法会返回一个 [Mockery](https://github.com/padraic/mockery) 的模拟对象。由于 Laravel 中的 Facade 实际上是由 [服务容器](/docs/laravel/12.x/container) 解析与管理的，因此相比传统的静态类，它们拥有更高的可测试性。

例如，以下示例模拟了调用 `Cache` Facade 的 `get` 方法：
```php tab=Pest
<?php

use Illuminate\Support\Facades\Cache;

test('get index', function () {
    Cache::expects('get')
        ->with('key')
        ->andReturn('value');

    $response = $this->get('/users');

    // ...
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Illuminate\Support\Facades\Cache;
use Tests\TestCase;

class UserControllerTest extends TestCase
{
    public function test_get_index(): void
    {
        Cache::expects('get')
            ->with('key')
            ->andReturn('value');

        $response = $this->get('/users');

        // ...
    }
}
```

⚠️ **警告**
**不建议模拟 `Request` Facade。**如果你需要特定输入，应直接传入相应的参数到测试方法中，如 `get` 或 `post` 方法。
同理，也不应模拟 `Config` Facade，请使用 `Config::set` 方法设置配置值。
<a name="facade-spies"></a>
### Facade 监视器

如果你想对某个 Facade 进行 监视（spy），可以直接在对应的 Facade 上调用 spy 方法。Spy 与 Mock 类似，但它会记录代码与该对象之间的所有交互，从而允许你在执行完逻辑后再进行断言：

```php tab=Pest
<?php

use Illuminate\Support\Facades\Cache;

test('values are be stored in cache', function () {
    Cache::spy();

    $response = $this->get('/');

    $response->assertStatus(200);

    Cache::shouldHaveReceived('put')->with('name', 'Taylor', 10);
});
```

```php tab=PHPUnit
use Illuminate\Support\Facades\Cache;

public function test_values_are_be_stored_in_cache(): void
{
    Cache::spy();

    $response = $this->get('/');

    $response->assertStatus(200);

    Cache::shouldHaveReceived('put')->with('name', 'Taylor', 10);
}
```



## 与时间交互
在编写测试时，有时你可能需要修改辅助函数如 now 或 Illuminate\Support\Carbon::now() 返回的当前时间。Laravel 的基础测试类提供了便捷的方法来操控当前时间：

```php tab=Pest
test('time can be manipulated', function () {
    // 向未来穿越...
    $this->travel(5)->milliseconds();
    $this->travel(5)->seconds();
    $this->travel(5)->minutes();
    $this->travel(5)->hours();
    $this->travel(5)->days();
    $this->travel(5)->weeks();
    $this->travel(5)->years();

    // 向过去穿越...
    $this->travel(-5)->hours();

    // 穿越到指定时间...
    $this->travelTo(now()->subHours(6));

    // 返回现在...
    $this->travelBack();
});
```

```php tab=PHPUnit
public function test_time_can_be_manipulated(): void
{
    // 向未来穿越...
    $this->travel(5)->milliseconds();
    $this->travel(5)->seconds();
    $this->travel(5)->minutes();
    $this->travel(5)->hours();
    $this->travel(5)->days();
    $this->travel(5)->weeks();
    $this->travel(5)->years();

    // 向过去穿越...
    $this->travel(-5)->hours();

    // 穿越到指定时间...
    $this->travelTo(now()->subHours(6));

    // 返回现在...
    $this->travelBack();
}
```

你也可以为时间旅行方法传入一个闭包，Laravel 会在指定时间“冻结”时间，然后执行闭包中的代码。一旦闭包执行完毕，时间将恢复正常流动：

```php
$this->travel(5)->days(function () {
    // 测试未来五天后的某些操作...
});

$this->travelTo(now()->subDays(10), function () {
    // 测试过去十天前某一刻的行为...
});
```

你还可以使用 freezeTime 方法冻结当前时间；如果只希望冻结到当前秒的起始位置，则可以使用 freezeSecond 方法：

```php
use Illuminate\Support\Carbon;

// 冻结时间，在闭包执行后恢复...
$this->freezeTime(function (Carbon $time) {
    // ...
});

// 冻结到当前秒的起始位置，闭包执行后恢复...
$this->freezeSecond(function (Carbon $time) {
    // ...
})
```



当然，前文提到的所有方法，主要都是用于测试与时间有关的应用行为，比如：在论坛中锁定一周内未活跃的帖子：

```php tab=Pest
use App\Models\Thread;

test('forum threads lock after one week of inactivity', function () {
    $thread = Thread::factory()->create();

    $this->travel(1)->week();

    expect($thread->isLockedByInactivity())->toBeTrue();
});
```

```php tab=PHPUnit
use App\Models\Thread;

public function test_forum_threads_lock_after_one_week_of_inactivity()
{
    $thread = Thread::factory()->create();

    $this->travel(1)->week();

    $this->assertTrue($thread->isLockedByInactivity());
}
```
