
# 数据库测试

- [简介](#introduction)
    - [在每次测试后重置数据库](#resetting-the-database-after-each-test)
- [使用模型工厂](#model-factories)
- [运行 Seeder](#running-seeders)
- [可用断言](#available-assertions)


## 简介

Laravel 提供了多种实用工具与断言，助你更轻松地测试基于数据库的应用程序。此外，Laravel 的模型工厂与 Seeder 能让你毫不费力地利用 Eloquent 模型及其关系创建测试用的数据库记录。接下来的文档将会介绍这些强大的功能。

### 在每次测试后重置数据库

在深入了解前，先来说说如何在每一次测试后重置数据库，以避免前一次测试的数据干扰后续测试。Laravel 提供了内建的 Illuminate\Foundation\Testing\RefreshDatabase Trait 来帮你完成这一操作。只需在测试类中使用该 Trait 即可：

```php tab=Pest
<?php

use Illuminate\Foundation\Testing\RefreshDatabase;

uses(RefreshDatabase::class);

test('basic example', function () {
    $response = $this->get('/');

    // ...
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    use RefreshDatabase;

    /**
     * A basic functional test example.
     */
    public function test_basic_example(): void
    {
        $response = $this->get('/');

        // ...
    }
}
```

Illuminate\Foundation\Testing\RefreshDatabase 这个 Trait 不会在数据库架构已经是最新状态时再次执行迁移操作。它只是将测试用例包裹在一个数据库事务中执行。因此，那些没有使用该 Trait 的测试所写入的记录，仍可能会残留在数据库中。



如果你希望彻底重置数据库，可以改用 Illuminate\Foundation\Testing\DatabaseMigrations 或 Illuminate\Foundation\Testing\DatabaseTruncation 这两个 Trait。然而，这两种方式的执行速度都比 RefreshDatabase 要慢得多。


## 模型工厂

在进行测试时，你可能需要在执行测试之前先插入一些数据记录。与其每次都手动填写每个字段的值，Laravel 更推荐你为每个 [Eloquent 模型](/docs/laravel/12.x/eloquent) 定义一组默认属性，这正是 [模型工厂](/docs/laravel/12.x/eloquent-factories) 的用武之地。

想了解如何创建和使用模型工厂，请参阅完整的 [模型工厂文档](/docs/laravel/12.x/eloquent-factories)。一旦定义好模型工厂后，你就可以在测试中直接调用：
```php tab=Pest
use App\Models\User;

test('models can be instantiated', function () {
    $user = User::factory()->create();

    // ...
});
```

```php tab=PHPUnit
use App\Models\User;

public function test_models_can_be_instantiated(): void
{
    $user = User::factory()->create();

    // ...
}
```

## 运行 Seeder

如果你希望在功能测试中使用 [数据库 Seeder](/docs/laravel/12.x/seeding) 来填充测试数据，可以使用 `seed` 方法。默认情况下，`seed` 方法会执行 `DatabaseSeeder` 类，该类通常会调用你所有其他的 Seeder。当然，你也可以传入指定的 Seeder 类名来只运行特定 Seeder：

```php tab=Pest
<?php

use Database\Seeders\OrderStatusSeeder;
use Database\Seeders\TransactionStatusSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;

uses(RefreshDatabase::class);

test('orders can be created', function () {
     // 执行 DatabaseSeeder...
    $this->seed();

    // 执行指定的 Seeder...
    $this->seed(OrderStatusSeeder::class);

    // ...

    // 执行多个指定的 Seeder...
    $this->seed([
        OrderStatusSeeder::class,
        TransactionStatusSeeder::class,
        // ...
    ]);
});
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Database\Seeders\OrderStatusSeeder;
use Database\Seeders\TransactionStatusSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    use RefreshDatabase;

    /**
     * 测试新订单的创建流程.
     */
    public function test_orders_can_be_created(): void
    {
        // 执行 DatabaseSeeder...
        $this->seed();

        // 执行指定的 Seeder...
        $this->seed(OrderStatusSeeder::class);

        // ...

        // 执行多个指定的 Seeder...
        $this->seed([
            OrderStatusSeeder::class,
            TransactionStatusSeeder::class,
            // ...
        ]);
    }
}
```



你也可以让 Laravel 在每次执行使用 `RefreshDatabase` Trait 的测试前，**自动运行数据库 Seeder**。只需在你的基础测试类中定义一个 `$seed` 属性即可实现这一行为：
```php
<?php

namespace Tests;

use Illuminate\Foundation\Testing\TestCase as BaseTestCase;

abstract class TestCase extends BaseTestCase
{
    /**
     * 是否在每次测试前运行默认 Seeder。
     *
     * @var bool
     */
    protected $seed = true;
}
```

当 $seed 属性设置为 true 时，Laravel 会在每个测试开始前执行 Database\Seeders\DatabaseSeeder 类。
如果你想指定特定的 Seeder，而不是默认的 DatabaseSeeder，可以在测试类中定义 $seeder 属性来实现：

```php
use Database\Seeders\OrderStatusSeeder;

/**
 * 在每个测试前运行指定的 Seeder。
 *
 * @var string
 */
protected $seeder = OrderStatusSeeder::class;
```

## 可用断言

Laravel 为 [Pest](https://pestphp.com) 和 [PHPUnit](https://phpunit.de) 的功能测试提供了多种数据库断言。下面是各个断言的具体介绍：

#### assertDatabaseCount

断言数据库中的某个表包含指定数量的记录：

```php
$this->assertDatabaseCount('users', 5);
```

#### assertDatabaseEmpty

断言数据库中的某个表不包含任何记录：

```php
$this->assertDatabaseEmpty('users');
```

#### assertDatabaseHas

断言数据库中的某个表包含符合指定键值条件的记录：

```php
$this->assertDatabaseHas('users', [
    'email' => 'sally@example.com',
]);
```

#### assertDatabaseMissing

断言数据库中的某个表不包含符合指定键值条件的记录：

```php
$this->assertDatabaseMissing('users', [
    'email' => 'sally@example.com',
]);
```



#### assertSoftDeleted

assertSoftDeleted 方法用于断言某个 Eloquent 模型已被「软删除」：

```php
$this->assertSoftDeleted($user);
```

#### assertNotSoftDeleted

assertNotSoftDeleted 方法用于断言某个 Eloquent 模型没有被软删除：

```php
$this->assertNotSoftDeleted($user);
```

#### assertModelExists

断言指定模型在数据库中确实存在：

```php
use App\Models\User;

$user = User::factory()->create();

$this->assertModelExists($user);
```

#### assertModelMissing

断言指定模型在数据库中不存在（例如已被删除）：

```php
use App\Models\User;

$user = User::factory()->create();

$user->delete();

$this->assertModelMissing($user);
```

#### expectsDatabaseQueryCount

可以在测试开始处调用 `expectsDatabaseQueryCount` 方法，明确**预期的数据库查询总数**。如果实际执行的查询数量与期望不一致，测试将失败：

```php
$this->expectsDatabaseQueryCount(5);

// Test...
```
