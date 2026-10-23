
# 测试：入门

- [介绍](#introduction)
- [环境](#environment)
- [创建测试](#creating-tests)
- [运行测试](#running-tests)
    - [并行运行测试](#running-tests-in-parallel)
    - [报告测试覆盖率](#reporting-test-coverage)
    - [测试分析](#profiling-tests)

<a name="introduction"></a>
## 介绍

Laravel 是以测试为中心构建的。实际上，框架内置了对 [Pest](https://pestphp.com) 和 [PHPUnit](https://phpunit.de) 的支持，并且已经为您的应用程序设置了一个 `phpunit.xml` 文件。框架还提供了方便的辅助方法，使您能够直观地测试您的应用程序。

默认情况下，您的应用程序的 `tests` 目录包含两个目录： `Feature` 和 `Unit` 。单元测试是专注于代码中非常小的、独立部分的测试。实际上，大多数单元测试可能只关注一个方法。"Unit" 测试目录中的测试不会启动您的 Laravel 应用程序，因此无法访问应用程序的数据库或其他框架服务。

功能测试可能会测试代码的更大部分，包括多个对象如何相互交互，甚至是对 JSON 端点的完整 HTTP 请求。 **通常，您的大多数测试应该是功能测试。这些类型的测试提供了系统整体正常运行的最大信心。**

在 `Feature` 和 `Unit` 测试目录中都提供了一个 `ExampleTest.php` 文件。安装新的 Laravel 应用程序后，执行  `vendor/bin/pest`、`vendor/bin/phpunit` 和 `php artisan test` 命令来运行您的测试。

<a name="environment"></a>


## 环境（Environment）

运行测试时，Laravel 会**自动将配置环境设置为 `testing`**，这是由于 `phpunit.xml` 文件中定义了相应的环境变量。
此外，Laravel 会将 **session 与 cache 驱动设置为 `array`**，以确保在测试过程中不会有数据被持久化。
您可以根据需要定义其他测试环境配置值。`testing` 环境变量可以在应用程序的 `phpunit.xml` 文件中配置，但在运行测试之前，请确保使用 `config:clear` Artisan 命令清除配置缓存！

#### .env.testing 文件

此外，你可以在项目根目录创建一个 `.env.testing` 文件。当你运行 Pest 或 PHPUnit 测试，或者使用 `--env=testing` 选项执行 Artisan 命令时，该文件将代替 `.env` 文件被加载

## 创建测试

要创建一个新的测试用例，可以使用 `make:test` Artisan 命令。默认情况下，测试文件将被放置在 `tests/Feature` 目录下：

```shell
php artisan make:test UserTest
```

如果你希望在 `tests/Unit` 目录中创建测试，可以在执行命令时添加 `--unit` 选项：

```shell
php artisan make:test UserTest --unit
```

> [!笔记]
> 你可以通过 [发布 stub 文件](/docs/laravel/12.x/artisan#stub-customization) 来自定义测试模板。

生成测试后，您可以使用 Pest 或 PHPUnit 正常定义测试。要运行测试，请从终端执行 `vendor/bin/pest`、`vendor/bin/phpunit` 或 `php artisan test` 命令：

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
     * 一个基础的测试示例。
     */
    public function test_basic_test(): void
    {
        $this->assertTrue(true);
    }
}
```

> [!警告]
> 如果你在测试类中自定义了 `setUp` / `tearDown` 方法，请务必调用父类的 `parent::setUp()` / `parent::tearDown()` 方法。通常，应在你自定义的 `setUp` 方法开头调用 `parent::setUp()`，并在 `tearDown` 方法末尾调用 `parent::tearDown()`。



## 运行测试

如前所述，编写好测试后，你可以使用 `pest` 或 `phpunit` 来运行它们：

```shell tab=Pest
./vendor/bin/pest
```

```shell tab=PHPUnit
./vendor/bin/phpunit
```

除了使用 `pest` 或 `phpunit` 命令，你还可以使用 Artisan 的 `test` 命令来运行测试。Artisan 的测试运行器会提供详细的测试报告，以便开发和调试：

```shell
php artisan test
```

任何可以传递给 `pest` 或 `phpunit` 的参数，也可以传递给 Artisan 的 `test` 命令：

```shell
php artisan test --testsuite=Feature --stop-on-failure
```

### 并行运行测试

默认情况下，Laravel 以及 Pest / PHPUnit 会在单个进程中顺序执行你的测试。不过，你可以通过在多个进程中同时运行测试来大幅缩短运行时间。首先，需要将 `brianium/paratest` 安装为开发依赖：

```shell
composer require brianium/paratest --dev

php artisan test --parallel
```

默认情况下，Laravel 会根据你的机器的 CPU 核心数来创建相应数量的进程。当然，你也可以使用 `--processes` 选项自定义进程数：

```shell
php artisan test --parallel --processes=4
```

> ⚠️ 注意
> 在并行运行测试时，某些 Pest / PHPUnit 的选项（如 --do-not-cache-result）可能不可用。


#### 并行测试与数据库

只要你配置了主数据库连接，Laravel 就会自动为每个并行进程创建并迁移一个测试数据库。这些测试数据库将会加上进程唯一的后缀标识。例如，如果你有两个并行测试进程，Laravel 将会分别创建并使用 `your_db_test_1` 和 `your_db_test_2` 数据库。



默认情况下，测试数据库会在每次调用 `test` Artisan 命令之后保留，以便后续的测试命令可以继续使用它们。不过，你也可以使用 `--recreate-databases` 选项强制重新创建数据库：

```shell
php artisan test --parallel --recreate-databases
```

#### 并行测试钩子（Hooks）

有时，你可能需要为应用的测试准备某些资源，以确保它们可以在多个测试进程中安全使用。

你可以通过 `ParallelTesting` facade 来定义在每个进程或测试用例的 `setUp` 和 `tearDown` 时执行的代码。提供的闭包将接收 `$token` 和 `$testCase` 变量，分别表示进程的标识符和当前的测试用例实例：

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

        // 当测试数据库被创建时执行...
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

#### 获取并行测试的 Token

如果你希望在应用测试代码的其他部分访问当前的并行进程标识符（token），可以使用 `token` 方法。这个 token 是当前测试进程的唯一字符串标识符，可用于区分不同的资源。例如，Laravel 会自动将这个 token 添加到每个并行测试进程所使用的测试数据库名称中：

    $token = ParallelTesting::token();



### 报告测试覆盖率

> [!警告]
> 此功能需要安装 [Xdebug](https://xdebug.org) 或 [PCOV](https://pecl.php.net/package/pcov)。

在运行应用测试时，你可能希望了解测试用例是否真正覆盖了应用程序代码，以及运行测试时实际使用了多少应用代码。为此，你可以在执行 `test` 命令时添加 `--coverage` 选项：

```shell
php artisan test --coverage
```

#### 强制执行最低覆盖率阈值

你可以使用 --min 选项为应用程序设置一个最低测试覆盖率阈值。如果测试覆盖率未达到该阈值，则测试套件将失败：

```shell
php artisan test --coverage --min=80.3
```

### 性能分析

Artisan 的测试运行器还提供了一个方便的功能，可以列出应用中执行时间最慢的测试。使用 `--profile` 选项运行 `test` 命令时，将显示前十个最慢的测试，帮助你轻松分析并优化测试套件中的瓶颈：

```shell
php artisan test --profile
```
