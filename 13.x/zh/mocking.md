# 测试模拟器

- [简介](#introduction)
- [模拟对象](#mocking-objects)
- [模拟 Facade](#mocking-facades)
    - [Facade 监视器](#facade-spies)
- [与时间交互](#interacting-with-time)

<a name="introduction"></a>
## 简介

测试 Laravel 应用时，你可能希望「模拟（mock）」应用的某些部分，使其在特定测试中不被实际执行。例如，测试一个会分发事件的控制器时，你可能希望模拟事件监听器，避免它们在测试中真正运行。这样，你就可以专注于测试控制器的 HTTP 响应，而无需考虑事件监听器的执行情况，因为监听器可以在独立的测试用例中测试。

Laravel 内置了便捷的方法，用于模拟事件、任务和其他 Facade。这些辅助方法主要是对 Mockery 的封装，让你无需手动编写复杂的 Mockery 方法调用。

<a name="mocking-objects"></a>
## 模拟对象

如果要模拟的对象会通过 Laravel 的 [服务容器](/docs/{{version}}/container) 注入应用，你需要以 `instance` 绑定的方式，将模拟实例绑定到容器中。这样，容器就会使用你提供的模拟实例，而不会自行构造该对象：

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

为了简化这一操作，你可以使用 Laravel 测试基类提供的 `mock` 方法。例如，以下示例与上面的示例等效：

```php
use App\Service;
use Mockery\MockInterface;

$mock = $this->mock(Service::class, function (MockInterface $mock) {
    $mock->expects('process');
});
```

如果只需要模拟对象的部分方法，可以使用 `partialMock` 方法。未被模拟的方法在调用时会正常执行：

```php
use App\Service;
use Mockery\MockInterface;

$mock = $this->partialMock(Service::class, function (MockInterface $mock) {
    $mock->expects('process');
});
```

同样，如果你想对某个对象进行 [监视（spy）](http://docs.mockery.io/en/latest/reference/spies.html)，Laravel 测试基类也提供了 `spy` 方法，方便你调用其封装的 `Mockery::spy` 方法。监视对象与模拟对象类似，但监视对象会记录它与被测代码之间的所有交互，让你可以在代码执行完毕后进行断言：

```php
use App\Service;

$spy = $this->spy(Service::class);

// ...

$spy->shouldHaveReceived('process');
```

<a name="mocking-facades"></a>
## 模拟 Facade

你可以模拟 [Facade](/docs/{{version}}/facades)（包括 [实时 Facade](/docs/{{version}}/facades#real-time-facades)），这是它相较于传统静态方法调用的一大优势，让你获得与传统依赖注入相同的可测试性。测试时，你可能经常需要模拟控制器中对某个 Laravel Facade 的调用。例如，考虑以下控制器方法：

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Cache;

class UserController extends Controller
{
    /**
     * 获取应用中所有用户的列表。
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

我们可以使用 `expects` 方法模拟对 `Cache` Facade 的调用，该方法会返回一个 [Mockery](https://github.com/padraic/mockery) 模拟实例。由于 Facade 实际上由 Laravel 的 [服务容器](/docs/{{version}}/container) 解析和管理，因此它们比普通静态类更易于测试。例如，下面模拟了对 `Cache` Facade 的 `get` 方法的调用：

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

> [!WARNING]
> 你不应模拟 `Request` Facade。运行测试时，应将所需的输入传给 `get`、`post` 等 [HTTP 测试方法](/docs/{{version}}/http-tests)。同样，也不应模拟 `Config` Facade，而应在测试中调用 `Config::set` 方法。

<a name="facade-spies"></a>
### Facade 监视器

如果你想 [监视（spy）](http://docs.mockery.io/en/latest/reference/spies.html) 某个 Facade，可以在相应的 Facade 上调用 `spy` 方法。监视对象与模拟对象类似，但监视对象会记录它与被测代码之间的所有交互，让你可以在代码执行完毕后进行断言：

```php tab=Pest
<?php

use Illuminate\Support\Facades\Cache;

test('values are stored in cache', function () {
    Cache::spy();

    $response = $this->get('/');

    $response->assertStatus(200);

    Cache::shouldHaveReceived('put')->with('name', 'Taylor', 10);
});
```

```php tab=PHPUnit
use Illuminate\Support\Facades\Cache;

public function test_values_are_stored_in_cache(): void
{
    Cache::spy();

    $response = $this->get('/');

    $response->assertStatus(200);

    Cache::shouldHaveReceived('put')->with('name', 'Taylor', 10);
}
```

<a name="interacting-with-time"></a>
## 与时间交互

测试时，你有时需要修改 `now` 或 `Illuminate\Support\Carbon::now()` 等辅助方法返回的时间。Laravel 的功能测试基类提供了辅助方法，让你可以操控当前时间：

```php tab=Pest
test('time can be manipulated', function () {
    // 前往未来……
    $this->travel(5)->milliseconds();
    $this->travel(5)->seconds();
    $this->travel(5)->minutes();
    $this->travel(5)->hours();
    $this->travel(5)->days();
    $this->travel(5)->weeks();
    $this->travel(5)->years();

    // 回到过去……
    $this->travel(-5)->hours();

    // 前往指定时刻……
    $this->travelTo(now()->minus(hours: 6));

    // 返回当前时间……
    $this->travelBack();
});
```

```php tab=PHPUnit
public function test_time_can_be_manipulated(): void
{
    // 前往未来……
    $this->travel(5)->milliseconds();
    $this->travel(5)->seconds();
    $this->travel(5)->minutes();
    $this->travel(5)->hours();
    $this->travel(5)->days();
    $this->travel(5)->weeks();
    $this->travel(5)->years();

    // 回到过去……
    $this->travel(-5)->hours();

    // 前往指定时刻……
    $this->travelTo(now()->minus(hours: 6));

    // 返回当前时间……
    $this->travelBack();
}
```

你也可以向各种时间旅行方法传入闭包。闭包执行期间，时间会冻结在指定时刻。闭包执行完毕后，时间将恢复正常：

```php
$this->travel(5)->days(function () {
    // 测试五天后的某项行为……
});

$this->travelTo(now()->minus(days: 10), function () {
    // 测试指定时刻的某项行为……
});
```

`freezeTime` 方法可以冻结当前时间。类似地，`freezeSecond` 方法会将时间冻结在当前秒的起始处：

```php
use Illuminate\Support\Carbon;

// 冻结时间，执行闭包后恢复正常时间……
$this->freezeTime(function (Carbon $time) {
    // ...
});

// 将时间冻结在当前秒的起始处，执行闭包后恢复正常时间……
$this->freezeSecond(function (Carbon $time) {
    // ...
});
```

上述所有方法主要用于测试与时间有关的应用行为，例如锁定论坛中长时间未活跃的帖子：

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
