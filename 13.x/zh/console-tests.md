# 命令行测试

- [简介](#introduction)
- [成功 / 失败预期](#success-failure-expectations)
- [输入 / 输出预期](#input-output-expectations)
- [控制台事件](#console-events)

<a name="introduction"></a>
## 简介

除了简化 HTTP 测试，Laravel 还提供了简洁的 API，用于测试应用的[自定义控制台命令](/docs/{{version}}/artisan)。

<a name="success-failure-expectations"></a>
## 成功 / 失败预期

首先，让我们看看如何对 Artisan 命令的退出码进行断言。我们会使用 `artisan` 方法在测试中调用 Artisan 命令，再使用 `assertExitCode` 方法断言该命令以给定的退出码结束：

```php tab=Pest
test('console command', function () {
    $this->artisan('inspire')->assertExitCode(0);
});
```

```php tab=PHPUnit
/**
 * 测试一个控制台命令。
 */
public function test_console_command(): void
{
    $this->artisan('inspire')->assertExitCode(0);
}
```

你可以使用 `assertNotExitCode` 方法，断言命令没有以给定的退出码结束：

```php
$this->artisan('inspire')->assertNotExitCode(1);
```

通常，终端命令在成功时以状态码 `0` 退出，失败时则以非零退出码退出。为方便测试，你可以使用 `assertSuccessful` 和 `assertFailed`，分别断言给定命令是否以成功或失败的退出码结束：

```php
$this->artisan('inspire')->assertSuccessful();

$this->artisan('inspire')->assertFailed();
```

<a name="input-output-expectations"></a>
## 输入 / 输出预期

Laravel 允许你使用 `expectsQuestion` 方法，轻松模拟控制台命令中的用户输入。此外，你可以使用 `assertExitCode` 和 `expectsOutput` 方法，指定命令预期的退出码和输出文本。例如，考虑以下控制台命令：

```php
Artisan::command('question', function () {
    $name = $this->ask('What is your name?');

    $language = $this->choice('Which language do you prefer?', [
        'PHP',
        'Ruby',
        'Python',
    ]);

    $this->line('Your name is '.$name.' and you prefer '.$language.'.');
});
```

你可以编写如下测试：

```php tab=Pest
test('console command', function () {
    $this->artisan('question')
        ->expectsQuestion('What is your name?', 'Taylor Otwell')
        ->expectsQuestion('Which language do you prefer?', 'PHP')
        ->expectsOutput('Your name is Taylor Otwell and you prefer PHP.')
        ->doesntExpectOutput('Your name is Taylor Otwell and you prefer Ruby.')
        ->assertExitCode(0);
});
```

```php tab=PHPUnit
/**
 * 测试一个控制台命令。
 */
public function test_console_command(): void
{
    $this->artisan('question')
        ->expectsQuestion('What is your name?', 'Taylor Otwell')
        ->expectsQuestion('Which language do you prefer?', 'PHP')
        ->expectsOutput('Your name is Taylor Otwell and you prefer PHP.')
        ->doesntExpectOutput('Your name is Taylor Otwell and you prefer Ruby.')
        ->assertExitCode(0);
}
```

如果你使用了 [Laravel Prompts](/docs/{{version}}/prompts) 提供的 `search` 或 `multisearch` 函数，可以使用 `expectsSearch` 断言来模拟用户输入、搜索结果及最终选择：

```php tab=Pest
test('console command', function () {
    $this->artisan('example')
        ->expectsSearch('What is your name?', search: 'Tay', answers: [
            'Taylor Otwell',
            'Taylor Swift',
            'Darian Taylor'
        ], answer: 'Taylor Otwell')
        ->assertExitCode(0);
});
```

```php tab=PHPUnit
/**
 * 测试一个控制台命令。
 */
public function test_console_command(): void
{
    $this->artisan('example')
        ->expectsSearch('What is your name?', search: 'Tay', answers: [
            'Taylor Otwell',
            'Taylor Swift',
            'Darian Taylor'
        ], answer: 'Taylor Otwell')
        ->assertExitCode(0);
}
```

你也可以使用 `doesntExpectOutput` 方法，断言控制台命令不会产生任何输出：

```php tab=Pest
test('console command', function () {
    $this->artisan('example')
        ->doesntExpectOutput()
        ->assertExitCode(0);
});
```

```php tab=PHPUnit
/**
 * 测试一个控制台命令。
 */
public function test_console_command(): void
{
    $this->artisan('example')
        ->doesntExpectOutput()
        ->assertExitCode(0);
}
```

你可以使用 `expectsOutputToContain` 和 `doesntExpectOutputToContain` 方法，对输出中的部分内容进行断言：

```php tab=Pest
test('console command', function () {
    $this->artisan('example')
        ->expectsOutputToContain('Taylor')
        ->assertExitCode(0);
});
```

```php tab=PHPUnit
/**
 * 测试一个控制台命令。
 */
public function test_console_command(): void
{
    $this->artisan('example')
        ->expectsOutputToContain('Taylor')
        ->assertExitCode(0);
}
```

<a name="confirmation-expectations"></a>
#### 确认提示预期

如果你编写的命令需要用户以「是」或「否」的形式进行确认，可以使用 `expectsConfirmation` 方法：

```php
$this->artisan('module:import')
    ->expectsConfirmation('Do you really wish to run this command?', 'no')
    ->assertExitCode(1);
```

<a name="table-expectations"></a>
#### 表格输出预期

如果命令使用 Artisan 的 `table` 方法展示表格信息，为整个表格编写输出预期可能会很繁琐。此时，你可以使用 `expectsTable` 方法。该方法的第一个参数接收表头，第二个参数接收表格数据：

```php
$this->artisan('users:all')
    ->expectsTable([
        'ID',
        'Email',
    ], [
        [1, 'taylor@example.com'],
        [2, 'abigail@example.com'],
    ]);
```

<a name="console-events"></a>
## 控制台事件

默认情况下，运行应用测试时不会派发 `Illuminate\Console\Events\CommandStarting` 和 `Illuminate\Console\Events\CommandFinished` 事件。不过，你可以为测试类添加 `Illuminate\Foundation\Testing\WithConsoleEvents` trait，为该类启用这些事件：

```php tab=Pest
<?php

use Illuminate\Foundation\Testing\WithConsoleEvents;

pest()->use(WithConsoleEvents::class);

// ...
```

```php tab=PHPUnit
<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\WithConsoleEvents;
use Tests\TestCase;

class ConsoleEventTest extends TestCase
{
    use WithConsoleEvents;

    // ...
}
```
