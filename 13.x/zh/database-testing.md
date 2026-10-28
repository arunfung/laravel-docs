# 数据库测试

- [简介](#introduction)
    - [每次测试后重置数据库](#resetting-the-database-after-each-test)
- [模型工厂](#model-factories)
- [运行 Seeder](#running-seeders)
- [可用断言](#available-assertions)

<a name="introduction"></a>
## 简介

Laravel 提供了多种实用工具和断言，让你更轻松地测试基于数据库的应用。此外，Laravel 的模型工厂和 Seeder 让你能够方便地利用应用的 Eloquent 模型及其关系创建供测试使用的数据库记录。下文将介绍这些强大的功能。

<a name="resetting-the-database-after-each-test"></a>
### 每次测试后重置数据库

在进一步介绍之前，我们先来讨论如何在每次测试后重置数据库，避免前一次测试的数据干扰后续测试。Laravel 内置的 `Illuminate\Foundation\Testing\RefreshDatabase` trait 可以为你完成这项工作。只需在测试类中使用该 trait：

```php tab=Pest
<?php

use Illuminate\Foundation\Testing\RefreshDatabase;

pest()->use(RefreshDatabase::class);

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
     * 一个基本的功能测试示例。
     */
    public function test_basic_example(): void
    {
        $response = $this->get('/');

        // ...
    }
}
```

如果数据库结构已经是最新状态，`Illuminate\Foundation\Testing\RefreshDatabase` trait 就不会执行数据库迁移，而只会在数据库事务中运行测试。因此，未使用该 trait 的测试用例写入数据库的记录，仍可能留在数据库中。

如果你希望彻底重置数据库，可以改用 `Illuminate\Foundation\Testing\DatabaseMigrations` 或 `Illuminate\Foundation\Testing\DatabaseTruncation` trait。不过，这两种方式都明显慢于 `RefreshDatabase` trait。

<a name="model-factories"></a>
## 模型工厂

测试时，你可能需要在执行测试之前向数据库插入一些记录。创建这些测试数据时，你无需手动指定每一列的值，Laravel 允许你通过[模型工厂](/docs/{{version}}/eloquent-factories)为每个 [Eloquent 模型](/docs/{{version}}/eloquent)定义一组默认属性。

要进一步了解如何定义模型工厂并使用它创建模型，请参阅完整的[模型工厂文档](/docs/{{version}}/eloquent-factories)。定义模型工厂后，你就可以在测试中使用该工厂创建模型：

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

<a name="running-seeders"></a>
## 运行 Seeder

如果你想在功能测试期间使用[数据库 Seeder](/docs/{{version}}/seeding)填充数据库，可以调用 `seed` 方法。默认情况下，`seed` 方法会执行 `DatabaseSeeder`，该类应当调用你的其他所有 Seeder。你也可以向 `seed` 方法传入指定的 Seeder 类名：

```php tab=Pest
<?php

use Database\Seeders\OrderStatusSeeder;
use Database\Seeders\TransactionStatusSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;

pest()->use(RefreshDatabase::class);

test('orders can be created', function () {
    // 运行 DatabaseSeeder……
    $this->seed();

    // 运行指定的 Seeder……
    $this->seed(OrderStatusSeeder::class);

    // ...

    // 运行数组中指定的多个 Seeder……
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
     * 测试创建新订单。
     */
    public function test_orders_can_be_created(): void
    {
        // 运行 DatabaseSeeder……
        $this->seed();

        // 运行指定的 Seeder……
        $this->seed(OrderStatusSeeder::class);

        // ...

        // 运行数组中指定的多个 Seeder……
        $this->seed([
            OrderStatusSeeder::class,
            TransactionStatusSeeder::class,
            // ...
        ]);
    }
}
```

你也可以让 Laravel 在每个使用 `RefreshDatabase` trait 的测试运行之前，自动填充数据库。只需在基础测试类上添加 `Seed` 特性：

```php
<?php

namespace Tests;

use Illuminate\Foundation\Testing\Attributes\Seed;
use Illuminate\Foundation\Testing\TestCase as BaseTestCase;

#[Seed]
abstract class TestCase extends BaseTestCase
{
}
```

添加 `Seed` 特性后，Laravel 会在每个使用 `RefreshDatabase` trait 的测试运行之前，执行 `Database\Seeders\DatabaseSeeder` 类。如果你希望运行指定的 Seeder，可以在测试类上使用 `Seeder` 特性：

```php
<?php

namespace Tests\Feature;

use Database\Seeders\OrderStatusSeeder;
use Illuminate\Foundation\Testing\Attributes\Seeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

#[Seeder(OrderStatusSeeder::class)]
class OrderTest extends TestCase
{
    use RefreshDatabase;

    // ...
}
```

<a name="available-assertions"></a>
## 可用断言

Laravel 为 [Pest](https://pestphp.com) 或 [PHPUnit](https://phpunit.de) 功能测试提供了多种数据库断言。下面将逐一介绍这些断言。

<a name="assert-database-count"></a>
#### assertDatabaseCount

断言数据库中的某张表包含给定数量的记录：

```php
$this->assertDatabaseCount('users', 5);
```

<a name="assert-database-empty"></a>
#### assertDatabaseEmpty

断言数据库中的某张表不包含任何记录：

```php
$this->assertDatabaseEmpty('users');
```

<a name="assert-database-has"></a>
#### assertDatabaseHas

断言数据库中的某张表包含符合给定键值查询条件的记录：

```php
$this->assertDatabaseHas('users', [
    'email' => 'sally@example.com',
]);
```

<a name="assert-database-missing"></a>
#### assertDatabaseMissing

断言数据库中的某张表不包含符合给定键值查询条件的记录：

```php
$this->assertDatabaseMissing('users', [
    'email' => 'sally@example.com',
]);
```

<a name="assert-deleted"></a>
#### assertSoftDeleted

`assertSoftDeleted` 方法用于断言给定的 Eloquent 模型已被「软删除」：

```php
$this->assertSoftDeleted($user);
```

<a name="assert-not-deleted"></a>
#### assertNotSoftDeleted

`assertNotSoftDeleted` 方法用于断言给定的 Eloquent 模型未被「软删除」：

```php
$this->assertNotSoftDeleted($user);
```

<a name="assert-model-exists"></a>
#### assertModelExists

断言给定模型或模型集合中的所有模型都存在于数据库中：

```php
use App\Models\User;

$user = User::factory()->create();

$this->assertModelExists($user);
```

<a name="assert-model-missing"></a>
#### assertModelMissing

断言给定模型或模型集合中的所有模型都不存在于数据库中：

```php
use App\Models\User;

$user = User::factory()->create();

$user->delete();

$this->assertModelMissing($user);
```

<a name="expects-database-query-count"></a>
#### expectsDatabaseQueryCount

你可以在测试开始时调用 `expectsDatabaseQueryCount` 方法，指定测试期间预期执行的数据库查询总数。如果实际执行的查询数量与预期不完全一致，测试就会失败：

```php
$this->expectsDatabaseQueryCount(5);

// 执行测试……
```
