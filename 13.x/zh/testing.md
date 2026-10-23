# 测试：入门

- [简介](#introduction)
- [环境](#environment)
- [创建测试](#creating-tests)
- [运行测试](#running-tests)
    - [并行运行测试](#running-tests-in-parallel)
    - [生成测试覆盖率报告](#reporting-test-coverage)
    - [测试性能分析](#profiling-tests)
- [配置缓存](#configuration-caching)

<a name="introduction"></a>
## 简介

Laravel 在设计时就考虑了测试。事实上，框架开箱即支持使用 [Pest](https://pestphp.com) 和 [PHPUnit](https://phpunit.de) 进行测试，并已为你的应用配置好 `phpunit.xml` 文件。框架还提供了便捷的辅助方法，让你能够以清晰易读的方式测试应用。

默认情况下，应用的 `tests` 目录包含两个子目录：`Feature` 和 `Unit`。单元测试专注于代码中很小且独立的一部分。事实上，大多数单元测试可能只针对一个方法。「Unit」测试目录中的测试不会启动 Laravel 应用，因此无法访问应用的数据库或其他框架服务。

功能测试可以测试更大范围的代码，包括多个对象之间的交互，甚至是向 JSON 端点发送的完整 HTTP 请求。**通常，你的大多数测试都应该是功能测试。这类测试最能让你确信整个系统按预期运行。**

`Feature` 和 `Unit` 测试目录中都提供了一个 `ExampleTest.php` 文件。安装新的 Laravel 应用后，执行 `vendor/bin/pest`、`vendor/bin/phpunit` 或 `php artisan test` 命令即可运行测试。

<a name="environment"></a>
## 环境

运行测试时，Laravel 会根据 `phpunit.xml` 文件中定义的环境变量，自动将[配置环境](/docs/{{version}}/configuration#environment-configuration)设为 `testing`。Laravel 还会自动将会话和缓存的驱动设为 `array`，确保测试期间不会持久化任何会话或缓存数据。

你可以根据需要定义其他测试环境配置值。`testing` 环境的变量可以在应用的 `phpunit.xml` 文件中配置，但运行测试前，请务必使用 `config:clear` Artisan 命令清除配置缓存！

<a name="the-env-testing-environment-file"></a>
#### `.env.testing` 环境文件

此外，你可以在项目根目录创建一个 `.env.testing` 文件。运行 Pest 和 PHPUnit 测试，或使用 `--env=testing` 选项执行 Artisan 命令时，该文件将替代 `.env` 文件。

<a name="creating-tests"></a>
## 创建测试

要创建新的测试用例，可以使用 `make:test` Artisan 命令。默认情况下，测试文件会放在 `tests/Feature` 目录中：

```shell
php artisan make:test UserTest
```

如果你想在 `tests/Unit` 目录中创建测试，可以在执行 `make:test` 命令时使用 `--unit` 选项：

```shell
php artisan make:test UserTest --unit
```

如果某个测试类中的大多数测试依赖 Laravel 的测试功能，但其中某个测试方法无需启动框架，你可以为该方法添加 `#[UnitTest]` 特性，仅在运行这个测试时跳过应用启动。

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\Attributes\UnitTest;
use Tests\TestCase;

class LocationServiceTest extends TestCase
{
    public function test_get_coordinates_resolves_address(): void
    {
        // 此测试使用 Laravel 的测试功能……
    }

    #[UnitTest]
    public function test_get_state_returns_state_from_abbreviation(): void
    {
        // 此测试运行时不会启动应用……
    }
}
```

> [!NOTE]
> 你可以通过[发布 stub 文件](/docs/{{version}}/artisan#stub-customization)来自定义测试模板。

生成测试后，你就可以像平常一样使用 Pest 或 PHPUnit 定义测试。要运行测试，请在终端执行 `vendor/bin/pest`、`vendor/bin/phpunit` 或 `php artisan test` 命令：

```php tab=Pest
<?php

test('basic', function () {
    expect(true)->toBeTrue();
});
```

```php tab=PHPUnit
<?php

namespace Tests\Unit;

use PHPUnit\Framework\TestCase;

class ExampleTest extends TestCase
{
    /**
     * 一个基本的测试示例。
     */
    public function test_basic_test(): void
    {
        $this->assertTrue(true);
    }
}
```

> [!WARNING]
> 如果你在测试类中自定义了 `setUp` / `tearDown` 方法，请务必分别调用父类的 `parent::setUp()` / `parent::tearDown()` 方法。通常，你应该在自定义的 `setUp` 方法开头调用 `parent::setUp()`，并在 `tearDown` 方法末尾调用 `parent::tearDown()`。

<a name="running-tests"></a>
## 运行测试

如前所述，编写好测试后，你可以使用 `pest` 或 `phpunit` 来运行测试：

```shell tab=Pest
./vendor/bin/pest
```

```shell tab=PHPUnit
./vendor/bin/phpunit
```

除了使用 `pest` 或 `phpunit` 命令，你还可以使用 `test` Artisan 命令来运行测试。Artisan 测试运行器会提供详细的测试报告，方便开发和调试：

```shell
php artisan test
```

所有可以传递给 `pest` 或 `phpunit` 命令的参数，也都可以传递给 Artisan 的 `test` 命令：

```shell
php artisan test --testsuite=Feature --stop-on-failure
```

<a name="running-tests-in-parallel"></a>
### 并行运行测试

默认情况下，Laravel 和 Pest / PHPUnit 会在单个进程中依次执行测试。不过，你可以通过在多个进程中同时运行测试，大幅缩短测试耗时。首先，将 `brianium/paratest` Composer 包安装为开发依赖。然后，在执行 `test` Artisan 命令时添加 `--parallel` 选项：

```shell
composer require brianium/paratest --dev

php artisan test --parallel
```

默认情况下，Laravel 创建的进程数量与你的机器上可用的 CPU 核心数相同。不过，你可以使用 `--processes` 选项调整进程数量：

```shell
php artisan test --parallel --processes=4
```

> [!WARNING]
> 并行运行测试时，某些 Pest / PHPUnit 选项（如 `--do-not-cache-result`）可能无法使用。

<a name="parallel-testing-and-databases"></a>
#### 并行测试与数据库

只要你配置了主数据库连接，Laravel 就会自动为每个运行测试的并行进程创建测试数据库并执行迁移。这些测试数据库的名称会加上各进程独有的标识符作为后缀。例如，如果你有两个并行测试进程，Laravel 就会创建并使用 `your_db_test_1` 和 `your_db_test_2` 测试数据库。

默认情况下，测试数据库会在多次调用 `test` Artisan 命令之间保留，以便后续运行 `test` 时再次使用。不过，你可以使用 `--recreate-databases` 选项重新创建它们：

```shell
php artisan test --parallel --recreate-databases
```

<a name="parallel-testing-hooks"></a>
#### 并行测试钩子

有时，你可能需要为应用测试准备某些资源，以便多个测试进程能够安全地使用它们。

你可以使用 `ParallelTesting` facade，指定在进程或测试用例的 `setUp` 和 `tearDown` 阶段执行的代码。传入的闭包会接收 `$token` 和 `$testCase` 变量，分别表示进程标识符和当前测试用例：

```php
<?php

namespace App\Providers;

use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\ParallelTesting;
use Illuminate\Support\ServiceProvider;
use PHPUnit\Framework\TestCase;

class AppServiceProvider extends ServiceProvider
{
    /**
     * 启动应用服务。
     */
    public function boot(): void
    {
        ParallelTesting::setUpProcess(function (int $token) {
            // ...
        });

        ParallelTesting::setUpTestCase(function (int $token, TestCase $testCase) {
            // ...
        });

        // 创建测试数据库时执行……
        ParallelTesting::setUpTestDatabase(function (string $database, int $token) {
            Artisan::call('db:seed');
        });

        ParallelTesting::tearDownTestCase(function (int $token, TestCase $testCase) {
            // ...
        });

        ParallelTesting::tearDownProcess(function (int $token) {
            // ...
        });
    }
}
```

<a name="accessing-the-parallel-testing-token"></a>
#### 获取并行测试标识符

如果你想在应用测试代码的其他位置访问当前并行进程的标识符（token），可以使用 `token` 方法。这个标识符是各个测试进程独有的字符串，可用于在并行测试进程之间划分资源。例如，Laravel 会自动将这个标识符追加到每个并行测试进程创建的测试数据库名称末尾：

    $token = ParallelTesting::token();

<a name="reporting-test-coverage"></a>
### 生成测试覆盖率报告

> [!WARNING]
> 此功能需要 [Xdebug](https://xdebug.org) 或 [PCOV](https://pecl.php.net/package/pcov)。

运行应用测试时，你可能想知道测试用例是否真正覆盖了应用代码，以及运行测试时实际执行了多少应用代码。为此，你可以在调用 `test` 命令时添加 `--coverage` 选项：

```shell
php artisan test --coverage
```

<a name="enforcing-a-minimum-coverage-threshold"></a>
#### 强制要求最低覆盖率

你可以使用 `--min` 选项为应用定义最低测试覆盖率。如果覆盖率未达到该阈值，测试套件将失败：

```shell
php artisan test --coverage --min=80.3
```

<a name="profiling-tests"></a>
### 测试性能分析

Artisan 测试运行器还提供了便捷的方式来列出应用中最慢的测试。使用 `--profile` 选项调用 `test` 命令时，会列出耗时最长的十个测试，方便你找出可以优化的测试，加快测试套件的运行速度：

```shell
php artisan test --profile
```

<a name="configuration-caching"></a>
## 配置缓存

运行测试时，Laravel 会为每个测试方法单独启动应用。如果没有缓存的配置文件，每个测试开始时都必须加载应用中的所有配置文件。要在一次测试运行中只构建一次配置，并让所有测试复用它，你可以使用 `Illuminate\Foundation\Testing\WithCachedConfig` trait：

```php tab=Pest
<?php

use Illuminate\Foundation\Testing\WithCachedConfig;

pest()->use(WithCachedConfig::class);

// ...
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\WithCachedConfig;
use Tests\TestCase;

class ConfigTest extends TestCase
{
    use WithCachedConfig;

    // ...
}
```
